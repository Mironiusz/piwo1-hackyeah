import type { Verdict } from "../api/types.ts";
import { readStored, STORAGE_KEYS, writeStored } from "./storage.ts";

/**
 * The latest vote of the person on one fact, as the device remembers it: the verdict, the day it was cast
 * and the instant from which the next vote is accepted.
 */
export interface OwnVote {
  verdict: Verdict;
  votedOn: string;
  repeatAllowedAt: string;
}

type OwnVotes = Record<string, OwnVote>;

/**
 * Tells whether a value has the form the device keeps the own votes in.
 */
function isOwnVotes(value: unknown): value is OwnVotes {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return false;
  }
  return Object.values(value).every((vote) => {
    if (typeof vote !== "object" || vote === null) {
      return false;
    }
    const candidate = vote as Record<string, unknown>;
    return (candidate.verdict === "confirm" || candidate.verdict === "deny") && typeof candidate.votedOn === "string" && typeof candidate.repeatAllowedAt === "string";
  });
}

/**
 * Writes two digits of a number, with a leading zero.
 */
function pad(value: number): string {
  return String(value).padStart(2, "0");
}

/**
 * Writes the calendar day of a moment on this device as YYYY-MM-DD.
 */
export function toDeviceDay(moment: Date): string {
  return `${moment.getFullYear()}-${pad(moment.getMonth() + 1)}-${pad(moment.getDate())}`;
}

/**
 * Writes a moment as an instant with the clock of this device and its offset, the form the service writes instants in.
 */
export function toDeviceInstant(moment: Date): string {
  const offsetMinutes = -moment.getTimezoneOffset();
  const sign = offsetMinutes < 0 ? "-" : "+";
  const offset = `${sign}${pad(Math.floor(Math.abs(offsetMinutes) / 60))}:${pad(Math.abs(offsetMinutes) % 60)}`;
  const time = `${pad(moment.getHours())}:${pad(moment.getMinutes())}:${pad(moment.getSeconds())}.${String(moment.getMilliseconds()).padStart(3, "0")}`;
  return `${toDeviceDay(moment)}T${time}${offset}`;
}

/**
 * Returns the instant at which the next calendar day starts on the clock of this device.
 * The service accepts one vote of a person on a fact in a calendar day, so the next vote is possible from that instant.
 */
export function startOfNextDay(moment: Date): string {
  return toDeviceInstant(new Date(moment.getFullYear(), moment.getMonth(), moment.getDate() + 1));
}

/**
 * Returns the vote the device remembers for a fact, or null.
 */
export function readOwnVote(factId: number): OwnVote | null {
  const votes = readStored(STORAGE_KEYS.ownVotes, isOwnVotes);
  return votes?.[String(factId)] ?? null;
}

/**
 * Remembers the latest vote of the person on a fact.
 */
export function saveOwnVote(factId: number, verdict: Verdict, votedOn: string, repeatAllowedAt: string): void {
  const votes = readStored(STORAGE_KEYS.ownVotes, isOwnVotes) ?? {};
  writeStored(STORAGE_KEYS.ownVotes, { ...votes, [String(factId)]: { verdict, votedOn, repeatAllowedAt } });
}

/**
 * Tells whether the person can vote on a fact now: no vote is remembered, or the calendar day after it has started.
 */
export function canVoteNow(factId: number, now: Date): boolean {
  const vote = readOwnVote(factId);
  if (vote === null) {
    return true;
  }
  const repeatAllowedAt = Date.parse(vote.repeatAllowedAt);
  return Number.isNaN(repeatAllowedAt) || repeatAllowedAt <= now.getTime();
}
