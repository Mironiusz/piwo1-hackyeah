import { isAmenity } from '../model/Labels';
import { Barrier, Fact, FactCategory, FactKind, FactSource, FactStatus, Vote } from '../model/Types';
import { distanceM } from './Geo';
import { Dataset, OsmFact } from './OsmMapping';
import { factStatus, lastConfirmation } from './Trust';

export const DUPLICATE_REACH_M: number = 15;
export const CONFLICT_REACH_M: number = 15;

const NO_VOTES: Vote[] = [];

export function categoryOf(kind: FactKind, isArea: boolean): FactCategory {
  if (isArea) {
    return FactCategory.AREA;
  }
  return isAmenity(kind) ? FactCategory.AMENITY : FactCategory.BARRIER;
}

export function reportFact(b: Barrier): Fact {
  return {
    id: b.id,
    kind: b.kind,
    category: categoryOf(b.kind, b.isArea),
    source: FactSource.REPORT,
    lat: b.lat,
    lon: b.lon,
    radiusM: b.isArea ? b.radiusM : 0,
    stepCount: b.stepCount,
    street: b.street,
    description: b.description,
    date: b.createdAt,
    lastConfirmed: lastConfirmation(b.createdAt, b.votes),
    status: factStatus(b.votes),
    isSample: b.isSample,
    conflictKind: '',
    conflictDate: 0,
    hidden: b.hidden,
    flagged: b.flagged
  };
}

export function osmFactView(o: OsmFact, votes: Vote[], isSample: boolean): Fact {
  return {
    id: o.id,
    kind: o.kind,
    category: categoryOf(o.kind, false),
    source: FactSource.OSM,
    lat: o.lat,
    lon: o.lon,
    radiusM: 0,
    stepCount: o.stepCount,
    street: o.street,
    description: '',
    date: o.date,
    lastConfirmed: lastConfirmation(0, votes),
    status: factStatus(votes),
    isSample: isSample,
    conflictKind: '',
    conflictDate: 0,
    hidden: false,
    flagged: false
  };
}

/** Rodzaj, który zaprzecza danemu, jeśli leży w tym samym miejscu: wysoki krawężnik i obniżony, schody i rampa. */
export function opposite(k: FactKind): string {
  if (k === FactKind.KERB) {
    return FactKind.LOWERED_KERB;
  }
  if (k === FactKind.LOWERED_KERB) {
    return FactKind.KERB;
  }
  return '';
}

/**
 * Wszystkie fakty do pokazania: zgłoszenia i elementy OpenStreetMap. Pomija fakty nieaktualne i ukryte przez
 * moderację. Zgłoszenie sprzeczne z OpenStreetMap w promieniu 15 m dostaje rodzaj i datę faktu z OSM.
 */
export function buildFacts(ds: Dataset, reports: Barrier[], osmVotes: Map<string, Vote[]>): Fact[] {
  const out: Fact[] = [];
  const osm: Fact[] = [];
  for (const o of ds.osmFacts) {
    const f = osmFactView(o, osmVotes.get(o.id) ?? NO_VOTES, ds.isSample);
    if (f.status !== FactStatus.OUTDATED) {
      osm.push(f);
    }
  }
  for (const b of reports) {
    const f = reportFact(b);
    if (f.status === FactStatus.OUTDATED || f.hidden) {
      continue;
    }
    const opp = opposite(f.kind);
    if (opp.length > 0 && f.category !== FactCategory.AREA) {
      for (const o of osm) {
        if (o.kind === opp && distanceM(o.lat, o.lon, f.lat, f.lon) <= CONFLICT_REACH_M) {
          f.conflictKind = o.kind;
          f.conflictDate = o.date;
        }
      }
    }
    out.push(f);
  }
  return out.concat(osm);
}

export interface NearbyFact {
  fact: Fact;
  distanceM: number;
}

/** Fakty tego samego rodzaju w promieniu 15 m od wskazanego punktu, najbliższe pierwsze. */
export function sameKindNearby(facts: Fact[], kind: FactKind, isArea: boolean, lat: number, lon: number): NearbyFact[] {
  const out: NearbyFact[] = [];
  for (const f of facts) {
    if (f.kind !== kind || (f.category === FactCategory.AREA) !== isArea) {
      continue;
    }
    const d = distanceM(lat, lon, f.lat, f.lon);
    if (d <= DUPLICATE_REACH_M + f.radiusM) {
      out.push({ fact: f, distanceM: d });
    }
  }
  out.sort((a: NearbyFact, b: NearbyFact) => a.distanceM - b.distanceM);
  return out;
}

/** Fakty w prostokącie widocznej mapy, posortowane od najbliższego środka. */
export function factsInView(facts: Fact[], lat: number, lon: number, halfLat: number, halfLon: number): Fact[] {
  const out: NearbyFact[] = [];
  for (const f of facts) {
    if (Math.abs(f.lat - lat) <= halfLat && Math.abs(f.lon - lon) <= halfLon) {
      out.push({ fact: f, distanceM: distanceM(lat, lon, f.lat, f.lon) });
    }
  }
  out.sort((a: NearbyFact, b: NearbyFact) => a.distanceM - b.distanceM);
  const list: Fact[] = [];
  for (const n of out) {
    list.push(n.fact);
  }
  return list;
}
