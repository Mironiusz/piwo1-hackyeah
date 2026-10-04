import { describe, expect, it } from "vitest";

import { formatDay, formatDistance } from "./format.ts";

describe("formatDay", () => {
  it("writes a day in the Polish form", () => {
    expect(formatDay("2026-10-03", "pl")).toBe("3.10.2026");
  });

  it("writes a day in the English form", () => {
    expect(formatDay("2026-10-03", "en")).toBe("3 Oct 2026");
  });

  it("keeps the two digits of the month in Polish and names the month in English", () => {
    expect(formatDay("2025-05-12", "pl")).toBe("12.05.2025");
    expect(formatDay("2025-05-12", "en")).toBe("12 May 2025");
  });

  it("drops the leading zero of the day in both languages", () => {
    expect(formatDay("2026-01-09", "pl")).toBe("9.01.2026");
    expect(formatDay("2026-01-09", "en")).toBe("9 Jan 2026");
  });

  it.each([
    ["01", "Jan"],
    ["02", "Feb"],
    ["03", "Mar"],
    ["04", "Apr"],
    ["05", "May"],
    ["06", "Jun"],
    ["07", "Jul"],
    ["08", "Aug"],
    ["09", "Sep"],
    ["10", "Oct"],
    ["11", "Nov"],
    ["12", "Dec"],
  ])("names the month %s as %s in English", (month, name) => {
    expect(formatDay(`2026-${month}-15`, "en")).toBe(`15 ${name} 2026`);
  });

  it("reads the day at the start of an instant", () => {
    expect(formatDay("2026-10-04T09:12:44.120+02:00", "pl")).toBe("4.10.2026");
    expect(formatDay("2026-10-04T09:12:44.120+02:00", "en")).toBe("4 Oct 2026");
  });

  it("returns a text that is not a day unchanged", () => {
    expect(formatDay("yesterday", "pl")).toBe("yesterday");
    expect(formatDay("yesterday", "en")).toBe("yesterday");
    expect(formatDay("3.10.2026", "en")).toBe("3.10.2026");
    expect(formatDay("", "pl")).toBe("");
  });
});

describe("formatDay for an instant", () => {
  it("writes the day of an instant of the service and converts no time zone", () => {
    expect(formatDay("2026-10-05T00:00:00.000+02:00", "pl")).toBe("5.10.2026");
    expect(formatDay("2026-10-05T00:00:00.000+02:00", "en")).toBe("5 Oct 2026");
    expect(formatDay("2026-10-04T23:30:00.000-05:00", "en")).toBe("4 Oct 2026");
  });
});

describe("formatDistance", () => {
  it("writes a distance under 1000 m in metres, the same in both languages", () => {
    expect(formatDistance(400, "pl")).toBe("400 m");
    expect(formatDistance(400, "en")).toBe("400 m");
    expect(formatDistance(0, "pl")).toBe("0 m");
  });

  it("writes 999 m, the last distance in metres", () => {
    expect(formatDistance(999, "pl")).toBe("999 m");
    expect(formatDistance(999, "en")).toBe("999 m");
  });

  it("writes 1000 m, the first distance in kilometres, with one decimal place", () => {
    expect(formatDistance(1000, "pl")).toBe("1,0 km");
    expect(formatDistance(1000, "en")).toBe("1.0 km");
  });

  it("writes a distance over 1000 m with a comma in Polish and a point in English", () => {
    expect(formatDistance(1300, "pl")).toBe("1,3 km");
    expect(formatDistance(1300, "en")).toBe("1.3 km");
    expect(formatDistance(1840, "pl")).toBe("1,8 km");
    expect(formatDistance(12000, "en")).toBe("12.0 km");
  });

  it("rounds to whole metres before it picks the unit", () => {
    expect(formatDistance(999.4, "pl")).toBe("999 m");
    expect(formatDistance(999.6, "pl")).toBe("1,0 km");
    expect(formatDistance(999.6, "en")).toBe("1.0 km");
  });
});
