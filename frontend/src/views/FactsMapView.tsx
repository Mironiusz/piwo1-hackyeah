import { useCallback, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useMatch, useNavigate, useOutlet } from "react-router";

import { listFactsInArea, readOsmCopy } from "../api/client.ts";
import type { Fact, FactsInArea, Point } from "../api/types.ts";
import { useRequest } from "../hooks/useRequest.ts";
import { useLanguage } from "../i18n/index.ts";
import { FACTS_MIN_ZOOM, INITIAL_MAP_VIEW } from "../map/krakowBounds.ts";
import { EMPTY_MAP_SCENE, useMap, useMapScene, type MapCamera, type MapScene } from "../map/mapScene.ts";
import { Button } from "../parts/Button.tsx";
import { FactRow } from "../parts/FactRow.tsx";
import { Icon } from "../parts/Icon.tsx";
import { Legend } from "../parts/Legend.tsx";
import { Note } from "../parts/Note.tsx";
import { Panel } from "../parts/Panel.tsx";
import { HINT, LIST_COUNT, LIST_HEADING } from "../parts/styles.ts";
import { Switch } from "../parts/Switch.tsx";
import { isInNeeds, useNeeds } from "../state/needs.tsx";
import { buildFactMarker, buildFactPath, buildFactZones, readFactMarkerId, type FactDetailContext } from "./factDetail.ts";

type Scope = "needs" | "all";

const FACTS_LEGEND = ["barrier", "amenity", "area", "outdated"] as const;
const NO_MAP_HALF_HEIGHT_DEGREES = 0.006;
const NO_MAP_HALF_WIDTH_DEGREES = 0.01;

/**
 * Returns the square of the distance between two points, which is enough to put facts in the order of their distance.
 */
function compareDistance(from: Point, to: Point): number {
  return (from.lat - to.lat) ** 2 + ((from.lon - to.lon) * Math.cos((from.lat * Math.PI) / 180)) ** 2;
}

/**
 * The map of facts, the view the application opens on: the barriers and amenities of the needs in the visible area,
 * with a switch to every fact, and under the map the same facts as a list, which is the text form of the map.
 * It asks for facts when the map has stood still and not when the map is zoomed out beyond a part of a district.
 * The detail of a fact opens in place of the list.
 */
