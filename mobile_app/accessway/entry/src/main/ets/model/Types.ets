export enum Roughness {
  SMOOTH = 0,
  MODERATE = 1,
  ROUGH = 2
}

export const NO_LIMIT: number = -1;

export interface Constraints {
  avoidSteps: boolean;
  maxKerbCm: number;
  maxInclinePct: number;
  maxRoughness: number;
  minWidthM: number;
}

export enum IssueKind {
  STEPS = 'steps',
  INCLINE = 'incline',
  INCLINE_UNKNOWN = 'incline_unknown',
  SURFACE = 'surface',
  SURFACE_UNKNOWN = 'surface_unknown',
  WIDTH = 'width',
  KERB = 'kerb',
  KERB_UNKNOWN = 'kerb_unknown',
  WIDTH_UNKNOWN = 'width_unknown',
  WHEELCHAIR_NO = 'wheelchair_no',
  BARRIER = 'barrier'
}

export enum IssueClass {
  NONE = 'none',
  BLOCKING = 'blocking',
  EXTRA = 'extra',
  INFO = 'info'
}

export enum TrustLevel {
  OFFICIAL = 'official',
  COMMUNITY = 'community',
  UNVERIFIED = 'unverified'
}

export enum EdgeState {
  BARRIER = 'barrier',
  CLEAR = 'clear',
  PARTIAL = 'partial',
  NO_DATA = 'no_data'
}

export interface EdgeIssue {
  kind: IssueKind;
  value: number;
  barrierId: string;
  barrierKind: string;
  source: string;
  observedAt: number;
  trust: TrustLevel;
  cls: IssueClass;
  unconfirmed: boolean;
  text: string;
}

export interface GraphNode {
  osmId: number;
  lat: number;
  lon: number;
  kerbCm: number;
  crossing: boolean;
}

export interface WalkEdge {
  index: number;
  a: number;
  b: number;
  lengthM: number;
  highway: string;
  name: string;
  isSteps: boolean;
  hasRamp: boolean;
  inclinePct: number;
  inclineUnknown: boolean;
  roughness: number;
  surfaceLabel: string;
  widthM: number;
  kerbCm: number;
  kerbUnknown: boolean;
  wheelchairNo: boolean;
  noSurfaceData: boolean;
  crossing: boolean;
}

export interface Place {
  id: string;
  name: string;
  category: string;
  lat: number;
  lon: number;
  street: string;
  tags: Record<string, string>;
  observedAt: number;
}

export interface PointFeature {
  kind: string;
  lat: number;
  lon: number;
  tags: Record<string, string>;
}

/**
 * Rodzaje faktów z makiet: pięć barier, których można unikać, i sześć udogodnień, których można potrzebować.
 * Obszar to zgłoszenie z promieniem, którego rodzaj jest jedną z barier.
 */
export enum FactKind {
  STEPS = 'steps',
  KERB = 'kerb',
  ROUGH_SURFACE = 'rough_surface',
  STEEP_SLOPE = 'steep_slope',
  NARROW_PASSAGE = 'narrow_passage',
  ELEVATOR = 'elevator',
  RAMP = 'ramp',
  LOWERED_KERB = 'lowered_kerb',
  ACCESSIBLE_TOILET = 'accessible_toilet',
  REST_SPOT = 'rest_spot',
  HANDRAIL = 'handrail'
}

export const BARRIER_KINDS: FactKind[] = [FactKind.STEPS, FactKind.KERB, FactKind.ROUGH_SURFACE, FactKind.STEEP_SLOPE,
  FactKind.NARROW_PASSAGE];

export const AMENITY_KINDS: FactKind[] = [FactKind.ELEVATOR, FactKind.RAMP, FactKind.LOWERED_KERB,
  FactKind.ACCESSIBLE_TOILET, FactKind.REST_SPOT, FactKind.HANDRAIL];

export enum FactCategory {
  BARRIER = 'barrier',
  AMENITY = 'amenity',
  AREA = 'area'
}

/** Statusy z makiety "O danych"; fakt nieaktualny nie jest nigdzie pokazywany. */
export enum FactStatus {
  CONFIRMED = 'confirmed',
  UNVERIFIED = 'unverified',
  DISPUTED = 'disputed',
  OUTDATED = 'outdated'
}

export enum FactSource {
  REPORT = 'report',
  OSM = 'osm'
}

export interface Vote {
  voterId: string;
  value: number;
  weight: number;
  at: number;
}

/** Zgłoszenie użytkownika. Po zapisaniu nikt go nie zmienia; autor nie jest przechowywany w treści. */
export interface Barrier {
  id: string;
  kind: FactKind;
  lat: number;
  lon: number;
  radiusM: number;
  isArea: boolean;
  stepCount: number;
  description: string;
  street: string;
  createdAt: number;
  isSample: boolean;
  votes: Vote[];
  hidden: boolean;
  flagged: boolean;
}

/** Fakt pokazywany w aplikacji: zgłoszenie albo element OpenStreetMap, z jednym statusem. */
export interface Fact {
  id: string;
  kind: FactKind;
  category: FactCategory;
  source: FactSource;
  lat: number;
  lon: number;
  radiusM: number;
  stepCount: number;
  street: string;
  description: string;
  date: number;
  lastConfirmed: number;
  status: FactStatus;
  isSample: boolean;
  conflictKind: string;
  conflictDate: number;
  hidden: boolean;
  flagged: boolean;
}

export interface LatLon {
  lat: number;
  lon: number;
}

export const DAY_MS: number = 24 * 60 * 60 * 1000;
