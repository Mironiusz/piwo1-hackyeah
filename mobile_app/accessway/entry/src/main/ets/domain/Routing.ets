import {
  Barrier,
  Constraints,
  EdgeIssue,
  EdgeState,
  IssueClass,
  LatLon,
  Place,
  WalkEdge
} from '../model/Types';
import { tr } from '../model/I18n';
import { Assessment, edgeIssues, PENALTY_BLOCKING_FALLBACK } from './EdgeRules';
import { bearingDeg, distanceM, turnAngle, WALK_SPEED_MPS, walkMinutes } from './Geo';
import { Dataset } from './OsmMapping';

export const SNAP_MAX_M: number = 300;

class MinHeap {
  private keys: number[] = [];
  private vals: number[] = [];

  get size(): number {
    return this.keys.length;
  }

  push(key: number, val: number): void {
    this.keys.push(key);
    this.vals.push(val);
    let i = this.keys.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (this.keys[p] <= this.keys[i]) {
        break;
      }
      this.swap(i, p);
      i = p;
    }
  }

  popVal(): number {
    const top = this.vals[0];
    const lastK = this.keys.pop() as number;
    const lastV = this.vals.pop() as number;
    if (this.keys.length > 0) {
      this.keys[0] = lastK;
      this.vals[0] = lastV;
      let i = 0;
      const n = this.keys.length;
      while (true) {
        const l = 2 * i + 1;
        const r = l + 1;
        let m = i;
        if (l < n && this.keys[l] < this.keys[m]) {
          m = l;
        }
        if (r < n && this.keys[r] < this.keys[m]) {
          m = r;
        }
        if (m === i) {
          break;
        }
        this.swap(i, m);
        i = m;
      }
    }
    return top;
  }

  private swap(i: number, j: number): void {
    const k = this.keys[i];
    this.keys[i] = this.keys[j];
    this.keys[j] = k;
    const v = this.vals[i];
    this.vals[i] = this.vals[j];
    this.vals[j] = v;
  }
}

export enum WeightMode {
  ACCESSIBLE = 0,
  FALLBACK = 1,
  PLAIN = 2
}

export class SearchResult {
  dist: number[] = [];
  prevEdge: number[] = [];
}

/** Dijkstra on the walking network, weight `length x (1 + penalty)`; accessible mode excludes blocking segments. */
export function dijkstra(ds: Dataset, as: Assessment, start: number, target: number, mode: WeightMode,
  maxCost: number): SearchResult {
  const n = ds.nodes.length;
  const res = new SearchResult();
  res.dist = new Array<number>(n).fill(Infinity);
  res.prevEdge = new Array<number>(n).fill(-1);
  const done: boolean[] = new Array<boolean>(n).fill(false);
  const heap = new MinHeap();
  res.dist[start] = 0;
  heap.push(0, start);
  while (heap.size > 0) {
    const u = heap.popVal();
    if (done[u]) {
      continue;
    }
    done[u] = true;
    if (u === target) {
      break;
    }
    const du = res.dist[u];
    if (du > maxCost) {
      break;
    }
    for (let k = ds.adjStart[u]; k < ds.adjStart[u + 1]; k++) {
      const ei = ds.adjEdge[k];
      const e = ds.edges[ei];
      let w = e.lengthM;
      if (mode !== WeightMode.PLAIN) {
        if (as.blocking[ei]) {
          if (mode === WeightMode.ACCESSIBLE) {
            continue;
          }
          w = e.lengthM * (1 + as.penalty[ei] + PENALTY_BLOCKING_FALLBACK);
        } else {
          w = e.lengthM * (1 + as.penalty[ei]);
        }
      }
      const v = e.a === u ? e.b : e.a;
      const nd = du + w;
      if (nd < res.dist[v]) {
        res.dist[v] = nd;
        res.prevEdge[v] = ei;
        heap.push(nd, v);
      }
    }
  }
  return res;
}

function pathEdges(ds: Dataset, sr: SearchResult, start: number, end: number): number[] {
  const out: number[] = [];
  let cur = end;
  while (cur !== start) {
    const ei = sr.prevEdge[cur];
    if (ei < 0) {
      return [];
    }
    out.push(ei);
    cur = ds.otherEnd(ei, cur);
  }
  out.reverse();
  return out;
}

export interface RouteIssue {
  issue: EdgeIssue;
  atM: number;
  street: string;
  lat: number;
  lon: number;
}

export interface RouteStep {
  title: string;
  instruction: string;
  lengthM: number;
  startM: number;
  state: EdgeState;
  issues: EdgeIssue[];
  edges: number[];
  turnDeg: number;
}

export interface Omitted {
  text: string;
  street: string;
  lat: number;
  lon: number;
}

export class RouteResult {
  ok: boolean = false;
  error: string = '';
  barrierFree: boolean = true;
  startNode: number = -1;
  endNode: number = -1;
  edges: number[] = [];
  nodes: number[] = [];
  lengthM: number = 0;
  minutes: number = 0;
  noDataM: number = 0;
  issueM: number = 0;
  steps: RouteStep[] = [];
  issuesInProfile: RouteIssue[] = [];
  issuesExtra: RouteIssue[] = [];
  missing: RouteIssue[] = [];
  partialM: number = 0;
  omitted: Omitted[] = [];
  extraMinutes: number = 0;
}

