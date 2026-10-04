import { TileData, TileLabel } from './TileTypes';

/** Tile pixels of the output; a tile is drawn about 512 to 1024 points wide. */
export const OUT_EXTENT: number = 512;
const SIMPLIFY_PX: number = 0.7;
const GREEN_KINDS: string[] = ['park', 'grass', 'garden', 'forest', 'wood', 'nature_reserve', 'cemetery',
  'recreation_ground', 'pitch', 'playground', 'golf_course', 'meadow', 'allotments', 'village_green', 'grassland',
  'scrub', 'orchard', 'zoo'];

/** Reader of a protobuf message, enough for the Mapbox Vector Tile format. */
class Pbf {
  buf: Uint8Array;
  pos: number;
  end: number;

  constructor(buf: Uint8Array, start: number, end: number) {
    this.buf = buf;
    this.pos = start;
    this.end = end;
  }

  varint(): number {
    let result = 0;
    let mul = 1;
    for (;;) {
      const b = this.buf[this.pos++];
      result += (b & 0x7f) * mul;
      if (b < 0x80) {
        return result;
      }
      mul *= 128;
    }
  }

  skip(wire: number): void {
    if (wire === 0) {
      this.varint();
    } else if (wire === 1) {
      this.pos += 8;
    } else if (wire === 2) {
      const n = this.varint();
      this.pos += n;
    } else if (wire === 5) {
      this.pos += 4;
    } else {
      throw new Error('mvt: unsupported wire type ' + wire);
    }
  }
}

/** Decodes UTF-8 without a platform module, so the decoder also runs in unit tests on Node. */
export function utf8(buf: Uint8Array, start: number, end: number): string {
  let out = '';
  let i = start;
  while (i < end) {
    const c = buf[i++];
    let cp = c;
    if (c >= 0xf0) {
      cp = ((c & 0x07) << 18) | ((buf[i] & 0x3f) << 12) | ((buf[i + 1] & 0x3f) << 6) | (buf[i + 2] & 0x3f);
      i += 3;
    } else if (c >= 0xe0) {
      cp = ((c & 0x0f) << 12) | ((buf[i] & 0x3f) << 6) | (buf[i + 1] & 0x3f);
      i += 2;
    } else if (c >= 0xc0) {
      cp = ((c & 0x1f) << 6) | (buf[i] & 0x3f);
      i += 1;
    }
    out += String.fromCodePoint(cp);
  }
  return out;
}

function zigzag(v: number): number {
  return (v % 2 === 1) ? -(v + 1) / 2 : v / 2;
}

/** Draw class of a feature at zoom z, or an empty string when the map does not draw it at that zoom. */
export function drawClass(layer: string, type: number, kind: string, z: number): string {
  if (type === 3) {
    if (layer === 'landcover' || (layer === 'landuse' && GREEN_KINDS.indexOf(kind) >= 0)) {
      return 'green';
    }
    if (layer === 'water') {
      return 'water';
    }
    if (layer === 'buildings' && z >= 14) {
      return 'building';
    }
    return '';
  }
  if (type === 2 && layer === 'roads') {
    if (kind === 'major_road' || kind === 'highway') {
      return 'major';
    }
    if (kind === 'minor_road' && z >= 13) {
      return 'minor';
    }
    if ((kind === 'path' || kind === 'other') && z >= 14) {
      return 'path';
    }
  }
  return '';
}

/** Douglas-Peucker on a flat list [x, y, ...]; keeps the first and the last point. */
export function simplify(pts: number[], tol: number): number[] {
  const n = pts.length / 2;
  if (n < 3) {
    return pts;
  }
  const keep = new Uint8Array(n);
  keep[0] = 1;
  keep[n - 1] = 1;
  const stack: number[] = [0, n - 1];
  const tol2 = tol * tol;
  while (stack.length > 0) {
    const b = stack.pop() as number;
    const a = stack.pop() as number;
    const ax = pts[a * 2];
    const ay = pts[a * 2 + 1];
    const dx = pts[b * 2] - ax;
    const dy = pts[b * 2 + 1] - ay;
    const den = dx * dx + dy * dy;
    let best = tol2;
    let idx = -1;
    for (let i = a + 1; i < b; i++) {
      const px = pts[i * 2] - ax;
      const py = pts[i * 2 + 1] - ay;
      let d = 0;
      if (den === 0) {
        d = px * px + py * py;
      } else {
        let t = (px * dx + py * dy) / den;
        t = t < 0 ? 0 : (t > 1 ? 1 : t);
        const ex = px - t * dx;
        const ey = py - t * dy;
        d = ex * ex + ey * ey;
      }
      if (d > best) {
        best = d;
        idx = i;
      }
    }
    if (idx >= 0) {
      keep[idx] = 1;
      stack.push(a, idx, idx, b);
    }
  }
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    if (keep[i] === 1) {
      out.push(pts[i * 2], pts[i * 2 + 1]);
    }
  }
  return out;
}

