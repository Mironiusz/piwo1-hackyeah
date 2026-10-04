import { describe, expect, it } from "vitest";

import type { Fact, FlaggedFact } from "../api/types.ts";
import { findNeighbour, isModeratorRefusal, keepChangedFact, splitFlaggedFacts } from "./moderationLists.ts";

/**
 * Builds a flagged fact of the moderation list with the given identifier, hidden or not.
 */
function buildFlagged(id: number, isHidden: boolean): FlaggedFact {
  const fact: Fact = {
    id,
    type: "high_kerb",
    point: { lat: 50.0678, lon: 19.9914 },
    geozone_radius_m: null,
    description: null,
    step_count: null,
    source: "user_report",
    status: "unverified",
    is_removed_from_osm: false,
    osm_edited_on: null,
    last_confirmed_on: "2026-10-03",
    is_sample: true,
    can_be_flagged: true,
  };
  return { fact, flagged_on: "2026-10-03", is_hidden: isHidden };
}

/**
 * Lists the identifiers of the facts of a list, in its order.
 */
function listIds(list: readonly FlaggedFact[]): number[] {
  return list.map((item) => item.fact.id);
}

describe("splitFlaggedFacts", () => {
  it("puts the hidden facts into one list and the others into the other, in the order of the service", () => {
    const lists = splitFlaggedFacts([buildFlagged(3, false), buildFlagged(2, true), buildFlagged(1, false)], []);

    expect(listIds(lists.flagged)).toEqual([3, 1]);
    expect(listIds(lists.hidden)).toEqual([2]);
  });

  it("returns two empty lists when nothing is flagged", () => {
    expect(splitFlaggedFacts([], [])).toEqual({ flagged: [], hidden: [] });
  });

  it("moves a fact to the hidden list when the service answered it as hidden", () => {
    const answered = buildFlagged(3, true);
    const lists = splitFlaggedFacts([buildFlagged(3, false), buildFlagged(2, true), buildFlagged(1, false)], [answered]);

    expect(listIds(lists.flagged)).toEqual([1]);
    expect(listIds(lists.hidden)).toEqual([3, 2]);
    expect(lists.hidden[0]).toBe(answered);
  });

  it("moves a fact back when the service answered it as restored", () => {
    const lists = splitFlaggedFacts([buildFlagged(3, false), buildFlagged(2, true)], [buildFlagged(2, false)]);

    expect(listIds(lists.flagged)).toEqual([3, 2]);
    expect(listIds(lists.hidden)).toEqual([]);
  });

  it("adds no fact that the service did not list", () => {
    const lists = splitFlaggedFacts([buildFlagged(3, false)], [buildFlagged(9, true)]);

    expect(listIds(lists.flagged)).toEqual([3]);
    expect(listIds(lists.hidden)).toEqual([]);
  });
});

describe("keepChangedFact", () => {
  it("adds the first answer for a fact", () => {
    expect(listIds(keepChangedFact([buildFlagged(1, true)], buildFlagged(2, true)))).toEqual([1, 2]);
  });

  it("replaces an earlier answer for the same fact", () => {
    const restored = buildFlagged(1, false);
    const changed = keepChangedFact([buildFlagged(1, true), buildFlagged(2, true)], restored);

    expect(listIds(changed)).toEqual([2, 1]);
    expect(changed[1]).toBe(restored);
  });

  it("leaves the list it was given unchanged", () => {
    const before = [buildFlagged(1, true)];

    keepChangedFact(before, buildFlagged(1, false));

    expect(before[0]?.is_hidden).toBe(true);
  });
});

describe("findNeighbour", () => {
  const list = [buildFlagged(3, false), buildFlagged(2, false), buildFlagged(1, false)];

  it("returns the item after the one that leaves", () => {
    expect(findNeighbour(list, 3)?.fact.id).toBe(2);
    expect(findNeighbour(list, 2)?.fact.id).toBe(1);
  });

  it("returns the item before the last one when the last one leaves", () => {
    expect(findNeighbour(list, 1)?.fact.id).toBe(2);
  });

  it("returns null when the only item leaves", () => {
    expect(findNeighbour([buildFlagged(3, false)], 3)).toBeNull();
  });

  it("returns null for a fact the list does not hold", () => {
    expect(findNeighbour(list, 9)).toBeNull();
  });
});

describe("isModeratorRefusal", () => {
  it.each(["moderator_role_required", "authentication_required"] as const)("is true for the code %s", (code) => {
    expect(isModeratorRefusal(code)).toBe(true);
  });

  it.each(["session_expired", "fact_not_flagged", "network_error", "internal_error"] as const)("is false for the code %s", (code) => {
    expect(isModeratorRefusal(code)).toBe(false);
  });
});
