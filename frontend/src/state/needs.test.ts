import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { FactType } from "../api/types.ts";
import { createMemoryStorage, type MemoryStorage } from "../testing/memoryStorage.ts";
import { applyNeedsPreset, EMPTY_NEEDS, isInNeeds, isNeeds, NEEDS_PRESETS, needsSignature, readStoredNeeds, toggleNeedsItem, type Needs, type NeedsPresetId } from "./needs.tsx";
import { STORAGE_KEYS } from "./storage.ts";

type PresetCell = "avoid" | "need" | "-";

/**
 * The table of M1 of docs/product/specification.md, row by row: the item, and what the presets
 * "I use a wheelchair", "I walk with a baby stroller" and "Walking is difficult for me" set for it.
 */
const M1_TABLE: [FactType, PresetCell, PresetCell, PresetCell][] = [
  ["stairs", "avoid", "avoid", "avoid"],
  ["high_kerb", "avoid", "avoid", "-"],
  ["poor_surface", "avoid", "avoid", "avoid"],
  ["steep_incline", "avoid", "-", "avoid"],
  ["narrow_passage", "avoid", "avoid", "-"],
  ["elevator", "need", "need", "-"],
  ["ramp", "need", "need", "-"],
  ["lowered_kerb", "need", "need", "-"],
  ["accessible_toilet", "need", "-", "-"],
  ["rest_place", "-", "-", "need"],
  ["handrail_at_stairs", "-", "-", "need"],
];

const M1_COLUMNS: [NeedsPresetId, 1 | 2 | 3][] = [
  ["wheelchair", 1],
  ["stroller", 2],
  ["walking", 3],
];

/**
 * Lists the items a column of the table of M1 marks with the given word, in the order of the table.
 */
function listItems(column: 1 | 2 | 3, cell: PresetCell): FactType[] {
  return M1_TABLE.filter((row) => row[column] === cell).map((row) => row[0]);
}

let storage: MemoryStorage;

