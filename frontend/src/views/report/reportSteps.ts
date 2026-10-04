import type { CreateFactRequest, GeozoneRadius } from "../../api/types.ts";
import { saveOwnVote, startOfNextDay, toDeviceDay } from "../../state/ownVotes.ts";
import type { ReportDraft, ReportKind } from "../../state/reportDraft.tsx";

/**
 * The steps of the flow, named as the last part of their addresses.
 */
export type ReportStep = "kind" | "place" | "details" | "existing" | "summary" | "saved";

/**
 * The address of every step of the flow.
 */
export const REPORT_PATHS: Record<ReportStep, string> = {
  kind: "/report",
  place: "/report/place",
  details: "/report/details",
  existing: "/report/existing",
  summary: "/report/summary",
  saved: "/report/saved",
};

/**
 * The kinds of a report in the order the first step lists them.
 */
export const REPORT_KINDS: readonly ReportKind[] = ["barrier", "amenity", "area"];

/**
 * The radii an area can have, in metres, as the contract lists them.
 */
export const GEOZONE_RADII: readonly GeozoneRadius[] = [10, 25, 50, 100];

/**
 * The longest description the contract accepts, in characters.
 */
export const DESCRIPTION_MAX_LENGTH = 500;

/**
 * The longest text of an address search the contract accepts, in characters.
 */
export const SEARCH_TEXT_MAX_LENGTH = 200;

/**
 * The identifier of the heading of a step, which names the panel and the first group of choices of the step.
 */
export const REPORT_HEADING_ID = "report-heading";

const POINT_STEP_COUNT = 5;
const AREA_STEP_COUNT = 4;
const STEP_COUNT_PATTERN = /^\d{1,3}$/;
const UUID_BYTE_COUNT = 16;

const STEP_NUMBERS: Record<Exclude<ReportStep, "summary" | "saved">, number> = { kind: 1, place: 2, details: 3, existing: 4 };

/**
 * Returns how many steps the flow of a kind counts: five for a barrier or an amenity, and four for an area,
 * which has no step of existing facts.
 */
export function countSteps(kind: ReportKind): number {
  return kind === "area" ? AREA_STEP_COUNT : POINT_STEP_COUNT;
}

/**
 * Returns the number of a step in the flow of a kind. The summary is always the last counted step.
 */
export function findStepNumber(step: Exclude<ReportStep, "saved">, kind: ReportKind): number {
  return step === "summary" ? countSteps(kind) : STEP_NUMBERS[step];
}

/**
 * Reads the number of steps a person typed: null for an empty field, the number for a whole number from 1 to 999,
 * and the word invalid for every other text.
 */
export function readStepCount(text: string): number | null | "invalid" {
  const trimmed = text.trim();
  if (trimmed === "") {
    return null;
  }
  if (!STEP_COUNT_PATTERN.test(trimmed)) {
    return "invalid";
  }
  const count = Number(trimmed);
  return count >= 1 ? count : "invalid";
}

/**
 * Tells whether the flow of a draft shows the step of existing facts: only for a barrier or an amenity,
 * and only when the check near its point found a fact.
 */
export function hasExistingStep(draft: ReportDraft): boolean {
  return draft.kind !== "area" && draft.existingFacts !== null && draft.existingFacts.length > 0;
}

/**
 * Returns the step the flow shows when a step is asked for by its address.
 * A saved report shows only the saved state, so it cannot be changed or sent again.
 * A step whose earlier steps have not given their data leads back to the first step.
 */
export function findOpenStep(draft: ReportDraft, wanted: ReportStep): ReportStep {
  if (draft.savedFact !== null) {
    return "saved";
  }
  if (wanted === "kind" || wanted === "saved" || draft.kind === null) {
    return "kind";
  }
  if (wanted === "place") {
    return "place";
  }
  if (draft.point === null) {
    return "kind";
  }
  if (wanted === "details") {
    return "details";
  }
  const isArea = draft.kind === "area";
  if (draft.type === null || (isArea && draft.radiusM === null)) {
    return "kind";
  }
  if (wanted === "existing") {
    return hasExistingStep(draft) ? "existing" : "kind";
  }
  return isArea || draft.existingFacts !== null ? "summary" : "kind";
}

/**
 * Builds the body of create_fact from a draft and the key of its save, or null for a draft that lacks a required part.
 * The description travels without the spaces around it and as null when it is empty, the number of steps only for stairs
 * reported at a point, and the radius only for an area.
 */
export function buildCreateFactRequest(draft: ReportDraft, idempotencyKey: string): CreateFactRequest | null {
  if (draft.kind === null || draft.point === null || draft.type === null) {
    return null;
  }
  const isArea = draft.kind === "area";
  if (isArea && draft.radiusM === null) {
    return null;
  }
  const description = draft.description.trim();
  return {
    idempotency_key: idempotencyKey,
    type: draft.type,
    point: draft.point,
    description: description === "" ? null : description,
    step_count: !isArea && draft.type === "stairs" ? draft.stepCount : null,
    geozone_radius_m: isArea ? draft.radiusM : null,
  };
}

/**
 * Remembers on the device that a voter confirmed a fact, by default at this moment, as the detail of a fact does after a vote,
 * so the detail shows the vote and from when the next one is possible. The voter is the pseudonym of the account of the session,
 * or null for a person without an account. A saved report is remembered the same way, because it carries the confirmation of its author.
 */
export function rememberConfirmation(factId: number, voter: string | null, now: Date = new Date()): void {
  saveOwnVote(factId, voter, "confirm", toDeviceDay(now), startOfNextDay(now));
}

/**
 * Makes the key of one save, a random UUID. A page served over plain HTTP has no crypto.randomUUID,
 * so there the key is built from random bytes in the form of a version 4 UUID.
 */
export function makeIdempotencyKey(): string {
  if (typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  const bytes = crypto.getRandomValues(new Uint8Array(UUID_BYTE_COUNT));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = [...bytes].map((byte) => byte.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
