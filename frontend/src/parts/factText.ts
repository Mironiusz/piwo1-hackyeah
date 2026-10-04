import type { TFunction } from "i18next";

import { isBarrierType, type Fact, type FactType } from "../api/types.ts";
import type { Language } from "../i18n/index.ts";

export type FactKind = "barrier" | "amenity" | "area";

/**
 * Returns the kind of a fact: an area for a fact that covers a circle, and else a barrier or an amenity by its type.
 */
export function findFactKind(fact: Pick<Fact, "type" | "geozone_radius_m">): FactKind {
  if (fact.geozone_radius_m !== null) {
    return "area";
  }
  return isBarrierType(fact.type) ? "barrier" : "amenity";
}

/**
 * Returns the name of a fact type with a small first letter, for the middle of a sentence.
 */
export function nameTypeInSentence(type: FactType, t: TFunction, language: Language): string {
  const name = t(`type.${type}`);
  return name.charAt(0).toLocaleLowerCase(language) + name.slice(1);
}

/**
 * Returns the title of a fact as a row and a panel show it: the name of its type, for stairs with a known number
 * of steps also that number, and for an area its barrier type and its radius.
 */
export function nameFact(fact: Pick<Fact, "type" | "geozone_radius_m" | "step_count">, t: TFunction, language: Language): string {
  if (fact.geozone_radius_m !== null) {
    return t("fact.area_row", { type: nameTypeInSentence(fact.type, t, language), radius: fact.geozone_radius_m });
  }
  if (fact.type === "stairs" && fact.step_count !== null) {
    return t("fact.stairs_with_steps", { steps: t("count.steps", { count: fact.step_count }) });
  }
  return t(`type.${fact.type}`);
}

/**
 * Returns the day a fact shows next to its source: the last edit of the map data for a fact from the map data,
 * and the last confirmation for a report. Null when the service gave none.
 */
export function findFactDay(fact: Pick<Fact, "source" | "osm_edited_on" | "last_confirmed_on">): string | null {
  return fact.source === "openstreetmap" ? fact.osm_edited_on : fact.last_confirmed_on;
}
