import { distanceM } from './Geo';
import { FactKind, GraphNode, Place, PointFeature, Roughness, WalkEdge } from '../model/Types';

export interface OverpassCenter {
  lat: number;
  lon: number;
}

export interface OverpassElement {
  type: string;
  id: number;
  lat?: number;
  lon?: number;
  nodes?: number[];
  tags?: Record<string, string>;
  center?: OverpassCenter;
  timestamp?: string;
}

export interface OverpassMeta {
  timestamp_osm_base?: string;
  copyright?: string;
}

export interface OverpassResponse {
  osm3s?: OverpassMeta;
  elements: OverpassElement[];
  accessway_sample?: boolean;
  accessway_fetched_at?: string;
}

export const WALKABLE: string[] = ['footway', 'pedestrian', 'path', 'living_street', 'residential', 'service',
  'steps', 'tertiary', 'secondary', 'primary', 'unclassified', 'cycleway', 'track', 'corridor', 'tertiary_link',
  'secondary_link', 'primary_link', 'elevator'];

const NO_SURFACE_INFO: string[] = ['footway', 'path', 'pedestrian', 'living_street', 'track'];
const SMOOTH_SURFACES: string[] = ['asphalt', 'concrete', 'concrete:plates', 'paved', 'metal', 'rubber', 'tartan',
  'wood', 'acrylic', 'paving_stones', 'paving_stones:30'];
const MODERATE_SURFACES: string[] = ['concrete:lanes', 'compacted', 'fine_gravel', 'bricks', 'grass_paver', 'sett'];
const ROUGH_SURFACES: string[] = ['cobblestone', 'unhewn_cobblestone', 'gravel', 'pebblestone', 'ground',
  'dirt', 'grass', 'sand', 'unpaved', 'earth', 'mud', 'woodchips', 'rock', 'stepping_stones'];
const PLACE_KEYS: string[] = ['amenity', 'tourism', 'shop', 'historic', 'public_transport', 'leisure', 'office',
  'healthcare', 'railway', 'building'];
const FEATURE_ONLY_AMENITIES: string[] = ['bench', 'toilets', 'waste_basket', 'bicycle_parking', 'parking_entrance',
  'vending_machine', 'recycling', 'post_box', 'telephone'];

/** Tło mapy: budynek albo zieleń, jako wielokąt. */
export interface MapArea {
  kind: string;
  name: string;
  pts: number[];
}

/** Fakt odczytany z OpenStreetMap: bariera albo udogodnienie przypisane do punktu. */
export interface OsmFact {
  id: string;
  kind: FactKind;
  lat: number;
  lon: number;
  street: string;
  date: number;
  stepCount: number;
}

export const OSM_STEEP_PCT: number = 6;
export const OSM_NARROW_M: number = 0.9;

export class Dataset {
  nodes: GraphNode[] = [];
  areas: MapArea[] = [];
  osmFacts: OsmFact[] = [];
  edges: WalkEdge[] = [];
  adjStart: number[] = [];
  adjEdge: number[] = [];
  places: Place[] = [];
  features: PointFeature[] = [];
  sourceDate: number = 0;
  fetchedAt: number = 0;
  isSample: boolean = false;
  minLat: number = 90;
  maxLat: number = -90;
  minLon: number = 180;
  maxLon: number = -180;
  private grid: Map<string, number[]> = new Map<string, number[]>();

  /** Indeks przestrzenny węzłów w siatce co 0.002 stopnia. */
  buildIndex(): void {
    this.grid.clear();
    for (let i = 0; i < this.nodes.length; i++) {
      const key = cellKey(this.nodes[i].lat, this.nodes[i].lon);
      const arr = this.grid.get(key);
      if (arr === undefined) {
        this.grid.set(key, [i]);
      } else {
        arr.push(i);
      }
    }
    const counts: number[] = new Array<number>(this.nodes.length + 1).fill(0);
    for (const e of this.edges) {
      counts[e.a + 1]++;
      counts[e.b + 1]++;
    }
    for (let i = 1; i < counts.length; i++) {
      counts[i] += counts[i - 1];
    }
    this.adjStart = counts.slice();
    const fill: number[] = counts.slice();
    this.adjEdge = new Array<number>(this.edges.length * 2).fill(0);
    for (const e of this.edges) {
      this.adjEdge[fill[e.a]++] = e.index;
      this.adjEdge[fill[e.b]++] = e.index;
    }
  }

