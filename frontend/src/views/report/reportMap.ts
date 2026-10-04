import type { FactType, Point } from "../../api/types.ts";
import type { MapCamera, MapMarker, MapZone } from "../../map/mapScene.ts";
import { findFactIcon } from "../../parts/iconPaths.ts";
import type { ReportKind } from "../../state/reportDraft.tsx";

const EQUATOR_METRES_PER_PIXEL_AT_ZOOM_0 = 40_075_016.686 / 512;
const ZONE_DIAMETER_PIXELS = 150;
const ZONE_MAX_ZOOM = 18;
const SAME_PLACE_DEGREES = 0.00001;
const MOVE_ZOOM = 17;
const REPORT_MARKER_ID = "report-point";

/**
 * The zoom at which the summary and the saved state show the point of a report: close enough to tell the place,
 * and wide enough to show the streets around it.
 */
export const REPORT_POINT_ZOOM = 17;

let lastMoveNumber = 0;

/**
 * Builds the marker of the point a person set for a report, before the report has a type.
 */
export function buildPointMarker(point: Point, label: string): MapMarker {
  return { id: REPORT_MARKER_ID, point, look: "end", icon: "pin", text: null, label, isSelected: false, isPressable: false };
}

/**
 * Builds the marker of a report that is not saved yet: the icon of its type, or of an area, in the look of its kind.
 */
export function buildReportMarker(kind: ReportKind, type: FactType, point: Point, label: string): MapMarker {
  return { id: REPORT_MARKER_ID, point, look: kind === "amenity" ? "amenity" : "barrier", icon: findFactIcon(type, kind === "area"), text: null, label, isSelected: false, isPressable: false };
}

/**
 * Builds the circle of an area a person reports.
 */
export function buildReportZone(point: Point, radiusM: number): MapZone {
  return { id: "report-zone", point, radiusM, isMuted: false };
}

/**
 * Returns the zoom at which the circle of an area is 150 pixels across, which fits the shortest map of the flow,
 * and at most the zoom 18 for the smallest radius. The zoom depends on the radius alone and not on the size of the map,
 * so it is right also while the map is changing its height between two steps.
 */
export function findZoneZoom(point: Point, radiusM: number): number {
  const metresPerPixel = (2 * radiusM) / ZONE_DIAMETER_PIXELS;
  const metresPerPixelAtZoom0 = EQUATOR_METRES_PER_PIXEL_AT_ZOOM_0 * Math.cos((point.lat * Math.PI) / 180);
  return Math.min(Math.log2(metresPerPixelAtZoom0 / metresPerPixel), ZONE_MAX_ZOOM);
}

/**
 * Builds the request that shows the point of a report in a step. The key names the step and the point,
 * so the map moves when a step opens and not again while the step only draws itself anew.
 */
export function buildPointCamera(step: string, point: Point, zoom: number | null): MapCamera {
  return { key: `report-${step}-${point.lat},${point.lon}`, target: { kind: "point", point, zoom } };
}

/**
 * Builds the request that shows the whole area of a report in the map of a step. The key names the radius too,
 * so the map moves again when the person picks another radius.
 */
export function buildZoneCamera(step: string, point: Point, radiusM: number): MapCamera {
  return { key: `report-${step}-${point.lat},${point.lon}-${radiusM}`, target: { kind: "point", point, zoom: findZoneZoom(point, radiusM) } };
}

/**
 * Builds the request that moves the map to a place a person asked for, the location of the device or a search result.
 * Every request has a new key, so asking for the same place twice moves the map twice.
 */
export function buildMoveCamera(point: Point): MapCamera {
  lastMoveNumber += 1;
  return { key: `report-move-${lastMoveNumber}`, target: { kind: "point", point, zoom: MOVE_ZOOM } };
}

/**
 * Tells whether two points are the same place for the eye, within about a metre.
 */
export function isSamePlace(first: Point, second: Point): boolean {
  return Math.abs(first.lat - second.lat) < SAME_PLACE_DEGREES && Math.abs(first.lon - second.lon) < SAME_PLACE_DEGREES;
}
