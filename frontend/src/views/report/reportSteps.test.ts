import { afterEach, describe, expect, it, vi } from "vitest";

import type { Fact, NearbyFact } from "../../api/types.ts";
import { readOwnVote } from "../../state/ownVotes.ts";
import { EMPTY_REPORT_DRAFT, type ReportDraft } from "../../state/reportDraft.tsx";
import { createMemoryStorage } from "../../testing/memoryStorage.ts";
import { buildCreateFactRequest, countSteps, findOpenStep, findStepNumber, hasExistingStep, makeIdempotencyKey, readStepCount, rememberConfirmation, type ReportStep } from "./reportSteps.ts";

const POINT = { lat: 50.0661, lon: 19.9878 };
const KEY = "6f1c2a9e-0b8d-4c55-9a51-3e2f7d1b9c40";
const UUID_VERSION_4_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const EVERY_STEP: readonly ReportStep[] = ["kind", "place", "details", "existing", "summary", "saved"];

/**
 * Builds a fact the service could return, with the given identifier.
 */
function buildFact(id: number): Fact {
  return {
    id,
    type: "stairs",
    point: POINT,
    geozone_radius_m: null,
    description: null,
    step_count: null,
    source: "user_report",
    status: "unverified",
    is_removed_from_osm: false,
    osm_edited_on: null,
    last_confirmed_on: "2026-10-04",
    is_sample: false,
    can_be_flagged: true,
  };
}

/**
 * Builds the list of existing facts a check near a point found: one fact.
 */
function buildNearby(): NearbyFact[] {
  return [{ fact: buildFact(7), distance_m: 8 }];
}

/**
 * Builds the draft of a barrier at a point with its type, before the check for existing facts.
 */
function buildBarrierDraft(): ReportDraft {
  return { ...EMPTY_REPORT_DRAFT, kind: "barrier", point: POINT, type: "stairs" };
}

/**
 * Builds the draft of an area with its point, its radius and its barrier type.
 */
function buildAreaDraft(): ReportDraft {
  return { ...EMPTY_REPORT_DRAFT, kind: "area", point: POINT, type: "poor_surface", radiusM: 25 };
}

/**
 * Puts a crypto in place that has no randomUUID, as on a page served over plain HTTP,
 * and fills every array of random bytes with the next value of the given function.
 */
