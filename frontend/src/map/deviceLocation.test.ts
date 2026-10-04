import { afterEach, describe, expect, it, vi } from "vitest";

import { describeLocationFailure, readDeviceLocation, type LocationState } from "./deviceLocation.ts";

const PERMISSION_DENIED = 1;
const POSITION_UNAVAILABLE = 2;
const TIMEOUT = 3;
const IN_KRAKOW = { lat: 50.0678, lon: 19.9914 };
const IN_WARSAW = { lat: 52.2297, lon: 21.0122 };

/**
 * Puts a stand-in of the browser in place: whether the page has a secure connection, and a location service
 * that answers with a point or with an error code, or no location service at all.
 */
function stubBrowser(isSecureContext: boolean, answer: { point: { lat: number; lon: number } } | { code: number } | null): void {
  vi.stubGlobal("window", { isSecureContext });
  if (answer === null) {
    vi.stubGlobal("navigator", {});
    return;
  }
  const getCurrentPosition = (onSuccess: (position: unknown) => void, onError: (failure: unknown) => void) => {
    if ("point" in answer) {
      onSuccess({ coords: { latitude: answer.point.lat, longitude: answer.point.lon } });
      return;
    }
    onError({ code: answer.code });
  };
  vi.stubGlobal("navigator", { geolocation: { getCurrentPosition } });
}

/**
 * Reads the location with the stand-in and returns the states it went through and the point it passed on.
 */
function read(): { states: LocationState[]; points: { lat: number; lon: number }[] } {
  const states: LocationState[] = [];
  const points: { lat: number; lon: number }[] = [];
  readDeviceLocation(
    (point) => points.push(point),
    (state) => states.push(state),
  );
  return { states, points };
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("describeLocationFailure", () => {
  it("names a refusal on a page with a secure connection as refused", () => {
    expect(describeLocationFailure(PERMISSION_DENIED, true)).toBe("refused");
  });

  it("names an unavailable position and a timeout as failed", () => {
    expect(describeLocationFailure(POSITION_UNAVAILABLE, true)).toBe("failed");
    expect(describeLocationFailure(TIMEOUT, true)).toBe("failed");
  });

  it("names every failure on a page without a secure connection as insecure", () => {
    expect(describeLocationFailure(PERMISSION_DENIED, false)).toBe("insecure");
    expect(describeLocationFailure(POSITION_UNAVAILABLE, false)).toBe("insecure");
  });
});

describe("readDeviceLocation", () => {
  it("passes on a point inside Kraków and ends idle", () => {
    stubBrowser(true, { point: IN_KRAKOW });
    expect(read()).toEqual({ states: ["waiting", "idle"], points: [IN_KRAKOW] });
  });

  it("passes on no point outside Kraków", () => {
    stubBrowser(true, { point: IN_WARSAW });
    expect(read()).toEqual({ states: ["waiting", "outside"], points: [] });
  });

  it("does not ask the browser on a page without a secure connection", () => {
    stubBrowser(false, { point: IN_KRAKOW });
    expect(read()).toEqual({ states: ["insecure"], points: [] });
  });

  it("tells a refusal", () => {
    stubBrowser(true, { code: PERMISSION_DENIED });
    expect(read()).toEqual({ states: ["waiting", "refused"], points: [] });
  });

  it("fails when the browser has no location service", () => {
    stubBrowser(true, null);
    expect(read()).toEqual({ states: ["failed"], points: [] });
  });
});
