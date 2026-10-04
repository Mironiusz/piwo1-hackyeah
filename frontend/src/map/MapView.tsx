import { addProtocol, AttributionControl, Map as MapLibreMap, Marker, NavigationControl, setWorkerUrl, type LayerSpecification, type StyleSpecification } from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import { Protocol } from "pmtiles";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";

import type { Point, Route } from "../api/types.ts";
import { useLanguage } from "../i18n/index.ts";
import { Icon } from "../parts/Icon.tsx";
import { INITIAL_MAP_VIEW, KRAKOW_BOUNDS } from "./krakowBounds.ts";
import { loadBaseMapStyle } from "./loadBaseMapStyle.ts";
import type { MapCamera, MapMarker, MapRest, MapZone } from "./mapScene.ts";
import { MARK_LOOKS } from "./markLooks.ts";
import { buildRouteLayers, ROUTE_COLORS, ROUTE_SOURCE_ID } from "./routeLayers.ts";

const ZONES_SOURCE_ID = "zones";
const REST_DELAY_MILLISECONDS = 300;
const BOUNDS_MARGIN_DEGREES = 0.05;
const CIRCLE_STEPS = 48;
const METRES_PER_DEGREE = 111_320;
const SELECTED_MARKER_CLASS = "z-[2]";

const EMPTY_STYLE: StyleSpecification = { version: 8, sources: {}, layers: [] };

let isMapLibraryReady = false;

/**
 * Prepares the map library once for the page: the worker script from the host of the page
 * and the protocol that reads tiles out of the one archive with byte range requests.
 */
function prepareMapLibrary(): void {
  if (isMapLibraryReady) {
    return;
  }
  setWorkerUrl(workerUrl);
  addProtocol("pmtiles", new Protocol().tile);
  isMapLibraryReady = true;
}

/**
 * Returns the outline of a circle of a radius in metres around a point, as a closed ring of longitude and latitude pairs.
 */
function buildCircle(point: Point, radiusM: number): [number, number][] {
  const latitudeRadius = radiusM / METRES_PER_DEGREE;
  const longitudeRadius = latitudeRadius / Math.cos((point.lat * Math.PI) / 180);
  const ring: [number, number][] = [];
  for (let step = 0; step <= CIRCLE_STEPS; step += 1) {
    const angle = (step / CIRCLE_STEPS) * 2 * Math.PI;
    ring.push([point.lon + longitudeRadius * Math.cos(angle), point.lat + latitudeRadius * Math.sin(angle)]);
  }
  return ring;
}

/**
 * Puts the areas and the route of a view into the style of the base map, under its first label layer,
 * so the names of the streets stay readable over them.
 */
function composeStyle(base: StyleSpecification, zones: MapZone[], route: Route | null, isRouteAssessed: boolean): StyleSpecification {
  const sources: StyleSpecification["sources"] = {
    ...base.sources,
    [ZONES_SOURCE_ID]: {
      type: "geojson",
      data: {
        type: "FeatureCollection",
        features: zones.map((zone) => ({
          type: "Feature",
          properties: { isMuted: zone.isMuted },
          geometry: { type: "Polygon", coordinates: [buildCircle(zone.point, zone.radiusM)] },
        })),
      },
    },
  };
  const overlays: LayerSpecification[] = [
    {
      id: "zones-fill",
      type: "fill",
      source: ZONES_SOURCE_ID,
      paint: { "fill-color": ["case", ["get", "isMuted"], ROUTE_COLORS.no_data, ROUTE_COLORS.barrier], "fill-opacity": 0.12 },
    },
    {
      id: "zones-outline",
      type: "line",
      source: ZONES_SOURCE_ID,
      paint: { "line-color": ["case", ["get", "isMuted"], ROUTE_COLORS.no_data, ROUTE_COLORS.barrier], "line-width": 2, "line-dasharray": [3, 2] },
    },
  ];
  if (route !== null) {
    const routeLayers = buildRouteLayers(route, isRouteAssessed);
    sources[ROUTE_SOURCE_ID] = routeLayers.source;
    overlays.push(...routeLayers.layers);
  }
  const firstLabel = base.layers.findIndex((layer) => layer.type === "symbol");
  const at = firstLabel === -1 ? base.layers.length : firstLabel;
  return { ...base, sources, layers: [...base.layers.slice(0, at), ...overlays, ...base.layers.slice(at)] };
}

/**
 * Moves the map to the place a view asked for: to a point, or so that a rectangle fits.
 * Without animation the map stands there at once.
 */
function moveCamera(map: MapLibreMap, camera: MapCamera, isAnimated: boolean): void {
  if (camera.target.kind === "point") {
    map.easeTo({ center: [camera.target.point.lon, camera.target.point.lat], zoom: camera.target.zoom ?? Math.max(map.getZoom(), 16), animate: isAnimated });
    return;
  }
  map.fitBounds(
    [
      [camera.target.southWest.lon, camera.target.southWest.lat],
      [camera.target.northEast.lon, camera.target.northEast.lat],
    ],
    { padding: 44, maxZoom: 17, animate: isAnimated },
  );
}

