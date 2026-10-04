import type { Route, RouteFact, SegmentState } from "../api/types.ts";

/**
 * A stretch of the summary line: the segments that follow each other in one state, with their joint length.
 */
export interface SummaryStretch {
  state: SegmentState;
  lengthM: number;
}

/**
 * A stop of the summary line: a barrier of the needs at its share of the way, with the label that fits next to it or none.
 */
export interface SummaryStop {
  factId: number;
  share: number;
  label: string | null;
  align: "left" | "center" | "right";
}

const LINE_WIDTH_PX = 290;
const LETTER_WIDTH_PX = 6.4;
const LABEL_GAP_PX = 8;
const EDGE_SHARE = 0.14;

/**
 * Joins the segments of a route that follow each other in the same state into stretches, in the order of the route.
 */
export function joinSummaryStretches(route: Route): SummaryStretch[] {
  const stretches: SummaryStretch[] = [];
  for (const segment of route.segments) {
    const last = stretches[stretches.length - 1];
    if (last !== undefined && last.state === segment.state) {
      last.lengthM += segment.length_m;
    } else {
      stretches.push({ state: segment.state, lengthM: segment.length_m });
    }
  }
  return stretches;
}

/**
 * Returns the length in metres of the segments of a route that are in the state no data.
 */
export function measureNoData(route: Route): number {
  return route.segments.reduce((sum, segment) => (segment.state === "no_data" ? sum + segment.length_m : sum), 0);
}

/**
 * Tells whether a route has a segment with partial data or no data, which is when the one note about missing data is shown.
 */
export function hasMissingData(route: Route): boolean {
  return route.segments.some((segment) => segment.state === "no_data" || segment.state === "partial_data");
}

/**
 * Places the barriers of the needs as stops of the summary line.
 * A stop always stands at its share of the way. Its label is drawn only where it does not run into the label before it:
 * the width of a label is estimated from its letters, and a label that would overlap is left out,
 * because the text description of the line and the list under the map name every barrier anyway.
 */
export function placeSummaryStops(barriers: readonly RouteFact[], lengthM: number, nameOf: (fact: RouteFact) => string): SummaryStop[] {
  const stops: SummaryStop[] = [];
  let takenUntilPx = -Infinity;
  for (const fact of barriers) {
    const share = lengthM > 0 ? Math.min(1, Math.max(0, fact.distance_from_start_m / lengthM)) : 0;
    const name = nameOf(fact);
    const width = name.length * LETTER_WIDTH_PX;
    const align = share < EDGE_SHARE ? "left" : share > 1 - EDGE_SHARE ? "right" : "center";
    const at = share * LINE_WIDTH_PX;
    const from = align === "left" ? at - 8 : align === "right" ? at + 8 - width : at - width / 2;
    const fits = from >= takenUntilPx + LABEL_GAP_PX;
    if (fits) {
      takenUntilPx = from + width;
    }
    stops.push({ factId: fact.id, share, label: fits ? name : null, align });
  }
  return stops;
}
