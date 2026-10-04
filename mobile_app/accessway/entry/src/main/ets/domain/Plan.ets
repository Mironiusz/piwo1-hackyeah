import {
  ErrorCode,
  RepoError,
  RouteAlternative,
  RouteFactItem,
  RouteGap,
  RoutePlan,
  RouteRequest,
  RouteSegment
} from '../data/Repository';
import { tr } from '../model/I18n';
import {
  Barrier,
  Constraints,
  EdgeState,
  Fact,
  FactCategory,
  FactKind,
  FactSource,
  FactStatus,
  IssueClass,
  IssueKind,
  LatLon,
  Vote
} from '../model/Types';
import { assessAll, edgeIssues, indexBarriers } from './EdgeRules';
import { distanceM } from './Geo';
import { hasBarriers, needsConstraints } from './Needs';
import { Dataset } from './OsmMapping';
import { factsOnRoute, missingNames } from './RouteExtras';
import { findRoute, RouteResult } from './Routing';

/** Odcinek dojścia od wskazanego punktu do sieci krótszy niż ten próg nie jest pokazywany jako luka w danych. */
export const CONNECTOR_MIN_M: number = 8;

function forcedConfirmed(b: Barrier): Barrier {
  const extra: Vote[] = [
    { voterId: '__alt1', value: 1, weight: 1, at: 0 },
    { voterId: '__alt2', value: 1, weight: 1, at: 0 }
  ];
  return {
    id: b.id, kind: b.kind, lat: b.lat, lon: b.lon, radiusM: b.radiusM, isArea: b.isArea, stepCount: b.stepCount,
    description: b.description, street: b.street, createdAt: b.createdAt, isSample: b.isSample,
    votes: b.votes.concat(extra), hidden: b.hidden, flagged: b.flagged
  };
}

class RawRoute {
  r: RouteResult = new RouteResult();
  states: EdgeState[] = [];
  c: Constraints = needsConstraints({ avoid: [], need: [] });
  idx: Map<number, Barrier[]> = new Map<number, Barrier[]>();
}

function rawRoute(ds: Dataset, reports: Barrier[], req: RouteRequest, avoid: string[]): RawRoute {
  const eff: Barrier[] = [];
  for (const b of reports) {
    eff.push(avoid.indexOf(b.id) >= 0 ? forcedConfirmed(b) : b);
  }
  const c = needsConstraints(req.needs);
  const idx = indexBarriers(ds, eff);
  const as = assessAll(ds, c, idx);
  const out = new RawRoute();
  out.r = findRoute(ds, as, c, idx, req.from, req.to);
  out.states = as.states;
  out.c = c;
  out.idx = idx;
  return out;
}

/** Atrybuty, których brak ma znaczenie dla potrzeb, w kolejności z makiety. */
function relevantMissing(req: RouteRequest): string[] {
  const out: string[] = [];
  const a = req.needs.avoid;
  if (a.indexOf(FactKind.KERB) >= 0) {
    out.push(tr('krawężniki', 'kerbs'));
  }
  if (a.indexOf(FactKind.ROUGH_SURFACE) >= 0) {
    out.push(tr('nawierzchnia', 'surface'));
  }
  if (a.indexOf(FactKind.STEEP_SLOPE) >= 0) {
    out.push(tr('nachylenie', 'incline'));
  }
  if (a.indexOf(FactKind.NARROW_PASSAGE) >= 0) {
    out.push(tr('szerokość', 'width'));
  }
  if (a.indexOf(FactKind.STEPS) >= 0) {
    out.push(tr('stopnie', 'steps'));
  }
  return out;
}

class Bounds {
  minLat: number = 90;
  maxLat: number = -90;
  minLon: number = 180;
  maxLon: number = -180;

  add(lat: number, lon: number): void {
    this.minLat = Math.min(this.minLat, lat);
    this.maxLat = Math.max(this.maxLat, lat);
    this.minLon = Math.min(this.minLon, lon);
    this.maxLon = Math.max(this.maxLon, lon);
  }
}

const NO_BARRIERS: Barrier[] = [];

function segmentsOf(ds: Dataset, raw: RawRoute, offsetM: number, bounds: Bounds, missing: IssueKind[][]): RouteSegment[] {
  const out: RouteSegment[] = [];
  const r = raw.r;
  let pos = offsetM;
  let cur: RouteSegment | null = null;
  let kinds: IssueKind[] = [];
  for (let i = 0; i < r.edges.length; i++) {
    const ei = r.edges[i];
    const e = ds.edges[ei];
    const a = ds.nodes[r.nodes[i]];
    const b = ds.nodes[r.nodes[i + 1]];
    const st = raw.states[ei];
    if (cur === null || cur.state !== st || (cur.street !== e.name && st !== EdgeState.CLEAR)) {
      const fresh: RouteSegment = { pts: [a.lat, a.lon], state: st, fromM: pos, toM: pos, street: e.name };
      cur = fresh;
      kinds = [];
      out.push(fresh);
      missing.push(kinds);
    }
    if (st === EdgeState.PARTIAL) {
      for (const iss of edgeIssues(e, raw.c, ds.sourceDate, raw.idx.get(ei) ?? NO_BARRIERS)) {
        if (iss.cls === IssueClass.INFO && kinds.indexOf(iss.kind) < 0) {
          kinds.push(iss.kind);
        }
      }
    }
    cur.pts.push(b.lat, b.lon);
    pos += e.lengthM;
    cur.toM = pos;
    bounds.add(a.lat, a.lon);
    bounds.add(b.lat, b.lon);
  }
  return out;
}