export function FactsMapView() {
  const { t } = useTranslation();
  const language = useLanguage();
  const navigate = useNavigate();
  const { needs } = useNeeds();
  const { rest, hasFailed } = useMap();
  const [scope, setScope] = useState<Scope>("needs");
  const [opened, setOpened] = useState<Fact | null>(null);
  const [camera, setCamera] = useState<MapCamera | null>(null);
  const match = useMatch("/fact/:factId");
  const openedId = match === null ? null : Number(match.params.factId);

  const hasNoNeeds = needs.avoid.length === 0 && needs.need.length === 0;
  const shownScope: Scope = hasNoNeeds ? "all" : scope;
  const isZoomedOut = rest !== null && rest.zoom < FACTS_MIN_ZOOM;
  const center = rest?.center ?? INITIAL_MAP_VIEW.center;

  const facts = useRequest<FactsInArea | null>(() => {
    if (hasFailed) {
      return listFactsInArea(
        { lat: INITIAL_MAP_VIEW.center.lat - NO_MAP_HALF_HEIGHT_DEGREES, lon: INITIAL_MAP_VIEW.center.lon - NO_MAP_HALF_WIDTH_DEGREES },
        { lat: INITIAL_MAP_VIEW.center.lat + NO_MAP_HALF_HEIGHT_DEGREES, lon: INITIAL_MAP_VIEW.center.lon + NO_MAP_HALF_WIDTH_DEGREES },
      );
    }
    if (rest === null || rest.zoom < FACTS_MIN_ZOOM) {
      return Promise.resolve(null);
    }
    return listFactsInArea(rest.southWest, rest.northEast);
  }, [rest, hasFailed]);
  const osmCopy = useRequest(readOsmCopy, []);
  const retryFacts = facts.retry;

  const shown = useMemo(() => {
    const all = facts.data?.facts ?? [];
    const inScope = shownScope === "all" ? all : all.filter((fact) => isInNeeds(needs, fact.type));
    return [...inScope].sort((first, second) => compareDistance(center, first.point) - compareDistance(center, second.point));
  }, [facts.data, shownScope, needs, center]);

  const onMap = useMemo(() => {
    const isOpenedShown = opened === null || opened.id !== openedId || shown.some((fact) => fact.id === opened.id);
    return isOpenedShown ? shown : [...shown, opened];
  }, [shown, opened, openedId]);

  const pressMarker = useCallback(
    (markerId: string) => {
      const factId = readFactMarkerId(markerId);
      if (factId !== null) {
        void navigate(buildFactPath("/", factId));
      }
    },
    [navigate],
  );

  const scene = useMemo<MapScene>(
    () => ({
      ...EMPTY_MAP_SCENE,
      label: t("aria.map.facts"),
      markers: isZoomedOut ? [] : onMap.map((fact) => buildFactMarker(fact, fact.id === openedId, false, t, language)),
      zones: isZoomedOut ? [] : buildFactZones(onMap),
      hasSampleData: !isZoomedOut && onMap.some((fact) => fact.is_sample),
      camera,
      onMarkerPress: pressMarker,
    }),
    [t, language, isZoomedOut, onMap, openedId, camera, pressMarker],
  );
  useMapScene(scene);

  const showOpened = useCallback(
    (fact: Fact) => {
      setOpened(fact);
      const isInView = rest !== null && fact.point.lat >= rest.southWest.lat && fact.point.lat <= rest.northEast.lat && fact.point.lon >= rest.southWest.lon && fact.point.lon <= rest.northEast.lon;
      if (!isInView) {
        setCamera({ key: `fact-${fact.id}`, target: { kind: "point", point: fact.point, zoom: null } });
      }
    },
    [rest],
  );

  const refresh = useCallback(
    (fact: Fact) => {
      setOpened(fact);
      retryFacts();
    },
    [retryFacts],
  );

  const context = useMemo<FactDetailContext>(() => ({ closePath: "/", routeFacts: [], onLoad: showOpened, onChange: refresh }), [showOpened, refresh]);
  const detail = useOutlet(context);

  if (detail !== null) {
    return detail;
  }

  const isLoading = facts.state === "loading" && !isZoomedOut;
  const hasList = facts.state !== "failed" && !isZoomedOut && shown.length > 0;

  return (
    <Panel isPadded={false}>
      <div className="px-4 pt-1 pb-[18px]">
        <h1 className="sr-only">{t("aria.map.facts")}</h1>
        <Link to="/route" className="flex min-h-[46px] w-full items-center gap-2.5 rounded-panel border-[1.5px] border-field bg-white px-3 py-2 text-left font-semibold text-ink no-underline">
          <Icon name="search" />
          {t("facts.plan")}
        </Link>
        <Switch
          label={t("aria.scope")}
          options={[
            { value: "needs", label: t("facts.scope.needs") },
            { value: "all", label: t("facts.scope.all") },
          ]}
          value={shownScope}
          onChange={setScope}
          isOff={hasNoNeeds}
          className="mt-3"
        />
        {hasNoNeeds ? <p className={`${HINT} mt-2`}>{t("facts.empty_needs")}</p> : null}
      </div>

      <section className="px-4 pb-[18px]">
        <h2 className={`${LIST_HEADING} mt-1.5!`}>
          {t("facts.list")}
          {hasList ? <span className={LIST_COUNT}>{shown.length}</span> : null}
        </h2>
        <output className="block">
          {isLoading && !hasList ? <p className={`${HINT} py-2`}>{t("state.loading")}</p> : null}
          {isZoomedOut ? <Note className="mt-2">{t("facts.zoom_in")}</Note> : null}
          {facts.state === "ready" && !isZoomedOut && shown.length === 0 ? <Note className="mt-2">{t(shownScope === "needs" ? "facts.none" : "facts.none_at_all")}</Note> : null}
          {facts.data?.is_truncated === true && !isZoomedOut ? (
            <Note kind="strong" className="mt-2">
              {t("facts.too_many")}
            </Note>
          ) : null}
        </output>
        {facts.state === "failed" ? (
          <Note kind="strong" announce="alert" className="mt-2">
            <p>{t(facts.error?.code === "network_error" ? "state.offline" : "facts.failed")}</p>
            <div className="mt-2">
              <Button isSmall onClick={retryFacts}>
                {t("action.retry")}
              </Button>
            </div>
          </Note>
        ) : null}
        {hasList ? (
          <ul>
            {shown.map((fact, index) => (
              <FactRow key={fact.id} fact={fact} to={buildFactPath("/", fact.id)} isFirst={index === 0} />
            ))}
          </ul>
        ) : null}
      </section>
      <div className="mt-1">
        <Legend segments="none" markers={FACTS_LEGEND} osmCopyDate={osmCopy.data} />
      </div>
    </Panel>
  );
}
