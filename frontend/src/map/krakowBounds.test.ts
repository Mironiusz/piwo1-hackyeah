import { describe, expect, it } from "vitest";

import { FACTS_MIN_ZOOM, INITIAL_MAP_VIEW, isInsideKrakow, KRAKOW_BOUNDS } from "./krakowBounds.ts";

const SOUTH = 49.9676668;
const NORTH = 50.1261338;
const WEST = 19.7922355;
const EAST = 20.2173455;
const MIDDLE = { lat: 50.05, lon: 20.0 };
const STEP = 0.0000001;

describe("KRAKOW_BOUNDS", () => {
  it("holds the bounds of the tile archive of Kraków", () => {
    expect(KRAKOW_BOUNDS).toEqual({ southWest: { lat: SOUTH, lon: WEST }, northEast: { lat: NORTH, lon: EAST } });
  });
});

describe("isInsideKrakow", () => {
  it("finds a point in the middle of Kraków inside", () => {
    expect(isInsideKrakow(MIDDLE)).toBe(true);
    expect(isInsideKrakow({ lat: 50.0678, lon: 19.9914 })).toBe(true);
  });

  it.each([
    ["southern", { lat: SOUTH, lon: MIDDLE.lon }],
    ["northern", { lat: NORTH, lon: MIDDLE.lon }],
    ["western", { lat: MIDDLE.lat, lon: WEST }],
    ["eastern", { lat: MIDDLE.lat, lon: EAST }],
  ])("finds a point on the %s border inside", (_name, point) => {
    expect(isInsideKrakow(point)).toBe(true);
  });

  it("finds the four corners inside", () => {
    expect(isInsideKrakow({ lat: SOUTH, lon: WEST })).toBe(true);
    expect(isInsideKrakow({ lat: SOUTH, lon: EAST })).toBe(true);
    expect(isInsideKrakow({ lat: NORTH, lon: WEST })).toBe(true);
    expect(isInsideKrakow({ lat: NORTH, lon: EAST })).toBe(true);
  });

  it.each([
    ["south", { lat: SOUTH - STEP, lon: MIDDLE.lon }],
    ["north", { lat: NORTH + STEP, lon: MIDDLE.lon }],
    ["west", { lat: MIDDLE.lat, lon: WEST - STEP }],
    ["east", { lat: MIDDLE.lat, lon: EAST + STEP }],
  ])("finds a point just %s of the bounds outside", (_name, point) => {
    expect(isInsideKrakow(point)).toBe(false);
  });

  it("finds a point outside when only one of its two coordinates is within the bounds", () => {
    expect(isInsideKrakow({ lat: 52.2297, lon: MIDDLE.lon })).toBe(false);
    expect(isInsideKrakow({ lat: MIDDLE.lat, lon: 21.0122 })).toBe(false);
  });

  it("finds another city outside", () => {
    expect(isInsideKrakow({ lat: 52.2297, lon: 21.0122 })).toBe(false);
    expect(isInsideKrakow({ lat: 49.2992, lon: 19.9496 })).toBe(false);
  });

  it("finds a point with its two coordinates swapped outside", () => {
    expect(isInsideKrakow({ lat: MIDDLE.lon, lon: MIDDLE.lat })).toBe(false);
  });
});

describe("INITIAL_MAP_VIEW", () => {
  it("opens the map on a place inside Kraków", () => {
    expect(isInsideKrakow(INITIAL_MAP_VIEW.center)).toBe(true);
  });

  it("opens the map at a zoom at which the map of facts asks for facts", () => {
    expect(INITIAL_MAP_VIEW.zoom).toBeGreaterThanOrEqual(FACTS_MIN_ZOOM);
  });
});

describe("FACTS_MIN_ZOOM", () => {
  it("is the zoom 14 the plan sets for asking for facts", () => {
    expect(FACTS_MIN_ZOOM).toBe(14);
  });
});
