/**
 * The keys under which the device keeps its values, each with its version.
 */
export const STORAGE_KEYS = {
  needs: "enableme.needs.v1",
  language: "enableme.language.v1",
  session: "enableme.session.v1",
  ownVotes: "enableme.ownVotes.v1",
} as const;

export type StorageKey = (typeof STORAGE_KEYS)[keyof typeof STORAGE_KEYS];

/**
 * Returns the storage of the browser, or null where it does not exist or the browser refuses it.
 */
function findStorage(): Storage | null {
  try {
    return typeof localStorage === "undefined" ? null : localStorage;
  } catch {
    return null;
  }
}

/**
 * Reads the value kept under a key.
 * A value that is missing, is not JSON or fails isValid reads as absent, and what was kept is removed.
 */
export function readStored<T>(key: StorageKey, isValid: (value: unknown) => value is T): T | null {
  const storage = findStorage();
  if (storage === null) {
    return null;
  }
  let text: string | null;
  try {
    text = storage.getItem(key);
  } catch {
    return null;
  }
  if (text === null) {
    return null;
  }
  try {
    const value: unknown = JSON.parse(text);
    if (isValid(value)) {
      return value;
    }
  } catch {
    removeStored(key);
    return null;
  }
  removeStored(key);
  return null;
}

/**
 * Keeps a value under a key as JSON. A storage that refuses the write is ignored: the value then lives until the page closes.
 */
export function writeStored(key: StorageKey, value: unknown): void {
  const storage = findStorage();
  if (storage === null) {
    return;
  }
  try {
    storage.setItem(key, JSON.stringify(value));
  } catch {
    return;
  }
}

/**
 * Removes the value kept under a key.
 */
export function removeStored(key: StorageKey): void {
  const storage = findStorage();
  if (storage === null) {
    return;
  }
  try {
    storage.removeItem(key);
  } catch {
    return;
  }
}

/**
 * Tells whether a value is a text, the check for the values kept as one text.
 */
export function isText(value: unknown): value is string {
  return typeof value === "string";
}