  /** Najbliższy węzeł połączony z siecią albo -1, gdy żaden nie leży w promieniu `maxM`. */
  nearestNode(lat: number, lon: number, maxM: number): number {
    let best = -1;
    let bestD = maxM;
    const ci = Math.floor(lat / CELL);
    const cj = Math.floor(lon / CELL);
    const reach = Math.ceil(maxM / 140) + 1;
    for (let di = -reach; di <= reach; di++) {
      for (let dj = -reach; dj <= reach; dj++) {
        const arr = this.grid.get(`${ci + di}:${cj + dj}`);
        if (arr === undefined) {
          continue;
        }
        for (const n of arr) {
          if (this.adjStart[n + 1] - this.adjStart[n] === 0) {
            continue;
          }
          const d = distanceM(lat, lon, this.nodes[n].lat, this.nodes[n].lon);
          if (d <= bestD) {
            bestD = d;
            best = n;
          }
        }
      }
    }
    return best;
  }

  otherEnd(edgeIndex: number, node: number): number {
    const e = this.edges[edgeIndex];
    return e.a === node ? e.b : e.a;
  }

  contains(lat: number, lon: number): boolean {
    return lat >= this.minLat && lat <= this.maxLat && lon >= this.minLon && lon <= this.maxLon;
  }
}

const CELL: number = 0.002;

function cellKey(lat: number, lon: number): string {
  return `${Math.floor(lat / CELL)}:${Math.floor(lon / CELL)}`;
}

export function parseNumber(raw: string): number {
  const m = raw.replace(',', '.').match(/-?\d+(\.\d+)?/);
  if (m === null) {
    return NaN;
  }
  return Number(m[0]);
}

/** Nachylenie w procentach z tagu `incline`; NaN, gdy tag nie niesie liczby. */
export function parseIncline(raw: string): number {
  const v = parseNumber(raw);
  if (isNaN(v)) {
    return NaN;
  }
  if (raw.indexOf('°') >= 0 || raw.indexOf('deg') >= 0) {
    return Math.tan(v * Math.PI / 180) * 100;
  }
  return v;
}

export function parseWidthM(raw: string): number {
  const v = parseNumber(raw);
  if (isNaN(v)) {
    return NaN;
  }
  if (raw.indexOf('cm') >= 0) {
    return v / 100;
  }
  return v;
}

/** Wysokość krawężnika w cm; -1, gdy krawężnik istnieje, ale wysokość jest nieznana. */
export function kerbHeightCm(tags: Record<string, string>): number {
  const h = tags['kerb:height'];
  if (h !== undefined) {
    const v = parseNumber(h);
    if (!isNaN(v)) {
      if (h.indexOf('cm') >= 0) {
        return v;
      }
      if (h.indexOf('m') >= 0 || v < 1) {
        return v * 100;
      }
      return v;
    }
  }
  const k = tags['kerb'];
  if (k === 'flush' || k === 'no') {
    return 0;
  }
  if (k === 'lowered') {
    return 3;
  }
  if (k === 'rolled') {
    return 5;
  }
  if (k === 'raised' || k === 'yes') {
    return 12;
  }
  return -1;
}

export function hasKerb(tags: Record<string, string>): boolean {
  return tags['barrier'] === 'kerb' || tags['kerb'] !== undefined || tags['kerb:height'] !== undefined;
}

export function roughnessOf(tags: Record<string, string>): number {
  const sm = tags['smoothness'];
  if (sm !== undefined) {
    if (sm === 'excellent' || sm === 'good') {
      return Roughness.SMOOTH;
    }
    if (sm === 'intermediate') {
      return Roughness.MODERATE;
    }
    return Roughness.ROUGH;
  }
  const s = tags['surface'];
  if (s === undefined) {
    return -1;
  }
  if (SMOOTH_SURFACES.indexOf(s) >= 0) {
    return Roughness.SMOOTH;
  }
  if (MODERATE_SURFACES.indexOf(s) >= 0) {
    return Roughness.MODERATE;
  }
  if (ROUGH_SURFACES.indexOf(s) >= 0) {
    return Roughness.ROUGH;
  }
  return Roughness.MODERATE;
}

