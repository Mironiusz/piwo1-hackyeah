import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate, useParams } from "react-router";

import { isInsideKrakow } from "../map/krakowBounds.ts";
import { EMPTY_MAP_SCENE, useMap, useMapScene, type MapScene } from "../map/mapScene.ts";
import { Button } from "../parts/Button.tsx";
import { Note } from "../parts/Note.tsx";
import { Panel } from "../parts/Panel.tsx";
import { ACTIONS, PANEL_TEXT, PANEL_TITLE } from "../parts/styles.ts";
import { usePlannedRoute } from "../state/plannedRoute.tsx";
import { isRouteEndName } from "./routeText.ts";

/**
 * Picking an end of the route on the map: a fixed mark stands at the center of the map,
 * the person moves the map under it, with touch or with the arrow keys, and confirms the point.
 * A point outside Kraków is refused with its message and not set.
 */
export function PointPickView() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const params = useParams();
  const { setEnd } = usePlannedRoute();
  const { readCenter, hasFailed } = useMap();
  const [isOutside, setIsOutside] = useState(false);

  const scene = useMemo<MapScene>(() => ({ ...EMPTY_MAP_SCENE, label: t("aria.map.pick"), isPicking: true }), [t]);
  useMapScene(scene);

  const end = params.end;
  if (!isRouteEndName(end)) {
    return <Navigate to="/route" replace />;
  }

  const confirm = () => {
    const point = readCenter();
    if (point === null) {
      return;
    }
    if (!isInsideKrakow(point)) {
      setIsOutside(true);
      return;
    }
    setEnd(end, { point, kind: "map", label: null });
    void navigate("/route");
  };

  return (
    <Panel>
      <h1 tabIndex={-1} className={`${PANEL_TITLE} outline-none`}>
        {t(`pick.title.${end}`)}
      </h1>
      <p className={PANEL_TEXT}>{t("plan.pick_point")}</p>
      {isOutside ? (
        <Note kind="strong" announce="alert" className="mt-3">
          {t("plan.outside")}
        </Note>
      ) : null}
      {hasFailed ? (
        <div className="mt-3">
          <Button look="link" to={`/route/search/${end}`}>
            {t("plan.address")}
          </Button>
        </div>
      ) : null}
      <div className={ACTIONS}>
        <Button to="/route">{t("action.cancel")}</Button>
        <Button look="primary" disabled={hasFailed} onClick={confirm}>
          {t("plan.set_point")}
        </Button>
      </div>
    </Panel>
  );
}
