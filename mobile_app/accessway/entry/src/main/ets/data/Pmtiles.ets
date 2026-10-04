/** The fixed-size header of a PMTiles v3 archive. */
export interface PmHeader {
  rootOffset: number;
  rootLength: number;
  metadataOffset: number;
  metadataLength: number;
  leafOffset: number;
  leafLength: number;
  dataOffset: number;
  dataLength: number;
  internalCompression: number;
  tileCompression: number;
  tileType: number;
  minZoom: number;
  maxZoom: number;
  minLon: number;
  minLat: number;
  maxLon: number;
  maxLat: number;
}

/** One directory of the archive as parallel arrays, sorted by tile id. */
export interface PmDirectory {
  ids: number[];
  runs: number[];
  lengths: number[];
  offsets: number[];
}

/** Where one tile lies: in the data section (`leaf` false) or in a leaf directory (`leaf` true). */
export interface PmEntry {
  leaf: boolean;
  offset: number;
  length: number;
}

export const HEADER_LENGTH: number = 127;
export const COMPRESSION_NONE: number = 1;
export const COMPRESSION_GZIP: number = 2;
export const TILE_TYPE_MVT: number = 1;

function u64(v: DataView, at: number): number {
  return v.getUint32(at, true) + v.getUint32(at + 4, true) * 4294967296;
}

/** Reads the header from the first bytes of the archive; throws when they are not PMTiles version 3. */
export function parseHeader(bytes: Uint8Array): PmHeader {
  const magic = [0x50, 0x4d, 0x54, 0x69, 0x6c, 0x65, 0x73];
  if (bytes.length < HEADER_LENGTH) {
    throw new Error('pmtiles: header too short');
  }
  for (let i = 0; i < magic.length; i++) {
    if (bytes[i] !== magic[i]) {
      throw new Error('pmtiles: not a PMTiles archive');
    }
  }
  if (bytes[7] !== 3) {
    throw new Error('pmtiles: only version 3 is supported');
  }
  const v = new DataView(bytes.buffer, bytes.byteOffset, HEADER_LENGTH);
  return {
    rootOffset: u64(v, 8),
    rootLength: u64(v, 16),
    metadataOffset: u64(v, 24),
    metadataLength: u64(v, 32),
    leafOffset: u64(v, 40),
    leafLength: u64(v, 48),
    dataOffset: u64(v, 56),
    dataLength: u64(v, 64),
    internalCompression: bytes[97],
    tileCompression: bytes[98],
    tileType: bytes[99],
    minZoom: bytes[100],
    maxZoom: bytes[101],
    minLon: v.getInt32(102, true) / 1e7,
    minLat: v.getInt32(106, true) / 1e7,
    maxLon: v.getInt32(110, true) / 1e7,
    maxLat: v.getInt32(114, true) / 1e7
  };
}

/** Hilbert tile id of PMTiles v3 for tile z/x/y. */
export function zxyToTileId(z: number, x0: number, y0: number): number {
  if (z === 0) {
    return 0;
  }
  let acc = (Math.pow(4, z) - 1) / 3;
  let x = x0;
  let y = y0;
  let s = Math.pow(2, z - 1);
  while (s >= 1) {
    const rx = (x & s) !== 0 ? 1 : 0;
    const ry = (y & s) !== 0 ? 1 : 0;
    acc += ((3 * rx) ^ ry) * s * s;
    if (ry === 0) {
      if (rx === 1) {
        x = s - 1 - x;
        y = s - 1 - y;
      }
      const t = x;
      x = y;
      y = t;
    }
    s = s / 2;
  }
  return acc;
}

/** Reader of unsigned varints that stay exact up to 2^53, past the 32 bits of the bit operators. */
class VarintReader {
  buf: Uint8Array;
  pos: number = 0;

  constructor(buf: Uint8Array) {
    this.buf = buf;
  }

  next(): number {
    let result = 0;
    let mul = 1;
    for (;;) {
      if (this.pos >= this.buf.length) {
        throw new Error('pmtiles: directory ends inside a varint');
      }
      const b = this.buf[this.pos++];
      result += (b & 0x7f) * mul;
      if (b < 0x80) {
        return result;
      }
      mul *= 128;
    }
  }
}

/** Decodes an uncompressed directory. */
export function parseDirectory(raw: Uint8Array): PmDirectory {
  const r = new VarintReader(raw);
  const n = r.next();
  const ids: number[] = [];
  const runs: number[] = [];
  const lengths: number[] = [];
  const offsets: number[] = [];
  let last = 0;
  for (let i = 0; i < n; i++) {
    last += r.next();
    ids.push(last);
  }
  for (let i = 0; i < n; i++) {
    runs.push(r.next());
  }
  for (let i = 0; i < n; i++) {
    lengths.push(r.next());
  }
  for (let i = 0; i < n; i++) {
    const v = r.next();
    offsets.push(v === 0 && i > 0 ? offsets[i - 1] + lengths[i - 1] : v - 1);
  }
  return { ids: ids, runs: runs, lengths: lengths, offsets: offsets };
}

/**
 * Finds the entry for a tile id in one directory: the tile itself, a leaf directory to read next, or null
 * when the archive has no such tile. Offsets are relative to the data section or the leaf section.
 */
export function findEntry(dir: PmDirectory, tileId: number): PmEntry | null {
  let lo = 0;
  let hi = dir.ids.length - 1;
  let found = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (dir.ids[mid] <= tileId) {
      found = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  if (found < 0) {
    return null;
  }
  if (dir.runs[found] === 0) {
    return { leaf: true, offset: dir.offsets[found], length: dir.lengths[found] };
  }
  if (tileId < dir.ids[found] + dir.runs[found]) {
    return { leaf: false, offset: dir.offsets[found], length: dir.lengths[found] };
  }
  return null;
}