beforeEach(() => {
  storage = createMemoryStorage();
  vi.stubGlobal("localStorage", storage);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("NEEDS_PRESETS", () => {
  it("holds the three presets of the specification and no other", () => {
    expect(Object.keys(NEEDS_PRESETS).sort()).toEqual(["stroller", "walking", "wheelchair"]);
  });

  it.each(M1_COLUMNS)("sets for the preset %s exactly what the table of M1 lists", (presetId, column) => {
    expect(NEEDS_PRESETS[presetId]).toEqual({ avoid: listItems(column, "avoid"), need: listItems(column, "need") });
  });

  it.each(M1_COLUMNS)("leaves for the preset %s the items the table of M1 marks with nothing", (presetId, column) => {
    const preset = NEEDS_PRESETS[presetId];
    const items: FactType[] = [...preset.avoid, ...preset.need];

    for (const item of listItems(column, "-")) {
      expect(items).not.toContain(item);
    }
  });
});

describe("EMPTY_NEEDS", () => {
  it("has no item and waits for the first opening", () => {
    expect(EMPTY_NEEDS).toEqual({ avoid: [], need: [], isSeen: false });
  });
});

describe("applyNeedsPreset", () => {
  it("puts the items of the preset in place of the ones that were set", () => {
    const needs: Needs = { avoid: ["steep_incline"], need: ["rest_place"], isSeen: true };

    expect(applyNeedsPreset(needs, "stroller")).toEqual({
      avoid: ["stairs", "high_kerb", "poor_surface", "narrow_passage"],
      need: ["elevator", "ramp", "lowered_kerb"],
      isSeen: true,
    });
  });

  it("keeps whether the first opening has happened", () => {
    expect(applyNeedsPreset({ ...EMPTY_NEEDS, isSeen: false }, "walking").isSeen).toBe(false);
    expect(applyNeedsPreset({ ...EMPTY_NEEDS, isSeen: true }, "walking").isSeen).toBe(true);
  });

  it("leaves the given needs as they were", () => {
    const needs: Needs = { avoid: ["steep_incline"], need: ["rest_place"], isSeen: false };

    applyNeedsPreset(needs, "wheelchair");

    expect(needs).toEqual({ avoid: ["steep_incline"], need: ["rest_place"], isSeen: false });
  });

  it("returns lists of its own, so a later change of the needs leaves the preset whole", () => {
    const needs = applyNeedsPreset(EMPTY_NEEDS, "walking");

    expect(needs.avoid).not.toBe(NEEDS_PRESETS.walking.avoid);
    expect(needs.need).not.toBe(NEEDS_PRESETS.walking.need);
  });

  it("can be changed item by item afterwards, as the specification lets a person untick stairs", () => {
    const needs = toggleNeedsItem(applyNeedsPreset(EMPTY_NEEDS, "walking"), "stairs");

    expect(needs.avoid).toEqual(["poor_surface", "steep_incline"]);
    expect(NEEDS_PRESETS.walking.avoid).toEqual(["stairs", "poor_surface", "steep_incline"]);
  });
});

describe("toggleNeedsItem", () => {
  it("sets a barrier that was clear", () => {
    expect(toggleNeedsItem(EMPTY_NEEDS, "stairs")).toEqual({ avoid: ["stairs"], need: [], isSeen: false });
  });

  it("clears a barrier that was set", () => {
    const needs: Needs = { avoid: ["stairs", "high_kerb"], need: [], isSeen: true };

    expect(toggleNeedsItem(needs, "stairs")).toEqual({ avoid: ["high_kerb"], need: [], isSeen: true });
  });

  it("sets an amenity that was clear", () => {
    expect(toggleNeedsItem(EMPTY_NEEDS, "ramp")).toEqual({ avoid: [], need: ["ramp"], isSeen: false });
  });

  it("clears an amenity that was set", () => {
    const needs: Needs = { avoid: ["stairs"], need: ["ramp", "rest_place"], isSeen: true };

    expect(toggleNeedsItem(needs, "rest_place")).toEqual({ avoid: ["stairs"], need: ["ramp"], isSeen: true });
  });

  it("keeps the barriers in the order of the closed list, whatever the order of the choices", () => {
    const needs = toggleNeedsItem(toggleNeedsItem(toggleNeedsItem(EMPTY_NEEDS, "narrow_passage"), "stairs"), "poor_surface");

    expect(needs.avoid).toEqual(["stairs", "poor_surface", "narrow_passage"]);
  });

  it("keeps the amenities in the order of the closed list, whatever the order of the choices", () => {
    const needs = toggleNeedsItem(toggleNeedsItem(toggleNeedsItem(EMPTY_NEEDS, "handrail_at_stairs"), "elevator"), "lowered_kerb");

    expect(needs.need).toEqual(["elevator", "lowered_kerb", "handrail_at_stairs"]);
  });

  it("returns to the same items when an item is switched twice", () => {
    const needs = applyNeedsPreset(EMPTY_NEEDS, "wheelchair");

    expect(toggleNeedsItem(toggleNeedsItem(needs, "high_kerb"), "high_kerb")).toEqual(needs);
    expect(toggleNeedsItem(toggleNeedsItem(needs, "rest_place"), "rest_place")).toEqual(needs);
  });

  it("leaves the given needs as they were", () => {
    const needs: Needs = { avoid: ["stairs"], need: ["ramp"], isSeen: false };

    toggleNeedsItem(needs, "stairs");
    toggleNeedsItem(needs, "elevator");

    expect(needs).toEqual({ avoid: ["stairs"], need: ["ramp"], isSeen: false });
  });
});

describe("isNeeds", () => {
  it("accepts the form the device keeps the needs in", () => {
    expect(isNeeds({ avoid: ["stairs"], need: ["ramp"], isSeen: true })).toBe(true);
    expect(isNeeds({ avoid: [], need: [], isSeen: false })).toBe(true);
    expect(isNeeds(applyNeedsPreset(EMPTY_NEEDS, "wheelchair"))).toBe(true);
  });

  it.each([
    ["nothing", null],
    ["a text", "stairs"],
    ["a list", ["stairs"]],
    ["needs without the barriers", { need: [], isSeen: true }],
    ["needs without the amenities", { avoid: [], isSeen: true }],
    ["needs without the mark of the first opening", { avoid: [], need: [] }],
    ["a mark of the first opening that is not true or false", { avoid: [], need: [], isSeen: "yes" }],
    ["barriers that are not a list", { avoid: "stairs", need: [], isSeen: true }],
    ["amenities that are not a list", { avoid: [], need: "ramp", isSeen: true }],
    ["a barrier outside the closed list", { avoid: ["dragon"], need: [], isSeen: true }],
    ["an amenity outside the closed list", { avoid: [], need: ["dragon"], isSeen: true }],
    ["an amenity among the barriers", { avoid: ["ramp"], need: [], isSeen: true }],
    ["a barrier among the amenities", { avoid: [], need: ["stairs"], isSeen: true }],
  ])("refuses %s", (_name, value) => {
    expect(isNeeds(value)).toBe(false);
  });
});

describe("readStoredNeeds", () => {
  it("returns the empty needs of a first opening when the device keeps none", () => {
    expect(readStoredNeeds()).toEqual(EMPTY_NEEDS);
  });

  it("returns the needs the device keeps", () => {
    const needs: Needs = { avoid: ["stairs", "poor_surface"], need: ["rest_place"], isSeen: true };
    storage.setItem(STORAGE_KEYS.needs, JSON.stringify(needs));

    expect(readStoredNeeds()).toEqual(needs);
  });

  it("returns the empty needs for a kept value of another form and removes that value", () => {
    storage.setItem(STORAGE_KEYS.needs, JSON.stringify({ avoid: ["dragon"], need: [], isSeen: true }));

    expect(readStoredNeeds()).toEqual(EMPTY_NEEDS);
    expect(storage.getItem(STORAGE_KEYS.needs)).toBeNull();
  });

  it("returns the empty needs without a local storage", () => {
    vi.stubGlobal("localStorage", undefined);

    expect(readStoredNeeds()).toEqual(EMPTY_NEEDS);
  });
});

describe("isInNeeds", () => {
  const needs: Needs = { avoid: ["stairs", "high_kerb"], need: ["ramp"], isSeen: true };

  it("finds a barrier the needs avoid", () => {
    expect(isInNeeds(needs, "stairs")).toBe(true);
    expect(isInNeeds(needs, "high_kerb")).toBe(true);
  });

  it("finds an amenity the needs ask for", () => {
    expect(isInNeeds(needs, "ramp")).toBe(true);
  });

  it("does not find an item that is not set", () => {
    expect(isInNeeds(needs, "poor_surface")).toBe(false);
    expect(isInNeeds(needs, "elevator")).toBe(false);
  });

  it("finds nothing in the empty needs", () => {
    expect(isInNeeds(EMPTY_NEEDS, "stairs")).toBe(false);
    expect(isInNeeds(EMPTY_NEEDS, "ramp")).toBe(false);
  });
});

describe("needsSignature", () => {
  it("is equal for two needs with the same items", () => {
    const first: Needs = { avoid: ["stairs", "high_kerb"], need: ["ramp"], isSeen: true };
    const second: Needs = { avoid: ["stairs", "high_kerb"], need: ["ramp"], isSeen: true };

    expect(needsSignature(first)).toBe(needsSignature(second));
  });

  it("does not depend on whether the first opening has happened", () => {
    const needs: Needs = { avoid: ["stairs"], need: ["ramp"], isSeen: false };

    expect(needsSignature(needs)).toBe(needsSignature({ ...needs, isSeen: true }));
  });

  it("differs when a barrier differs", () => {
    const needs: Needs = { avoid: ["stairs"], need: ["ramp"], isSeen: true };

    expect(needsSignature(needs)).not.toBe(needsSignature(toggleNeedsItem(needs, "high_kerb")));
    expect(needsSignature(needs)).not.toBe(needsSignature(toggleNeedsItem(needs, "stairs")));
  });

  it("differs when an amenity differs", () => {
    const needs: Needs = { avoid: ["stairs"], need: ["ramp"], isSeen: true };

    expect(needsSignature(needs)).not.toBe(needsSignature(toggleNeedsItem(needs, "elevator")));
    expect(needsSignature(needs)).not.toBe(needsSignature(toggleNeedsItem(needs, "ramp")));
  });

  it("differs for each of the three presets and for the empty needs", () => {
    const signatures = [EMPTY_NEEDS, applyNeedsPreset(EMPTY_NEEDS, "wheelchair"), applyNeedsPreset(EMPTY_NEEDS, "stroller"), applyNeedsPreset(EMPTY_NEEDS, "walking")].map(needsSignature);

    expect(new Set(signatures).size).toBe(4);
  });
});