function stubPlainHttpCrypto(readNextByte: () => number): void {
  vi.stubGlobal("crypto", { getRandomValues: (bytes: Uint8Array) => bytes.fill(readNextByte()) });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("countSteps and findStepNumber", () => {
  it("counts five steps for a barrier and an amenity, and four for an area", () => {
    expect(countSteps("barrier")).toBe(5);
    expect(countSteps("amenity")).toBe(5);
    expect(countSteps("area")).toBe(4);
  });

  it("numbers the steps of a barrier from the kind to the summary", () => {
    expect((["kind", "place", "details", "existing", "summary"] as const).map((step) => findStepNumber(step, "barrier"))).toEqual([1, 2, 3, 4, 5]);
  });

  it("numbers the summary of an area as its fourth and last step", () => {
    expect((["kind", "place", "details", "summary"] as const).map((step) => findStepNumber(step, "area"))).toEqual([1, 2, 3, 4]);
  });
});

describe("readStepCount", () => {
  it("reads an empty field as no number", () => {
    expect(readStepCount("")).toBeNull();
    expect(readStepCount("   ")).toBeNull();
  });

  it("reads a whole number from 1 to 999", () => {
    expect(readStepCount("1")).toBe(1);
    expect(readStepCount("4")).toBe(4);
    expect(readStepCount(" 12 ")).toBe(12);
    expect(readStepCount("007")).toBe(7);
    expect(readStepCount("999")).toBe(999);
  });

  it.each(["0", "000", "1000", "-1", "4.5", "4,5", "1e2", "four", "4 5"])("refuses the text %s", (text) => {
    expect(readStepCount(text)).toBe("invalid");
  });
});

describe("hasExistingStep", () => {
  it("shows the step when the check found a fact near a barrier or an amenity", () => {
    expect(hasExistingStep({ ...buildBarrierDraft(), existingFacts: buildNearby() })).toBe(true);
    expect(hasExistingStep({ ...buildBarrierDraft(), kind: "amenity", type: "ramp", existingFacts: buildNearby() })).toBe(true);
  });

  it("skips the step when the check found nothing or did not run", () => {
    expect(hasExistingStep({ ...buildBarrierDraft(), existingFacts: [] })).toBe(false);
    expect(hasExistingStep(buildBarrierDraft())).toBe(false);
  });

  it("skips the step for an area", () => {
    expect(hasExistingStep({ ...buildAreaDraft(), existingFacts: buildNearby() })).toBe(false);
  });
});

describe("findOpenStep", () => {
  it("leads every step of an empty draft back to the first step", () => {
    expect(EVERY_STEP.map((step) => findOpenStep(EMPTY_REPORT_DRAFT, step))).toEqual(["kind", "kind", "kind", "kind", "kind", "kind"]);
  });

  it("opens the place once the kind is given, and nothing later", () => {
    const draft: ReportDraft = { ...EMPTY_REPORT_DRAFT, kind: "barrier" };

    expect(findOpenStep(draft, "place")).toBe("place");
    expect(findOpenStep(draft, "details")).toBe("kind");
    expect(findOpenStep(draft, "summary")).toBe("kind");
  });

  it("opens the details once the point is given, and nothing later without a type", () => {
    const draft: ReportDraft = { ...EMPTY_REPORT_DRAFT, kind: "barrier", point: POINT };

    expect(findOpenStep(draft, "details")).toBe("details");
    expect(findOpenStep(draft, "existing")).toBe("kind");
    expect(findOpenStep(draft, "summary")).toBe("kind");
  });

  it("keeps the summary of a barrier closed until the check for existing facts has run", () => {
    expect(findOpenStep(buildBarrierDraft(), "summary")).toBe("kind");
    expect(findOpenStep({ ...buildBarrierDraft(), existingFacts: [] }, "summary")).toBe("summary");
    expect(findOpenStep({ ...buildBarrierDraft(), existingFacts: buildNearby() }, "summary")).toBe("summary");
  });

  it("opens the existing facts only when the check found one", () => {
    expect(findOpenStep({ ...buildBarrierDraft(), existingFacts: buildNearby() }, "existing")).toBe("existing");
    expect(findOpenStep({ ...buildBarrierDraft(), existingFacts: [] }, "existing")).toBe("kind");
    expect(findOpenStep(buildBarrierDraft(), "existing")).toBe("kind");
  });

  it("opens the summary of an area without a check, and never its existing facts", () => {
    expect(findOpenStep(buildAreaDraft(), "summary")).toBe("summary");
    expect(findOpenStep(buildAreaDraft(), "existing")).toBe("kind");
  });

  it("keeps the summary of an area closed without a radius", () => {
    expect(findOpenStep({ ...buildAreaDraft(), radiusM: null }, "summary")).toBe("kind");
  });

  it("leads the saved state back to the first step when nothing is saved", () => {
    expect(findOpenStep({ ...buildBarrierDraft(), existingFacts: [] }, "saved")).toBe("kind");
  });

  it("shows only the saved state once the report is saved", () => {
    const draft: ReportDraft = { ...buildBarrierDraft(), existingFacts: [], savedFact: buildFact(100) };

    expect(EVERY_STEP.map((step) => findOpenStep(draft, step))).toEqual(["saved", "saved", "saved", "saved", "saved", "saved"]);
  });
});

describe("buildCreateFactRequest", () => {
  it("builds the body of a point report with its key, its type and its point", () => {
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), type: "high_kerb" }, KEY)).toEqual({
      idempotency_key: KEY,
      type: "high_kerb",
      point: POINT,
      description: null,
      step_count: null,
      geozone_radius_m: null,
    });
  });

  it("sends the description without the spaces around it, and an empty one as null", () => {
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), description: "  No handrail on the right.  " }, KEY)?.description).toBe("No handrail on the right.");
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), description: "   " }, KEY)?.description).toBeNull();
  });

  it("sends the number of steps only for stairs", () => {
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), stepCount: 4 }, KEY)?.step_count).toBe(4);
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), type: "high_kerb", stepCount: 4 }, KEY)?.step_count).toBeNull();
  });

  it("builds the body of an area with its radius and without a number of steps", () => {
    expect(buildCreateFactRequest({ ...buildAreaDraft(), type: "stairs", stepCount: 4, description: "Pavement works" }, KEY)).toEqual({
      idempotency_key: KEY,
      type: "stairs",
      point: POINT,
      description: "Pavement works",
      step_count: null,
      geozone_radius_m: 25,
    });
  });

  it("sends no radius for a point report, also when the draft still holds one", () => {
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), radiusM: 50 }, KEY)?.geozone_radius_m).toBeNull();
  });

  it("builds nothing for a draft that lacks its kind, its point, its type or the radius of an area", () => {
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), kind: null }, KEY)).toBeNull();
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), point: null }, KEY)).toBeNull();
    expect(buildCreateFactRequest({ ...buildBarrierDraft(), type: null }, KEY)).toBeNull();
    expect(buildCreateFactRequest({ ...buildAreaDraft(), radiusM: null }, KEY)).toBeNull();
  });
});

describe("rememberConfirmation", () => {
  it("remembers a confirmation with its voter, its day and the start of the next calendar day", () => {
    vi.stubGlobal("localStorage", createMemoryStorage());
    const now = new Date(2026, 9, 4, 9, 5, 7, 8);

    rememberConfirmation(42, "anna", now);

    const vote = readOwnVote(42, "anna");
    expect(readOwnVote(42, null)).toBeNull();
    expect(vote?.verdict).toBe("confirm");
    expect(vote?.votedOn).toBe("2026-10-04");
    expect(vote?.repeatAllowedAt.startsWith("2026-10-05T")).toBe(true);
  });
});

describe("makeIdempotencyKey", () => {
  it("makes a UUID, a new one every time", () => {
    const first = makeIdempotencyKey();
    const second = makeIdempotencyKey();

    expect(first).toMatch(UUID_VERSION_4_PATTERN);
    expect(second).toMatch(UUID_VERSION_4_PATTERN);
    expect(second).not.toBe(first);
  });

  it("makes a version 4 UUID from random bytes where the browser has no randomUUID, as on a page served over plain HTTP", () => {
    stubPlainHttpCrypto(() => 0xff);

    expect(makeIdempotencyKey()).toBe("ffffffff-ffff-4fff-bfff-ffffffffffff");
  });

  it("makes different keys from different random bytes", () => {
    let last = 0;
    stubPlainHttpCrypto(() => {
      last += 1;
      return last;
    });

    const first = makeIdempotencyKey();
    const second = makeIdempotencyKey();

    expect(first).toMatch(UUID_VERSION_4_PATTERN);
    expect(second).toMatch(UUID_VERSION_4_PATTERN);
    expect(second).not.toBe(first);
  });
});
