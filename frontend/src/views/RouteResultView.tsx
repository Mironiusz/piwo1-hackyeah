import { useCallback, useEffect, useMemo } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import { Link, Navigate, useMatch, useNavigate, useOutlet } from "react-router";

import type { Route, RouteFact } from "../api/types.ts";
import { formatDistance } from "../format/format.ts";
import { useLanguage } from "../i18n/index.ts";
import { EMPTY_MAP_SCENE, useMap, useMapScene, type MapCamera, type MapScene } from "../map/mapScene.ts";
import { findRouteBounds } from "../map/routeLayers.ts";
import { Button } from "../parts/Button.tsx";
import { FactRow } from "../parts/FactRow.tsx";
import { nameTypeInSentence } from "../parts/factText.ts";
import { Icon } from "../parts/Icon.tsx";
import { Legend } from "../parts/Legend.tsx";
import { Note } from "../parts/Note.tsx";
import { Panel } from "../parts/Panel.tsx";
import { hasMissingData, measureNoData } from "../parts/routeSummary.ts";
import { RouteSummaryLine } from "../parts/RouteSummaryLine.tsx";
import { RouteTiles } from "../parts/RouteTiles.tsx";
import { ACTIONS_ONE, HINT, LIST_COUNT, LIST_HEADING } from "../parts/styles.ts";
import { useNeeds } from "../state/needs.tsx";
import { usePlannedRoute } from "../state/plannedRoute.tsx";
import { buildFactMarker, buildFactPath, buildFactZones, readFactMarkerId, type FactDetailContext } from "./factDetail.ts";
import { buildEndMarkers, nameRouteEndShortly } from "./routeText.ts";

const BASE_PATH = "/route/result";
const ROUTE_LEGEND = ["barrier", "amenity", "overruled"] as const;
const NEUTRAL_ROUTE_LEGEND = ["amenity"] as const;

/**
 * Does nothing. The route result has nothing to do when the detail of a fact was loaded or changed:
 * a saved vote marks the route as stale by itself, and the view plans it again.
 */
function ignore(): void {
  return undefined;
}

interface GroupProps {
  title: string;
  facts: readonly RouteFact[];
  emptyText: string;
  alternative: { underFactId: number; text: string; onShow: () => void } | null;
}

/**
 * One group of the list of the route: its name with the number of its facts, the facts in the order of the route,
 * and for an empty group the text that says what is not known. An empty group never reads as a route free of barriers.
 * The proposal of the alternative route stands directly under the barrier that causes it.
 */
function Group({ title, facts, emptyText, alternative }: GroupProps) {
  const { t } = useTranslation();
  return (
    <>
      <h2 className={LIST_HEADING}>
        {title}
        {facts.length > 0 ? <span className={LIST_COUNT}>{facts.length}</span> : null}
      </h2>
      {facts.length === 0 ? (
        <Note>{emptyText}</Note>
      ) : (
        <ul>
          {facts.map((fact, index) => (
            <FactRowWithProposal
              key={fact.id}
              fact={fact}
              isFirst={index === 0}
              proposal={alternative !== null && alternative.underFactId === fact.id ? alternative : null}
              showLabel={t("action.show")}
            />
          ))}
        </ul>
      )}
    </>
  );
}

interface FactRowWithProposalProps {
  fact: RouteFact;
  isFirst: boolean;
  proposal: { text: string; onShow: () => void } | null;
  showLabel: string;
}

/**
 * A fact of the route as a row, followed by the proposal of the alternative route when this fact is its reason.
 */
function FactRowWithProposal({ fact, isFirst, proposal, showLabel }: FactRowWithProposalProps) {
  return (
    <>
      <FactRow fact={fact} to={buildFactPath(BASE_PATH, fact.id)} distanceM={fact.distance_from_start_m} isFirst={isFirst} />
      {proposal !== null ? (
        <li className="mt-0.5 mb-2.5 ml-[34px] flex items-center gap-2.5 rounded-panel border border-line px-3 py-2.5 text-[13px]">
          <p className="flex-1">{proposal.text}</p>
          <Button isSmall onClick={proposal.onShow}>
            {showLabel}
          </Button>
        </li>
      ) : null}
    </>
  );
}

