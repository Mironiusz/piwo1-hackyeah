import { createContext, useContext, useMemo, useReducer, type ReactNode } from "react";

import { AMENITY_TYPES, BARRIER_TYPES, type Fact, type FactType, type GeozoneRadius, type NearbyFact, type Point } from "../api/types.ts";

/**
 * What a person reports: a barrier or an amenity at a point, or an area that is hard to pass.
 */
export type ReportKind = "barrier" | "amenity" | "area";

/**
 * A report a person is writing: what they gave so far, the existing facts found near its point,
 * the key of its save and the fact the service saved. It lives while the flow is open and is written nowhere.
 */
export interface ReportDraft {
  kind: ReportKind | null;
  point: Point | null;
  type: FactType | null;
  description: string;
  stepCount: number | null;
  radiusM: GeozoneRadius | null;
  existingFacts: NearbyFact[] | null;
  idempotencyKey: string | null;
  savedFact: Fact | null;
}

/**
 * The draft of a flow that has just opened: nothing is given yet.
 */
export const EMPTY_REPORT_DRAFT: ReportDraft = {
  kind: null,
  point: null,
  type: null,
  description: "",
  stepCount: null,
  radiusM: null,
  existingFacts: null,
  idempotencyKey: null,
  savedFact: null,
};

/**
 * One change of the draft.
 */
export type ReportDraftChange =
  | { name: "kind"; kind: ReportKind }
  | { name: "point"; point: Point }
  | { name: "type"; type: FactType }
  | { name: "description"; description: string }
  | { name: "step_count"; stepCount: number | null }
  | { name: "radius"; radiusM: GeozoneRadius }
  | { name: "existing_facts"; facts: NearbyFact[] }
  | { name: "idempotency_key"; key: string | null }
  | { name: "saved_fact"; fact: Fact }
  | { name: "clear" };

/**
 * Returns the closed list of fact types a report of a kind picks from: the amenities for an amenity,
 * and the barriers for a barrier and for an area.
 */
export function listTypesOfKind(kind: ReportKind): readonly FactType[] {
  return kind === "amenity" ? AMENITY_TYPES : BARRIER_TYPES;
}

/**
 * Returns the draft after one change.
 * A new kind drops a type that is not on its list. A new kind, a new point and a new type drop the existing facts found,
 * because they were found for the old ones. A saved fact drops the key of its save.
 */
export function changeReportDraft(draft: ReportDraft, change: ReportDraftChange): ReportDraft {
  switch (change.name) {
    case "kind": {
      if (change.kind === draft.kind) {
        return draft;
      }
      const keepsType = draft.type !== null && listTypesOfKind(change.kind).includes(draft.type);
      return { ...draft, kind: change.kind, type: keepsType ? draft.type : null, existingFacts: null };
    }
    case "point":
      return { ...draft, point: change.point, existingFacts: null };
    case "type":
      return change.type === draft.type ? draft : { ...draft, type: change.type, existingFacts: null };
    case "description":
      return { ...draft, description: change.description };
    case "step_count":
      return { ...draft, stepCount: change.stepCount };
    case "radius":
      return { ...draft, radiusM: change.radiusM };
    case "existing_facts":
      return { ...draft, existingFacts: change.facts };
    case "idempotency_key":
      return { ...draft, idempotencyKey: change.key };
    case "saved_fact":
      return { ...draft, savedFact: change.fact, idempotencyKey: null };
    case "clear":
      return EMPTY_REPORT_DRAFT;
  }
}

interface ReportDraftContextValue {
  draft: ReportDraft;
  setKind: (kind: ReportKind) => void;
  setPoint: (point: Point) => void;
  setType: (type: FactType) => void;
  setDescription: (description: string) => void;
  setStepCount: (stepCount: number | null) => void;
  setRadius: (radiusM: GeozoneRadius) => void;
  keepExistingFacts: (facts: NearbyFact[]) => void;
  keepIdempotencyKey: (key: string) => void;
  dropIdempotencyKey: () => void;
  keepSavedFact: (fact: Fact) => void;
  clear: () => void;
}

const ReportDraftContext = createContext<ReportDraftContextValue | null>(null);

/**
 * Keeps the draft of a report for the steps of the flow, so a person who goes a step back finds what was given.
 * The draft ends with the flow: leaving the flow drops it, and nothing of it is written to the device.
 */
export function ReportDraftProvider({ children }: { children: ReactNode }) {
  const [draft, change] = useReducer(changeReportDraft, EMPTY_REPORT_DRAFT);

  const value = useMemo<ReportDraftContextValue>(
    () => ({
      draft,
      setKind: (kind) => change({ name: "kind", kind }),
      setPoint: (point) => change({ name: "point", point }),
      setType: (type) => change({ name: "type", type }),
      setDescription: (description) => change({ name: "description", description }),
      setStepCount: (stepCount) => change({ name: "step_count", stepCount }),
      setRadius: (radiusM) => change({ name: "radius", radiusM }),
      keepExistingFacts: (facts) => change({ name: "existing_facts", facts }),
      keepIdempotencyKey: (key) => change({ name: "idempotency_key", key }),
      dropIdempotencyKey: () => change({ name: "idempotency_key", key: null }),
      keepSavedFact: (fact) => change({ name: "saved_fact", fact }),
      clear: () => change({ name: "clear" }),
    }),
    [draft],
  );

  return <ReportDraftContext.Provider value={value}>{children}</ReportDraftContext.Provider>;
}

/**
 * Returns the draft of the report and the actions that change it and clear it.
 */
export function useReportDraft(): ReportDraftContextValue {
  const value = useContext(ReportDraftContext);
  if (value === null) {
    throw new Error("useReportDraft is used outside ReportDraftProvider");
  }
  return value;
}
