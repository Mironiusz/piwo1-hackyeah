import { describe, expect, it } from "vitest";

import type { AnsweredSegmentState, Route } from "../api/types.ts";
import { isRouteAssessed } from "./routeSummary.ts";

/**
 * Builds a route of segments in the given states, without a fact.
 */
function buildRoute(states: AnsweredSegmentState[]): Route {
  return {
    length_m: states.length * 20,
    segments: states.map((state) => ({ line: [], length_m: 20, state, missing_attributes: [], is_marked_wheelchair_no: false })),
    profile_barriers: [],
    additional_barriers: [],
    amenities: [],
  };
}

describe("isRouteAssessed", () => {
  it("tells that a route in the four states is assessed", () => {
    expect(isRouteAssessed(buildRoute(["no_barrier", "barrier", "partial_data", "no_data"]))).toBe(true);
  });

  it("tells that a route the service did not assess is not assessed", () => {
    expect(isRouteAssessed(buildRoute(["not_assessed", "not_assessed"]))).toBe(false);
  });
});
