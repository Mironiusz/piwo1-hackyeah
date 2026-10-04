import { opposite } from '../domain/Facts';
import { tr } from '../model/I18n';
import { EdgeState, Fact, FactCategory, FactKind, FactSource, FactStatus } from '../model/Types';
import { ApiFact, ApiPlanRouteResponse, ApiRoute, ApiRouteFact } from './ApiTypes';
import { RouteAlternative, RouteFactItem, RouteGap, RoutePlan, RouteSegment } from './Repository';

/**
 * Translation between the API contract shapes and the app types. No network calls and no platform API,
 * so it works in unit tests on Node.
 */

const KIND_CODES: string[][] = [
  ['stairs', FactKind.STEPS],
  ['high_kerb', FactKind.KERB],
  ['poor_surface', FactKind.ROUGH_SURFACE],
  ['steep_incline', FactKind.STEEP_SLOPE],
  ['narrow_passage', FactKind.NARROW_PASSAGE],
  ['ramp', FactKind.RAMP],
  ['elevator', FactKind.ELEVATOR],
  ['lowered_kerb', FactKind.LOWERED_KERB],
  ['accessible_toilet', FactKind.ACCESSIBLE_TOILET],
  ['rest_place', FactKind.REST_SPOT],
  ['handrail_at_stairs', FactKind.HANDRAIL]
];

export function kindToApi(k: FactKind): string {
  for (const p of KIND_CODES) {
    if (p[1] === k) {
      return p[0];
    }
  }
  return k;
}

export function kindFromApi(code: string): FactKind {
  for (const p of KIND_CODES) {
    if (p[0] === code) {
      return p[1] as FactKind;
    }
  }
  return FactKind.STEPS;
}

export function knownKind(code: string): boolean {
  for (const p of KIND_CODES) {
    if (p[0] === code) {
      return true;
    }
  }
  return false;
}

export function statusFromApi(code: string): FactStatus {
  if (code === 'confirmed') {
    return FactStatus.CONFIRMED;
  }
  if (code === 'disputed') {
    return FactStatus.DISPUTED;
  }
  if (code === 'outdated') {
    return FactStatus.OUTDATED;
  }
  return FactStatus.UNVERIFIED;
}

export function stateFromApi(code: string): EdgeState {
  if (code === 'barrier') {
    return EdgeState.BARRIER;
  }
  if (code === 'no_barrier') {
    return EdgeState.CLEAR;
  }
  if (code === 'partial_data') {
    return EdgeState.PARTIAL;
  }
  return EdgeState.NO_DATA;
}

/** A `YYYY-MM-DD` day computed by the server, as the moment at noon of that day, so it displays without shifts. */
export function dayToMs(day: string | null): number {
  if (day === null || day.length < 10) {
    return 0;
  }
  const y = parseInt(day.substring(0, 4), 10);
  const m = parseInt(day.substring(5, 7), 10);
  const d = parseInt(day.substring(8, 10), 10);
  if (isNaN(y) || isNaN(m) || isNaN(d)) {
    return 0;
  }
  return new Date(y, m - 1, d, 12).getTime();
}

export function factFromApi(a: ApiFact): Fact {
  const kind = kindFromApi(a.type);
  const isArea = a.geozone_radius_m !== null && a.geozone_radius_m > 0;
  const osm = a.source === 'openstreetmap';
  const confirmed = dayToMs(a.last_confirmed_on);
  return {
    id: `${a.id}`,
    kind: kind,
    category: isArea ? FactCategory.AREA : (FactKind.ELEVATOR === kind || FactKind.RAMP === kind ||
      FactKind.LOWERED_KERB === kind || FactKind.ACCESSIBLE_TOILET === kind || FactKind.REST_SPOT === kind ||
      FactKind.HANDRAIL === kind ? FactCategory.AMENITY : FactCategory.BARRIER),
    source: osm ? FactSource.OSM : FactSource.REPORT,
    lat: a.point.lat,
    lon: a.point.lon,
    radiusM: isArea ? (a.geozone_radius_m as number) : 0,
    stepCount: a.step_count ?? 0,
    street: '',
    description: a.description ?? '',
    date: osm ? dayToMs(a.osm_edited_on) : confirmed,
    lastConfirmed: confirmed,
    status: statusFromApi(a.status),
    isSample: a.is_sample,
    conflictKind: '',
    conflictDate: 0,
    hidden: false,
    flagged: false
  };
}

