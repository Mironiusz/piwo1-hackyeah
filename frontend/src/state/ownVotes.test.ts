import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createMemoryStorage, type MemoryStorage } from "../testing/memoryStorage.ts";
import { canVoteNow, readOwnVote, saveOwnVote, startOfNextDay, toDeviceDay, toDeviceInstant } from "./ownVotes.ts";
import { STORAGE_KEYS } from "./storage.ts";

const INSTANT_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2}$/;
const REPEAT_ALLOWED_AT = "2026-10-05T09:12:44.120+02:00";

let storage: MemoryStorage;

/**
 * Builds the moment 4 October 2026, 9:05:07.008 on the clock of a device that lies the given minutes east of UTC.
 */
function buildMomentEastOfUtc(minutes: number): Date {
  const moment = new Date(2026, 9, 4, 9, 5, 7, 8);
  moment.getTimezoneOffset = () => -minutes;
  return moment;
}

beforeEach(() => {
  storage = createMemoryStorage();
  vi.stubGlobal("localStorage", storage);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("saveOwnVote and readOwnVote", () => {
  it("remembers no vote for a fact nobody voted on", () => {
    expect(readOwnVote(42)).toBeNull();
  });

  it("returns the vote that was saved for a fact", () => {
    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(readOwnVote(42)).toEqual({ verdict: "confirm", votedOn: "2026-10-04", repeatAllowedAt: REPEAT_ALLOWED_AT });
  });

  it("keeps the votes on different facts apart", () => {
    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);
    saveOwnVote(43, "deny", "2026-10-03", "2026-10-04T18:00:00.000+02:00");

    expect(readOwnVote(42)).toEqual({ verdict: "confirm", votedOn: "2026-10-04", repeatAllowedAt: REPEAT_ALLOWED_AT });
    expect(readOwnVote(43)).toEqual({ verdict: "deny", votedOn: "2026-10-03", repeatAllowedAt: "2026-10-04T18:00:00.000+02:00" });
    expect(readOwnVote(44)).toBeNull();
  });

  it("replaces the earlier vote on the same fact with the latest one", () => {
    saveOwnVote(42, "confirm", "2026-10-03", "2026-10-04T09:12:44.120+02:00");
    saveOwnVote(42, "deny", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(readOwnVote(42)).toEqual({ verdict: "deny", votedOn: "2026-10-04", repeatAllowedAt: REPEAT_ALLOWED_AT });
  });

  it("keeps the votes under their key, each under the identifier of its fact", () => {
    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(JSON.parse(storage.getItem(STORAGE_KEYS.ownVotes) ?? "null")).toEqual({
      "42": { verdict: "confirm", votedOn: "2026-10-04", repeatAllowedAt: REPEAT_ALLOWED_AT },
    });
  });

  it("reads a kept value of another form as no vote and removes it", () => {
    storage.setItem(STORAGE_KEYS.ownVotes, JSON.stringify({ "42": { verdict: "maybe", votedOn: "2026-10-04", repeatAllowedAt: REPEAT_ALLOWED_AT } }));

    expect(readOwnVote(42)).toBeNull();
    expect(storage.getItem(STORAGE_KEYS.ownVotes)).toBeNull();
  });

  it("remembers nothing without a local storage", () => {
    vi.stubGlobal("localStorage", undefined);

    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(readOwnVote(42)).toBeNull();
  });
});

describe("canVoteNow", () => {
  it("allows a vote on a fact without a remembered vote", () => {
    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(canVoteNow(43, new Date("2026-10-04T10:00:00.000+02:00"))).toBe(true);
  });

  it("refuses a vote before the instant from which the next one is accepted", () => {
    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(canVoteNow(42, new Date("2026-10-04T09:12:44.120+02:00"))).toBe(false);
    expect(canVoteNow(42, new Date("2026-10-05T09:12:44.119+02:00"))).toBe(false);
  });

  it("allows a vote at the instant from which the next one is accepted", () => {
    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(canVoteNow(42, new Date(REPEAT_ALLOWED_AT))).toBe(true);
  });

  it("allows a vote after that instant", () => {
    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(canVoteNow(42, new Date("2026-10-05T09:12:44.121+02:00"))).toBe(true);
    expect(canVoteNow(42, new Date("2026-10-06T00:00:00.000+02:00"))).toBe(true);
  });

  it("compares the two instants as moments, whatever offset each is written with", () => {
    saveOwnVote(42, "confirm", "2026-10-04", REPEAT_ALLOWED_AT);

    expect(canVoteNow(42, new Date("2026-10-05T07:12:44.119Z"))).toBe(false);
    expect(canVoteNow(42, new Date("2026-10-05T07:12:44.120Z"))).toBe(true);
  });

  it("allows a vote when the remembered instant cannot be read", () => {
    saveOwnVote(42, "confirm", "2026-10-04", "tomorrow");

    expect(canVoteNow(42, new Date("2026-10-04T10:00:00.000+02:00"))).toBe(true);
  });

  it("refuses a second vote until the next calendar day starts on the clock of the device", () => {
    const votedAt = new Date(2026, 9, 4, 9, 12, 44, 120);
    saveOwnVote(42, "deny", toDeviceDay(votedAt), startOfNextDay(votedAt));

    expect(canVoteNow(42, votedAt)).toBe(false);
    expect(canVoteNow(42, new Date(2026, 9, 4, 23, 59, 59, 999))).toBe(false);
    expect(canVoteNow(42, new Date(2026, 9, 5, 0, 0, 0, 0))).toBe(true);
  });
});

describe("toDeviceDay", () => {
  it("writes the calendar day of the device as YYYY-MM-DD", () => {
    expect(toDeviceDay(new Date(2026, 9, 4, 9, 5))).toBe("2026-10-04");
  });

  it("writes the month and the day with two digits", () => {
    expect(toDeviceDay(new Date(2026, 0, 9, 12, 0))).toBe("2026-01-09");
  });

  it("takes the day from the clock of the device at both ends of a day", () => {
    expect(toDeviceDay(new Date(2026, 9, 4, 0, 0, 0, 0))).toBe("2026-10-04");
    expect(toDeviceDay(new Date(2026, 9, 4, 23, 59, 59, 999))).toBe("2026-10-04");
  });
});

describe("toDeviceInstant", () => {
  it("writes the clock of the device with milliseconds and an offset east of UTC", () => {
    expect(toDeviceInstant(buildMomentEastOfUtc(120))).toBe("2026-10-04T09:05:07.008+02:00");
  });

  it("writes an offset west of UTC with its minutes", () => {
    expect(toDeviceInstant(buildMomentEastOfUtc(-210))).toBe("2026-10-04T09:05:07.008-03:30");
  });

  it("writes an offset east of UTC with its minutes", () => {
    expect(toDeviceInstant(buildMomentEastOfUtc(345))).toBe("2026-10-04T09:05:07.008+05:45");
  });

  it("writes the offset of UTC itself with a plus sign", () => {
    expect(toDeviceInstant(buildMomentEastOfUtc(0))).toBe("2026-10-04T09:05:07.008+00:00");
  });

  it("writes an instant that reads back as the same moment", () => {
    const moment = new Date(2026, 9, 4, 9, 5, 7, 8);
    const instant = toDeviceInstant(moment);

    expect(instant).toMatch(INSTANT_PATTERN);
    expect(Date.parse(instant)).toBe(moment.getTime());
  });

  it("reads back as the same moment in winter time and in summer time", () => {
    const winter = new Date(2026, 0, 15, 12, 0, 0, 0);
    const summer = new Date(2026, 6, 15, 12, 0, 0, 0);

    expect(Date.parse(toDeviceInstant(winter))).toBe(winter.getTime());
    expect(Date.parse(toDeviceInstant(summer))).toBe(summer.getTime());
  });
});

describe("startOfNextDay", () => {
  it("returns the instant at which the next calendar day starts on the clock of the device", () => {
    const moment = new Date(2026, 9, 4, 9, 12, 44, 120);
    const instant = startOfNextDay(moment);

    expect(instant).toMatch(INSTANT_PATTERN);
    expect(instant.startsWith("2026-10-05T00:00:00.000")).toBe(true);
    expect(Date.parse(instant)).toBe(new Date(2026, 9, 5).getTime());
  });

  it("goes over the end of a month and of a year", () => {
    expect(startOfNextDay(new Date(2026, 9, 31, 23, 59)).startsWith("2026-11-01T00:00:00.000")).toBe(true);
    expect(startOfNextDay(new Date(2026, 11, 31, 12, 0)).startsWith("2027-01-01T00:00:00.000")).toBe(true);
  });

  it("returns the same instant for every moment of one day", () => {
    expect(startOfNextDay(new Date(2026, 9, 4, 0, 0, 0, 0))).toBe(startOfNextDay(new Date(2026, 9, 4, 23, 59, 59, 999)));
  });

  it("leaves the given moment as it was", () => {
    const moment = new Date(2026, 9, 4, 9, 12, 44, 120);
    const before = moment.getTime();

    startOfNextDay(moment);

    expect(moment.getTime()).toBe(before);
  });
});