export function parseOsmDate(raw: string | undefined): number {
  if (raw === undefined || raw.length === 0) {
    return 0;
  }
  const t = Date.parse(raw);
  return isNaN(t) ? 0 : t;
}

function isWalkable(tags: Record<string, string>): boolean {
  const hw = tags['highway'];
  if (hw === undefined || WALKABLE.indexOf(hw) < 0) {
    return false;
  }
  const access = tags['access'];
  const foot = tags['foot'];
  if (foot === 'no' || foot === 'private') {
    return false;
  }
  if ((access === 'no' || access === 'private') && foot !== 'yes' && foot !== 'designated') {
    return false;
  }
  if (hw === 'cycleway' && foot !== 'yes' && foot !== 'designated') {
    return false;
  }
  return true;
}

function placeCategory(tags: Record<string, string>): string {
  for (const k of PLACE_KEYS) {
    const v = tags[k];
    if (v !== undefined) {
      if (k === 'building' && tags['name'] === undefined) {
        return '';
      }
      return `${k}=${v}`;
    }
  }
  return '';
}

function emptyTags(): Record<string, string> {
  const t: Record<string, string> = {};
  return t;
}

/** Odwzorowuje odpowiedź Overpass na sieć pieszą, miejsca i punkty udogodnień. */
export function buildDataset(resp: OverpassResponse): Dataset {
  const ds = new Dataset();
  ds.isSample = resp.accessway_sample === true;
  ds.sourceDate = parseOsmDate(resp.osm3s?.timestamp_osm_base);
  ds.fetchedAt = parseOsmDate(resp.accessway_fetched_at);
  const coords: Map<number, OverpassElement> = new Map<number, OverpassElement>();
  for (const el of resp.elements) {
    if (el.type === 'node' && el.lat !== undefined) {
      coords.set(el.id, el);
    }
  }
  const nodeIndex: Map<number, number> = new Map<number, number>();
  const nodeFor = (osmId: number): number => {
    const known = nodeIndex.get(osmId);
    if (known !== undefined) {
      return known;
    }
    const el = coords.get(osmId);
    if (el === undefined || el.lat === undefined || el.lon === undefined) {
      return -1;
    }
    const tags = el.tags ?? emptyTags();
    let kerb = -2;
    if (hasKerb(tags)) {
      kerb = kerbHeightCm(tags);
    }
    const idx = ds.nodes.length;
    const crossing = tags['highway'] === 'crossing' || tags['crossing'] !== undefined || tags['railway'] === 'crossing';
    ds.nodes.push({ osmId: osmId, lat: el.lat, lon: el.lon, kerbCm: kerb, crossing: crossing });
    nodeIndex.set(osmId, idx);
    ds.minLat = Math.min(ds.minLat, el.lat);
    ds.maxLat = Math.max(ds.maxLat, el.lat);
    ds.minLon = Math.min(ds.minLon, el.lon);
    ds.maxLon = Math.max(ds.maxLon, el.lon);
    return idx;
  };

  for (const el of resp.elements) {
    const tags = el.tags ?? emptyTags();
    if (el.type === 'way' && el.nodes !== undefined && isWalkable(tags)) {
      addWay(ds, el.nodes, tags, nodeFor);
      addWayFacts(ds, el, tags, coords);
    } else if (el.type === 'way' && el.nodes !== undefined) {
      addArea(ds, el.nodes, tags, coords);
    }
  }

  for (const el of resp.elements) {
    const tags = el.tags;
    if (tags === undefined) {
      continue;
    }
    let lat = el.lat;
    let lon = el.lon;
    if (el.center !== undefined) {
      lat = el.center.lat;
      lon = el.center.lon;
    }
    if (lat === undefined || lon === undefined) {
      continue;
    }
    addNodeFacts(ds, el, tags, lat, lon);
    const amenity = tags['amenity'];
    if (amenity === 'bench' || tags['leisure'] === 'picnic_table' || tags['bench'] === 'yes') {
      ds.features.push({ kind: 'bench', lat: lat, lon: lon, tags: tags });
    }
    if (amenity === 'toilets') {
      ds.features.push({ kind: 'toilets', lat: lat, lon: lon, tags: tags });
    }
    if (tags['highway'] === 'elevator' && el.type === 'node') {
      ds.features.push({ kind: 'elevator', lat: lat, lon: lon, tags: tags });
    }
    if (tags['entrance'] !== undefined && el.type === 'node') {
      ds.features.push({ kind: 'entrance', lat: lat, lon: lon, tags: tags });
    }
    const name = tags['name'];
    if (name === undefined || name.length === 0) {
      continue;
    }
    if (amenity !== undefined && FEATURE_ONLY_AMENITIES.indexOf(amenity) >= 0) {
      continue;
    }
    if (tags['highway'] !== undefined && tags['highway'] !== 'bus_stop') {
      continue;
    }
    const cat = tags['highway'] === 'bus_stop' ? 'highway=bus_stop' : placeCategory(tags);
    if (cat.length === 0) {
      continue;
    }
    const street = tags['addr:street'] !== undefined ?
      `${tags['addr:street']} ${tags['addr:housenumber'] ?? ''}`.trim() : '';
    ds.places.push({
      id: `${el.type}/${el.id}`,
      name: name,
      category: cat,
      lat: lat,
      lon: lon,
      street: street,
      tags: tags,
      observedAt: parseOsmDate(el.timestamp)
    });
  }
  ds.places = dedupePlaces(ds.places);
  ds.buildIndex();
  for (const f of ds.osmFacts) {
    if (f.street.length === 0) {
      f.street = nearestStreet(ds, f.lat, f.lon);
    }
  }
  return ds;
}

