import { http } from '@kit.NetworkKit';

/** Podpis ulicy z kafelka: nazwa i jej linie w punktach kafelka. */
export interface TileLabel {
  name: string;
  geom: number[][];
}

/** Geometria wielokątów jednej klasy rysowania, każda część to płaska lista [x, y, ...] w punktach kafelka. */
export interface TileFills {
  green: number[][];
  water: number[][];
  building: number[][];
}

/** Linie ulic według rangi, w punktach kafelka. */
export interface TileLines {
  path: number[][];
  minor: number[][];
  major: number[][];
}

/**
 * Kafelek gotowy do rysowania (format `render-v2` serwera): geometria uproszczona do około jednego punktu ekranu,
 * pogrupowana według klasy i zapisana w całkowitych punktach kafelka 0..extent. Na ekran przelicza ją jedna
 * skala i przesunięcie na kafelek.
 */
export interface TileData {
  z: number;
  x: number;
  y: number;
  extent: number;
  fills: TileFills;
  lines: TileLines;
  labels: TileLabel[];
}

interface TileInfo {
  min_zoom: number;
  max_zoom: number;
  bounds: number[];
  attribution: string;
  build: string;
}

const MAX_CACHE: number = 96;
const MAX_PARALLEL: number = 4;
const RETRY_MS: number = 8000;
const NOTIFY_MS: number = 90;
const TILE_PX: number = 512;
const EARTH_M: number = 40075016.686;

export function lonToTileX(lon: number, z: number): number {
  return Math.floor((lon + 180) / 360 * Math.pow(2, z));
}

export function latToTileY(lat: number, z: number): number {
  const r = lat * Math.PI / 180;
  return Math.floor((1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * Math.pow(2, z));
}

/** Długość geograficzna lewej krawędzi kolumny kafelków x. */
export function tileXToLon(x: number, z: number): number {
  return x / Math.pow(2, z) * 360 - 180;
}

/** Szerokość geograficzna górnej krawędzi wiersza kafelków y. */
export function tileYToLat(y: number, z: number): number {
  const n = Math.PI - 2 * Math.PI * y / Math.pow(2, z);
  return Math.atan(Math.sinh(n)) * 180 / Math.PI;
}

function emptyTile(z: number, x: number, y: number): TileData {
  return {
    z: z, x: x, y: y, extent: 512,
    fills: { green: [], water: [], building: [] },
    lines: { path: [], minor: [], major: [] },
    labels: []
  };
}

/**
 * Kafelki mapy z serwera (`tools/mock_backend/server.py`, później serwer projektu): informacje o archiwum,
 * pobieranie kafelków JSON w tle, pamięć ostatnich kafelków i powiadomienie mapy, gdy przyjdzie nowy.
 * Bez adresu albo gdy serwer nie odpowiada, mapa rysuje podkład z danych w aplikacji.
 */
export class TileStore {
  baseUrl: string = '';
  ready: boolean = false;
  minZoom: number = 0;
  maxZoom: number = 15;
  attribution: string = '';
  build: string = '';
  onChange: () => void = () => {
  };
  private cache: Map<string, TileData> = new Map<string, TileData>();
  private order: string[] = [];
  private pending: Set<string> = new Set<string>();
  private failedAt: Map<string, number> = new Map<string, number>();
  private queue: string[] = [];
  private running: number = 0;
  private notifyTimer: number = -1;
  /** Rośnie przy każdym nowym kafelku; mapa porównuje go, żeby wiedzieć, kiedy odświeżyć podkład. */
  version: number = 0;

  configure(url: string): void {
    let u = url.trim();
    while (u.endsWith('/')) {
      u = u.substring(0, u.length - 1);
    }
    this.baseUrl = u;
  }

  private async getText(path: string, timeoutMs: number): Promise<string> {
    const req = http.createHttp();
    try {
      const res = await req.request(`${this.baseUrl}${path}`, {
        method: http.RequestMethod.GET,
        expectDataType: http.HttpDataType.STRING,
        connectTimeout: timeoutMs,
        readTimeout: timeoutMs
      });
      if (res.responseCode === 404) {
        return '';
      }
      if (res.responseCode !== 200) {
        throw new Error(`HTTP ${res.responseCode}`);
      }
      return res.result as string;
    } finally {
      req.destroy();
    }
  }

  /** Pyta serwer o archiwum; zwraca false, gdy adresu nie ma albo serwer nie odpowiada w 3 sekundy. */
  async init(): Promise<boolean> {
    this.ready = false;
    if (this.baseUrl.length === 0) {
      return false;
    }
    try {
      const info = JSON.parse(await this.getText('/tiles/info.json', 3000)) as TileInfo;
      this.minZoom = info.min_zoom;
      this.maxZoom = info.max_zoom;
      this.attribution = info.attribution;
      this.build = info.build;
      this.ready = true;
    } catch (e) {
      this.ready = false;
    }
    return this.ready;
  }

  /**
   * Poziom kafelków, przy którym kafelek ma na ekranie około 512-1024 punktów, jak w mapie bazowej Protomaps.
   * Przy oddaleniu oznacza to mniej kafelków i mniej szczegółów do narysowania.
   */
  zoomFor(pxPerM: number, lat: number): number {
    const tileM = TILE_PX / Math.max(pxPerM, 1e-6);
    const z = Math.floor(Math.log2(EARTH_M * Math.cos(lat * Math.PI / 180) / tileM));
    return Math.max(this.minZoom, Math.min(this.maxZoom, z));
  }

  peek(z: number, x: number, y: number): TileData | null {
    return this.cache.get(`${z}/${x}/${y}`) ?? null;
  }

  /** Kafelek z pamięci albo null; brakujący trafia do kolejki pobierania. */
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

  /** Kilka kafelków przychodzi naraz; mapa przerysowuje się raz na paczkę, a nie po każdym. */
  private notifySoon(): void {
    if (this.notifyTimer >= 0) {
      return;
    }
    this.notifyTimer = setTimeout(() => {
      this.notifyTimer = -1;
      this.onChange();
    }, NOTIFY_MS);
  }

  private async fetchTile(key: string): Promise<void> {
    try {
      const text = await this.getText(`/tiles/${key}.json`, 10000);
      const parts = key.split('/');
      const data: TileData = text.length > 0 ? JSON.parse(text) as TileData :
        emptyTile(parseInt(parts[0], 10), parseInt(parts[1], 10), parseInt(parts[2], 10));
      this.cache.set(key, data);
      this.order.push(key);
      while (this.order.length > MAX_CACHE) {
        const old = this.order.shift() as string;
        this.cache.delete(old);
      }
      this.failedAt.delete(key);
      this.version++;
      this.notifySoon();
    } catch (e) {
      this.failedAt.set(key, Date.now());
    } finally {
      this.pending.delete(key);
    }
  }
}

export const tileStore: TileStore = new TileStore();
