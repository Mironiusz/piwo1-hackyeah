import { decimal, tr } from '../model/I18n';
import { isAmenity, kindLabel, surfaceName } from '../model/Labels';
import {
  Barrier,
  Constraints,
  EdgeIssue,
  EdgeState,
  FactKind,
  FactStatus,
  IssueClass,
  IssueKind,
  NO_LIMIT,
  Roughness,
  TrustLevel,
  WalkEdge
} from '../model/Types';
import { pointSegmentDistanceM } from './Geo';
import { Dataset } from './OsmMapping';
import { factStatus, lastConfirmation } from './Trust';

export const BARRIER_REACH_M: number = 15;
export const PENALTY_EXTRA: number = 0.3;
export const PENALTY_INFO: number = 0.1;
export const PENALTY_BLOCKING_FALLBACK: number = 50;
export const EXTRA_INCLINE_PCT: number = 4;

/** Way types where width matters for passage; the width of a street's roadway says nothing about the sidewalk. */
const WIDTH_RELEVANT: string[] = ['footway', 'path', 'steps', 'corridor', 'cycleway', 'track'];

function osmIssue(kind: IssueKind, value: number, cls: IssueClass, text: string, date: number): EdgeIssue {
  return {
    kind: kind,
    value: value,
    barrierId: '',
    barrierKind: '',
    source: 'OpenStreetMap',
    observedAt: date,
    trust: TrustLevel.OFFICIAL,
    cls: cls,
    unconfirmed: false,
    text: text
  };
}

/** Whether a barrier of the given kind belongs to the needs, that is, violates the constraints derived from them. */
export function barrierViolates(kind: FactKind, c: Constraints): boolean {
  if (kind === FactKind.STEPS) {
    return c.avoidSteps;
  }
  if (kind === FactKind.KERB) {
    return c.maxKerbCm !== NO_LIMIT;
  }
  if (kind === FactKind.NARROW_PASSAGE) {
    return c.minWidthM !== NO_LIMIT;
  }
  if (kind === FactKind.ROUGH_SURFACE) {
    return c.maxRoughness !== Roughness.ROUGH;
  }
  if (kind === FactKind.STEEP_SLOPE) {
    return c.maxInclinePct !== NO_LIMIT;
  }
  return false;
}

/**
 * Effect of a report on a segment. A confirmed report of a barrier from the needs blocks the segment; an unconfirmed
 * or disputed one is only information and does not change the route, which until then follows OpenStreetMap.
 */
export function barrierIssue(b: Barrier, c: Constraints): EdgeIssue | null {
  if (isAmenity(b.kind) || b.hidden) {
    return null;
  }
  const st = factStatus(b.votes);
  if (st === FactStatus.OUTDATED) {
    return null;
  }
  const verified = st === FactStatus.CONFIRMED;
  let cls = IssueClass.EXTRA;
  if (verified && barrierViolates(b.kind, c)) {
    cls = IssueClass.BLOCKING;
  }
  const label = kindLabel(b.kind);
  return {
    kind: IssueKind.BARRIER,
    value: 0,
    barrierId: b.id,
    barrierKind: b.kind,
    source: tr('zgłoszenie', 'report'),
    observedAt: lastConfirmation(b.createdAt, b.votes),
    trust: verified ? TrustLevel.COMMUNITY : TrustLevel.UNVERIFIED,
    cls: cls,
    unconfirmed: !verified,
    text: label
  };
}

function surfaceRelevant(c: Constraints): boolean {
  return c.maxRoughness !== Roughness.ROUGH;
}

function inclineRelevant(e: WalkEdge, c: Constraints): boolean {
  return c.maxInclinePct !== NO_LIMIT && !e.isSteps;
}

function widthRelevant(e: WalkEdge, c: Constraints): boolean {
  return c.minWidthM !== NO_LIMIT && WIDTH_RELEVANT.indexOf(e.highway) >= 0;
}

function kerbRelevant(e: WalkEdge, c: Constraints): boolean {
  return c.maxKerbCm !== NO_LIMIT && (e.crossing || e.kerbUnknown || e.kerbCm >= 0);
}