function areaKind(tags: Record<string, string>): string {
  if (tags['building'] !== undefined) {
    return 'building';
  }
  const green = ['park', 'garden', 'grass', 'meadow', 'recreation_ground', 'village_green'];
  if (green.indexOf(tags['leisure'] ?? '') >= 0 || green.indexOf(tags['landuse'] ?? '') >= 0) {
    return 'green';
  }
  return '';
}

function addArea(ds: Dataset, refs: number[], tags: Record<string, string>, coords: Map<number, OverpassElement>): void {
  const kind = areaKind(tags);
  if (kind.length === 0) {
    return;
  }
  const pts: number[] = [];
  for (const ref of refs) {
    const el = coords.get(ref);
    if (el !== undefined && el.lat !== undefined && el.lon !== undefined) {
      pts.push(el.lat, el.lon);
    }
  }
  if (pts.length >= 6) {
    ds.areas.push({ kind: kind, name: tags['name'] ?? '', pts: pts });
  }
}

function osmFact(ds: Dataset, id: string, kind: FactKind, lat: number, lon: number, street: string, date: number,
  steps: number): void {
  ds.osmFacts.push({ id: id, kind: kind, lat: lat, lon: lon, street: street, date: date, stepCount: steps });
}

/** Punkt w połowie drogi, liczony po długości odcinków. */
function wayMiddle(refs: number[], coords: Map<number, OverpassElement>): number[] {
  const pts: number[] = [];
  for (const ref of refs) {
    const el = coords.get(ref);
    if (el !== undefined && el.lat !== undefined && el.lon !== undefined) {
      pts.push(el.lat, el.lon);
    }
  }
  if (pts.length < 2) {
    return [];
  }
  let total = 0;
  for (let i = 2; i < pts.length; i += 2) {
    total += distanceM(pts[i - 2], pts[i - 1], pts[i], pts[i + 1]);
  }
  let acc = 0;
  for (let i = 2; i < pts.length; i += 2) {
    const d = distanceM(pts[i - 2], pts[i - 1], pts[i], pts[i + 1]);
    if (acc + d >= total / 2 && d > 0) {
      const t = (total / 2 - acc) / d;
      return [pts[i - 2] + (pts[i] - pts[i - 2]) * t, pts[i - 1] + (pts[i + 1] - pts[i - 1]) * t];
    }
    acc += d;
  }
  return [pts[0], pts[1]];
}

