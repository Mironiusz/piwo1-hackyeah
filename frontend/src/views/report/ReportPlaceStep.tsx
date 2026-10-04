import { useEffect, useId, useMemo, useRef, useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate } from "react-router";

import { searchAddress } from "../../api/client.ts";
import { errorTextKey, toApiError } from "../../api/errors.ts";
import type { AddressMatch, Point } from "../../api/types.ts";
import { LOCATION_TEXTS, readDeviceLocation, type LocationState } from "../../map/deviceLocation.ts";
import { focusMap } from "../../map/focusMap.ts";
import { isInsideKrakow } from "../../map/krakowBounds.ts";
import { EMPTY_MAP_SCENE, useMap, useMapScene, type MapCamera, type MapRest, type MapScene } from "../../map/mapScene.ts";
import { Button } from "../../parts/Button.tsx";
import { Icon } from "../../parts/Icon.tsx";
import { Note } from "../../parts/Note.tsx";
import { Panel } from "../../parts/Panel.tsx";
import { ACTIONS, HINT, PANEL_TEXT } from "../../parts/styles.ts";
import { useReportDraft } from "../../state/reportDraft.tsx";
import { splitLabel } from "../routeText.ts";
import { buildMoveCamera, isSamePlace } from "./reportMap.ts";
import { ReportStepHead } from "./ReportStepHead.tsx";
import { countSteps, findOpenStep, findStepNumber, REPORT_HEADING_ID, REPORT_PATHS, SEARCH_TEXT_MAX_LENGTH } from "./reportSteps.ts";

type SearchState = { kind: "idle" } | { kind: "searching" } | { kind: "results"; matches: AddressMatch[] } | { kind: "none" } | { kind: "invalid" } | { kind: "refused"; textKey: string };

/**
 * A place a person asked the map to move to: the location of the device, or a result of the address search with its match.
 * It remembers where the map rested when the move was asked for, which tells whether the map has arrived since.
 */
interface MoveTarget {
  point: Point;
  match: AddressMatch | null;
  restAtStart: MapRest | null;
}

interface AddressSearchProps {
  picked: AddressMatch | null;
  onPick: (match: AddressMatch) => void;
}

/**
 * The address search of an area. It asks the service only when the person submits the text, with the Enter key or the button,
 * and suggests nothing while typing. The matches are always a list to pick from, also when there is one,
 * and a picked match only moves the map: the point is set by the confirmation of the step.
 * Nothing found, a search that does not answer and a refused text each have their own message.
 */
