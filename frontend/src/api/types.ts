/**
 * The types of docs/product/api_contract.md. The field names are the ones of the contract, in snake case,
 * because the frontend passes the answers on as they are and checks none of them at run time.
 */

export const BARRIER_TYPES = ["stairs", "high_kerb", "poor_surface", "steep_incline", "narrow_passage"] as const;

export const AMENITY_TYPES = ["elevator", "ramp", "lowered_kerb", "accessible_toilet", "rest_place", "handrail_at_stairs"] as const;

export type BarrierType = (typeof BARRIER_TYPES)[number];

export type AmenityType = (typeof AMENITY_TYPES)[number];

export type FactType = BarrierType | AmenityType;

export type FactStatus = "unverified" | "confirmed" | "disputed" | "outdated";

export type FactSource = "openstreetmap" | "user_report";

export type Verdict = "confirm" | "deny";

export type GeozoneRadius = 10 | 25 | 50 | 100;

export interface Point {
  lat: number;
  lon: number;
}

export interface Fact {
  id: number;
  type: FactType;
  point: Point;
  geozone_radius_m: GeozoneRadius | null;
  description: string | null;
  step_count: number | null;
  source: FactSource;
  status: FactStatus;
  is_removed_from_osm: boolean;
  osm_edited_on: string | null;
  last_confirmed_on: string | null;
  is_sample: boolean;
  can_be_flagged: boolean;
}

export interface RouteFact extends Fact {
  distance_from_start_m: number;
  is_overruled_by_osm: boolean;
}

export type SegmentState = "barrier" | "no_barrier" | "partial_data" | "no_data";

/**
 * The state of a segment as the service answers it: one of the four states, or not_assessed for every segment
 * of a route whose needs name no barrier.
 */
export type AnsweredSegmentState = SegmentState | "not_assessed";

export type MissingAttribute = "kerbs" | "surface" | "incline" | "width" | "steps";

export interface Segment {
  line: [number, number][];
  length_m: number;
  state: AnsweredSegmentState;
  missing_attributes: MissingAttribute[];
  is_marked_wheelchair_no: boolean;
}

export interface Route {
  length_m: number;
  segments: Segment[];
  profile_barriers: RouteFact[];
  additional_barriers: RouteFact[];
  amenities: RouteFact[];
}

export interface RouteAlternative {
  route: Route;
  avoided_barriers: RouteFact[];
}

export interface PlanRouteRequest {
  start: Point;
  destination: Point;
  avoid: BarrierType[];
  need: AmenityType[];
}

export interface PlanRouteResponse {
  osm_copy_date: string;
  barrier_free_route_exists: boolean;
  route: Route;
  alternative: RouteAlternative | null;
}

export interface AddressMatch {
  label: string;
  point: Point;
}

export interface FactsInArea {
  facts: Fact[];
  is_truncated: boolean;
}

export interface NearbyFact {
  fact: Fact;
  distance_m: number;
}

export interface CreateFactRequest {
  idempotency_key: string;
  type: FactType;
  point: Point;
  description: string | null;
  step_count: number | null;
  geozone_radius_m: GeozoneRadius | null;
}

export interface Account {
  pseudonym: string;
  is_moderator: boolean;
}

export interface FlaggedFact {
  fact: Fact;
  flagged_on: string;
  is_hidden: boolean;
}

/**
 * The error codes of the contract, and network_error for a request that got no answer at all.
 */
export type ApiErrorCode =
  | "invalid_request"
  | "authentication_required"
  | "session_expired"
  | "moderator_role_required"
  | "not_found"
  | "fact_not_found"
  | "internal_error"
  | "routing_unavailable"
  | "point_outside_krakow"
  | "invalid_search_text"
  | "address_search_unavailable"
  | "idempotency_key_reused"
  | "vote_too_soon"
  | "fact_not_flaggable"
  | "pseudonym_taken"
  | "invalid_credentials"
  | "fact_not_flagged"
  | "network_error";

/**
 * Tells whether a fact type is a barrier.
 */
export function isBarrierType(type: FactType): type is BarrierType {
  return (BARRIER_TYPES as readonly string[]).includes(type);
}
