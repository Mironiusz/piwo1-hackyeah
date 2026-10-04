import type { Point } from "../api/types.ts";
import { isInsideKrakow } from "./krakowBounds.ts";

/**
 * Where a request for the location of the device stands: not asked, waiting for the browser, or ended with a message.
 */
export type LocationState = "idle" | "waiting" | "insecure" | "refused" | "failed" | "outside";

/**
 * The key of the text of each state that ends with a message.
 */
export const LOCATION_TEXTS: Record<Exclude<LocationState, "idle" | "waiting">, string> = {
  insecure: "plan.location_insecure",
  refused: "plan.location_refused",
  failed: "plan.location_failed",
  outside: "plan.outside",
};

const PERMISSION_DENIED = 1;

/**
 * Tells why the browser gave no location. A browser gives the location only to a page with a secure connection
 * and answers every other page as if the person had refused, so a refusal on a page without one is named as such.
 */
export function describeLocationFailure(code: number, isSecureContext: boolean): Exclude<LocationState, "idle" | "waiting" | "outside"> {
  if (!isSecureContext) {
    return "insecure";
  }
  return code === PERMISSION_DENIED ? "refused" : "failed";
}

/**
 * Reads the location of the device once, in the browser, and passes it on only when it lies inside Kraków.
 * Every step is told through the state, from waiting to the message that ends it, or idle once the point is passed on.
 */
export function readDeviceLocation(onPoint: (point: Point) => void, onState: (state: LocationState) => void): void {
  if (!window.isSecureContext) {
    onState("insecure");
    return;
  }
  if (!("geolocation" in navigator)) {
    onState("failed");
    return;
  }
  onState("waiting");
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const point = { lat: position.coords.latitude, lon: position.coords.longitude };
      if (!isInsideKrakow(point)) {
        onState("outside");
        return;
      }
      onState("idle");
      onPoint(point);
    },
    (failure) => onState(describeLocationFailure(failure.code, window.isSecureContext)),
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
  );
}
