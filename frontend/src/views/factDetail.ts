import type { TFunction } from "i18next";

import type { Fact, RouteFact } from "../api/types.ts";
import type { Language } from "../i18n/index.ts";
import type { MapMarker, MapZone } from "../map/mapScene.ts";
import { findFactKind, nameFact } from "../parts/factText.ts";
import { findFactIcon } from "../parts/iconPaths.ts";

/**
 * What a map view hands to the detail of a fact that opens over it: the address the detail closes to,
 * the facts of the shown route with their distance from the start, and what to do when the fact was loaded or changed.
 */
export interface FactDetailContext {
  closePath: string;
  routeFacts: readonly RouteFact[];
  onLoad: (fact: Fact) => void;
  onChange: (fact: Fact) => void;
}

/**
 * Returns the address of the detail of a fact under a map view.
 */
export function buildFactPath(basePath: string, factId: number): string {
  return `${basePath === "/" ? "" : basePath}/fact/${factId}`;
}

/**
 * Returns the identifier of the marker of a fact.
 */
export function buildFactMarkerId(factId: number): string {
  return `fact-${factId}`;
}

/**
 * Returns the identifier of the fact a marker stands for, or null for a marker that is no fact.
 */
export function readFactMarkerId(markerId: string): number | null {
  const match = /^fact-(\d+)$/.exec(markerId);
  return match === null ? null : Number(match[1]);
}

/**
 * Builds the marker of a fact: its look by what it is, and a text name with its status and the sample data mark,
 * which is what a screen reader says for the marker.
 */
export function buildFactMarker(fact: Fact, isSelected: boolean, isOverruled: boolean, t: TFunction, language: Language): MapMarker {
  const kind = findFactKind(fact);
  const look = fact.status === "outdated" ? "outdated" : isOverruled ? "overruled" : kind === "amenity" ? "amenity" : "barrier";
  const name = t("fact.marker", { name: nameFact(fact, t, language), status: t(`status.${fact.status}`) });
  return {
    id: buildFactMarkerId(fact.id),
    point: fact.point,
    look,
    icon: findFactIcon(fact.type, kind === "area"),
    text: null,
    label: fact.is_sample ? `${name}, ${t("sample.mark")}` : name,
    isSelected,
    isPressable: true,
  };
}

/**
 * Builds the circles of the facts that cover an area.
 */
export function buildFactZones(facts: readonly Fact[]): MapZone[] {
  const zones: MapZone[] = [];
  for (const fact of facts) {
    if (fact.geozone_radius_m !== null) {
      zones.push({ id: `zone-${fact.id}`, point: fact.point, radiusM: fact.geozone_radius_m, isMuted: fact.status === "outdated" });
    }
  }
  return zones;
}