/**
 * One part simplified to about one screen pixel and rounded to OUT_EXTENT tile pixels, without repeated points;
 * null when it is too small to see.
 */
export function compact(part: number[], extent: number, closed: boolean): number[] | null {
  const scale = OUT_EXTENT / extent;
  const pts = simplify(part, SIMPLIFY_PX / scale);
  const flat: number[] = [];
  let lx = NaN;
  let ly = NaN;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (let i = 0; i < pts.length; i += 2) {
    const qx = Math.round(pts[i] * scale);
    const qy = Math.round(pts[i + 1] * scale);
    if (qx === lx && qy === ly) {
      continue;
    }
    flat.push(qx, qy);
    lx = qx;
    ly = qy;
    minX = Math.min(minX, qx);
    maxX = Math.max(maxX, qx);
    minY = Math.min(minY, qy);
    maxY = Math.max(maxY, qy);
  }
  const count = flat.length / 2;
  if (closed) {
    if (count < 3 || (maxX - minX) * (maxY - minY) < 2) {
      return null;
    }
  } else if (count < 2 || (maxX - minX) + (maxY - minY) < 2) {
    return null;
  }
  return flat;
}

/** Geometry commands of one feature to parts, each a flat list [x, y, ...] in tile units; rings are closed. */
function geometry(p: Pbf, end: number): number[][] {
  const parts: number[][] = [];
  let cur: number[] | null = null;
  let x = 0;
  let y = 0;
  while (p.pos < end) {
    const c = p.varint();
    const id = c & 7;
    const count = Math.floor(c / 8);
    if (id === 1 || id === 2) {
      for (let k = 0; k < count; k++) {
        x += zigzag(p.varint());
        y += zigzag(p.varint());
        if (id === 1) {
          cur = [x, y];
          parts.push(cur);
        } else if (cur !== null) {
          cur.push(x, y);
        }
      }
    } else if (id === 7) {
      if (cur !== null && cur.length >= 2) {
        cur.push(cur[0], cur[1]);
      }
    } else {
      throw new Error('mvt: bad geometry command ' + id);
    }
  }
  return parts;
}

/** Accumulates the draw classes of one tile. */
class TileBuilder {
  data: TileData;
  z: number;

  constructor(z: number, x: number, y: number) {
    this.z = z;
    this.data = {
      z: z, x: x, y: y, extent: OUT_EXTENT,
      fills: { green: [], water: [], building: [] },
      lines: { path: [], minor: [], major: [] },
      labels: []
    };
  }

  target(cls: string): number[][] {
    if (cls === 'green') {
      return this.data.fills.green;
    }
    if (cls === 'water') {
      return this.data.fills.water;
    }
    if (cls === 'building') {
      return this.data.fills.building;
    }
    if (cls === 'path') {
      return this.data.lines.path;
    }
    if (cls === 'minor') {
      return this.data.lines.minor;
    }
    return this.data.lines.major;
  }
}