/**
 * One marker of the map: a button with a text name for a fact, and a named mark for an end of the route.
 * A marker is left out of the order of the Tab key, because the panel under the map lists the same facts as buttons.
 */
function MapMark({ marker, onPress }: { marker: MapMarker; onPress: (markerId: string) => void }) {
  const mark = (
    <span
      aria-hidden="true"
      className={`flex size-[26px] items-center justify-center shadow-[0_1px_3px_rgba(17,20,24,0.35)] ${MARK_LOOKS[marker.look]} ${marker.isSelected ? "outline-[3px] outline-ink" : ""}`}
    >
      {marker.icon !== null ? <Icon name={marker.icon} size={17} /> : null}
      {marker.text !== null ? <span className="text-[12px] leading-none font-bold">{marker.text}</span> : null}
    </span>
  );
  if (!marker.isPressable) {
    return (
      <span className="flex size-[26px] items-center justify-center">
        <span className="sr-only">{marker.label}</span>
        {mark}
      </span>
    );
  }
  return (
    <button
      type="button"
      tabIndex={-1}
      aria-label={marker.label}
      aria-pressed={marker.isSelected}
      onClick={() => onPress(marker.id)}
      className="flex size-10 items-center justify-center rounded-panel"
    >
      {mark}
    </button>
  );
}

export interface MapHandle {
  readCenter: () => Point;
}

interface MapViewProps {
  label: string;
  markers: MapMarker[];
  zones: MapZone[];
  route: Route | null;
  isRouteAssessed: boolean;
  isPicking: boolean;
  hasSampleData: boolean;
  camera: MapCamera | null;
  onReady: (handle: MapHandle | null) => void;
  onMarkerPress: (markerId: string) => void;
  onRest: (rest: MapRest) => void;
  onFail: () => void;
}

/**
 * The one map of the application, drawn from the tile archive of the host of the page.
 * It takes the markers, the areas, the route and the picking mode of the view on the screen,
 * tells when a marker is pressed, and tells where it rests 0.3 seconds after it stopped moving and never while it moves.
 * When the size of the map changes, the map goes back to the place the view asked for, unless the person has moved it since:
 * a move that was still running would otherwise end at the center of the old size.
 * It tells that the map failed when the map cannot be created, when its style does not load and when the tile archive cannot be read.
 * An error of one tile or of a font is passed over, because the rest of the map is still drawn.
 */
