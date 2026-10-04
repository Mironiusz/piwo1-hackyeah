import type { MapMarker } from "./mapScene.ts";

/**
 * The look of a marker of the map by what it stands for. A barrier is a filled red square, an amenity a green outline,
 * a report the map data contradict a dashed red outline, an outdated fact a grey outline, and an end of a route a ring.
 * The shape of the border and the icon inside carry the meaning next to the color.
 */
export const MARK_LOOKS: Record<MapMarker["look"], string> = {
  barrier: "rounded-[6px] border-2 border-white bg-barrier text-white",
  amenity: "rounded-[6px] border-2 border-clear bg-white text-clear",
  overruled: "rounded-[6px] border-2 border-dashed border-barrier bg-white text-barrier",
  outdated: "rounded-[6px] border-2 border-nodata bg-white text-nodata",
  end: "rounded-full border-2 border-ink bg-white text-ink",
};
