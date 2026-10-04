import { NearbyFact } from '../domain/Facts';
import { Needs } from '../domain/Needs';
import { EdgeState, Fact, FactKind, LatLon } from '../model/Types';

/**
 * Boundary between the UI and the data. Screens use only these types and methods; today LocalRepository answers
 * them (data on the device), and once the team's API is connected a second implementation of the same interface
 * is enough. All methods are asynchronous, and an error is reported as a RepoError with a code.
 */

export enum ErrorCode {
  UNAVAILABLE = 'unavailable',
  NOT_FOUND = 'not_found',
  NO_ROUTE = 'no_route',
  OUTSIDE_AREA = 'outside_area',
  BAD_CREDENTIALS = 'bad_credentials',
  TAKEN = 'taken',
  INVALID_PSEUDONYM = 'invalid_pseudonym',
  INVALID_PASSWORD = 'invalid_password',
  VOTE_TOO_SOON = 'vote_too_soon',
  FORBIDDEN = 'forbidden',
  SESSION_EXPIRED = 'session_expired',
  AUTH_REQUIRED = 'authentication_required',
  INVALID_REQUEST = 'invalid_request',
  NOT_FLAGGABLE = 'not_flaggable',
  INTERNAL = 'internal'
}

export class RepoError extends Error {
  code: ErrorCode;

  constructor(code: ErrorCode, message: string) {
    super(message);
    this.code = code;
  }
}

export interface DataInfo {
  osmDate: number;
  isSample: boolean;
}

export interface MyVote {
  stillThere: boolean;
  at: number;
}

export interface NewReport {
  /** UUID generated once when the person approves the summary and sent unchanged with every attempt. */
  idempotencyKey: string;
  kind: FactKind;
  isArea: boolean;
  lat: number;
  lon: number;
  radiusM: number;
  stepCount: number;
  description: string;
}

export interface GeocodeResult {
  id: string;
  name: string;
  address: string;
  lat: number;
  lon: number;
}

/** A part of the route in one state, with geometry to draw on the map. */
export interface RouteSegment {
  pts: number[];
  state: EdgeState;
  fromM: number;
  toM: number;
  street: string;
}

export interface RouteFactItem {
  fact: Fact;
  atM: number;
}

export interface RouteGap {
  fromM: number;
  toM: number;
  street: string;
  missing: string[];
  isStart: boolean;
  isEnd: boolean;
}

/** A route that avoids one unverified or disputed fact from the needs, computed as if it were confirmed. */
export interface RouteAlternative {
  factId: string;
  extraM: number;
}

export interface RouteRequest {
  from: LatLon;
  to: LatLon;
  needs: Needs;
  avoidFactIds: string[];
}

export interface RoutePlan {
  rated: boolean;
  barrierFree: boolean;
  lengthM: number;
  noDataM: number;
  segments: RouteSegment[];
  facts: RouteFactItem[];
  gaps: RouteGap[];
  alternatives: RouteAlternative[];
  minLat: number;
  maxLat: number;
  minLon: number;
  maxLon: number;
}

export interface Account {
  pseudonym: string;
  moderator: boolean;
}

/** Map rectangle from which we take facts. */
export interface Area {
  south: number;
  west: number;
  north: number;
  east: number;
}

export interface FactsPage {
  facts: Fact[];
  truncated: boolean;
}

export interface FactsRepository {
  info(): DataInfo;
  refreshInfo(): Promise<DataInfo>;
  listFacts(area: Area): Promise<FactsPage>;
  findNearby(kind: FactKind, isArea: boolean, lat: number, lon: number): Promise<NearbyFact[]>;
  getFact(id: string): Promise<Fact>;
  myVote(id: string): Promise<MyVote | null>;
  vote(id: string, stillThere: boolean): Promise<MyVote>;
  report(input: NewReport): Promise<Fact>;
  flagForModeration(id: string): Promise<void>;
}

export interface RoutingRepository {
  route(req: RouteRequest): Promise<RoutePlan>;
}

export interface GeocodingRepository {
  search(text: string): Promise<GeocodeResult[]>;
  streetAt(lat: number, lon: number): Promise<string>;
}

export interface AccountRepository {
  current(): Promise<Account | null>;
  login(pseudonym: string, password: string): Promise<Account>;
  signup(pseudonym: string, password: string): Promise<Account>;
  logout(): Promise<void>;
  deleteAccount(): Promise<void>;
}

export interface ModerationRepository {
  flagged(): Promise<Fact[]>;
  hiddenFacts(): Promise<Fact[]>;
  hide(id: string): Promise<void>;
  restore(id: string): Promise<void>;
}

export interface Repository {
  facts: FactsRepository;
  routing: RoutingRepository;
  geocoding: GeocodingRepository;
  accounts: AccountRepository;
  moderation: ModerationRepository;
}

export const PSEUDONYM_MIN: number = 3;
export const PSEUDONYM_MAX: number = 30;
export const PASSWORD_MIN: number = 5;

/** Nickname as in the mockup: 3 to 30 characters, letters, digits, underscore and hyphen. */
export function pseudonymValid(p: string): boolean {
  return p.length >= PSEUDONYM_MIN && p.length <= PSEUDONYM_MAX && /^[A-Za-z0-9_ąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+$/.test(p);
}

export function passwordValid(p: string): boolean {
  return p.length >= PASSWORD_MIN;
}
