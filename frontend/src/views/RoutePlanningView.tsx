import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";

import { isInsideKrakow } from "../map/krakowBounds.ts";
import { EMPTY_MAP_SCENE, useMapScene, type MapScene } from "../map/mapScene.ts";
import { Button } from "../parts/Button.tsx";
import { Note } from "../parts/Note.tsx";
import { Panel } from "../parts/Panel.tsx";
import { ACTIONS_ONE, HINT, PANEL_TITLE } from "../parts/styles.ts";
import { useNeeds } from "../state/needs.tsx";
import { usePlannedRoute, type RouteEnd, type RouteEndName } from "../state/plannedRoute.tsx";
import { buildEndMarkers, buildEndsCamera, nameRouteEnd } from "./routeText.ts";

type LocationState = "idle" | "waiting" | "refused" | "failed" | "outside";

const LOCATION_TEXTS: Record<Exclude<LocationState, "idle" | "waiting">, string> = {
  refused: "plan.location_refused",
  failed: "plan.location_failed",
  outside: "plan.outside",
};

interface EndRowProps {
  name: RouteEndName;
  letter: string;
  end: RouteEnd | null;
  isFirst: boolean;
  onUseLocation: (() => void) | null;
  onClear: () => void;
}

/**
 * One end of the route in the form: its letter, its name, the point that is set, and the ways to give or change it.
 * The ways stay open while the end is not set, and fold behind the change action once it is.
 */
function EndRow({ name, letter, end, isFirst, onUseLocation, onClear }: EndRowProps) {
  const { t } = useTranslation();
  const [isChanging, setIsChanging] = useState(false);
  const isOpen = end === null || isChanging;
  return (
    <>
      <div className={`grid grid-cols-[26px_1fr_auto] items-center gap-2.5 py-2.5 ${isFirst ? "" : "border-t border-line"}`}>
        <span aria-hidden="true" className="inline-flex size-6 items-center justify-center rounded-full border-2 border-ink bg-white text-[12px] leading-none font-bold">
          {letter}
        </span>
        <div className="min-w-0">
          <div className="text-[12.5px] text-muted">{t(`plan.${name}`)}</div>
          <div className="font-semibold break-words">{end !== null ? nameRouteEnd(end, t) : t("plan.not_set")}</div>
        </div>
        {end !== null ? (
          <Button look="link" aria-expanded={isOpen} onClick={() => setIsChanging((current) => !current)}>
            <span>{t("action.change")}</span>
            <span className="sr-only">{`: ${t(`plan.${name}`)}`}</span>
          </Button>
        ) : null}
      </div>
      {isOpen ? (
        <fieldset aria-label={t(`plan.${name}`)} className="m-0 flex min-w-0 flex-wrap gap-2 border-0 p-0 pb-3 pl-9">
          {onUseLocation !== null ? (
            <Button isSmall icon="location" onClick={onUseLocation}>
              {t("plan.my_location")}
            </Button>
          ) : null}
          <Button isSmall to={`/route/search/${name}`}>
            {t("plan.address")}
          </Button>
          <Button isSmall to={`/route/pick/${name}`}>
            {t("plan.map_point")}
          </Button>
          {end !== null ? (
            <Button
              isSmall
              onClick={() => {
                onClear();
                setIsChanging(false);
              }}
            >
              {t("plan.clear")}
            </Button>
          ) : null}
        </fieldset>
      ) : null}
    </>
  );
}

/**
 * Route planning: the start given by the location of the device, an address or a point on the map,
 * the destination by an address or a point, and the action that asks for the route once both are set.
 * The location of the device is read only when the person asks for it and travels only in the route request.
 * When no route can be planned the view says so plainly and shows no route.
 */
export function RoutePlanningView() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { needs } = useNeeds();
  const { start, destination, setEnd, state, error, plan } = usePlannedRoute();
  const [location, setLocation] = useState<LocationState>("idle");

  const scene = useMemo<MapScene>(
    () => ({
      ...EMPTY_MAP_SCENE,
      label: t("aria.map.route"),
      markers: buildEndMarkers(start, destination, t),
      camera: buildEndsCamera(start?.point ?? null, destination?.point ?? null),
    }),
    [t, start, destination],
  );
  useMapScene(scene);

  const readLocation = () => {
    if (typeof navigator === "undefined" || !("geolocation" in navigator)) {
      setLocation("failed");
      return;
    }
    setLocation("waiting");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const point = { lat: position.coords.latitude, lon: position.coords.longitude };
        if (!isInsideKrakow(point)) {
          setLocation("outside");
          return;
        }
        setEnd("start", { point, kind: "location", label: null });
        setLocation("idle");
      },
      (failure) => setLocation(failure.code === failure.PERMISSION_DENIED ? "refused" : "failed"),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
    );
  };

  const submit = async () => {
    if (await plan()) {
      void navigate("/route/result");
    }
  };

  const isPlanning = state === "loading";
  const hasFailed = state === "failed" && error !== null;
  const isOutside =
    hasFailed && (error.code === "point_outside_krakow" || (error.code === "invalid_request" && error.fields.some((field) => field.startsWith("start") || field.startsWith("destination"))));

  return (
    <Panel>
      <h1 tabIndex={-1} className={`${PANEL_TITLE} outline-none`}>
        {t("plan.title")}
      </h1>
      <EndRow name="start" letter="A" end={start} isFirst onUseLocation={readLocation} onClear={() => setEnd("start", null)} />
      <output className="block pl-9">
        {location === "waiting" ? <p className={`${HINT} pb-3`}>{t("plan.locating")}</p> : null}
        {location !== "idle" && location !== "waiting" ? (
          <Note kind="strong" className="mb-3">
            {t(LOCATION_TEXTS[location])}
          </Note>
        ) : null}
      </output>
      <EndRow name="destination" letter="B" end={destination} isFirst={false} onUseLocation={null} onClear={() => setEnd("destination", null)} />

      <Note className="mt-1">
        {t("plan.needs_summary", {
          barriers: t("count.barriers", { count: needs.avoid.length }),
          amenities: t("count.amenities", { count: needs.need.length }),
        })}{" "}
        <Link to="/needs" className="font-semibold">
          {t("plan.change_needs")}
        </Link>
      </Note>

      {hasFailed ? (
        <Note kind="strong" announce="alert" className="mt-3">
          {error.code === "routing_unavailable" ? (
            <p>
              <b className="font-bold">{t("plan.unavailable.title")}</b> {t("plan.unavailable.body")}
            </p>
          ) : (
            <p>{t(isOutside ? "plan.outside" : error.code === "network_error" ? "state.offline" : "state.failed")}</p>
          )}
        </Note>
      ) : null}
      <output className="block">{isPlanning ? <p className={`${HINT} mt-3`}>{t("plan.loading")}</p> : null}</output>

      <div className={ACTIONS_ONE}>
        <Button look="primary" disabled={start === null || destination === null || isPlanning} onClick={() => void submit()}>
          {t(hasFailed && !isOutside ? "action.retry" : "plan.submit")}
        </Button>
      </div>
    </Panel>
  );
}
