import { useMemo, useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { Link, Navigate, useNavigate, useParams } from "react-router";

import { searchAddress } from "../api/client.ts";
import { toApiError } from "../api/errors.ts";
import type { AddressMatch } from "../api/types.ts";
import { isInsideKrakow } from "../map/krakowBounds.ts";
import { EMPTY_MAP_SCENE, useMapScene, type MapScene } from "../map/mapScene.ts";
import { Button } from "../parts/Button.tsx";
import { Icon } from "../parts/Icon.tsx";
import { Note } from "../parts/Note.tsx";
import { Panel } from "../parts/Panel.tsx";
import { HINT, PANEL_TITLE } from "../parts/styles.ts";
import { usePlannedRoute } from "../state/plannedRoute.tsx";
import { buildEndMarkers, buildEndsCamera, isRouteEndName, splitLabel } from "./routeText.ts";

const MAX_TEXT_LENGTH = 200;

type SearchState =
  | { kind: "idle" }
  | { kind: "searching" }
  | { kind: "results"; matches: AddressMatch[] }
  | { kind: "none" }
  | { kind: "unavailable" }
  | { kind: "invalid" }
  | { kind: "outside" }
  | { kind: "failed"; textKey: string };

/**
 * The address search for an end of the route. It asks the service only when the person submits the text,
 * with the Enter key or the button, and suggests nothing while typing. The matches are always a list to pick from,
 * also when there is one, and nothing is set until the person picks. The text never stands in the address of the page.
 */
export function AddressSearchView() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const params = useParams();
  const { start, destination, setEnd } = usePlannedRoute();
  const [text, setText] = useState("");
  const [search, setSearch] = useState<SearchState>({ kind: "idle" });

  const scene = useMemo<MapScene>(
    () => ({
      ...EMPTY_MAP_SCENE,
      label: t("aria.map.route"),
      mapSize: "short",
      markers: buildEndMarkers(start, destination, t),
      camera: buildEndsCamera(start?.point ?? null, destination?.point ?? null),
    }),
    [t, start, destination],
  );
  useMapScene(scene);

  const end = params.end;
  if (!isRouteEndName(end)) {
    return <Navigate to="/route" replace />;
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (text.trim() === "" || [...text].length > MAX_TEXT_LENGTH) {
      setSearch({ kind: "invalid" });
      return;
    }
    setSearch({ kind: "searching" });
    try {
      const matches = await searchAddress(text);
      setSearch(matches.length === 0 ? { kind: "none" } : { kind: "results", matches });
    } catch (caught) {
      const error = toApiError(caught);
      if (error.code === "invalid_search_text") {
        setSearch({ kind: "invalid" });
      } else if (error.code === "address_search_unavailable") {
        setSearch({ kind: "unavailable" });
      } else {
        setSearch({ kind: "failed", textKey: error.code === "network_error" ? "state.offline" : "state.failed" });
      }
    }
  };

  const pick = (match: AddressMatch) => {
    if (!isInsideKrakow(match.point)) {
      setSearch({ kind: "outside" });
      return;
    }
    setEnd(end, { point: match.point, kind: "address", label: match.label });
    void navigate("/route");
  };

  const isInvalid = search.kind === "invalid";

  return (
    <Panel>
      <div className="flex items-start gap-2">
        <h1 tabIndex={-1} className={`${PANEL_TITLE} min-w-0 flex-1 outline-none`}>
          {t(`search.title.${end}`)}
        </h1>
        <Link to="/route" aria-label={t("search.close")} className="inline-flex size-11 flex-none items-center justify-center rounded-panel text-ink">
          <Icon name="close" />
        </Link>
      </div>

      <form onSubmit={(event) => void submit(event)} noValidate className="mt-1.5 grid gap-[5px]">
        <label htmlFor="address-text" className="text-[13.5px] font-semibold">
          {t("search.field")}
        </label>
        <div className="grid grid-cols-[1fr_auto] gap-2">
          <input
            id="address-text"
            type="search"
            value={text}
            onChange={(event) => setText(event.target.value)}
            enterKeyHint="search"
            autoComplete="off"
            aria-invalid={isInvalid}
            aria-describedby={isInvalid ? "address-text-error address-text-hint" : "address-text-hint"}
            className={`min-h-[46px] w-full rounded-panel border-[1.5px] bg-white px-3 py-2 text-[16px] text-ink ${isInvalid ? "border-barrier" : "border-field"}`}
          />
          <Button type="submit" look="primary" disabled={search.kind === "searching"}>
            {t("search.submit")}
          </Button>
        </div>
        {isInvalid ? (
          <p id="address-text-error" role="alert" className="text-[13px] font-semibold text-barrier">
            {t("search.invalid")}
          </p>
        ) : null}
        <p id="address-text-hint" className={HINT}>
          {t("search.hint")}
        </p>
      </form>

      <output className="mt-[18px] block">
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
      {search.kind === "unavailable" || search.kind === "failed" || search.kind === "outside" ? (
        <Note kind="strong" announce="alert">
          {t(search.kind === "unavailable" ? "search.unavailable" : search.kind === "outside" ? "plan.outside" : search.textKey)}
        </Note>
      ) : null}

      {search.kind === "results" ? (
        <>
          <ul className="mt-1.5 border-b border-line">
            {search.matches.map((match) => {
              const label = splitLabel(match.label);
              return (
                <li key={`${match.label}-${match.point.lat}-${match.point.lon}`} className="border-t border-line">
                  <button type="button" onClick={() => pick(match)} className="grid min-h-14 w-full grid-cols-[24px_1fr_auto] items-center gap-2.5 py-3 text-left -outline-offset-[3px]">
                    <Icon name="pin" />
                    <span className="min-w-0">
                      <span className="block font-semibold break-words">{label.name}</span>
                      {label.rest !== "" ? <span className="block text-[13px] break-words text-muted">{label.rest}</span> : null}
                    </span>
                    <Icon name="chevron" />
                  </button>
                </li>
              );
            })}
          </ul>
          <p className={`${HINT} mt-2.5`}>{t("search.pick")}</p>
        </>
      ) : null}
      {search.kind === "none" ? <p className={`${HINT} mt-2.5`}>{t("search.none.point")}</p> : null}

      <div className="mt-2">
        <Button look="link" to={`/route/pick/${end}`}>
          {t("search.map_point")}
        </Button>
      </div>
    </Panel>
  );
}
