import { createContext, useContext, useEffect } from "react";

import type { Point, Route } from "../api/types.ts";
import type { IconName } from "../parts/iconPaths.ts";

/**
 * A marker of the map. It is a button with a text name, so a screen reader can name what the map shows.
 */
export interface MapMarker {
  id: string;
  point: Point;
  look: "barrier" | "amenity" | "overruled" | "outdated" | "end";
  icon: IconName | null;
  text: string | null;
  label: string;
  isSelected: boolean;
  isPressable: boolean;
}

/**
 * The area of a fact that covers a circle: its center and its radius in metres.
 */
export interface MapZone {
  id: string;
  point: Point;
  radiusM: number;
  isMuted: boolean;
}

/**
 * A request to move the map. The map moves once for every new key.
 */
export interface MapCamera {
  key: string;
  target: { kind: "point"; point: Point; zoom: number | null } | { kind: "bounds"; southWest: Point; northEast: Point };
}

/**
 * Where the map stands once it has stopped moving.
 */
export interface MapRest {
  center: Point;
  zoom: number;
  southWest: Point;
  northEast: Point;
}

/**
 * Everything a view puts on the one map of the application.
 * The size of the map is normal unless a view asks for a short one, to leave room for a list, or a tall one; a map in the picking mode is tall.
 */
export interface MapScene {
  label: string;
  markers: MapMarker[];
  zones: MapZone[];
  route: Route | null;
  isRouteAssessed: boolean;
  isPicking: boolean;
  hasSampleData: boolean;
  camera: MapCamera | null;
  onMarkerPress: ((markerId: string) => void) | null;
  mapSize?: "short" | "normal" | "tall";
}

export const EMPTY_MAP_SCENE: MapScene = {
  label: "",
  markers: [],
  zones: [],
  route: null,
  isRouteAssessed: true,
  isPicking: false,
  hasSampleData: false,
  camera: null,
  onMarkerPress: null,
};

export interface MapSceneContextValue {
  setScene: (scene: MapScene) => void;
  rest: MapRest | null;
  readCenter: () => Point | null;
  hasFailed: boolean;
  topSlot: HTMLElement | null;
}

export const MapSceneContext = createContext<MapSceneContextValue | null>(null);

/**
 * Returns the state of the one map: where it rests, its center at this moment, and whether it could be drawn.
 */
export function useMap(): MapSceneContextValue {
  const value = useContext(MapSceneContext);
  if (value === null) {
    throw new Error("useMap is used outside the layout of the map views");
  }
  return value;
}

/**
 * Puts the scene of a view on the map. The scene has to keep its identity between renders that change nothing,
 * so a view builds it with useMemo.
 */
export function useMapScene(scene: MapScene): void {
  const { setScene } = useMap();
  useEffect(() => {
    setScene(scene);
  }, [scene, setScene]);
}
