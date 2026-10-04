import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate } from "react-router";

import { EMPTY_MAP_SCENE, useMapScene, type MapScene } from "../../map/mapScene.ts";
import { Button } from "../../parts/Button.tsx";
import { Panel } from "../../parts/Panel.tsx";
import { ACTIONS } from "../../parts/styles.ts";
import { readLastMapPath } from "../../state/lastMapPath.ts";
import { useReportDraft, type ReportKind } from "../../state/reportDraft.tsx";
import { ReportStepHead } from "./ReportStepHead.tsx";
import { countSteps, findOpenStep, findStepNumber, REPORT_HEADING_ID, REPORT_KINDS, REPORT_PATHS } from "./reportSteps.ts";

const FIRST_KIND: ReportKind = "barrier";

/**
 * The first step of a report: what a person reports, a barrier, an amenity or an area, each with a hint of what it covers.
 * The barrier is chosen until the person picks another kind, as the mock of the step shows it.
 */
export function ReportKindStep() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { draft, setKind } = useReportDraft();

  const scene = useMemo<MapScene>(() => ({ ...EMPTY_MAP_SCENE, label: t("report.map.plain") }), [t]);
  useMapScene(scene);

  const open = findOpenStep(draft, "kind");
  if (open !== "kind") {
    return <Navigate to={REPORT_PATHS[open]} replace />;
  }

  const chosen = draft.kind ?? FIRST_KIND;

  /**
   * Keeps the chosen kind, also when it is the one chosen from the start, and opens the step of the place.
   */
  const approve = () => {
    setKind(chosen);
    void navigate(REPORT_PATHS.place);
  };

  return (
    <Panel labelledBy={REPORT_HEADING_ID}>
      <ReportStepHead counter={t("report.step", { n: findStepNumber("kind", chosen), total: countSteps(chosen) })} title={t("report.kind.title")} />
      <fieldset aria-labelledby={REPORT_HEADING_ID} className="m-0 mt-2 min-w-0 border-0 p-0">
        <ul className="border-b border-line">
          {REPORT_KINDS.map((kind) => (
            <li key={kind} className="border-t border-line">
              <label className="flex min-h-12 items-center gap-3 py-1.5">
                <input type="radio" name="report-kind" checked={chosen === kind} onChange={() => setKind(kind)} className="m-0 size-[22px] flex-none accent-shell" />
                <span>
                  {t(`report.kind.${kind}`)}
                  <span className="block text-[12.5px] text-muted">{t(`report.kind.${kind}.hint`)}</span>
                </span>
              </label>
            </li>
          ))}
        </ul>
      </fieldset>
      <div className={ACTIONS}>
        <Button to={readLastMapPath()}>{t("action.cancel")}</Button>
        <Button look="primary" onClick={approve}>
          {t("action.next")}
        </Button>
      </div>
    </Panel>
  );
}
