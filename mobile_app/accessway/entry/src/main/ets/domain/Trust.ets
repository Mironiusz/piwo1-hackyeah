import { DAY_MS, FactStatus, Vote } from '../model/Types';

export const CONFIRM_THRESHOLD: number = 2.0;
export const OUTDATED_THRESHOLD: number = 2.0;
export const WEIGHT_ACCOUNT: number = 1.0;
export const WEIGHT_ANON: number = 0.5;
export const VOTE_COOLDOWN_MS: number = DAY_MS;

export function voteWeight(loggedIn: boolean): number {
  return loggedIn ? WEIGHT_ACCOUNT : WEIGHT_ANON;
}

/** The latest vote of each person; a later vote by the same person replaces the earlier one. */
export function latestVotes(votes: Vote[]): Vote[] {
  const byVoter: Map<string, Vote> = new Map<string, Vote>();
  for (const v of votes) {
    const prev = byVoter.get(v.voterId);
    if (prev === undefined || v.at >= prev.at) {
      byVoter.set(v.voterId, v);
    }
  }
  return Array.from(byVoter.values());
}

/**
 * Fact status from votes. Outdated when "już nie ma" (no longer there) votes outweigh by the threshold; disputed
 * when there are votes of both kinds; confirmed when "nadal jest" (still there) votes reach the threshold;
 * otherwise unverified. The status does not change by itself over time.
 */
export function factStatus(votes: Vote[]): FactStatus {
  let yes = 0;
  let no = 0;
  for (const v of latestVotes(votes)) {
    if (v.value > 0) {
      yes += v.weight;
    } else {
      no += v.weight;
    }
  }
  if (no - yes >= OUTDATED_THRESHOLD) {
    return FactStatus.OUTDATED;
  }
  if (yes > 0 && no > 0) {
    return FactStatus.DISPUTED;
  }
  if (yes >= CONFIRM_THRESHOLD) {
    return FactStatus.CONFIRMED;
  }
  return FactStatus.UNVERIFIED;
}

export function lastConfirmation(createdAt: number, votes: Vote[]): number {
  let t = createdAt;
  for (const v of votes) {
    if (v.value > 0) {
      t = Math.max(t, v.at);
    }
  }
  return t;
}

/** This person's vote cast within the last 24 hours, or null. */
export function recentVote(votes: Vote[], voterId: string, now: number): Vote | null {
  let found: Vote | null = null;
  for (const v of votes) {
    if (v.voterId === voterId && now - v.at < VOTE_COOLDOWN_MS) {
      if (found === null || v.at > found.at) {
        found = v;
      }
    }
  }
  return found;
}