function addWayFacts(ds: Dataset, el: OverpassElement, tags: Record<string, string>,
  coords: Map<number, OverpassElement>): void {
  const refs = el.nodes ?? [];
  const mid = wayMiddle(refs, coords);
  if (mid.length < 2) {
    return;
  }
  const id = `osm:way/${el.id}`;
  const street = tags['name'] ?? '';
  const date = parseOsmDate(el.timestamp);
  const hw = tags['highway'] ?? '';
  if (hw === 'steps') {
    const n = parseNumber(tags['step_count'] ?? '');
    osmFact(ds, id, FactKind.STEPS, mid[0], mid[1], street, date, isNaN(n) ? 0 : Math.round(n));
    if (tags['handrail'] === 'yes' || tags['handrail:left'] === 'yes' || tags['handrail:right'] === 'yes') {
      osmFact(ds, `${id}#handrail`, FactKind.HANDRAIL, mid[0], mid[1], street, date, 0);
    }
  }
  if (tags['ramp'] === 'yes' || tags['ramp:wheelchair'] === 'yes' || tags['ramp:stroller'] === 'yes') {
    osmFact(ds, `${id}#ramp`, FactKind.RAMP, mid[0], mid[1], street, date, 0);
  }
  const inc = tags['incline'] !== undefined ? parseIncline(tags['incline']) : NaN;
  if (hw !== 'steps' && !isNaN(inc) && Math.abs(inc) >= OSM_STEEP_PCT) {
    osmFact(ds, `${id}#incline`, FactKind.STEEP_SLOPE, mid[0], mid[1], street, date, 0);
  }
  const w = tags['width'] !== undefined ? parseWidthM(tags['width']) : NaN;
  if (!isNaN(w) && w < OSM_NARROW_M) {
    osmFact(ds, `${id}#width`, FactKind.NARROW_PASSAGE, mid[0], mid[1], street, date, 0);
  }
  if (roughnessOf(tags) === Roughness.ROUGH) {
    osmFact(ds, `${id}#surface`, FactKind.ROUGH_SURFACE, mid[0], mid[1], street, date, 0);
  }
}

function addNodeFacts(ds: Dataset, el: OverpassElement, tags: Record<string, string>, lat: number, lon: number): void {
  if (el.type !== 'node') {
    return;
  }
  const id = `osm:node/${el.id}`;
  const date = parseOsmDate(el.timestamp);
  if (hasKerb(tags)) {
    const h = kerbHeightCm(tags);
    if (h > 3) {
      osmFact(ds, id, FactKind.KERB, lat, lon, '', date, 0);
    } else if (h >= 0) {
      osmFact(ds, id, FactKind.LOWERED_KERB, lat, lon, '', date, 0);
    }
  }
  if (tags['highway'] === 'elevator') {
    osmFact(ds, id, FactKind.ELEVATOR, lat, lon, '', date, 0);
  }
  if (tags['amenity'] === 'toilets' && (tags['wheelchair'] === 'yes' || tags['toilets:wheelchair'] === 'yes')) {
    osmFact(ds, id, FactKind.ACCESSIBLE_TOILET, lat, lon, '', date, 0);
  }
  if (tags['amenity'] === 'bench' || tags['leisure'] === 'picnic_table') {
    osmFact(ds, id, FactKind.REST_SPOT, lat, lon, '', date, 0);
  }
  if (tags['kerb'] === 'ramp' || tags['ramp'] === 'yes') {
    osmFact(ds, `${id}#ramp`, FactKind.RAMP, lat, lon, '', date, 0);
  }
}

