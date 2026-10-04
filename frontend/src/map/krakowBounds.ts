import type { Point } from "../api/types.ts";

/**
 * The bounds of the tile archive of Kraków, in degrees of WGS 84. A route works only inside them.
 */
export const KRAKOW_BOUNDS = {
  southWest: { lat: 49.9676668, lon: 19.7922355 },
  northEast: { lat: 50.1261338, lon: 20.2173455 },
} as const;

/**
 * The view the map opens on: the surroundings of Tauron Arena, where the sample data of the demo lies.
 */
export const INITIAL_MAP_VIEW = { center: { lat: 50.0678, lon: 19.9914 }, zoom: 15 } as const;

/**
 * The lowest zoom at which the map of facts asks for facts: a phone screen then shows about a part of a district.
 */
export const FACTS_MIN_ZOOM = 14;

/**
 * Tells whether a point lies inside the bounds of Kraków, the borders included.
 */
export function isInsideKrakow(point: Point): boolean {
  return point.lat >= KRAKOW_BOUNDS.southWest.lat && point.lat <= KRAKOW_BOUNDS.northEast.lat && point.lon >= KRAKOW_BOUNDS.southWest.lon && point.lon <= KRAKOW_BOUNDS.northEast.lon;
}