/** Number of profile-relevant attributes that are known on the segment. */
export function knownRelevant(e: WalkEdge, c: Constraints): number {
  let n = 0;
  if (surfaceRelevant(c) && e.roughness >= 0) {
    n++;
  }
  if (inclineRelevant(e, c) && !isNaN(e.inclinePct)) {
    n++;
  }
  if (widthRelevant(e, c) && !isNaN(e.widthM)) {
    n++;
  }
  if (kerbRelevant(e, c) && e.kerbCm >= 0) {
    n++;
  }
  return n;
}

/**
 * List of the segment's issues against the constraints. Class blocking is a profile barrier, extra is an obstacle
 * outside the profile, info is a missing profile-relevant attribute.
 */
export function edgeIssues(e: WalkEdge, c: Constraints, date: number, barriers: Barrier[]): EdgeIssue[] {
  const out: EdgeIssue[] = [];
  if (e.isSteps && !e.hasRamp) {
    out.push(osmIssue(IssueKind.STEPS, 0, c.avoidSteps ? IssueClass.BLOCKING : IssueClass.EXTRA,
      tr('Schody', 'Stairs'), date));
  }
  if (!isNaN(e.inclinePct)) {
    const v = Math.abs(e.inclinePct);
    const txt = tr(`Nachylenie ${Math.round(v)}%`, `Incline ${Math.round(v)}%`);
    if (c.maxInclinePct !== NO_LIMIT && v > c.maxInclinePct) {
      out.push(osmIssue(IssueKind.INCLINE, v, IssueClass.BLOCKING, txt, date));
    } else if (v >= EXTRA_INCLINE_PCT) {
      out.push(osmIssue(IssueKind.INCLINE, v, IssueClass.EXTRA, txt, date));
    }
  } else if (inclineRelevant(e, c)) {
    out.push(osmIssue(IssueKind.INCLINE_UNKNOWN, 0, IssueClass.INFO, tr('Nachylenie nieznane', 'Incline unknown'), date));
  }
  if (e.roughness >= 0) {
    const txt = tr(`Nawierzchnia: ${surfaceName(e.surfaceLabel)}`, `Surface: ${surfaceName(e.surfaceLabel)}`);
    if (e.roughness > c.maxRoughness) {
      out.push(osmIssue(IssueKind.SURFACE, e.roughness, IssueClass.BLOCKING, txt, date));
    } else if (e.roughness >= Roughness.MODERATE) {
      out.push(osmIssue(IssueKind.SURFACE, e.roughness, IssueClass.EXTRA, txt, date));
    }
  } else if (surfaceRelevant(c)) {
    out.push(osmIssue(IssueKind.SURFACE_UNKNOWN, 0, IssueClass.INFO, tr('Nawierzchnia nieznana', 'Surface unknown'), date));
  }
  if (!isNaN(e.widthM)) {
    if (c.minWidthM !== NO_LIMIT && e.widthM < c.minWidthM) {
      out.push(osmIssue(IssueKind.WIDTH, e.widthM, IssueClass.BLOCKING,
        tr(`Szerokość ${decimal(e.widthM, 2)} m`, `Width ${decimal(e.widthM, 2)} m`), date));
    }
  } else if (widthRelevant(e, c)) {
    out.push(osmIssue(IssueKind.WIDTH_UNKNOWN, 0, IssueClass.INFO, tr('Szerokość nieznana', 'Width unknown'), date));
  }
  if (e.kerbCm >= 0) {
    const txt = tr(`Krawężnik ${Math.round(e.kerbCm)} cm`, `Kerb ${Math.round(e.kerbCm)} cm`);
    if (c.maxKerbCm !== NO_LIMIT && e.kerbCm > c.maxKerbCm) {
      out.push(osmIssue(IssueKind.KERB, e.kerbCm, IssueClass.BLOCKING, txt, date));
    } else if (e.kerbCm > 3) {
      out.push(osmIssue(IssueKind.KERB, e.kerbCm, IssueClass.EXTRA, txt, date));
    }
  } else if (kerbRelevant(e, c)) {
    out.push(osmIssue(IssueKind.KERB_UNKNOWN, 0, IssueClass.INFO,
      tr('Krawężnik na przejściu: wysokość nieznana', 'Kerb at the crossing: height unknown'), date));
  }
  if (e.wheelchairNo) {
    out.push(osmIssue(IssueKind.WHEELCHAIR_NO, 0, c.avoidSteps ? IssueClass.BLOCKING : IssueClass.EXTRA,
      tr('Oznaczone jako niedostępne dla wózków', 'Marked as not accessible for wheelchairs'), date));
  }
  for (const b of barriers) {
    const issue = barrierIssue(b, c);
    if (issue !== null) {
      out.push(issue);
    }
  }
  return out;
}

