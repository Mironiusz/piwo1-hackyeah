import { http } from '@kit.NetworkKit';
import { taskpool } from '@kit.ArkTS';
import { gunzip } from './Inflate';
import {
  COMPRESSION_GZIP, COMPRESSION_NONE, findEntry, parseDirectory, parseHeader, PmDirectory, PmEntry, PmHeader,
  TILE_TYPE_MVT, zxyToTileId
} from './Pmtiles';
import { emptyTile, TileData } from './TileTypes';
import { decodeTileTask } from './TileWorker';

const MAX_CACHE: number = 96;
const MAX_PARALLEL: number = 4;
const RETRY_MS: number = 8000;
const NOTIFY_MS: number = 90;
const TILE_PX: number = 512;
const EARTH_M: number = 40075016.686;
const FIRST_FETCH: number = 16384;
const INIT_TIMEOUT_MS: number = 3000;
const TILE_TIMEOUT_MS: number = 10000;
const MAX_LEAF_DEPTH: number = 3;

export function lonToTileX(lon: number, z: number): number {
  return Math.floor((lon + 180) / 360 * Math.pow(2, z));
}

export function latToTileY(lat: number, z: number): number {
  const r = lat * Math.PI / 180;
  return Math.floor((1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * Math.pow(2, z));
}

/** Longitude of the left edge of tile column x. */
export function tileXToLon(x: number, z: number): number {
  return x / Math.pow(2, z) * 360 - 180;
}

/** Latitude of the top edge of tile row y. */
export function tileYToLat(y: number, z: number): number {
  const n = Math.PI - 2 * Math.PI * y / Math.pow(2, z);
  return Math.atan(Math.sinh(n)) * 180 / Math.PI;
}

/**
 * The base map of Kraków from the one PMTiles archive of the project, read in byte ranges like the web app reads
 * it (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-3 and D-5). It reads the header and the root
 * directory once, then each tile the map asks for: leaf directory if needed, the tile bytes, and decoding on a
 * worker thread. Decoded tiles stay in memory and the map is told when a batch has arrived. Without an address,
 * or when the archive does not answer, the map draws the sample base map bundled in the app.
 */
export class TileStore {
  archiveUrl: string = '';
  ready: boolean = false;
  minZoom: number = 0;
  maxZoom: number = 15;
  /** Grows with every new tile; the map compares it to know when to redraw its base map. */
  version: number = 0;
  onChange: () => void = () => {
  };
  private header: PmHeader | null = null;
  private root: PmDirectory | null = null;
  private leaves: Map<number, PmDirectory> = new Map<number, PmDirectory>();
  private cache: Map<string, TileData> = new Map<string, TileData>();
  private order: string[] = [];
  private pending: Set<string> = new Set<string>();
  private failedAt: Map<string, number> = new Map<string, number>();
  private queue: string[] = [];
  private running: number = 0;
  private notifyTimer: number = -1;

  /** Sets the full address of the archive, for example `http://10.0.2.2:8090/krakow.pmtiles`. */
  configure(url: string): void {
    this.archiveUrl = url.trim();
  }

  /** Reads bytes [offset, offset + length) of the archive with one range request. */
  private async range(offset: number, length: number, timeoutMs: number): Promise<Uint8Array> {
    const req = http.createHttp();
    try {
      const res = await req.request(this.archiveUrl, {
        method: http.RequestMethod.GET,
        header: { 'Range': `bytes=${offset}-${offset + length - 1}` },
        expectDataType: http.HttpDataType.ARRAY_BUFFER,
        connectTimeout: timeoutMs,
        readTimeout: timeoutMs
      });
      const body = new Uint8Array(res.result as ArrayBuffer);
      if (res.responseCode === 206) {
        return body;
      }
      if (res.responseCode === 200 && body.length >= offset + length) {
        return body.subarray(offset, offset + length);
      }
      throw new Error(`HTTP ${res.responseCode}`);
    } finally {
      req.destroy();
    }
  }

  private unpack(bytes: Uint8Array, compression: number): Uint8Array {
    if (compression === COMPRESSION_GZIP) {
      return gunzip(bytes);
    }
    if (compression === COMPRESSION_NONE || compression === 0) {
      return bytes;
    }
    throw new Error(`pmtiles: compression ${compression} is not supported`);
  }

  /** Reads the header and the root directory; false when there is no address or the archive does not answer in time. */
  async init(): Promise<boolean> {
    this.ready = false;
    this.header = null;
    this.root = null;
    this.leaves.clear();
    if (this.archiveUrl.length === 0) {
      return false;
    }
    try {
      const first = await this.range(0, FIRST_FETCH, INIT_TIMEOUT_MS);
      const h = parseHeader(first);
      if (h.tileType !== TILE_TYPE_MVT) {
        throw new Error('pmtiles: the archive does not hold vector tiles');
      }
      const rootEnd = h.rootOffset + h.rootLength;
      const rootRaw = rootEnd <= first.length ? first.subarray(h.rootOffset, rootEnd) :
        await this.range(h.rootOffset, h.rootLength, INIT_TIMEOUT_MS);
      this.root = parseDirectory(this.unpack(rootRaw, h.internalCompression));
      this.header = h;
      this.minZoom = h.minZoom;
      this.maxZoom = h.maxZoom;
      this.ready = true;
    } catch (e) {
      this.ready = false;
    }
    return this.ready;
  }

  /**
   * Tile zoom at which one tile is about 512 to 1024 points wide on screen, as the Protomaps basemap is meant
   * to be shown; zoomed out this means fewer tiles with less detail.
   */
  zoomFor(pxPerM: number, lat: number): number {
    const tileM = TILE_PX / Math.max(pxPerM, 1e-6);
    const z = Math.floor(Math.log2(EARTH_M * Math.cos(lat * Math.PI / 180) / tileM));
    return Math.max(this.minZoom, Math.min(this.maxZoom, z));
  }

  peek(z: number, x: number, y: number): TileData | null {
    return this.cache.get(`${z}/${x}/${y}`) ?? null;
  }

  /** A tile from memory, or null after queueing it for download. */
  want(z: number, x: number, y: number): TileData | null {
    const key = `${z}/${x}/${y}`;
    const hit = this.cache.get(key);
    if (hit !== undefined) {
      return hit;
    }
    const failed = this.failedAt.get(key);
    if (!this.pending.has(key) && (failed === undefined || Date.now() - failed > RETRY_MS)) {
      this.pending.add(key);
      this.queue.push(key);
      this.pump();
    }
    return null;
  }

  private pump(): void {
    while (this.running < MAX_PARALLEL && this.queue.length > 0) {
      const key = this.queue.pop() as string;
      this.running++;
      this.fetchTile(key).then(() => {
        this.running--;
        this.pump();
      });
    }
  }

  /** Several tiles arrive together; the map redraws once per batch, not after each tile. */
  private notifySoon(): void {
    if (this.notifyTimer >= 0) {
      return;
    }
    this.notifyTimer = setTimeout(() => {
      this.notifyTimer = -1;
      this.onChange();
    }, NOTIFY_MS);
  }

  private async leaf(h: PmHeader, e: PmEntry): Promise<PmDirectory> {
    const at = h.leafOffset + e.offset;
    const known = this.leaves.get(at);
    if (known !== undefined) {
      return known;
    }
    const dir = parseDirectory(this.unpack(await this.range(at, e.length, TILE_TIMEOUT_MS), h.internalCompression));
    this.leaves.set(at, dir);
    return dir;
  }

  /** Where the tile lies in the data section, following leaf directories; null when the archive has no such tile. */
  private async locate(h: PmHeader, root: PmDirectory, tileId: number): Promise<PmEntry | null> {
    let dir = root;
    for (let depth = 0; depth <= MAX_LEAF_DEPTH; depth++) {
      const e = findEntry(dir, tileId);
      if (e === null || !e.leaf) {
        return e;
      }
      dir = await this.leaf(h, e);
    }
    return null;
  }

  private store(key: string, data: TileData): void {
    this.cache.set(key, data);
    this.order.push(key);
    while (this.order.length > MAX_CACHE) {
      const old = this.order.shift() as string;
      this.cache.delete(old);
    }
    this.failedAt.delete(key);
    this.version++;
    this.notifySoon();
  }

  private async fetchTile(key: string): Promise<void> {
    const h = this.header;
    const root = this.root;
    const parts = key.split('/');
    const z = parseInt(parts[0], 10);
    const x = parseInt(parts[1], 10);
    const y = parseInt(parts[2], 10);
    try {
      if (h === null || root === null) {
        throw new Error('pmtiles: archive not open');
      }
      const e = await this.locate(h, root, zxyToTileId(z, x, y));
      if (e === null) {
        this.store(key, emptyTile(z, x, y));
        return;
      }
      const raw = await this.range(h.dataOffset + e.offset, e.length, TILE_TIMEOUT_MS);
      const copy = raw.slice().buffer;
      const data = await taskpool.execute(decodeTileTask, copy, z, x, y) as TileData;
      this.store(key, data);
    } catch (err) {
      this.failedAt.set(key, Date.now());
    } finally {
      this.pending.delete(key);
    }
  }
}

export const tileStore: TileStore = new TileStore();