/** Nazwa najbliższej nazwanej drogi w promieniu 40 m albo pusty tekst. */
export function nearestStreet(ds: Dataset, lat: number, lon: number): string {
  let best = '';
  let bestD = 40;
  const n = ds.nearestNode(lat, lon, 80);
  if (n < 0) {
    return '';
  }
  for (const e of ds.edges) {
    if (e.name.length === 0) {
      continue;
    }
    const a = ds.nodes[e.a];
    const b = ds.nodes[e.b];
    const d = Math.min(distanceM(lat, lon, a.lat, a.lon), distanceM(lat, lon, b.lat, b.lon),
      distanceM(lat, lon, (a.lat + b.lat) / 2, (a.lon + b.lon) / 2));
    if (d < bestD) {
      bestD = d;
      best = e.name;
    }
  }
  return best;
}

function addWay(ds: Dataset, refs: number[], tags: Record<string, string>, nodeFor: (id: number) => number): void {
  const hw = tags['highway'] ?? '';
  const isSteps = hw === 'steps';
  const hasRamp = tags['ramp:wheelchair'] === 'yes' || tags['ramp'] === 'yes' || tags['ramp:stroller'] === 'yes';
  const inclineRaw = tags['incline'];
  let incline = NaN;
  let inclineUnknown = false;
  if (inclineRaw !== undefined) {
    incline = parseIncline(inclineRaw);
    inclineUnknown = isNaN(incline);
  }
  const widthRaw = tags['width'] ?? tags['est_width'];
  const width = widthRaw !== undefined ? parseWidthM(widthRaw) : NaN;
  const rough = roughnessOf(tags);
  const surfaceLabel = tags['surface'] ?? tags['smoothness'] ?? '';
  const noSurfaceData = rough < 0 && NO_SURFACE_INFO.indexOf(hw) >= 0;
  const name = tags['name'] ?? '';
  const wayCrossing = tags['footway'] === 'crossing' || tags['path'] === 'crossing';
  let prev = -1;
  for (const ref of refs) {
    const cur = nodeFor(ref);
    if (cur < 0) {
      prev = -1;
      continue;
    }
    if (prev >= 0 && prev !== cur) {
      const na = ds.nodes[prev];
      const nb = ds.nodes[cur];
      let kerb = -2;
      let kerbUnknown = false;
      for (const k of [na.kerbCm, nb.kerbCm]) {
        if (k === -1) {
          kerbUnknown = true;
        } else if (k >= 0) {
          kerb = Math.max(kerb, k);
        }
      }
      ds.edges.push({
        index: ds.edges.length,
        a: prev,
        b: cur,
        lengthM: distanceM(na.lat, na.lon, nb.lat, nb.lon),
        highway: hw,
        name: name,
        isSteps: isSteps,
        hasRamp: hasRamp,
        inclinePct: incline,
        inclineUnknown: inclineUnknown,
        roughness: rough,
        surfaceLabel: surfaceLabel,
        widthM: width,
        kerbCm: kerb,
        kerbUnknown: kerbUnknown && kerb < 0,
        wheelchairNo: tags['wheelchair'] === 'no',
        noSurfaceData: noSurfaceData,
        crossing: wayCrossing || na.crossing || nb.crossing
      });
    }
    prev = cur;
  }
}

function dedupePlaces(list: Place[]): Place[] {
  const seen: Map<string, Place> = new Map<string, Place>();
  const out: Place[] = [];
  for (const p of list) {
    const key = p.name.toLowerCase();
    const other = seen.get(key);
    if (other !== undefined && distanceM(other.lat, other.lon, p.lat, p.lon) < 60) {
      continue;
    }
    seen.set(key, p);
    out.push(p);
  }
  return out;
}

export function foldPolish(s: string): string {
  const from = 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ';
  const to = 'acelnoszzACELNOSZZ';
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s.charAt(i);
    const k = from.indexOf(ch);
    out += k >= 0 ? to.charAt(k) : ch;
  }
  return out.toLowerCase();
}

export function searchPlaces(ds: Dataset, query: string, limit: number): Place[] {
  const q = foldPolish(query.trim());
  if (q.length === 0) {
    return [];
  }
  const starts: Place[] = [];
  const contains: Place[] = [];
  for (const p of ds.places) {
    const n = foldPolish(p.name);
    if (n.startsWith(q)) {
      starts.push(p);
    } else if (n.indexOf(q) >= 0) {
      contains.push(p);
    }
  }
  return starts.concat(contains).slice(0, limit);
}