/** Reads one layer message and adds its drawn features to the builder. */
function readLayer(buf: Uint8Array, start: number, end: number, out: TileBuilder): void {
  const p = new Pbf(buf, start, end);
  let name = '';
  let extent = 4096;
  const keys: string[] = [];
  const values: string[] = [];
  const features: number[] = [];
  while (p.pos < end) {
    const key = p.varint();
    const field = Math.floor(key / 8);
    const wire = key & 7;
    if (field === 1 && wire === 2) {
      const n = p.varint();
      name = utf8(buf, p.pos, p.pos + n);
      p.pos += n;
    } else if (field === 2 && wire === 2) {
      const n = p.varint();
      features.push(p.pos, p.pos + n);
      p.pos += n;
    } else if (field === 3 && wire === 2) {
      const n = p.varint();
      keys.push(utf8(buf, p.pos, p.pos + n));
      p.pos += n;
    } else if (field === 4 && wire === 2) {
      const n = p.varint();
      values.push(readStringValue(buf, p.pos, p.pos + n));
      p.pos += n;
    } else if (field === 5 && wire === 0) {
      extent = p.varint();
    } else {
      p.skip(wire);
    }
  }
  if (['landcover', 'landuse', 'water', 'buildings', 'roads'].indexOf(name) < 0) {
    return;
  }
  for (let f = 0; f < features.length; f += 2) {
    readFeature(buf, features[f], features[f + 1], name, extent, keys, values, out);
  }
}

function readStringValue(buf: Uint8Array, start: number, end: number): string {
  const p = new Pbf(buf, start, end);
  while (p.pos < end) {
    const key = p.varint();
    const field = Math.floor(key / 8);
    const wire = key & 7;
    if (field === 1 && wire === 2) {
      const n = p.varint();
      return utf8(buf, p.pos, p.pos + n);
    }
    p.skip(wire);
  }
  return '';
}

function readFeature(buf: Uint8Array, start: number, end: number, layer: string, extent: number, keys: string[],
  values: string[], out: TileBuilder): void {
  const p = new Pbf(buf, start, end);
  let type = 0;
  const tags: number[] = [];
  let geomStart = -1;
  let geomEnd = -1;
  while (p.pos < end) {
    const key = p.varint();
    const field = Math.floor(key / 8);
    const wire = key & 7;
    if (field === 2 && wire === 2) {
      const n = p.varint();
      const stop = p.pos + n;
      while (p.pos < stop) {
        tags.push(p.varint());
      }
    } else if (field === 3 && wire === 0) {
      type = p.varint();
    } else if (field === 4 && wire === 2) {
      const n = p.varint();
      geomStart = p.pos;
      geomEnd = p.pos + n;
      p.pos += n;
    } else {
      p.skip(wire);
    }
  }
  let kind = '';
  let pmapKind = '';
  let nameAny = '';
  let namePl = '';
  for (let i = 0; i + 1 < tags.length; i += 2) {
    const k = tags[i] < keys.length ? keys[tags[i]] : '';
    const v = tags[i + 1] < values.length ? values[tags[i + 1]] : '';
    if (k === 'kind') {
      kind = v;
    } else if (k === 'pmap:kind') {
      pmapKind = v;
    } else if (k === 'name') {
      nameAny = v;
    } else if (k === 'name:pl') {
      namePl = v;
    }
  }
  const cls = drawClass(layer, type, kind.length > 0 ? kind : pmapKind, out.z);
  if (cls.length === 0 || geomStart < 0) {
    return;
  }
  const closed = type === 3;
  const gp = new Pbf(buf, geomStart, geomEnd);
  const parts: number[][] = [];
  for (const part of geometry(gp, geomEnd)) {
    const c = compact(part, extent, closed);
    if (c !== null) {
      parts.push(c);
    }
  }
  if (parts.length === 0) {
    return;
  }
  const target = out.target(cls);
  for (const part of parts) {
    target.push(part);
  }
  const label = namePl.length > 0 ? namePl : nameAny;
  if (!closed && label.length > 0 && (cls === 'major' || (cls === 'minor' && out.z >= 14))) {
    const l: TileLabel = { name: label, geom: parts };
    out.data.labels.push(l);
  }
}

/**
 * Decodes one Mapbox Vector Tile of the Protomaps basemap into a tile ready to draw: green areas, water,
 * buildings from zoom 14, streets in three ranks and the street names, simplified to about one screen pixel.
 */
export function decodeMvt(buf: Uint8Array, z: number, x: number, y: number): TileData {
  const out = new TileBuilder(z, x, y);
  const p = new Pbf(buf, 0, buf.length);
  while (p.pos < buf.length) {
    const key = p.varint();
    const field = Math.floor(key / 8);
    const wire = key & 7;
    if (field === 3 && wire === 2) {
      const n = p.varint();
      readLayer(buf, p.pos, p.pos + n, out);
      p.pos += n;
    } else {
      p.skip(wire);
    }
  }
  return out.data;
}
