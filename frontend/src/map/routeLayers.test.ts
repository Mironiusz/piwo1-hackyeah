import type { LineLayerSpecification } from "maplibre-gl";
import { describe, expect, it } from "vitest";

import type { AnsweredSegmentState, Route, Segment, SegmentState } from "../api/types.ts";
import { buildRouteLayers, findRouteBounds, ROUTE_COLORS, ROUTE_SOURCE_ID, type DrawnState, type RouteLayers } from "./routeLayers.ts";

type Position = [number, number];

const SEGMENT_STATES: SegmentState[] = ["barrier", "no_barrier", "partial_data", "no_data"];

const A: Position = [19.98, 50.06];
const B: Position = [19.981, 50.061];
const C: Position = [19.982, 50.062];
const D: Position = [19.983, 50.063];
const E: Position = [19.984, 50.064];
const F: Position = [19.985, 50.065];
const G: Position = [19.986, 50.066];

/**
 * Builds a segment of a route in one state along the given line.
 */
function buildSegment(state: AnsweredSegmentState, line: Position[]): Segment {
  return { line, length_m: 14, state, missing_attributes: [], is_marked_wheelchair_no: false };
}

/**
 * Builds a route of the given segments, without a fact.
 */
function buildRoute(segments: Segment[]): Route {
  return { length_m: segments.length * 14, segments, profile_barriers: [], additional_barriers: [], amenities: [] };
}

/**
 * Builds a route that holds every state: two segments without a barrier that follow each other,
 * one segment in each of the three other states, and a last segment without a barrier again.
 */
function buildMixedRoute(): Route {
  return buildRoute([
    buildSegment("no_barrier", [A, B]),
    buildSegment("no_barrier", [B, C]),
    buildSegment("partial_data", [C, D]),
    buildSegment("no_data", [D, E]),
    buildSegment("barrier", [E, F]),
    buildSegment("no_barrier", [F, G]),
  ]);
}

/**
 * Builds the source a route is expected to give: one line feature for each stretch, with the state it is drawn in.
 */
function buildExpectedSource(stretches: { state: DrawnState; line: Position[] }[]): RouteLayers["source"] {
  return {
    type: "geojson",
    data: {
      type: "FeatureCollection",
      features: stretches.map((stretch) => ({
        type: "Feature",
        properties: { state: stretch.state },
        geometry: { type: "LineString", coordinates: stretch.line },
      })),
    },
  };
}

/**
 * Returns the layers that draw only the stretches in the given state.
 */
function findLayersOfState(layers: LineLayerSpecification[], state: string): LineLayerSpecification[] {
  const filter = JSON.stringify(["==", ["get", "state"], state]);
  return layers.filter((layer) => JSON.stringify(layer.filter) === filter);
}

/**
 * Returns the colors the layers of one state draw with, the lowest layer first.
 */
function findColorsOfState(layers: LineLayerSpecification[], state: string): unknown[] {
  return findLayersOfState(layers, state).map((layer) => layer.paint?.["line-color"]);
}

/**
 * Returns the line patterns of one state as texts, one for each of its layers that has a pattern.
 */
function findDashesOfState(layers: LineLayerSpecification[], state: string): string[] {
  return findLayersOfState(layers, state)
    .map((layer) => layer.paint?.["line-dasharray"])
    .filter((dash) => dash !== undefined)
    .map((dash) => JSON.stringify(dash));
}

