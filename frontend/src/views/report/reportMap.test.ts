import { afterEach, describe, expect, it, vi } from "vitest";

import { buildMoveCamera, buildPointCamera, buildPointMarker, buildReportMarker, buildReportZone, buildZoneCamera, findZoneZoom, focusMap, isSamePlace } from "./reportMap.ts";

const POINT = { lat: 50.0661, lon: 19.9878 };
const EQUATOR_METRES_PER_PIXEL_AT_ZOOM_0 = 40_075_016.686 / 512;

/**
 * Returns how many pixels across the circle of a radius is on the map at a zoom, at the latitude of the test point.
 */
function measureDiameterInPixels(radiusM: number, zoom: number): number {
  const metresPerPixel = (EQUATOR_METRES_PER_PIXEL_AT_ZOOM_0 * Math.cos((POINT.lat * Math.PI) / 180)) / 2 ** zoom;
  return (2 * radiusM) / metresPerPixel;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("buildPointMarker and buildReportMarker", () => {
  it("builds the marker of the point as a named mark that cannot be pressed", () => {
    expect(buildPointMarker(POINT, "Point of the report")).toEqual({
      id: "report-point",
      point: POINT,
      look: "end",
      icon: "pin",
      text: null,
      label: "Point of the report",
      isSelected: false,
      isPressable: false,
    });
  });

  it("draws a barrier with the icon of its type in the look of a barrier", () => {
    const marker = buildReportMarker("barrier", "stairs", POINT, "Stairs");

    expect(marker.look).toBe("barrier");
    expect(marker.icon).toBe("stairs");
    expect(marker.label).toBe("Stairs");
    expect(marker.isPressable).toBe(false);
  });

  it("draws an amenity in the look of an amenity", () => {
    const marker = buildReportMarker("amenity", "ramp", POINT, "Ramp");

    expect(marker.look).toBe("amenity");
    expect(marker.icon).toBe("ramp");
  });

  it("draws an area with the icon of an area in the look of a barrier", () => {
    const marker = buildReportMarker("area", "poor_surface", POINT, "Area");

    expect(marker.look).toBe("barrier");
    expect(marker.icon).toBe("area");
  });
});

describe("buildReportZone", () => {
  it("builds the circle of the area around its point", () => {
    expect(buildReportZone(POINT, 25)).toEqual({ id: "report-zone", point: POINT, radiusM: 25, isMuted: false });
  });
});

describe("findZoneZoom", () => {
  it.each([25, 50, 100])("shows the circle of %s m 150 pixels across", (radiusM) => {
    expect(measureDiameterInPixels(radiusM, findZoneZoom(POINT, radiusM))).toBeCloseTo(150, 6);
  });

  it("stops at the zoom 18 for the smallest radius, where the circle is smaller than 150 pixels", () => {
    expect(findZoneZoom(POINT, 10)).toBe(18);
    expect(measureDiameterInPixels(10, 18)).toBeLessThan(150);
    expect(measureDiameterInPixels(10, 18)).toBeGreaterThan(90);
  });

  it("zooms out by one level for a radius twice as large", () => {
    expect(findZoneZoom(POINT, 50) - findZoneZoom(POINT, 100)).toBeCloseTo(1, 10);
  });
});

describe("buildPointCamera and buildZoneCamera", () => {
  it("names the step and the point in the key, so the same step with the same point asks for no second move", () => {
    const first = buildPointCamera("details", POINT, null);
    const second = buildPointCamera("details", POINT, null);

    expect(first.key).toBe(second.key);
    expect(first.target).toEqual({ kind: "point", point: POINT, zoom: null });
  });

  it("gives another step and another point another key", () => {
    const key = buildPointCamera("details", POINT, null).key;

    expect(buildPointCamera("summary", POINT, null).key).not.toBe(key);
    expect(buildPointCamera("details", { lat: POINT.lat, lon: POINT.lon + 0.001 }, null).key).not.toBe(key);
  });

  it("passes the zoom a step asks for", () => {
    expect(buildPointCamera("existing", POINT, 18).target).toEqual({ kind: "point", point: POINT, zoom: 18 });
  });

  it("shows the area at the zoom of its radius, with a key that changes with the radius", () => {
    const camera = buildZoneCamera("details", POINT, 25);

    expect(camera.target).toEqual({ kind: "point", point: POINT, zoom: findZoneZoom(POINT, 25) });
    expect(buildZoneCamera("details", POINT, 50).key).not.toBe(camera.key);
    expect(buildZoneCamera("details", POINT, 25).key).toBe(camera.key);
  });
});

describe("buildMoveCamera", () => {
  it("moves the map to the place at a close zoom", () => {
    expect(buildMoveCamera(POINT).target).toEqual({ kind: "point", point: POINT, zoom: 17 });
  });

  it("gives every request a new key, also for the same place", () => {
    expect(buildMoveCamera(POINT).key).not.toBe(buildMoveCamera(POINT).key);
  });
});

describe("isSamePlace", () => {
  it("takes a point and itself, and two points less than a metre apart, for the same place", () => {
    expect(isSamePlace(POINT, POINT)).toBe(true);
    expect(isSamePlace(POINT, { lat: POINT.lat + 0.000004, lon: POINT.lon - 0.000004 })).toBe(true);
  });

  it("tells two points some metres apart from each other", () => {
    expect(isSamePlace(POINT, { lat: POINT.lat + 0.0001, lon: POINT.lon })).toBe(false);
    expect(isSamePlace(POINT, { lat: POINT.lat, lon: POINT.lon - 0.0001 })).toBe(false);
  });
});

describe("focusMap", () => {
  it("moves the focus to the canvas of the map", () => {
    const focus = vi.fn();
    const querySelector = vi.fn(() => ({ focus }));
    vi.stubGlobal("document", { querySelector });

    focusMap();

    expect(querySelector).toHaveBeenCalledWith(".maplibregl-canvas");
    expect(focus).toHaveBeenCalledTimes(1);
  });

  it("does nothing where no map is drawn", () => {
    vi.stubGlobal("document", { querySelector: () => null });

    expect(() => focusMap()).not.toThrow();
  });
});