function connector(from: LatLon, to: LatLon, fromM: number, toM: number): RouteSegment {
  return { pts: [from.lat, from.lon, to.lat, to.lon], state: EdgeState.NO_DATA, fromM: fromM, toM: toM, street: '' };
}

/**
 * Plan trasy dla potrzeb: geometria w stanach, fakty na trasie, luki w danych i trasy alternatywne. Bez żadnej
 * bariery w potrzebach odcinki nie są oceniane, więc plan nie ma luk ani alternatyw.
 */
export function buildPlan(ds: Dataset, facts: Fact[], reports: Barrier[], req: RouteRequest): RoutePlan {
  const raw = rawRoute(ds, reports, req, req.avoidFactIds);
  const r = raw.r;
  if (!r.ok) {
    const outside = r.startNode < 0 || r.endNode < 0;
    throw new RepoError(outside ? ErrorCode.OUTSIDE_AREA : ErrorCode.NO_ROUTE, r.error);
  }
  const rated = hasBarriers(req.needs);
  const bounds = new Bounds();
  bounds.add(req.from.lat, req.from.lon);
  bounds.add(req.to.lat, req.to.lon);
  const sNode = ds.nodes[r.startNode];
  const eNode = ds.nodes[r.endNode];
  const dStart = distanceM(req.from.lat, req.from.lon, sNode.lat, sNode.lon);
  const dEnd = distanceM(req.to.lat, req.to.lon, eNode.lat, eNode.lon);
  const total = dStart + r.lengthM + dEnd;
  const segments: RouteSegment[] = [];
  if (dStart >= 1) {
    segments.push(connector(req.from, { lat: sNode.lat, lon: sNode.lon }, 0, dStart));
  }
  const missing: IssueKind[][] = [];
  const network = segmentsOf(ds, raw, dStart, bounds, missing);
  for (const s of network) {
    segments.push(s);
  }
  if (dEnd >= 1) {
    segments.push(connector({ lat: eNode.lat, lon: eNode.lon }, req.to, dStart + r.lengthM, total));
  }
  const items: RouteFactItem[] = [];
  for (const rf of factsOnRoute(ds, r, facts)) {
    items.push({ fact: rf.fact, atM: rf.atM + dStart });
  }
  const gaps: RouteGap[] = [];
  const alternatives: RouteAlternative[] = [];
  let noDataM = 0;
  if (rated) {
    const all = relevantMissing(req);
    const noSteps = all.filter((m: string) => m !== tr('stopnie', 'steps'));
    if (dStart >= CONNECTOR_MIN_M) {
      gaps.push({ fromM: 0, toM: dStart, street: '', missing: all, isStart: true, isEnd: false });
    }
    for (let i = 0; i < network.length; i++) {
      const s = network[i];
      if (s.state === EdgeState.PARTIAL || s.state === EdgeState.NO_DATA) {
        gaps.push({ fromM: s.fromM, toM: s.toM, street: s.street,
          missing: s.state === EdgeState.NO_DATA ? noSteps : missingNames(missing[i]), isStart: false, isEnd: false });
      }
    }
    if (dEnd >= CONNECTOR_MIN_M) {
      gaps.push({ fromM: dStart + r.lengthM, toM: total, street: '', missing: all, isStart: false, isEnd: true });
    }
    noDataM = r.noDataM + dStart + dEnd;
    for (const it of items) {
      const f = it.fact;
      if (f.source !== FactSource.REPORT || f.category === FactCategory.AMENITY || f.status === FactStatus.CONFIRMED ||
        req.needs.avoid.indexOf(f.kind) < 0 || req.avoidFactIds.indexOf(f.id) >= 0) {
        continue;
      }
      const alt = rawRoute(ds, reports, req, req.avoidFactIds.concat([f.id])).r;
      if (alt.ok && alt.edges.join(',') !== r.edges.join(',') && factsOnRoute(ds, alt, [f]).length === 0) {
        alternatives.push({ factId: f.id, extraM: Math.max(0, alt.lengthM - r.lengthM) });
      }
    }
  }
  return {
    rated: rated,
    barrierFree: !rated || r.barrierFree,
    lengthM: total,
    noDataM: noDataM,
    segments: segments,
    facts: items,
    gaps: gaps,
    alternatives: alternatives,
    minLat: bounds.minLat,
    maxLat: bounds.maxLat,
    minLon: bounds.minLon,
    maxLon: bounds.maxLon
  };
}