describe("buildRouteLayers for an assessed route", () => {
  it("draws the stretches of each of the four states with layers of that state alone", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), true);

    for (const state of SEGMENT_STATES) {
      expect(findLayersOfState(layers, state).length).toBeGreaterThanOrEqual(1);
    }
  });

  it("gives each state its own color", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), true);
    const colors = SEGMENT_STATES.map((state) => findColorsOfState(layers, state)[0]);

    expect(colors).toEqual(SEGMENT_STATES.map((state) => ROUTE_COLORS[state]));
    expect(new Set(colors).size).toBe(SEGMENT_STATES.length);
  });

  it("draws a stretch without a barrier as a plain line and each other state with a line pattern", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), true);

    expect(findDashesOfState(layers, "no_barrier")).toEqual([]);
    expect(findDashesOfState(layers, "partial_data")).toHaveLength(1);
    expect(findDashesOfState(layers, "no_data")).toHaveLength(1);
    expect(findDashesOfState(layers, "barrier")).toHaveLength(1);
  });

  it("gives each state with a line pattern its own dash, so the states are told apart without color", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), true);
    const dashes = ["partial_data", "no_data", "barrier"].flatMap((state) => findDashesOfState(layers, state));

    expect(new Set(dashes).size).toBe(3);
  });

  it("draws the casing first, under every stretch", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), true);

    expect(layers[0]?.filter).toBeUndefined();
    expect(layers[0]?.paint?.["line-color"]).toBe(ROUTE_COLORS.casing);
  });

  it("builds only line layers of the route source, each with its own identifier", () => {
    const { layers, source } = buildRouteLayers(buildMixedRoute(), true);
    const identifiers = layers.map((layer) => layer.id);

    expect(source.type).toBe("geojson");
    expect(new Set(identifiers).size).toBe(identifiers.length);
    for (const layer of layers) {
      expect(layer.type).toBe("line");
      expect(layer.source).toBe(ROUTE_SOURCE_ID);
    }
  });

  it("has no layer that draws anything but the casing and the four states", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), true);
    const layersOfStates = SEGMENT_STATES.flatMap((state) => findLayersOfState(layers, state));

    expect(layersOfStates).toHaveLength(layers.length - 1);
    expect(findLayersOfState(layers, "neutral")).toEqual([]);
  });

  it("joins the segments that follow each other in one state into one stretch", () => {
    const { source } = buildRouteLayers(buildMixedRoute(), true);

    expect(source).toEqual(
      buildExpectedSource([
        { state: "no_barrier", line: [A, B, C] },
        { state: "partial_data", line: [C, D] },
        { state: "no_data", line: [D, E] },
        { state: "barrier", line: [E, F] },
        { state: "no_barrier", line: [F, G] },
      ]),
    );
  });

  it("joins three and more segments of one state and keeps the points inside each of them", () => {
    const route = buildRoute([buildSegment("no_data", [A, B, C]), buildSegment("no_data", [C, D]), buildSegment("no_data", [D, E, F])]);

    expect(buildRouteLayers(route, true).source).toEqual(buildExpectedSource([{ state: "no_data", line: [A, B, C, D, E, F] }]));
  });

  it("starts a new stretch when a segment in the same state does not start where the last one ended", () => {
    const route = buildRoute([buildSegment("barrier", [A, B]), buildSegment("barrier", [C, D])]);

    expect(buildRouteLayers(route, true).source).toEqual(
      buildExpectedSource([
        { state: "barrier", line: [A, B] },
        { state: "barrier", line: [C, D] },
      ]),
    );
  });

  it("leaves the lines of the given route as they were", () => {
    const route = buildMixedRoute();

    buildRouteLayers(route, true);

    expect(route).toEqual(buildMixedRoute());
  });

  it("builds the same layers for a route without a segment, over a source without a stretch", () => {
    const empty = buildRouteLayers(buildRoute([]), true);

    expect(empty.source).toEqual(buildExpectedSource([]));
    expect(empty.layers).toEqual(buildRouteLayers(buildMixedRoute(), true).layers);
  });
});

describe("buildRouteLayers for a route that is not assessed", () => {
  it("draws the neutral layers only", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), false);

    expect(findLayersOfState(layers, "neutral")).toHaveLength(layers.length - 1);
    expect(layers[0]?.filter).toBeUndefined();
    for (const state of SEGMENT_STATES) {
      expect(findLayersOfState(layers, state)).toEqual([]);
    }
  });

  it("draws with none of the colors of the four states", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), false);
    const stateColors: unknown[] = SEGMENT_STATES.map((state) => ROUTE_COLORS[state]);

    expect(findColorsOfState(layers, "neutral")[0]).toBe(ROUTE_COLORS.neutral);
    for (const layer of layers) {
      expect(stateColors).not.toContain(layer.paint?.["line-color"]);
    }
  });

  it("marks every stretch as neutral, whatever state its segments carry", () => {
    const { source } = buildRouteLayers(buildMixedRoute(), false);

    expect(source).toEqual(buildExpectedSource([{ state: "neutral", line: [A, B, C, D, E, F, G] }]));
  });

  it("builds only line layers of the route source, each with its own identifier", () => {
    const { layers } = buildRouteLayers(buildMixedRoute(), false);
    const identifiers = layers.map((layer) => layer.id);

    expect(new Set(identifiers).size).toBe(identifiers.length);
    for (const layer of layers) {
      expect(layer.type).toBe("line");
      expect(layer.source).toBe(ROUTE_SOURCE_ID);
    }
  });
});

describe("findRouteBounds", () => {
  it("returns the corners of the rectangle that holds every point of the route", () => {
    const route = buildRoute([
      buildSegment("no_barrier", [
        [19.99, 50.07],
        [19.97, 50.08],
      ]),
      buildSegment("no_data", [
        [19.97, 50.08],
        [20.01, 50.05],
        [19.98, 50.06],
      ]),
    ]);

    expect(findRouteBounds(route)).toEqual({ southWest: { lat: 50.05, lon: 19.97 }, northEast: { lat: 50.08, lon: 20.01 } });
  });

  it("returns the same corner twice for a route of one point", () => {
    expect(findRouteBounds(buildRoute([buildSegment("no_data", [A])]))).toEqual({ southWest: { lat: 50.06, lon: 19.98 }, northEast: { lat: 50.06, lon: 19.98 } });
  });

  it("returns null for a route without a segment", () => {
    expect(findRouteBounds(buildRoute([]))).toBeNull();
  });

  it("returns null for a route whose segments have no point", () => {
    expect(findRouteBounds(buildRoute([buildSegment("no_data", []), buildSegment("barrier", [])]))).toBeNull();
  });
});
