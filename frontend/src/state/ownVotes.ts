import type { Verdict } from "../api/types.ts";
import { readStored, STORAGE_KEYS, writeStored } from "./storage.ts";

/**
 * The latest vote of a person on one fact, as the device remembers it: who cast it, the verdict, the day it was cast
 * and the instant from which the next vote is accepted. The voter is the pseudonym of the account of the session,
 * or null for a person without an account.
 */
export interface OwnVote {
  voter: string | null;
  verdict: Verdict;
  votedOn: string;
  repeatAllowedAt: string;
}

/**
 * A vote as the device keeps it. A vote kept before the voter was remembered has none
 * and is read as the vote of a person without an account.
 */
type KeptVote = Omit<OwnVote, "voter"> & { voter?: string | null };

type OwnVotes = Record<string, KeptVote>;

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
    const hasVoter = candidate.voter === undefined || candidate.voter === null || typeof candidate.voter === "string";
    return hasVoter && (candidate.verdict === "confirm" || candidate.verdict === "deny") && typeof candidate.votedOn === "string" && typeof candidate.repeatAllowedAt === "string";
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
 * Returns the vote the device remembers for a fact and a voter, or null.
 * The vote of another voter on the same fact is not returned, so nobody is shown the vote of someone else who used the device.
 */
export function readOwnVote(factId: number, voter: string | null): OwnVote | null {
  const kept = readStored(STORAGE_KEYS.ownVotes, isOwnVotes)?.[String(factId)];
  if (kept === undefined || (kept.voter ?? null) !== voter) {
    return null;
  }
  return { voter, verdict: kept.verdict, votedOn: kept.votedOn, repeatAllowedAt: kept.repeatAllowedAt };
}

/**
 * Remembers the latest vote of a voter on a fact. The device keeps one vote for a fact, the latest one cast on it.
 */
export function saveOwnVote(factId: number, voter: string | null, verdict: Verdict, votedOn: string, repeatAllowedAt: string): void {
  const votes = readStored(STORAGE_KEYS.ownVotes, isOwnVotes) ?? {};
  writeStored(STORAGE_KEYS.ownVotes, { ...votes, [String(factId)]: { voter, verdict, votedOn, repeatAllowedAt } });
}

/**
 * Tells whether a voter can vote on a fact now: no vote of theirs is remembered, or the calendar day after it has started.
 */
export function canVoteNow(factId: number, voter: string | null, now: Date): boolean {
  const vote = readOwnVote(factId, voter);
  if (vote === null) {
    return true;
  }
  const repeatAllowedAt = Date.parse(vote.repeatAllowedAt);
  return Number.isNaN(repeatAllowedAt) || repeatAllowedAt <= now.getTime();
}
