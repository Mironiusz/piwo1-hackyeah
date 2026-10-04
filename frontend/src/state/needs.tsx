import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { AMENITY_TYPES, BARRIER_TYPES, isBarrierType, type AmenityType, type BarrierType, type FactType } from "../api/types.ts";
import { readStored, STORAGE_KEYS, writeStored } from "./storage.ts";

/**
 * The needs of a person: the barriers to avoid, the amenities needed, and whether the first opening has happened.
 * They live only on the device.
 */
export interface Needs {
  avoid: BarrierType[];
  need: AmenityType[];
  isSeen: boolean;
}

export type NeedsPresetId = "wheelchair" | "stroller" | "walking";

/**
 * The three presets, as the table of M1 of the specification lists them. A preset only sets the items and is never kept.
 */
export const NEEDS_PRESETS: Record<NeedsPresetId, { avoid: BarrierType[]; need: AmenityType[] }> = {
  wheelchair: {
    avoid: ["stairs", "high_kerb", "poor_surface", "steep_incline", "narrow_passage"],
    need: ["elevator", "ramp", "lowered_kerb", "accessible_toilet"],
  },
  stroller: {
    avoid: ["stairs", "high_kerb", "poor_surface", "narrow_passage"],
    need: ["elevator", "ramp", "lowered_kerb"],
  },
  walking: {
    avoid: ["stairs", "poor_surface", "steep_incline"],
    need: ["rest_place", "handrail_at_stairs"],
  },
};

export const EMPTY_NEEDS: Needs = { avoid: [], need: [], isSeen: false };

/**
 * Tells whether a value has the form the device keeps the needs in.
 */
export function isNeeds(value: unknown): value is Needs {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const candidate = value as Record<string, unknown>;
  const barriers: readonly unknown[] = BARRIER_TYPES;
  const amenities: readonly unknown[] = AMENITY_TYPES;
  return (
    Array.isArray(candidate.avoid) &&
    candidate.avoid.every((item) => barriers.includes(item)) &&
    Array.isArray(candidate.need) &&
    candidate.need.every((item) => amenities.includes(item)) &&
    typeof candidate.isSeen === "boolean"
  );
}

/**
 * Reads the needs kept on the device, or the empty needs of a first opening.
 */
export function readStoredNeeds(): Needs {
  return readStored(STORAGE_KEYS.needs, isNeeds) ?? EMPTY_NEEDS;
}

/**
 * Returns the needs with one item switched: set when it was clear, and cleared when it was set.
 * The items keep the order of the closed list.
 */
export function toggleNeedsItem(needs: Needs, type: FactType): Needs {
  if (isBarrierType(type)) {
    const isSet = needs.avoid.includes(type);
    return { ...needs, avoid: BARRIER_TYPES.filter((item) => (item === type ? !isSet : needs.avoid.includes(item))) };
  }
  const isSet = needs.need.includes(type);
  return { ...needs, need: AMENITY_TYPES.filter((item) => (item === type ? !isSet : needs.need.includes(item))) };
}

/**
 * Returns the needs with the items of a preset in place of the ones that were set.
 */
export function applyNeedsPreset(needs: Needs, presetId: NeedsPresetId): Needs {
  const preset = NEEDS_PRESETS[presetId];
  return { ...needs, avoid: [...preset.avoid], need: [...preset.need] };
}

/**
 * Tells whether a fact type is one of the items of the needs.
 */
export function isInNeeds(needs: Needs, type: FactType): boolean {
  return isBarrierType(type) ? needs.avoid.includes(type) : needs.need.includes(type);
}

/**
 * Returns a text that is equal for two needs with the same items, for telling whether a route was planned for the needs of now.
 */
export function needsSignature(needs: Needs): string {
  return `${needs.avoid.join(",")}|${needs.need.join(",")}`;
}

interface NeedsContextValue {
  needs: Needs;
  toggleItem: (type: FactType) => void;
  applyPreset: (presetId: NeedsPresetId) => void;
  markSeen: () => void;
}

const NeedsContext = createContext<NeedsContextValue | null>(null);

/**
 * Keeps the needs for the whole application and writes every change to the device.
 */
export function NeedsProvider({ children }: { children: ReactNode }) {
  const [needs, setNeeds] = useState<Needs>(readStoredNeeds);

  const change = useCallback((update: (current: Needs) => Needs) => {
    setNeeds((current) => {
      const next = update(current);
      writeStored(STORAGE_KEYS.needs, next);
      return next;
    });
  }, []);

  const value = useMemo<NeedsContextValue>(
    () => ({
      needs,
      toggleItem: (type) => change((current) => toggleNeedsItem(current, type)),
      applyPreset: (presetId) => change((current) => applyNeedsPreset(current, presetId)),
      markSeen: () => change((current) => (current.isSeen ? current : { ...current, isSeen: true })),
    }),
    [needs, change],
  );

  return <NeedsContext.Provider value={value}>{children}</NeedsContext.Provider>;
}

/**
 * Returns the needs and the actions that change them.
 */
export function useNeeds(): NeedsContextValue {
  const value = useContext(NeedsContext);
  if (value === null) {
    throw new Error("useNeeds is used outside NeedsProvider");
  }
  return value;
}