function AddressSearch({ picked, onPick }: AddressSearchProps) {
  const { t } = useTranslation();
  const [text, setText] = useState("");
  const [search, setSearch] = useState<SearchState>({ kind: "idle" });

  /**
   * Sends the text to the address search and keeps the outcome: the matches, nothing found, or the refusal.
   */
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (text.trim() === "" || [...text].length > SEARCH_TEXT_MAX_LENGTH) {
      setSearch({ kind: "invalid" });
      return;
    }
    setSearch({ kind: "searching" });
    try {
      const matches = await searchAddress(text);
      setSearch(matches.length === 0 ? { kind: "none" } : { kind: "results", matches });
    } catch (caught) {
      const code = toApiError(caught).code;
      setSearch(code === "invalid_search_text" ? { kind: "invalid" } : { kind: "refused", textKey: errorTextKey(code) });
    }
  };

  /**
   * Hands a match inside Kraków to the step, and refuses a match outside it with its message.
   */
  const pick = (match: AddressMatch) => {
    if (!isInsideKrakow(match.point)) {
      setSearch({ kind: "refused", textKey: "plan.outside" });
      return;
    }
    onPick(match);
  };

  const isInvalid = search.kind === "invalid";

  return (
    <>
      <form onSubmit={(event) => void submit(event)} noValidate className="mt-4 grid gap-[5px]">
        <label htmlFor="report-search-text" className="text-[13.5px] font-semibold">
          {t("search.field")}
        </label>
        <div className="grid grid-cols-[1fr_auto] gap-2">
          <input
            id="report-search-text"
            type="search"
            value={text}
            onChange={(event) => setText(event.target.value)}
            enterKeyHint="search"
            autoComplete="off"
            aria-invalid={isInvalid}
            aria-describedby={isInvalid ? "report-search-error report-search-hint" : "report-search-hint"}
            className={`min-h-[46px] w-full rounded-panel border-[1.5px] bg-white px-3 py-2 text-[16px] text-ink ${isInvalid ? "border-barrier" : "border-field"}`}
          />
          <Button type="submit" look="primary" disabled={search.kind === "searching"}>
            {t("search.submit")}
          </Button>
        </div>
        {isInvalid ? (
          <p id="report-search-error" role="alert" className="text-[13px] font-semibold text-barrier">
            {t("search.invalid")}
          </p>
        ) : null}
        <p id="report-search-hint" className={HINT}>
          {t("search.hint")}
        </p>
      </form>

      <output className="mt-3 block">
        {search.kind === "searching" ? <p className={HINT}>{t("search.searching")}</p> : null}
        {search.kind === "results" ? <p className="font-semibold">{t("search.count", { results: t("count.results", { count: search.matches.length }) })}</p> : null}
        {search.kind === "none" ? (
          <Note kind="strong">
            <p>
              <b className="font-bold">{t("search.none.title")}</b> {t("search.none.body")}
            </p>
          </Note>
        ) : null}
      </output>
      {search.kind === "refused" ? (
        <Note kind="strong" announce="alert">
          {t(search.textKey)}
        </Note>
      ) : null}

      {search.kind === "results" ? (
        <>
          <ul className="mt-1.5 border-b border-line">
            {search.matches.map((match) => {
              const label = splitLabel(match.label);
              const isPicked = match === picked;
              return (
                <li key={`${match.label}-${match.point.lat}-${match.point.lon}`} className="border-t border-line">
                  <button
                    type="button"
                    aria-pressed={isPicked}
                    onClick={() => pick(match)}
                    className="grid min-h-14 w-full grid-cols-[24px_1fr_auto] items-center gap-2.5 py-3 text-left -outline-offset-[3px]"
                  >
                    <Icon name="pin" />
                    <span className="min-w-0">
                      <span className="block font-semibold break-words">{label.name}</span>
                      {label.rest !== "" ? <span className="block text-[13px] break-words text-muted">{label.rest}</span> : null}
                    </span>
                    <Icon name={isPicked ? "status_confirmed" : "chevron"} />
                  </button>
                </li>
              );
            })}
          </ul>
          <p className={`${HINT} mt-2.5`}>{t("search.pick")}</p>
        </>
      ) : null}
      {search.kind === "none" ? <p className={`${HINT} mt-2.5`}>{t("search.none.point")}</p> : null}
      <output className="block">{picked !== null ? <Note className="mt-2.5">{t("report.search.picked", { label: picked.label })}</Note> : null}</output>
    </>
  );
}

/**
 * The place of a report. The map stands in the picking mode with a fixed mark at its center: the person moves the map
 * under the mark, with touch or with the arrow keys, and confirms the point. A button moves the map to the location
 * of the device, which is read in the browser, sent nowhere and never saved by itself, and another one moves the keyboard focus
 * to the map, which stands before the panel in the order of focus. For an area the map can also be moved
 * by the address search. A point outside Kraków is refused with its message and not set.
 */
