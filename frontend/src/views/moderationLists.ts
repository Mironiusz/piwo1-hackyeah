import type { ApiErrorCode, FlaggedFact } from "../api/types.ts";

/**
 * The two lists of the moderation view: the flagged facts that are not hidden, and the hidden ones.
 */
export interface ModerationLists {
  flagged: FlaggedFact[];
  hidden: FlaggedFact[];
}

/**
 * Splits the flagged facts the service listed into the two lists of the moderation view, in the order of the service.
 * An item the service answered again after it was hidden or restored replaces the listed one,
 * so it moves between the lists without the list being asked for again.
 */
export function splitFlaggedFacts(listed: readonly FlaggedFact[], changed: readonly FlaggedFact[]): ModerationLists {
  const lists: ModerationLists = { flagged: [], hidden: [] };
  for (const item of listed) {
    const current = changed.find((candidate) => candidate.fact.id === item.fact.id) ?? item;
    if (current.is_hidden) {
      lists.hidden.push(current);
    } else {
      lists.flagged.push(current);
    }
  }
  return lists;
}

/**
 * Returns the changed items with one more answer of the service, which takes the place of an earlier answer for the same fact.
 */
export function keepChangedFact(changed: readonly FlaggedFact[], item: FlaggedFact): FlaggedFact[] {
  return [...changed.filter((candidate) => candidate.fact.id !== item.fact.id), item];
}

/**
 * Returns the item of a list that stands after the item of a fact, or else the one before it, or null when the list holds no other item.
 * It is where the keyboard focus goes when that item leaves the list.
 */
export function findNeighbour(list: readonly FlaggedFact[], factId: number): FlaggedFact | null {
  const index = list.findIndex((item) => item.fact.id === factId);
  if (index === -1) {
    return null;
  }
  return list[index + 1] ?? list[index - 1] ?? null;
}

/**
 * Tells whether the service refused a request because the account is missing or does not hold the moderator role.
 */
export function isModeratorRefusal(code: ApiErrorCode): boolean {
  return code === "moderator_role_required" || code === "authentication_required";
}

/**
 * Returns the identifier of the title of an item of the moderation view, by which the item is named and found for the keyboard focus.
 */
export function buildItemTitleId(factId: number): string {
  return `moderation-item-${factId}`;
}

/**
 * Returns the identifier of the button that hides or restores an item of the moderation view.
 */
export function buildItemActionId(factId: number): string {
  return `moderation-action-${factId}`;
}
