import type { TFunction } from "i18next";

import type { Point } from "../api/types.ts";
import type { MapCamera, MapMarker } from "../map/mapScene.ts";
import type { RouteEnd, RouteEndName } from "../state/plannedRoute.tsx";

/**
 * Splits the label of an address match into its name, the part before the first comma, and the rest.
 */
export function splitLabel(label: string): { name: string; rest: string } {
  const comma = label.indexOf(",");
  if (comma === -1) {
    return { name: label, rest: "" };
  }
  return { name: label.slice(0, comma).trim(), rest: label.slice(comma + 1).trim() };
}

/**
 * Returns the first two parts of the label of an address match, which is enough to tell a place in a short line.
 */
export function shortenLabel(label: string): string {
  return label
    .split(",")
    .slice(0, 2)
    .map((part) => part.trim())
    .join(", ");
}

/**
 * Returns the text that names an end of a route: the short label of its address, or the way the person gave it.
 */
export function nameRouteEnd(end: RouteEnd, t: TFunction): string {
  if (end.kind === "address" && end.label !== null) {
    return shortenLabel(end.label);
  }
  return t(end.kind === "location" ? "plan.my_location" : "plan.map_point");
}

/**
 * Returns the shortest text that names an end of a route, for the ends of the summary line: the name of its address
 * without the street, or the way the person gave it.
 */
export function nameRouteEndShortly(end: RouteEnd, t: TFunction): string {
  if (end.kind === "address" && end.label !== null) {
    return splitLabel(end.label).name;
  }
  return nameRouteEnd(end, t);
}

/**
 * Tells whether a text of the address is one of the two names of an end of a route.
 */
export function isRouteEndName(value: string | undefined): value is RouteEndName {
  return value === "start" || value === "destination";
}

/**
 * Builds the markers of the ends of a route that are set: A for the start and B for the destination, each with a text name.
 */
export function buildEndMarkers(start: RouteEnd | null, destination: RouteEnd | null, t: TFunction): MapMarker[] {
  const markers: MapMarker[] = [];
  if (start !== null) {
    markers.push({ id: "end-start", point: start.point, look: "end", icon: null, text: "A", label: t("route.end.start"), isSelected: false, isPressable: false });
  }
  if (destination !== null) {
    markers.push({ id: "end-destination", point: destination.point, look: "end", icon: null, text: "B", label: t("route.end.destination"), isSelected: false, isPressable: false });
  }
  return markers;
}

/**
 * Builds the request that moves the map to the ends of a route that are set: to both, to the one, or nowhere.
 */
export function buildEndsCamera(start: Point | null, destination: Point | null): MapCamera | null {
  if (start !== null && destination !== null) {
    return {
      key: `ends-${start.lat},${start.lon}-${destination.lat},${destination.lon}`,
      target: {
        kind: "bounds",
        southWest: { lat: Math.min(start.lat, destination.lat), lon: Math.min(start.lon, destination.lon) },
        northEast: { lat: Math.max(start.lat, destination.lat), lon: Math.max(start.lon, destination.lon) },
      },
    };
  }
  const only = start ?? destination;
  return only === null ? null : { key: `end-${only.lat},${only.lon}`, target: { kind: "point", point: only, zoom: null } };
}
