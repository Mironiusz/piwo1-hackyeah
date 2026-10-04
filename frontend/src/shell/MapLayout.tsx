import { useCallback, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Outlet } from "react-router";

import { EMPTY_MAP_SCENE, MapSceneContext, type MapResize, type MapRest, type MapScene, type MapSceneContextValue, type MapSpan } from "../map/mapScene.ts";
import { MapView, type MapHandle } from "../map/MapView.tsx";
import { Note } from "../parts/Note.tsx";

const MAP_SIZES = {
  short: "h-[min(190px,30vh)]",
  normal: "h-[min(262px,40vh)]",
  tall: "h-[min(380px,42vh)]",
} as const;

type MapSize = keyof typeof MAP_SIZES;

const MAP_MIN_HEIGHT_PX = 120;
const PANEL_MIN_HEIGHT_PX = 140;

/**
 * The layout of the map views. It holds the one map of the application, which stays on the screen and keeps its position
 * while the views under it change, and hands the views the way to put their scene on it.
 * Above the map stands a slot a view can fill, and below it the panel of the view, which fills the rest of the screen.
 * The map has one of three fixed heights, so a list that grows under it never changes its size.
 * Each height is capped by a share of the height of the screen, so the actions of the panel stay on a short phone screen.
 * A person can drag the map to another height, between a low floor and the height that still leaves the top of the panel on the screen.
 * The dragged height holds while the views keep asking for the same size, and a view that asks for another size gets it again.
 */
export function MapLayout() {
  const { t } = useTranslation();
  const [scene, setScene] = useState<MapScene>(EMPTY_MAP_SCENE);
  const [rest, setRest] = useState<MapRest | null>(null);
  const [hasFailed, setHasFailed] = useState(false);
  const [topSlot, setTopSlot] = useState<HTMLElement | null>(null);
  const [dragged, setDragged] = useState<{ size: MapSize; height: number } | null>(null);
  const handle = useRef<MapHandle | null>(null);
  const mapSection = useRef<HTMLElement | null>(null);
  const size: MapSize = scene.isPicking ? "tall" : (scene.mapSize ?? "normal");
  const draggedHeight = dragged !== null && dragged.size === size ? dragged.height : null;

  const readCenter = useCallback(() => handle.current?.readCenter() ?? null, []);
  const keepHandle = useCallback((ready: MapHandle | null) => {
    handle.current = ready;
  }, []);
  const fail = useCallback(() => setHasFailed(true), []);
  const pressMarker = useCallback((markerId: string) => scene.onMarkerPress?.(markerId), [scene]);

  const readSpan = useCallback((): MapSpan | null => {
    const section = mapSection.current;
    const frame = section?.closest("main") ?? null;
    if (section === null || frame === null) {
      return null;
    }
    const sectionBox = section.getBoundingClientRect();
    const top = sectionBox.top - frame.getBoundingClientRect().top + frame.scrollTop;
    return { height: sectionBox.height, min: MAP_MIN_HEIGHT_PX, max: Math.max(MAP_MIN_HEIGHT_PX, frame.clientHeight - top - PANEL_MIN_HEIGHT_PX) };
  }, []);
  const setHeight = useCallback((height: number) => setDragged({ size, height }), [size]);
  const watchSpan = useCallback(
    (listener: (span: MapSpan) => void) => {
      const section = mapSection.current;
      if (section === null) {
        return () => undefined;
      }
      const tell = () => {
        const span = readSpan();
        if (span !== null) {
          listener(span);
        }
      };
      const observer = new ResizeObserver(tell);
      observer.observe(section);
      tell();
      return () => observer.disconnect();
    },
    [readSpan],
  );
  const resize = useMemo<MapResize | null>(() => (hasFailed ? null : { readSpan, setHeight, watchSpan }), [hasFailed, readSpan, setHeight, watchSpan]);

  const value = useMemo<MapSceneContextValue>(() => ({ setScene, rest, readCenter, hasFailed, topSlot, resize }), [rest, readCenter, hasFailed, topSlot, resize]);

  return (
    <MapSceneContext.Provider value={value}>
      <div className="flex flex-1 flex-col">
        <div ref={setTopSlot} className="flex-none empty:hidden" />
        {hasFailed ? (
          <div className="flex-none bg-surface px-4 pt-4 pb-6">
            <Note kind="strong" announce="alert">
              <p>{t("state.map_failed")}</p>
            </Note>
          </div>
        ) : (
          <section
            ref={mapSection}
            aria-label={scene.label}
            className={`relative z-0 flex-none bg-[#ecece3] ${MAP_SIZES[size]}`}
            style={draggedHeight !== null ? { height: draggedHeight } : undefined}
          >
            <div className="absolute inset-0">
              <MapView
                label={scene.label}
                markers={scene.markers}
                zones={scene.zones}
                route={scene.route}
                isRouteAssessed={scene.isRouteAssessed}
                isPicking={scene.isPicking}
                hasSampleData={scene.hasSampleData}
                camera={scene.camera}
                onReady={keepHandle}
                onMarkerPress={pressMarker}
                onRest={setRest}
                onFail={fail}
              />
            </div>
          </section>
        )}
        <Outlet />
      </div>
    </MapSceneContext.Provider>
  );
}