/**
 * Segment state: profile barrier, no barrier (all relevant attributes known), partial data or no data.
 * Obstacles outside the profile and unconfirmed reports do not change the state, so a segment without complete
 * data is never marked as barrier-free.
 */
export function stateOf(issues: EdgeIssue[], known: number): EdgeState {
  let missing = 0;
  for (const i of issues) {
    if (i.cls === IssueClass.BLOCKING) {
      return EdgeState.BARRIER;
    }
    if (i.cls === IssueClass.INFO) {
      missing++;
    }
  }
  if (missing === 0) {
    return EdgeState.CLEAR;
  }
  return known > 0 ? EdgeState.PARTIAL : EdgeState.NO_DATA;
}

export function edgeState(e: WalkEdge, c: Constraints, issues: EdgeIssue[]): EdgeState {
  return stateOf(issues, knownRelevant(e, c));
}

export function hasBlocking(issues: EdgeIssue[]): boolean {
  for (const i of issues) {
    if (i.cls === IssueClass.BLOCKING) {
      return true;
    }
  }
  return false;
}

/** Segment weight penalty; an unconfirmed report does not affect the route. */
export function penaltyOf(issues: EdgeIssue[]): number {
  let p = 0;
  for (const i of issues) {
    if (i.cls === IssueClass.EXTRA && !i.unconfirmed) {
      p += PENALTY_EXTRA;
    } else if (i.cls === IssueClass.INFO) {
      p += PENALTY_INFO;
    }
  }
  return p;
}

/** Barriers assigned to the segments that pass within the barrier's radius plus 15 m. */
export function indexBarriers(ds: Dataset, barriers: Barrier[]): Map<number, Barrier[]> {
  const out: Map<number, Barrier[]> = new Map<number, Barrier[]>();
  for (const b of barriers) {
    const reach = b.radiusM + BARRIER_REACH_M;
    const dLat = reach / 111000 + 0.0005;
    const dLon = reach / 71000 + 0.0005;
    for (const e of ds.edges) {
      const na = ds.nodes[e.a];
      const nb = ds.nodes[e.b];
      if (Math.min(na.lat, nb.lat) > b.lat + dLat || Math.max(na.lat, nb.lat) < b.lat - dLat ||
        Math.min(na.lon, nb.lon) > b.lon + dLon || Math.max(na.lon, nb.lon) < b.lon - dLon) {
        continue;
      }
      if (pointSegmentDistanceM(b.lat, b.lon, na.lat, na.lon, nb.lat, nb.lon) <= reach) {
        const list = out.get(e.index);
        if (list === undefined) {
          out.set(e.index, [b]);
        } else {
          list.push(b);
        }
      }
    }
  }
  return out;
}

export const STATE_ORDER: EdgeState[] = [EdgeState.CLEAR, EdgeState.PARTIAL, EdgeState.NO_DATA, EdgeState.BARRIER];

export class Assessment {
  states: EdgeState[] = [];
  blocking: boolean[] = [];
  penalty: number[] = [];
  counts: number[] = [0, 0, 0, 0];
}

const NO_BARRIERS: Barrier[] = [];

export function assessAll(ds: Dataset, c: Constraints, barrierIndex: Map<number, Barrier[]>): Assessment {
  const a = new Assessment();
  a.states = new Array<EdgeState>(ds.edges.length);
  a.blocking = new Array<boolean>(ds.edges.length);
  a.penalty = new Array<number>(ds.edges.length);
  for (const e of ds.edges) {
    const issues = edgeIssues(e, c, ds.sourceDate, barrierIndex.get(e.index) ?? NO_BARRIERS);
    const st = edgeState(e, c, issues);
    a.states[e.index] = st;
    a.blocking[e.index] = st === EdgeState.BARRIER;
    a.penalty[e.index] = penaltyOf(issues);
    a.counts[STATE_ORDER.indexOf(st)]++;
  }
  return a;
}