export function wayLabel(e: WalkEdge): string {
  if (e.name.length > 0) {
    return e.name;
  }
  if (e.highway === 'steps') {
    return tr('schody', 'stairs');
  }
  if (e.highway === 'pedestrian') {
    return tr('deptak', 'pedestrian street');
  }
  if (e.highway === 'footway' || e.highway === 'path' || e.highway === 'corridor') {
    return tr('chodnik / ścieżka piesza', 'sidewalk / footpath');
  }
  if (e.highway === 'elevator') {
    return tr('winda', 'elevator');
  }
  return tr('ulica bez nazwy', 'unnamed street');
}

function turnText(angle: number): string {
  const a = Math.abs(angle);
  if (a < 25) {
    return tr('Idź prosto', 'Go straight');
  }
  if (a < 60) {
    return angle > 0 ? tr('Odbij lekko w prawo', 'Bear right') : tr('Odbij lekko w lewo', 'Bear left');
  }
  if (a <= 165) {
    return angle > 0 ? tr('Skręć w prawo', 'Turn right') : tr('Skręć w lewo', 'Turn left');
  }
  return tr('Zawróć', 'Turn around');
}

function edgeBearing(ds: Dataset, ei: number, fromNode: number): number {
  const e = ds.edges[ei];
  const a = ds.nodes[fromNode];
  const b = ds.nodes[e.a === fromNode ? e.b : e.a];
  return bearingDeg(a.lat, a.lon, b.lat, b.lon);
}

const EMPTY: Barrier[] = [];

/** Order of states from best to worst; a route step takes the worst state of its segments. */
const SEVERITY: EdgeState[] = [EdgeState.CLEAR, EdgeState.PARTIAL, EdgeState.NO_DATA, EdgeState.BARRIER];

/** Route for the constraints per the spec's Route section, with the barriers avoided compared to the shortest path. */
export function findRoute(ds: Dataset, as: Assessment, c: Constraints, barrierIndex: Map<number, Barrier[]>,
  from: LatLon, to: LatLon): RouteResult {
  const r = new RouteResult();
  r.startNode = ds.nearestNode(from.lat, from.lon, SNAP_MAX_M);
  r.endNode = ds.nearestNode(to.lat, to.lon, SNAP_MAX_M);
  if (r.startNode < 0) {
    r.error = tr('Punkt startu leży poza obszarem danych (ponad 300 m od sieci pieszej).',
      'The start is outside the data area (more than 300 m from the walking network).');
    return r;
  }
  if (r.endNode < 0) {
    r.error = tr('Cel leży poza obszarem danych (ponad 300 m od sieci pieszej).',
      'The destination is outside the data area (more than 300 m from the walking network).');
    return r;
  }
  if (r.startNode === r.endNode) {
    r.ok = true;
    r.nodes = [r.startNode];
    r.minutes = 0;
    return r;
  }
  let sr = dijkstra(ds, as, r.startNode, r.endNode, WeightMode.ACCESSIBLE, Infinity);
  if (sr.dist[r.endNode] === Infinity) {
    r.barrierFree = false;
    sr = dijkstra(ds, as, r.startNode, r.endNode, WeightMode.FALLBACK, Infinity);
  }
  if (sr.dist[r.endNode] === Infinity) {
    r.error = tr('Te punkty nie są połączone siecią pieszą w danych.',
      'These points are not connected by the walking network in the data.');
    return r;
  }
  r.edges = pathEdges(ds, sr, r.startNode, r.endNode);
  r.ok = true;
  let cur = r.startNode;
  r.nodes.push(cur);
  for (const ei of r.edges) {
    cur = ds.otherEnd(ei, cur);
    r.nodes.push(cur);
  }
  buildSteps(ds, as, c, barrierIndex, r);
  r.minutes = walkMinutes(r.lengthM);
  if (r.barrierFree) {
    buildOmitted(ds, as, c, barrierIndex, r);
  }
  return r;
}