/**
 * The route result. Above the map stands the summary: the route as a line in the patterns of the segment states,
 * and three numbers. The map draws the route, and the panel holds the statement of the route, the legend,
 * the one note about missing data and the list in three groups. The states and the groups are shown as the service gave them.
 * A route for needs without a barrier is drawn in the neutral style and its stretches are not assessed.
 * The route is planned again once when it went stale: the needs changed, or a vote or a report was saved.
 */
export function RouteResultView() {
  const { t } = useTranslation();
  const language = useLanguage();
  const navigate = useNavigate();
  const { needs } = useNeeds();
  const { topSlot } = useMap();
  const { start, destination, state, answer, error, isAssessed, isStale, shown, shownRoute, show, planAgain } = usePlannedRoute();
  const match = useMatch(`${BASE_PATH}/fact/:factId`);
  const openedId = match === null ? null : Number(match.params.factId);

  useEffect(() => {
    if (isStale && state !== "loading") {
      planAgain();
    }
  }, [isStale, state, planAgain]);

  const routeFacts = useMemo<RouteFact[]>(() => {
    if (answer === null || shownRoute === null) {
      return [];
    }
    return [...shownRoute.profile_barriers, ...shownRoute.additional_barriers, ...shownRoute.amenities, ...(answer.alternative?.avoided_barriers ?? [])];
  }, [answer, shownRoute]);

  const pressMarker = useCallback(
    (markerId: string) => {
      const factId = readFactMarkerId(markerId);
      if (factId !== null) {
        void navigate(buildFactPath(BASE_PATH, factId));
      }
    },
    [navigate],
  );

  const camera = useMemo<MapCamera | null>(() => {
    const bounds = shownRoute === null ? null : findRouteBounds(shownRoute);
    if (bounds === null || shownRoute === null) {
      return null;
    }
    return { key: `route-${shown}-${shownRoute.length_m}-${bounds.southWest.lat}-${bounds.northEast.lon}`, target: { kind: "bounds", ...bounds } };
  }, [shownRoute, shown]);

  const scene = useMemo<MapScene>(() => {
    const onMap: RouteFact[] = shownRoute === null ? [] : [...shownRoute.profile_barriers, ...shownRoute.amenities];
    return {
      ...EMPTY_MAP_SCENE,
      label: t("aria.map.route"),
      route: shownRoute,
      isRouteAssessed: isAssessed,
      markers: [...buildEndMarkers(start, destination, t), ...onMap.map((fact) => buildFactMarker(fact, fact.id === openedId, fact.is_overruled_by_osm, t, language))],
      zones: buildFactZones(onMap),
      hasSampleData: onMap.some((fact) => fact.is_sample),
      camera,
      onMarkerPress: pressMarker,
    };
  }, [t, language, shownRoute, isAssessed, start, destination, openedId, camera, pressMarker]);
  useMapScene(scene);

  const context = useMemo<FactDetailContext>(() => ({ closePath: BASE_PATH, routeFacts, onLoad: ignore, onChange: ignore }), [routeFacts]);
  const detail = useOutlet(context);

  if (start === null || destination === null) {
    return <Navigate to="/route" replace />;
  }

  if (answer === null || shownRoute === null) {
    return (
      <Panel>
        <h1 tabIndex={-1} className="sr-only">
          {t("route.title")}
        </h1>
        {state === "failed" && error !== null ? (
          <>
            <Note kind="strong" announce="alert">
              {error.code === "routing_unavailable" ? (
                <p>
                  <b className="font-bold">{t("plan.unavailable.title")}</b> {t("plan.unavailable.body")}
                </p>
              ) : (
                <p>{t(error.code === "network_error" ? "state.offline" : error.code === "point_outside_krakow" ? "plan.outside" : "route.failed")}</p>
              )}
            </Note>
            <div className={ACTIONS_ONE}>
              <Button look="primary" onClick={planAgain}>
                {t("action.retry")}
              </Button>
              <Button to="/route">{t("route.change")}</Button>
            </div>
          </>
        ) : (
          <output className={`${HINT} block`}>{t(state === "loading" ? "plan.loading" : "route.no_route")}</output>
        )}
        {state === "idle" ? (
          <div className={ACTIONS_ONE}>
            <Button look="primary" to="/route">
              {t("plan.title")}
            </Button>
          </div>
        ) : null}
      </Panel>
    );
  }

  const route: Route = shownRoute;
  const isAlternativeShown = shown === "alternative" && answer.alternative !== null;
  const noDataDistance = formatDistance(measureNoData(route), language);
  const reason = answer.alternative?.avoided_barriers[0] ?? null;
  const proposal =
    !isAlternativeShown && answer.alternative !== null && reason !== null
      ? {
          underFactId: reason.id,
          text: t("route.alternative", {
            distance: formatDistance(Math.max(0, answer.alternative.route.length_m - answer.route.length_m), language),
            type: nameTypeInSentence(reason.type, t, language),
            status: t(`status.${reason.status}`),
          }),
          onShow: () => show("alternative"),
        }
      : null;

  const summary = (
    <section aria-label={t("aria.summary")} className="bg-shell px-4 pb-3.5 text-white">
      {detail === null ? (
        <h1 tabIndex={-1} className="sr-only">
          {t("route.title")}
        </h1>
      ) : null}
      <div className="flex items-center gap-2">
        <Link to="/needs" className="inline-flex min-h-11 items-center gap-1.5 rounded-control bg-yellow px-2.5 py-1.5 text-[13.5px] font-semibold text-ink no-underline focus-visible:outline-white">
          <Icon name="needs" />
          {needs.avoid.length > 0 ? t("route.needs", { barriers: t("count.barriers", { count: needs.avoid.length }) }) : t("route.needs.none")}
          <Icon name="chevron" />
        </Link>
        <Link
          to="/route"
          className="ml-auto inline-flex min-h-11 items-center rounded-control border border-white px-2.5 py-[5px] text-[13px] font-semibold text-white no-underline focus-visible:outline-yellow"
        >
          {t("route.change")}
        </Link>
      </div>
      <RouteSummaryLine route={route} isAssessed={isAssessed} startName={nameRouteEndShortly(start, t)} destinationName={nameRouteEndShortly(destination, t)} />
      <RouteTiles route={route} isAssessed={isAssessed} />
    </section>
  );

  return (
    <>
      {topSlot !== null ? createPortal(summary, topSlot) : null}
      {detail ?? (
        <Panel isPadded={false}>
          <div className="px-4 pt-1">
            <output className="block">{state === "loading" ? <p className={`${HINT} pb-2`}>{t("route.replanning")}</p> : null}</output>
            {isAlternativeShown ? (
              <Note className="mb-3">
                <p>{t("route.alternative.shown")}</p>
                <div className="mt-2">
                  <Button isSmall onClick={() => show("first")}>
                    {t("route.alternative.back")}
                  </Button>
                </div>
              </Note>
            ) : null}
            {isAssessed && !answer.barrier_free_route_exists && !isAlternativeShown ? (
              <Note kind="strong" className="mb-3">
                <p>
                  <b className="font-bold">{t("route.none.title")}</b> {t("route.none.body", { n: route.profile_barriers.length })}
                </p>
              </Note>
            ) : null}
            {!isAssessed ? (
              <div className="mb-3">
                <Note kind="strong">{t("route.not_assessed")}</Note>
                <div className="mt-2.5 grid">
                  <Button look="primary" to="/needs">
                    {t("route.set_needs")}
                  </Button>
                </div>
              </div>
            ) : null}
          </div>

          <Legend segments={isAssessed ? "four" : "neutral"} markers={isAssessed ? ROUTE_LEGEND : NEUTRAL_ROUTE_LEGEND} osmCopyDate={answer.osm_copy_date} />

          {isAssessed && hasMissingData(route) ? (
            <div className="px-4 pt-3">
              <Note kind="dash">{t("route.no_data_note")}</Note>
            </div>
          ) : null}

          <section className="px-4 pt-0.5 pb-[18px]">
            {isAssessed ? <Group title={t("route.group.profile")} facts={route.profile_barriers} emptyText={t("route.empty.profile", { distance: noDataDistance })} alternative={proposal} /> : null}
            <Group
              title={t(isAssessed ? "route.group.additional" : "route.group.all")}
              facts={route.additional_barriers}
              emptyText={t("route.empty.additional", { distance: noDataDistance })}
              alternative={null}
            />
            <Group title={t("route.group.amenities")} facts={route.amenities} emptyText={t(needs.need.length === 0 ? "route.empty.amenities.no_needs" : "route.empty.amenities")} alternative={null} />
            {route.segments.some((segment) => segment.is_marked_wheelchair_no) ? <Note className="mt-[18px]">{t("route.wheelchair_no")}</Note> : null}
          </section>
        </Panel>
      )}
    </>
  );
}
