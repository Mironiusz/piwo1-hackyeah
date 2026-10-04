import type { GeoJSONSourceSpecification, LineLayerSpecification } from "maplibre-gl";

import type { Route, SegmentState } from "../api/types.ts";

export const ROUTE_SOURCE_ID = "route";

/**
 * The state a stretch of the route is drawn in: one of the four states of the service, or neutral for a route
 * whose stretches are not assessed.
 */
export type DrawnState = SegmentState | "neutral";

/**
 * The colors of the route on the map, the same values as the theme of the interface.
 */
export const ROUTE_COLORS = {
  casing: "#ffffff",
  no_barrier: "#1e7a46",
  barrier: "#c8321e",
  partial_data: "#e0a100",
  no_data: "#6f7480",
  neutral: "#12306b",
  ink: "#111418",
} as const;

export interface RouteLayers {
  source: GeoJSONSourceSpecification;
  layers: LineLayerSpecification[];
}

interface Stretch {
  state: DrawnState;
  line: [number, number][];
}

/**
 * Joins the segments that follow each other in the same state into one stretch, so a line pattern runs through them unbroken.
 */
function joinStretches(route: Route, isAssessed: boolean): Stretch[] {
  const stretches: Stretch[] = [];
  for (const segment of route.segments) {
    const state: DrawnState = isAssessed ? segment.state : "neutral";
    const last = stretches[stretches.length - 1];
    const lastPoint = last?.line[last.line.length - 1];
    const firstPoint = segment.line[0];
    const continues = last !== undefined && last.state === state && lastPoint !== undefined && firstPoint !== undefined && lastPoint[0] === firstPoint[0] && lastPoint[1] === firstPoint[1];
    if (continues) {
      last.line.push(...segment.line.slice(1));
    } else {
      stretches.push({ state, line: [...segment.line] });
    }
  }
  return stretches;
}

/**
 * Builds one line layer of the route for the stretches in one state.
 */
function buildLayer(id: string, state: DrawnState | null, paint: LineLayerSpecification["paint"], cap: "butt" | "round"): LineLayerSpecification {
  const layer: LineLayerSpecification = {
    id,
    type: "line",
    source: ROUTE_SOURCE_ID,
    layout: { "line-cap": cap, "line-join": "round" },
    paint,
  };
  if (state !== null) {
    layer.filter = ["==", ["get", "state"], state];
  }
  return layer;
}

/**
 * Builds the source and the layers that draw a route on the map.
 * An assessed route gets one layer for each of the four segment states, each with its own color and its own line pattern,
 * so the states can be told apart without color. A route that is not assessed gets one neutral layer, which is none of the four.
 * A dash pattern of the map library is counted in widths of the line.
 */
export function buildRouteLayers(route: Route, isAssessed: boolean): RouteLayers {
  const source: GeoJSONSourceSpecification = {
    type: "geojson",
    data: {
      type: "FeatureCollection",
      features: joinStretches(route, isAssessed).map((stretch) => ({
        type: "Feature",
        properties: { state: stretch.state },
        geometry: { type: "LineString", coordinates: stretch.line },
      })),
    },
  };

  const casing = buildLayer("route-casing", null, { "line-color": ROUTE_COLORS.casing, "line-width": 12 }, "round");

  if (!isAssessed) {
    return {
      source,
      layers: [
        casing,
        buildLayer("route-neutral", "neutral", { "line-color": ROUTE_COLORS.neutral, "line-width": 8 }, "round"),
        buildLayer("route-neutral-inside", "neutral", { "line-color": ROUTE_COLORS.casing, "line-width": 4 }, "round"),
      ],
    };
  }

  return {
    source,
    layers: [
      casing,
      buildLayer("route-no_barrier", "no_barrier", { "line-color": ROUTE_COLORS.no_barrier, "line-width": 7 }, "butt"),
      buildLayer("route-partial_data", "partial_data", { "line-color": ROUTE_COLORS.partial_data, "line-width": 7 }, "butt"),
      buildLayer("route-partial_data-pattern", "partial_data", { "line-color": ROUTE_COLORS.ink, "line-width": 2.5, "line-dasharray": [2.8, 2.8] }, "butt"),
      buildLayer("route-no_data", "no_data", { "line-color": ROUTE_COLORS.no_data, "line-width": 4, "line-dasharray": [0.5, 2] }, "round"),
      buildLayer("route-barrier", "barrier", { "line-color": ROUTE_COLORS.barrier, "line-width": 7 }, "butt"),
      buildLayer("route-barrier-pattern", "barrier", { "line-color": ROUTE_COLORS.casing, "line-width": 7, "line-dasharray": [0.36, 0.71] }, "butt"),
    ],
  };
}

/**
 * Returns the corners of the rectangle that holds every point of a route, or null for a route without a point.
 */
export function findRouteBounds(route: Route): { southWest: { lat: number; lon: number }; northEast: { lat: number; lon: number } } | null {
  let south = Infinity;
  let west = Infinity;
  let north = -Infinity;
  let east = -Infinity;
  for (const segment of route.segments) {
    for (const [lon, lat] of segment.line) {
      south = Math.min(south, lat);
      north = Math.max(north, lat);
      west = Math.min(west, lon);
      east = Math.max(east, lon);
    }
  }
  if (!Number.isFinite(south)) {
    return null;
  }
  return { southWest: { lat: south, lon: west }, northEast: { lat: north, lon: east } };
}