function buildSteps(ds: Dataset, as: Assessment, c: Constraints, barrierIndex: Map<number, Barrier[]>,
  r: RouteResult): void {
  let pos = 0;
  let step: RouteStep | null = null;
  let prevBearing = -1;
  const seenBarriers: Set<string> = new Set<string>();
  for (let i = 0; i < r.edges.length; i++) {
    const ei = r.edges[i];
    const e = ds.edges[ei];
    const from = r.nodes[i];
    const label = wayLabel(e);
    const st = as.states[ei];
    const issues = edgeIssues(e, c, ds.sourceDate, barrierIndex.get(ei) ?? EMPTY);
    const bearing = edgeBearing(ds, ei, from);
    if (step === null || step.title !== label) {
      const angle = prevBearing < 0 ? 0 : turnAngle(prevBearing, bearing);
      const verb = step === null ? tr('Ruszaj', 'Start') : turnText(angle);
      const fresh: RouteStep = {
        title: label,
        instruction: `${verb}: ${label}`,
        lengthM: 0,
        startM: pos,
        state: st,
        issues: [],
        edges: [],
        turnDeg: angle
      };
      step = fresh;
      r.steps.push(fresh);
    }
    step.edges.push(ei);
    step.lengthM += e.lengthM;
    if (SEVERITY.indexOf(st) > SEVERITY.indexOf(step.state)) {
      step.state = st;
    }
    const nf = ds.nodes[from];
    for (const iss of issues) {
      if (iss.barrierId.length > 0) {
        if (seenBarriers.has(iss.barrierId)) {
          continue;
        }
        seenBarriers.add(iss.barrierId);
      }
      let dup = false;
      for (const known of step.issues) {
        if (known.text === iss.text && known.barrierId === iss.barrierId) {
          dup = true;
        }
      }
      if (dup) {
        continue;
      }
      step.issues.push(iss);
      const ri: RouteIssue = { issue: iss, atM: pos, street: label, lat: nf.lat, lon: nf.lon };
      if (iss.cls === IssueClass.BLOCKING) {
        r.issuesInProfile.push(ri);
      } else if (iss.cls === IssueClass.EXTRA) {
        r.issuesExtra.push(ri);
      } else if (iss.cls === IssueClass.INFO) {
        r.missing.push(ri);
      }
    }
    if (st === EdgeState.NO_DATA) {
      r.noDataM += e.lengthM;
    } else if (st === EdgeState.PARTIAL) {
      r.partialM += e.lengthM;
    } else if (st === EdgeState.BARRIER) {
      r.issueM += e.lengthM;
    }
    pos += e.lengthM;
    prevBearing = bearing;
  }
  r.lengthM = pos;
}

function buildOmitted(ds: Dataset, as: Assessment, c: Constraints, barrierIndex: Map<number, Barrier[]>,
  r: RouteResult): void {
  const plain = dijkstra(ds, as, r.startNode, r.endNode, WeightMode.PLAIN, Infinity);
  const edges = pathEdges(ds, plain, r.startNode, r.endNode);
  const onRoute: Set<number> = new Set<number>(r.edges);
  let plainLen = 0;
  const seen: Set<string> = new Set<string>();
  for (const ei of edges) {
    const e = ds.edges[ei];
    plainLen += e.lengthM;
    if (onRoute.has(ei) || !as.blocking[ei]) {
      continue;
    }
    const label = wayLabel(e);
    for (const iss of edgeIssues(e, c, ds.sourceDate, barrierIndex.get(ei) ?? EMPTY)) {
      if (iss.cls !== IssueClass.BLOCKING) {
        continue;
      }
      const key = `${iss.text}|${label}`;
      if (seen.has(key)) {
        continue;
      }
      seen.add(key);
      const n = ds.nodes[e.a];
      r.omitted.push({ text: iss.text, street: label, lat: n.lat, lon: n.lon });
    }
  }
  r.extraMinutes = Math.max(0, Math.round((r.lengthM - plainLen) / WALK_SPEED_MPS / 60));
}

export interface Reachable {
  place: Place;
  minutes: number;
  distanceM: number;
}

/** Places reachable without blocking segments within the minute limit, sorted by walking time. */
export function reachability(ds: Dataset, as: Assessment, from: LatLon, minutes: number): Reachable[] {
  const start = ds.nearestNode(from.lat, from.lon, SNAP_MAX_M);
  if (start < 0) {
    return [];
  }
  const limitM = minutes * 60 * WALK_SPEED_MPS;
  const sr = dijkstra(ds, as, start, -1, WeightMode.ACCESSIBLE, limitM * 3);
  const lengths = realLengths(ds, sr, start);
  const out: Reachable[] = [];
  for (const p of ds.places) {
    const node = ds.nearestNode(p.lat, p.lon, 60);
    if (node < 0 || lengths[node] === Infinity) {
      continue;
    }
    const d = lengths[node] + distanceM(p.lat, p.lon, ds.nodes[node].lat, ds.nodes[node].lon);
    if (d <= limitM) {
      out.push({ place: p, minutes: Math.max(1, Math.round(d / WALK_SPEED_MPS / 60)), distanceM: d });
    }
  }
  out.sort((x: Reachable, y: Reachable) => x.distanceM - y.distanceM);
  return out;
}

function realLengths(ds: Dataset, sr: SearchResult, start: number): number[] {
  const n = ds.nodes.length;
  const len: number[] = new Array<number>(n).fill(Infinity);
  len[start] = 0;
  const order: number[] = [];
  for (let i = 0; i < n; i++) {
    if (sr.dist[i] !== Infinity) {
      order.push(i);
    }
  }
  order.sort((a: number, b: number) => sr.dist[a] - sr.dist[b]);
  for (const v of order) {
    const ei = sr.prevEdge[v];
    if (ei < 0) {
      continue;
    }
    const u = ds.otherEnd(ei, v);
    len[v] = len[u] + ds.edges[ei].lengthM;
  }
  return len;
}