export function MapView({ label, markers, zones, route, isRouteAssessed, isPicking, hasSampleData, camera, onReady, onMarkerPress, onRest, onFail }: MapViewProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  const [map, setMap] = useState<MapLibreMap | null>(null);
  const [baseStyle, setBaseStyle] = useState<StyleSpecification | null>(null);
  const [mounts, setMounts] = useState<Record<string, HTMLElement>>({});
  const drawnMarkers = useRef(new Map<string, Marker>());
  const appliedCamera = useRef<string | null>(null);
  const liveCamera = useRef<MapCamera | null>(null);
  const latest = useRef({ onReady, onRest, onFail });

  useEffect(() => {
    latest.current = { onReady, onRest, onFail };
  });

  const markerIds = new Set(markers.map((marker) => marker.id));
  if (Object.keys(mounts).length !== markerIds.size || [...markerIds].some((id) => mounts[id] === undefined)) {
    const next: Record<string, HTMLElement> = {};
    for (const id of markerIds) {
      next[id] = mounts[id] ?? document.createElement("div");
    }
    setMounts(next);
  }

  const attach = useCallback((element: HTMLDivElement | null) => {
    if (element === null) {
      return undefined;
    }
    const drawn = drawnMarkers.current;
    let created: MapLibreMap;
    try {
      prepareMapLibrary();
      created = new MapLibreMap({
        container: element,
        style: EMPTY_STYLE,
        center: [INITIAL_MAP_VIEW.center.lon, INITIAL_MAP_VIEW.center.lat],
        zoom: INITIAL_MAP_VIEW.zoom,
        minZoom: 9,
        maxZoom: 19,
        maxBounds: [
          [KRAKOW_BOUNDS.southWest.lon - BOUNDS_MARGIN_DEGREES, KRAKOW_BOUNDS.southWest.lat - BOUNDS_MARGIN_DEGREES],
          [KRAKOW_BOUNDS.northEast.lon + BOUNDS_MARGIN_DEGREES, KRAKOW_BOUNDS.northEast.lat + BOUNDS_MARGIN_DEGREES],
        ],
        attributionControl: false,
        dragRotate: false,
        pitchWithRotate: false,
        touchPitch: false,
      });
    } catch {
      latest.current.onFail();
      return undefined;
    }
    created.touchZoomRotate.disableRotation();
    created.keyboard.disableRotation();
    created.addControl(new AttributionControl({ compact: false }), "bottom-right");
    created.addControl(new NavigationControl({ showCompass: false }), "top-right");
    latest.current.onReady({
      readCenter: () => {
        const center = created.getCenter();
        return { lat: center.lat, lon: center.lng };
      },
    });
    setMap(created);
    return () => {
      latest.current.onReady(null);
      drawn.clear();
      created.remove();
      setMap(null);
    };
  }, []);

  useEffect(() => {
    let isCurrent = true;
    loadBaseMapStyle(language).then(
      (style) => {
        if (isCurrent) {
          setBaseStyle(style);
        }
      },
      () => {
        if (isCurrent) {
          latest.current.onFail();
        }
      },
    );
    return () => {
      isCurrent = false;
    };
  }, [language]);

  const style = useMemo(() => (baseStyle === null ? null : composeStyle(baseStyle, zones, route, isRouteAssessed)), [baseStyle, zones, route, isRouteAssessed]);

  useEffect(() => {
    if (map !== null && style !== null) {
      map.setStyle(style);
    }
  }, [map, style]);

  useEffect(() => {
    if (map === null) {
      return undefined;
    }
    let timer: number | null = null;
    const cancel = () => {
      if (timer !== null) {
        window.clearTimeout(timer);
        timer = null;
      }
    };
    const report = () => {
      const center = map.getCenter();
      const bounds = map.getBounds();
      latest.current.onRest({
        center: { lat: center.lat, lon: center.lng },
        zoom: map.getZoom(),
        southWest: { lat: bounds.getSouth(), lon: bounds.getWest() },
        northEast: { lat: bounds.getNorth(), lon: bounds.getEast() },
      });
    };
    const schedule = () => {
      cancel();
      timer = window.setTimeout(report, REST_DELAY_MILLISECONDS);
    };
    const start = (event: { originalEvent?: unknown }) => {
      if (event.originalEvent !== undefined) {
        liveCamera.current = null;
      }
      cancel();
    };
    const keepPlace = () => {
      if (liveCamera.current !== null) {
        moveCamera(map, liveCamera.current, false);
      }
    };
    const fail = (event: { error: unknown; sourceId?: string; tile?: unknown }) => {
      const isOfBaseMap = event.sourceId !== undefined && event.sourceId !== ZONES_SOURCE_ID && event.sourceId !== ROUTE_SOURCE_ID;
      if (isOfBaseMap && event.tile === undefined) {
        latest.current.onFail();
      }
    };
    map.on("movestart", start);
    map.on("moveend", schedule);
    map.on("resize", keepPlace);
    map.on("error", fail);
    schedule();
    return () => {
      cancel();
      map.off("movestart", start);
      map.off("moveend", schedule);
      map.off("resize", keepPlace);
      map.off("error", fail);
    };
  }, [map]);

  useEffect(() => {
    if (map === null) {
      return;
    }
    const drawn = drawnMarkers.current;
    for (const [id, drawnMarker] of drawn) {
      if (mounts[id] === undefined) {
        drawnMarker.remove();
        drawn.delete(id);
      }
    }
    for (const marker of markers) {
      const element = mounts[marker.id];
      if (element === undefined) {
        continue;
      }
      const position: [number, number] = [marker.point.lon, marker.point.lat];
      const drawnMarker = drawn.get(marker.id) ?? new Marker({ element }).setLngLat(position).addTo(map);
      drawn.set(marker.id, drawnMarker);
      drawnMarker.setLngLat(position);
      if (marker.isSelected) {
        drawnMarker.addClassName(SELECTED_MARKER_CLASS);
      } else {
        drawnMarker.removeClassName(SELECTED_MARKER_CLASS);
      }
    }
  }, [map, markers, mounts]);

  useEffect(() => {
    if (map === null || camera === null || appliedCamera.current === camera.key) {
      return;
    }
    appliedCamera.current = camera.key;
    liveCamera.current = camera;
    moveCamera(map, camera, true);
  }, [map, camera]);

  useEffect(() => {
    if (map === null) {
      return;
    }
    map.getCanvas().setAttribute("aria-label", label);
    const names: [string, string][] = [
      [".maplibregl-ctrl-zoom-in", t("map.zoom_in")],
      [".maplibregl-ctrl-zoom-out", t("map.zoom_out")],
    ];
    for (const [selector, name] of names) {
      const button = map.getContainer().querySelector(selector);
      button?.setAttribute("aria-label", name);
      button?.setAttribute("title", name);
    }
  }, [map, label, t, language]);

  return (
    <div className="relative size-full">
      <div ref={attach} className="size-full" />
      {hasSampleData ? <span className="absolute top-2.5 left-2.5 rounded-control border border-line bg-surface px-[9px] py-1 text-[11.5px] font-semibold text-ink">{t("sample.badge")}</span> : null}
      {isPicking ? (
        <span aria-hidden="true" className="pointer-events-none absolute top-1/2 left-1/2 size-12 -translate-x-1/2 -translate-y-1/2 text-shell">
          <Icon name="cross" size={48} strokeWidth={2.5} />
        </span>
      ) : null}
      {markers.map((marker) => {
        const mount = mounts[marker.id];
        return mount === undefined ? null : createPortal(<MapMark marker={marker} onPress={onMarkerPress} />, mount, marker.id);
      })}
    </div>
  );
}