export function ReportPlaceStep() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const mountId = useId();
  const { draft, setPoint } = useReportDraft();
  const { rest, readCenter, hasFailed } = useMap();
  const [openedPoint] = useState(draft.point);
  const [moved, setMoved] = useState<MapCamera | null>(null);
  const [target, setTarget] = useState<MoveTarget | null>(null);
  const [location, setLocation] = useState<LocationState>("idle");
  const [problem, setProblem] = useState<"outside" | "unread" | null>(null);
  const latestRest = useRef(rest);

  useEffect(() => {
    latestRest.current = rest;
  });

  const scene = useMemo<MapScene>(() => {
    const opened: MapCamera | null = openedPoint === null ? null : { key: `report-place-${mountId}`, target: { kind: "point", point: openedPoint, zoom: null } };
    return { ...EMPTY_MAP_SCENE, label: t("aria.map.pick"), isPicking: true, camera: moved ?? opened };
  }, [t, mountId, openedPoint, moved]);
  useMapScene(scene);

  const open = findOpenStep(draft, "place");
  const kind = draft.kind;
  if (open !== "place" || kind === null) {
    return <Navigate to={REPORT_PATHS[open === "place" ? "kind" : open]} replace />;
  }

  const isSettling = target !== null && rest === target.restAtStart;
  const shownTarget = target !== null && (isSettling || (rest !== null && isSamePlace(rest.center, target.point))) ? target : null;
  const unreadText = kind === "area" ? "report.point.no_map.area" : "report.point.no_map";

  /**
   * Moves the map to a place and remembers it as the target of the move.
   */
  const moveTo = (point: Point, match: AddressMatch | null) => {
    setTarget({ point, match, restAtStart: latestRest.current });
    setMoved(buildMoveCamera(point));
    setProblem(null);
  };

  /**
   * Reads the location of the device in the browser and moves the map there. The location goes to no request.
   */
  const readLocation = () => readDeviceLocation((point) => moveTo(point, null), setLocation);

  /**
   * Sets the point under the mark as the place of the report and opens the details.
   * While the map is still on its way to a place the person asked for, the point is that place, not a point on the way.
   */
  const confirm = () => {
    const point = target !== null && isSettling ? target.point : readCenter();
    if (point === null) {
      setProblem("unread");
      return;
    }
    if (!isInsideKrakow(point)) {
      setProblem("outside");
      return;
    }
    setPoint(point);
    void navigate(REPORT_PATHS.details);
  };

  return (
    <Panel labelledBy={REPORT_HEADING_ID}>
      <ReportStepHead counter={t("report.step", { n: findStepNumber("place", kind), total: countSteps(kind) })} title={t(`report.point.${kind}`)} />
      {hasFailed ? (
        <Note kind="strong" className="mt-2">
          {t(unreadText)}
        </Note>
      ) : (
        <>
          <p className={PANEL_TEXT}>{t("report.point.hint")}</p>
          <p className={`${HINT} mt-2`}>{t("report.point.location")}</p>
          <div className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1">
            <Button isSmall icon="location" disabled={location === "waiting"} onClick={readLocation}>
              {t("plan.my_location")}
            </Button>
            <Button look="link" onClick={focusMap}>
              {t("report.point.to_map")}
            </Button>
          </div>
          <output className="block">
            {location === "waiting" ? <p className={`${HINT} mt-2`}>{t("plan.locating")}</p> : null}
            {location !== "idle" && location !== "waiting" ? (
              <Note kind="strong" className="mt-2">
                {t(LOCATION_TEXTS[location])}
              </Note>
            ) : null}
            {location === "idle" && shownTarget !== null && shownTarget.match === null ? <Note className="mt-2">{t("report.point.located")}</Note> : null}
          </output>
        </>
      )}
      {kind === "area" ? <AddressSearch picked={shownTarget?.match ?? null} onPick={(match) => moveTo(match.point, match)} /> : null}
      {problem !== null ? (
        <Note kind="strong" announce="alert" className="mt-3">
          {t(problem === "outside" ? "plan.outside" : unreadText)}
        </Note>
      ) : null}
      <div className={ACTIONS}>
        <Button to={REPORT_PATHS.kind}>{t("action.back")}</Button>
        <Button look="primary" disabled={hasFailed && target === null} onClick={confirm}>
          {t("plan.set_point")}
        </Button>
      </div>
    </Panel>
  );
}
