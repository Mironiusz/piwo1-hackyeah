/**
 * Kształty JSON z `docs/product/api_contract.md` w repozytorium piwo1-hackyeah (stan z 2026-10-04), jeden do
 * jednego, z nazwami pól w snake case jak w kontrakcie. Zmiana kontraktu zaczyna się od tego pliku.
 */

export interface ApiPoint {
  lat: number;
  lon: number;
}

export interface ApiFact {
  id: number;
  type: string;
  point: ApiPoint;
  geozone_radius_m: number | null;
  description: string | null;
  step_count: number | null;
  source: string;
  status: string;
  is_removed_from_osm: boolean;
  osm_edited_on: string | null;
  last_confirmed_on: string | null;
  is_sample: boolean;
  can_be_flagged: boolean;
}

export interface ApiRouteFact extends ApiFact {
  distance_from_start_m: number;
  is_overruled_by_osm: boolean;
}

export interface ApiAccount {
  pseudonym: string;
  is_moderator: boolean;
}

export interface ApiErrorDetail {
  code: string;
  fields?: string[];
  repeat_allowed_at?: string;
}

export interface ApiErrorBody {
  error: ApiErrorDetail;
}

export interface ApiPlanRouteRequest {
  start: ApiPoint;
  destination: ApiPoint;
  avoid: string[];
  need: string[];
}

export interface ApiSegment {
  line: number[][];
  length_m: number;
  state: string;
  missing_attributes: string[];
  is_marked_wheelchair_no: boolean;
}

export interface ApiRoute {
  length_m: number;
  segments: ApiSegment[];
  profile_barriers: ApiRouteFact[];
  additional_barriers: ApiRouteFact[];
  amenities: ApiRouteFact[];
}

export interface ApiAlternative {
  route: ApiRoute;
  avoided_barriers: ApiRouteFact[];
}

export interface ApiPlanRouteResponse {
  osm_copy_date: string | null;
  barrier_free_route_exists: boolean;
  route: ApiRoute;
  alternative: ApiAlternative | null;
}

export interface ApiSearchRequest {
  text: string;
}

export interface ApiMatch {
  label: string;
  point: ApiPoint;
}

export interface ApiSearchResponse {
  matches: ApiMatch[];
}

export interface ApiOsmCopy {
  date: string | null;
}

export interface ApiAreaRequest {
  south_west: ApiPoint;
  north_east: ApiPoint;
}

export interface ApiFactsResponse {
  facts: ApiFact[];
  is_truncated: boolean;
}

export interface ApiFactResponse {
  fact: ApiFact;
}

export interface ApiNearbyRequest {
  type: string;
  point: ApiPoint;
}

export interface ApiNearbyItem {
  fact: ApiFact;
  distance_m: number;
}

export interface ApiNearbyResponse {
  facts: ApiNearbyItem[];
}

export interface ApiCreateFactRequest {
  idempotency_key: string;
  type: string;
  point: ApiPoint;
  description: string | null;
  step_count: number | null;
  geozone_radius_m: number | null;
}

export interface ApiVoteRequest {
  verdict: string;
}

export interface ApiCredentials {
  pseudonym: string;
  password: string;
}

export interface ApiAccountResponse {
  account: ApiAccount;
}

export interface ApiFlaggedItem {
  fact: ApiFact;
  flagged_on: string;
  is_hidden: boolean;
}

export interface ApiFlaggedResponse {
  facts: ApiFlaggedItem[];
}
