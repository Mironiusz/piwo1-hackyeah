import { startTransition, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate } from "react-router";

import { useLanguage } from "../../i18n/index.ts";
import { EMPTY_MAP_SCENE, useMapScene, type MapScene } from "../../map/mapScene.ts";
import { Button } from "../../parts/Button.tsx";
import { Note } from "../../parts/Note.tsx";
import { Panel } from "../../parts/Panel.tsx";
import { ACTIONS, PANEL_TEXT } from "../../parts/styles.ts";
import { readLastMapPath } from "../../state/lastMapPath.ts";
import { useReportDraft } from "../../state/reportDraft.tsx";
import { buildFactMarker, buildFactZones } from "../factDetail.ts";
import { ReportFactLine } from "./ReportFactLine.tsx";
import { buildPointCamera, buildZoneCamera, REPORT_POINT_ZOOM } from "./reportMap.ts";
import { ReportStepHead } from "./ReportStepHead.tsx";
import { findOpenStep, REPORT_HEADING_ID, REPORT_PATHS } from "./reportSteps.ts";

/**
 * The saved report: the message, the new fact as the service returned it, on the map and as text,
 * and the two ways on, another report or the map. A saved report offers no way to change it.
 */
export function ReportSavedStep() {
  const { t } = useTranslation();
  const language = useLanguage();
  const navigate = useNavigate();
  const { draft, clear } = useReportDraft();
  const saved = draft.savedFact;

  const scene = useMemo<MapScene>(() => {
    const plain: MapScene = { ...EMPTY_MAP_SCENE, label: t("report.map.saved") };
    if (saved === null) {
      return plain;
    }
    return {
      ...plain,
      markers: [{ ...buildFactMarker(saved, true, false, t, language), isPressable: false }],
      zones: buildFactZones([saved]),
      hasSampleData: saved.is_sample,
      camera: saved.geozone_radius_m === null ? buildPointCamera("saved", saved.point, REPORT_POINT_ZOOM) : buildZoneCamera("saved", saved.point, saved.geozone_radius_m),
    };
  }, [t, language, saved]);
  useMapScene(scene);

  const open = findOpenStep(draft, "saved");
  if (open !== "saved" || saved === null) {
    return <Navigate to={REPORT_PATHS.kind} replace />;
  }

  /**
   * Starts a new report from the first step. The draft is cleared in the same change of the screen as the address.
   */
  const reportAgain = () => {
    startTransition(clear);
    void navigate(REPORT_PATHS.kind, { replace: true });
  };

  return (
    <Panel labelledBy={REPORT_HEADING_ID}>
      <ReportStepHead counter={null} title={t("report.saved.title")} hasCancel={false} />
      <p className={PANEL_TEXT}>{t("report.saved.body")}</p>
      <ReportFactLine fact={saved} />
      <Note>{t("report.saved.hint")}</Note>
      <div className={ACTIONS}>
        <Button onClick={reportAgain}>{t("report.again")}</Button>
        <Button look="primary" to={readLastMapPath()}>
          {t("report.to_map")}
        </Button>
      </div>
    </Panel>
  );
}
