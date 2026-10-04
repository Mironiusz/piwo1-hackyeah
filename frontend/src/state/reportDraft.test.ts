import { describe, expect, it } from "vitest";

import { AMENITY_TYPES, BARRIER_TYPES, type Fact, type NearbyFact } from "../api/types.ts";
import { changeReportDraft, EMPTY_REPORT_DRAFT, listTypesOfKind, type ReportDraft } from "./reportDraft.tsx";

const POINT = { lat: 50.0661, lon: 19.9878 };
const OTHER_POINT = { lat: 50.0678, lon: 19.9914 };
const KEY = "6f1c2a9e-0b8d-4c55-9a51-3e2f7d1b9c40";

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
 * Builds the list of existing facts a check near a point found.
 */
function buildNearby(): NearbyFact[] {
  return [{ fact: buildFact(7), distance_m: 8 }];
}

/**
 * Builds the draft of a barrier whose details were approved: the stairs at a point, with the existing facts found and a key.
 */
function buildCheckedDraft(): ReportDraft {
  return { ...EMPTY_REPORT_DRAFT, kind: "barrier", point: POINT, type: "stairs", description: "Three steps", stepCount: 3, existingFacts: buildNearby(), idempotencyKey: KEY };
}

describe("listTypesOfKind", () => {
  it("lists the barriers for a barrier and for an area", () => {
    expect(listTypesOfKind("barrier")).toEqual(BARRIER_TYPES);
    expect(listTypesOfKind("area")).toEqual(BARRIER_TYPES);
  });

  it("lists the amenities for an amenity", () => {
    expect(listTypesOfKind("amenity")).toEqual(AMENITY_TYPES);
  });
});

describe("changeReportDraft", () => {
  it("sets the kind of an empty draft", () => {
    expect(changeReportDraft(EMPTY_REPORT_DRAFT, { name: "kind", kind: "amenity" })).toEqual({ ...EMPTY_REPORT_DRAFT, kind: "amenity" });
  });

  it("returns the same draft when the kind does not change, so the existing facts found stay", () => {
    const draft = buildCheckedDraft();

    expect(changeReportDraft(draft, { name: "kind", kind: "barrier" })).toBe(draft);
  });

  it("keeps a barrier type when a barrier becomes an area, and drops the existing facts found", () => {
    const changed = changeReportDraft(buildCheckedDraft(), { name: "kind", kind: "area" });

    expect(changed.kind).toBe("area");
    expect(changed.type).toBe("stairs");
    expect(changed.existingFacts).toBeNull();
  });

  it("drops a type that is not on the list of the new kind", () => {
    const toAmenity = changeReportDraft(buildCheckedDraft(), { name: "kind", kind: "amenity" });
    const toBarrier = changeReportDraft({ ...EMPTY_REPORT_DRAFT, kind: "amenity", type: "ramp" }, { name: "kind", kind: "barrier" });

    expect(toAmenity.type).toBeNull();
    expect(toBarrier.type).toBeNull();
  });

  it("keeps what else was given when the kind changes", () => {
    const changed = changeReportDraft(buildCheckedDraft(), { name: "kind", kind: "amenity" });

    expect(changed.point).toEqual(POINT);
    expect(changed.description).toBe("Three steps");
    expect(changed.idempotencyKey).toBe(KEY);
  });

  it("drops the existing facts found when the point changes", () => {
    const changed = changeReportDraft(buildCheckedDraft(), { name: "point", point: OTHER_POINT });

    expect(changed.point).toEqual(OTHER_POINT);
    expect(changed.existingFacts).toBeNull();
    expect(changed.type).toBe("stairs");
  });

  it("drops the existing facts found when the type changes, and keeps them when it does not", () => {
    const draft = buildCheckedDraft();

    expect(changeReportDraft(draft, { name: "type", type: "high_kerb" })).toEqual({ ...draft, type: "high_kerb", existingFacts: null });
    expect(changeReportDraft(draft, { name: "type", type: "stairs" })).toBe(draft);
  });

  it("changes the description, the number of steps and the radius without touching the existing facts found", () => {
    const draft = buildCheckedDraft();

    expect(changeReportDraft(draft, { name: "description", description: "Four steps" })).toEqual({ ...draft, description: "Four steps" });
    expect(changeReportDraft(draft, { name: "step_count", stepCount: null })).toEqual({ ...draft, stepCount: null });
    expect(changeReportDraft(draft, { name: "radius", radiusM: 50 })).toEqual({ ...draft, radiusM: 50 });
  });

  it("keeps the existing facts a check found, also an empty list", () => {
    const facts = buildNearby();

    expect(changeReportDraft(EMPTY_REPORT_DRAFT, { name: "existing_facts", facts }).existingFacts).toBe(facts);
    expect(changeReportDraft(EMPTY_REPORT_DRAFT, { name: "existing_facts", facts: [] }).existingFacts).toEqual([]);
  });

  it("keeps the key of a save and drops it", () => {
    const kept = changeReportDraft(EMPTY_REPORT_DRAFT, { name: "idempotency_key", key: KEY });

    expect(kept.idempotencyKey).toBe(KEY);
    expect(changeReportDraft(kept, { name: "idempotency_key", key: null }).idempotencyKey).toBeNull();
  });

  it("keeps the key through every change of what the report says", () => {
    const draft = buildCheckedDraft();

    expect(changeReportDraft(draft, { name: "point", point: OTHER_POINT }).idempotencyKey).toBe(KEY);
    expect(changeReportDraft(draft, { name: "type", type: "high_kerb" }).idempotencyKey).toBe(KEY);
    expect(changeReportDraft(draft, { name: "description", description: "" }).idempotencyKey).toBe(KEY);
  });

  it("keeps the saved fact and drops the key of its save", () => {
    const fact = buildFact(100);
    const saved = changeReportDraft(buildCheckedDraft(), { name: "saved_fact", fact });

    expect(saved.savedFact).toBe(fact);
    expect(saved.idempotencyKey).toBeNull();
  });

  it("clears everything", () => {
    const saved = changeReportDraft(buildCheckedDraft(), { name: "saved_fact", fact: buildFact(100) });

    expect(changeReportDraft(saved, { name: "clear" })).toBe(EMPTY_REPORT_DRAFT);
  });
});