export function routeFactFromApi(a: ApiRouteFact): Fact {
  const f = factFromApi(a);
  if (a.is_overruled_by_osm) {
    f.conflictKind = opposite(f.kind);
  }
  return f;
}

function missingLabel(code: string): string {
  if (code === 'kerbs') {
    return tr('krawężniki', 'kerbs');
  }
  if (code === 'surface') {
    return tr('nawierzchnia', 'surface');
  }
  if (code === 'incline') {
    return tr('nachylenie', 'incline');
  }
  if (code === 'width') {
    return tr('szerokość', 'width');
  }
  if (code === 'steps') {
    return tr('stopnie', 'steps');
  }
  return code;
}

/** A short no-data segment at the start or end of a route is the walk from the chosen point to the sidewalks. */
const CONNECTOR_MAX_M: number = 80;

/**
 * Route plan from the `plan_route` response. Segment states, fact groups and missing attributes come from the
 * server; the app only computes segment positions from the start and the map rectangle. `rated` says whether the
 * needs have any barrier, because without one the result screen shows the route without a rating.
 */
export function planFromApi(route: ApiRoute, barrierFree: boolean, rated: boolean,
  alternative: ApiPlanRouteResponse | null): RoutePlan {
  const segments: RouteSegment[] = [];
  const gaps: RouteGap[] = [];
  let pos = 0;
  let noData = 0;
  let minLat = 90;
  let maxLat = -90;
  let minLon = 180;
  let maxLon = -180;
  const last = route.segments.length - 1;
  for (let i = 0; i < route.segments.length; i++) {
    const s = route.segments[i];
    const pts: number[] = [];
    for (const p of s.line) {
      pts.push(p[1], p[0]);
      minLat = Math.min(minLat, p[1]);
      maxLat = Math.max(maxLat, p[1]);
      minLon = Math.min(minLon, p[0]);
      maxLon = Math.max(maxLon, p[0]);
    }
    const state = stateFromApi(s.state);
    segments.push({ pts: pts, state: state, fromM: pos, toM: pos + s.length_m, street: '' });
    if (rated && (state === EdgeState.PARTIAL || state === EdgeState.NO_DATA)) {
      const missing = s.missing_attributes.map((c: string): string => missingLabel(c));
      if (s.is_marked_wheelchair_no) {
        missing.push(tr('OpenStreetMap oznacza tę drogę jako niedostępną dla wózków',
          'OpenStreetMap marks this way as not accessible for wheelchairs'));
      }
      const prev = gaps.length > 0 ? gaps[gaps.length - 1] : null;
      const short = state === EdgeState.NO_DATA && s.length_m <= CONNECTOR_MAX_M;
      if (prev !== null && Math.abs(prev.toM - pos) < 1 && !prev.isStart && !(i === last && short)) {
        prev.toM = pos + s.length_m;
        for (const m of missing) {
          if (prev.missing.indexOf(m) < 0) {
            prev.missing.push(m);
          }
        }
      } else {
        gaps.push({ fromM: pos, toM: pos + s.length_m, street: '', missing: missing,
          isStart: i === 0 && short, isEnd: i === last && short });
      }
    }
    if (state === EdgeState.NO_DATA) {
      noData += s.length_m;
    }
    pos += s.length_m;
  }
  const facts: RouteFactItem[] = [];
  const groups: ApiRouteFact[][] = [route.profile_barriers, route.additional_barriers, route.amenities];
  for (const g of groups) {
    for (const f of g) {
      facts.push({ fact: routeFactFromApi(f), atM: f.distance_from_start_m });
    }
  }
  facts.sort((a: RouteFactItem, b: RouteFactItem) => a.atM - b.atM);
  const alternatives: RouteAlternative[] = [];
  if (alternative !== null && alternative.alternative !== null) {
    const alt = alternative.alternative;
    for (const b of alt.avoided_barriers) {
      alternatives.push({ factId: `${b.id}`, extraM: Math.max(0, alt.route.length_m - route.length_m) });
    }
  }
  return {
    rated: rated,
    barrierFree: !rated || barrierFree,
    lengthM: route.length_m,
    noDataM: rated ? noData : 0,
    segments: segments,
    facts: facts,
    gaps: gaps,
    alternatives: alternatives,
    minLat: minLat,
    maxLat: maxLat,
    minLon: minLon,
    maxLon: maxLon
  };
}
