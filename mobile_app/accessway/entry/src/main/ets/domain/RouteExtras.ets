import { tr } from '../model/I18n';
import { isAmenity } from '../model/Labels';
import { EdgeState, Fact, FactCategory, IssueKind } from '../model/Types';
import { distanceM, pointSegmentDistanceM } from './Geo';
import { Dataset } from './OsmMapping';
import { RouteResult } from './Routing';

export const AMENITY_REACH_M: number = 50;
export const BARRIER_REACH_ROUTE_M: number = 15;

export interface RouteFact {
  fact: Fact;
  atM: number;
}

/** Odległość od startu trasy do każdego jej węzła, w metrach. */
export function cumulativeM(ds: Dataset, r: RouteResult): number[] {
  const out: number[] = [0];
  for (let i = 1; i < r.nodes.length; i++) {
    const a = ds.nodes[r.nodes[i - 1]];
    const b = ds.nodes[r.nodes[i]];
    out.push(out[i - 1] + distanceM(a.lat, a.lon, b.lat, b.lon));
  }
  return out;
}

/** Pozycja punktu na trasie: odległość od startu do najbliższego miejsca na odcinkach trasy, albo -1 poza zasięgiem. */
export function positionOnRoute(ds: Dataset, r: RouteResult, cum: number[], lat: number, lon: number, reachM: number): number {
  let best = -1;
  let bestD = reachM;
  for (let i = 1; i < r.nodes.length; i++) {
    const a = ds.nodes[r.nodes[i - 1]];
    const b = ds.nodes[r.nodes[i]];
    const d = pointSegmentDistanceM(lat, lon, a.lat, a.lon, b.lat, b.lon);
    if (d <= bestD) {
      bestD = d;
      const along = Math.sqrt(Math.max(0, Math.pow(distanceM(lat, lon, a.lat, a.lon), 2) - d * d));
      best = cum[i - 1] + Math.min(along, cum[i] - cum[i - 1]);
    }
  }
  return best;
}

/**
 * Fakty na trasie z odległością od startu: bariery i obszary w zasięgu 15 m (plus promień obszaru), udogodnienia
 * w zasięgu 50 m. Fakty nieaktualne i ukryte przez moderację nie trafiają tu wcale, bo nie ma ich na liście.
 */
export function factsOnRoute(ds: Dataset, r: RouteResult, facts: Fact[]): RouteFact[] {
  const out: RouteFact[] = [];
  if (!r.ok || r.nodes.length < 2) {
    return out;
  }
  const cum = cumulativeM(ds, r);
  for (const f of facts) {
    const reach = isAmenity(f.kind) && f.category !== FactCategory.AREA ? AMENITY_REACH_M :
      BARRIER_REACH_ROUTE_M + f.radiusM;
    const at = positionOnRoute(ds, r, cum, f.lat, f.lon, reach);
    if (at >= 0) {
      out.push({ fact: f, atM: at });
    }
  }
  out.sort((x: RouteFact, y: RouteFact) => x.atM - y.atM);
  return out;
}

export interface DataGap {
  fromM: number;
  toM: number;
  noData: boolean;
  street: string;
  missing: string[];
}

function missingName(k: IssueKind): string {
  if (k === IssueKind.KERB_UNKNOWN) {
    return tr('krawężniki', 'kerbs');
  }
  if (k === IssueKind.SURFACE_UNKNOWN) {
    return tr('nawierzchnia', 'surface');
  }
  if (k === IssueKind.INCLINE_UNKNOWN) {
    return tr('nachylenie', 'incline');
  }
  if (k === IssueKind.WIDTH_UNKNOWN) {
    return tr('szerokość', 'width');
  }
  return '';
}

const MISSING_ORDER: IssueKind[] = [IssueKind.KERB_UNKNOWN, IssueKind.SURFACE_UNKNOWN, IssueKind.INCLINE_UNKNOWN,
  IssueKind.WIDTH_UNKNOWN];

/** Nazwy brakujących atrybutów w kolejności z makiety: krawężniki, nawierzchnia, nachylenie, szerokość. */
export function missingNames(kinds: IssueKind[]): string[] {
  const out: string[] = [];
  for (const k of MISSING_ORDER) {
    if (kinds.indexOf(k) >= 0) {
      out.push(missingName(k));
    }
  }
  return out;
}

/** Odcinki trasy z danymi niepełnymi albo bez danych, ze nazwą ulicy i brakującymi atrybutami. */
export function dataGaps(r: RouteResult): DataGap[] {
  const out: DataGap[] = [];
  for (const s of r.steps) {
    if (s.state !== EdgeState.PARTIAL && s.state !== EdgeState.NO_DATA) {
      continue;
    }
    const kinds: IssueKind[] = [];
    for (const i of s.issues) {
      if (kinds.indexOf(i.kind) < 0) {
        kinds.push(i.kind);
      }
    }
    const missing: string[] = [];
    for (const k of MISSING_ORDER) {
      if (kinds.indexOf(k) >= 0) {
        missing.push(missingName(k));
      }
    }
    const last = out.length > 0 ? out[out.length - 1] : null;
    if (last !== null && Math.abs(last.toM - s.startM) < 1 && last.street === s.title) {
      last.toM = s.startM + s.lengthM;
      last.noData = last.noData && s.state === EdgeState.NO_DATA;
      for (const m of missing) {
        if (last.missing.indexOf(m) < 0) {
          last.missing.push(m);
        }
      }
      continue;
    }
    out.push({ fromM: s.startM, toM: s.startM + s.lengthM, noData: s.state === EdgeState.NO_DATA, street: s.title,
      missing: missing });
  }
  return out;
}
