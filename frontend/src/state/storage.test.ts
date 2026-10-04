import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createMemoryStorage, type MemoryStorage } from "../testing/memoryStorage.ts";
import { isText, readStored, removeStored, STORAGE_KEYS, writeStored } from "./storage.ts";

let storage: MemoryStorage;

/**
 * Tells whether a value is the language Polish, a check that refuses every other value kept under the key.
 */
function isPolish(value: unknown): value is "pl" {
  return value === "pl";
}

/**
 * Tells whether a value is an object with a number under count, a check for a kept value that is not a text.
 */
function isCounter(value: unknown): value is { count: number } {
  return typeof value === "object" && value !== null && "count" in value && typeof value.count === "number";
}

/**
 * Throws, as an operation of a storage that is full or blocked does.
 */
function failOnUse(): never {
  throw new Error("The storage is broken");
}

/**
 * Takes the local storage away, as in Node.js and in a browser that has none.
 */
function removeStorage(): void {
  vi.stubGlobal("localStorage", undefined);
}

/**
 * Makes every access to the local storage throw, as a browser does when it refuses the storage to a page.
 */
function refuseStorage(): void {
  vi.stubGlobal("localStorage", undefined);
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    get: () => {
      throw new Error("The storage is refused");
    },
  });
}

/**
 * Puts a storage in place whose three operations all throw, as a storage that is full or blocked does.
 */
function breakStorage(): void {
  vi.stubGlobal("localStorage", { getItem: failOnUse, setItem: failOnUse, removeItem: failOnUse });
}

beforeEach(() => {
  storage = createMemoryStorage();
  vi.stubGlobal("localStorage", storage);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("STORAGE_KEYS", () => {
  it("names the four keys of the device, each with its version", () => {
    expect(STORAGE_KEYS).toEqual({
      needs: "enableme.needs.v1",
      language: "enableme.language.v1",
      session: "enableme.session.v1",
      ownVotes: "enableme.ownVotes.v1",
    });
  });
});

describe("readStored", () => {
  it("reads a missing value as absent", () => {
    expect(readStored(STORAGE_KEYS.session, isText)).toBeNull();
  });

  it("returns a kept value that passes the check", () => {
    storage.setItem(STORAGE_KEYS.session, JSON.stringify("token-1"));

    expect(readStored(STORAGE_KEYS.session, isText)).toBe("token-1");
    expect(storage.getItem(STORAGE_KEYS.session)).toBe(JSON.stringify("token-1"));
  });

  it("returns a kept object that passes the check", () => {
    storage.setItem(STORAGE_KEYS.needs, JSON.stringify({ count: 3 }));

    expect(readStored(STORAGE_KEYS.needs, isCounter)).toEqual({ count: 3 });
  });

  it("reads a value that is not JSON as absent and removes it", () => {
    storage.setItem(STORAGE_KEYS.session, "{not json");

    expect(readStored(STORAGE_KEYS.session, isText)).toBeNull();
    expect(storage.getItem(STORAGE_KEYS.session)).toBeNull();
  });

  it("reads a value that fails the check as absent and removes it", () => {
    storage.setItem(STORAGE_KEYS.language, JSON.stringify("en"));

    expect(readStored(STORAGE_KEYS.language, isPolish)).toBeNull();
    expect(storage.getItem(STORAGE_KEYS.language)).toBeNull();
  });

  it("removes only the value of its own key", () => {
    storage.setItem(STORAGE_KEYS.language, JSON.stringify("en"));
    storage.setItem(STORAGE_KEYS.session, JSON.stringify("token-1"));

    readStored(STORAGE_KEYS.language, isPolish);

    expect(storage.getItem(STORAGE_KEYS.session)).toBe(JSON.stringify("token-1"));
  });

  it("reads every value as absent without a local storage", () => {
    removeStorage();

    expect(readStored(STORAGE_KEYS.session, isText)).toBeNull();
  });

  it("reads every value as absent when the browser refuses the storage", () => {
    refuseStorage();

    expect(readStored(STORAGE_KEYS.session, isText)).toBeNull();
  });

  it("reads every value as absent when the storage throws", () => {
    breakStorage();

    expect(readStored(STORAGE_KEYS.session, isText)).toBeNull();
  });
});

describe("writeStored", () => {
  it("keeps a value as JSON under its key", () => {
    writeStored(STORAGE_KEYS.language, "en");

    expect(storage.getItem(STORAGE_KEYS.language)).toBe('"en"');
  });

  it("keeps a value that readStored returns", () => {
    writeStored(STORAGE_KEYS.session, "token-1");

    expect(readStored(STORAGE_KEYS.session, isText)).toBe("token-1");
  });

  it("replaces the value kept before", () => {
    writeStored(STORAGE_KEYS.session, "token-1");
    writeStored(STORAGE_KEYS.session, "token-2");

    expect(readStored(STORAGE_KEYS.session, isText)).toBe("token-2");
  });

  it("does nothing without a local storage", () => {
    removeStorage();

    expect(() => writeStored(STORAGE_KEYS.session, "token-1")).not.toThrow();
  });

  it("does nothing when the browser refuses the storage", () => {
    refuseStorage();

    expect(() => writeStored(STORAGE_KEYS.session, "token-1")).not.toThrow();
  });

  it("ignores a storage that refuses the write", () => {
    breakStorage();

    expect(() => writeStored(STORAGE_KEYS.session, "token-1")).not.toThrow();
  });
});

describe("removeStored", () => {
  it("removes the value kept under a key", () => {
    writeStored(STORAGE_KEYS.session, "token-1");

    removeStored(STORAGE_KEYS.session);

    expect(storage.getItem(STORAGE_KEYS.session)).toBeNull();
    expect(readStored(STORAGE_KEYS.session, isText)).toBeNull();
  });

  it("leaves the values of the other keys", () => {
    writeStored(STORAGE_KEYS.session, "token-1");
    writeStored(STORAGE_KEYS.language, "pl");

    removeStored(STORAGE_KEYS.session);

    expect(readStored(STORAGE_KEYS.language, isPolish)).toBe("pl");
  });

  it("does nothing for a key without a value", () => {
    expect(() => removeStored(STORAGE_KEYS.session)).not.toThrow();
  });

  it("does nothing without a local storage", () => {
    removeStorage();

    expect(() => removeStored(STORAGE_KEYS.session)).not.toThrow();
  });

  it("does nothing when the browser refuses the storage", () => {
    refuseStorage();

    expect(() => removeStored(STORAGE_KEYS.session)).not.toThrow();
  });

  it("ignores a storage that refuses the removal", () => {
    breakStorage();

    expect(() => removeStored(STORAGE_KEYS.session)).not.toThrow();
  });
});

describe("isText", () => {
  it("accepts a text, the empty one included", () => {
    expect(isText("token-1")).toBe(true);
    expect(isText("")).toBe(true);
  });

  it("refuses every value that is not a text", () => {
    expect(isText(42)).toBe(false);
    expect(isText(null)).toBe(false);
    expect(isText(undefined)).toBe(false);
    expect(isText(["token-1"])).toBe(false);
    expect(isText({ token: "token-1" })).toBe(false);
  });
});
