import type { FactType } from "../api/types.ts";

/**
 * One drawn part of an icon on the 24 by 24 grid of the mocks: a path, a circle or a rectangle.
 */
export type IconShape =
  | { kind: "path"; d: string }
  | { kind: "circle"; cx: number; cy: number; r: number; dash?: string }
  | { kind: "rect"; x: number; y: number; width: number; height: number; rx: number };

/**
 * Builds the list of shapes of an icon that is one path.
 */
function path(d: string): IconShape[] {
  return [{ kind: "path", d }];
}

/**
 * The icons of the interface, taken from the mocks in .impeccable/briefs/views/. Every icon is a line drawing without a fill.
 */
export const ICON_PATHS = {
  stairs: path("M4 20h4v-4h4v-4h4V8h4"),
  high_kerb: path("M3 18h9V10h9"),
  poor_surface: path("M3 15c2-3 4-3 6 0s4 3 6 0 4-3 6 0M3 20h18"),
  steep_incline: path("M3 19 21 8v11z"),
  narrow_passage: path("M8 4v16M16 4v16M3 12h3M18 12h3"),
  elevator: [
    { kind: "rect", x: 5, y: 3, width: 14, height: 18, rx: 1.5 },
    { kind: "path", d: "M9.5 10 12 7.5 14.5 10M9.5 14 12 16.5 14.5 14" },
  ],
  ramp: path("M3 19h18M5 19 19 11v8"),
  lowered_kerb: path("M3 17h7l4-4h7"),
  accessible_toilet: path("M6 4v8a4 4 0 0 0 4 4h4a4 4 0 0 0 4-4v-1H6M9 16v4h6v-4"),
  rest_place: path("M4 11h16M4 15h16M6 15v4M18 15v4M6 7v4M18 7v4"),
  handrail_at_stairs: path("M4 20h4v-4h4v-4h4V8h4M4 12l14-8"),
  area: [
    { kind: "circle", cx: 12, cy: 12, r: 8, dash: "4 3" },
    { kind: "circle", cx: 12, cy: 12, r: 1.5 },
  ],
  menu: path("M4 7h16M4 12h16M4 17h16"),
  close: path("M6 6l12 12M18 6 6 18"),
  chevron: path("M9 6l6 6-6 6"),
  back: path("M15 6l-6 6 6 6"),
  search: [
    { kind: "circle", cx: 11, cy: 11, r: 6.5 },
    { kind: "path", d: "M16 16l4.5 4.5" },
  ],
  map: path("M3 6.5 9 4l6 2.5L21 4v13.5L15 20l-6-2.5L3 20zM9 4v13.5M15 6.5V20"),
  report: path("M6 21V4M6 5h11l-2 4 2 4H6"),
  needs: [
    { kind: "path", d: "M4 7h9M17 7h3M4 17h3M11 17h9" },
    { kind: "circle", cx: 15, cy: 7, r: 2 },
    { kind: "circle", cx: 9, cy: 17, r: 2 },
  ],
  account: [
    { kind: "circle", cx: 12, cy: 8, r: 3.5 },
    { kind: "path", d: "M5 20a7 7 0 0 1 14 0" },
  ],
  language: [
    { kind: "circle", cx: 12, cy: 12, r: 8.5 },
    { kind: "path", d: "M3.5 12h17M12 3.5c3 3 3 14 0 17M12 3.5c-3 3-3 14 0 17" },
  ],
  privacy: [
    { kind: "rect", x: 5, y: 10, width: 14, height: 10, rx: 2 },
    { kind: "path", d: "M8 10V7a4 4 0 0 1 8 0v3" },
  ],
  info: [
    { kind: "circle", cx: 12, cy: 12, r: 8.5 },
    { kind: "path", d: "M12 11v6M12 7.5v.01" },
  ],
  moderation: path("M12 3 5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6z"),
  status_confirmed: path("M5 12.5l4.5 4.5L19 7.5"),
  status_unverified: [
    { kind: "circle", cx: 12, cy: 12, r: 8, dash: "3 3" },
    { kind: "path", d: "M12 8v5M12 16.5v.01" },
  ],
  status_disputed: path("M4 9h13M13 5l4 4-4 4M20 15H7M11 11l-4 4 4 4"),
  status_outdated: [
    { kind: "circle", cx: 12, cy: 12, r: 8 },
    { kind: "path", d: "M6.5 17.5 17.5 6.5" },
  ],
  preset_wheelchair: [
    { kind: "circle", cx: 10, cy: 5, r: 1.6 },
    { kind: "path", d: "M10 8v6h5l2.5 5M10 11h4M7 12a5 5 0 1 0 6.5 6.5" },
  ],
  preset_stroller: [
    { kind: "circle", cx: 8, cy: 19, r: 2 },
    { kind: "circle", cx: 17, cy: 19, r: 2 },
    { kind: "path", d: "M4 5h2l3 9h9a6 6 0 0 0-6-6H7.5" },
  ],
  preset_walking: [
    { kind: "circle", cx: 11, cy: 4.5, r: 1.6 },
    { kind: "path", d: "M11 8v6l-2.5 6M11 14l3 6M11 9.5l4 2.5M18 12v8" },
  ],
  location: [
    { kind: "circle", cx: 12, cy: 12, r: 3 },
    { kind: "path", d: "M12 2.5v4M12 17.5v4M2.5 12h4M17.5 12h4" },
  ],
  pin: [
    { kind: "path", d: "M12 21s6.5-6 6.5-11a6.5 6.5 0 0 0-13 0c0 5 6.5 11 6.5 11z" },
    { kind: "circle", cx: 12, cy: 10, r: 2.2 },
  ],
  cross: path("M12 3v7M12 14v7M3 12h7M14 12h7"),
} satisfies Record<string, IconShape[]>;

export type IconName = keyof typeof ICON_PATHS;

/**
 * Returns the icon of a fact: the one of its type, or the one of an area for a fact that covers a circle.
 */
export function findFactIcon(type: FactType, isArea: boolean): IconName {
  return isArea ? "area" : type;
}
