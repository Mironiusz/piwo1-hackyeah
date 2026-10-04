import { startTransition, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate } from "react-router";

import { castVote } from "../../api/client.ts";
import { toApiError } from "../../api/errors.ts";
import type { Fact } from "../../api/types.ts";
import { formatDay } from "../../format/format.ts";
import { useLanguage } from "../../i18n/index.ts";
import { EMPTY_MAP_SCENE, useMapScene, type MapScene } from "../../map/mapScene.ts";
import { Button } from "../../parts/Button.tsx";
import { Note } from "../../parts/Note.tsx";
import { Panel } from "../../parts/Panel.tsx";
import { ACTIONS, HINT, PANEL_TEXT } from "../../parts/styles.ts";
import { readLastMapPath } from "../../state/lastMapPath.ts";
import { startOfNextDay } from "../../state/ownVotes.ts";
import { usePlannedRoute } from "../../state/plannedRoute.tsx";
import { useReportDraft } from "../../state/reportDraft.tsx";
import { useSession } from "../../state/session.tsx";
import { buildFactMarker, buildFactZones } from "../factDetail.ts";
import { ReportFactLine } from "./ReportFactLine.tsx";
import { buildPointCamera, buildPointMarker } from "./reportMap.ts";
import { ReportStepHead } from "./ReportStepHead.tsx";
import { countSteps, findOpenStep, findStepNumber, rememberConfirmation, REPORT_HEADING_ID, REPORT_PATHS } from "./reportSteps.ts";

const EXISTING_ZOOM = 18;

type VoteState = { kind: "idle" } | { kind: "saving" } | { kind: "confirmed"; fact: Fact } | { kind: "too_soon"; repeatAllowedAt: string | null } | { kind: "failed"; textKey: string };

/**
 * The existing facts of the same type near the point of a report, each with what a fact shows and its distance,
 * and the question whether the report is one of them. The answer that it is the same confirms that fact with a vote
 * and saves no report; a vote refused because the person already voted on that fact the same day is a plain message. The answer that it is something else
 * leads to the summary.
 */
export function ReportExistingStep() {
  const { t } = useTranslation();
  const language = useLanguage();
  const navigate = useNavigate();
  const { draft, clear } = useReportDraft();
  const { markStale } = usePlannedRoute();
  const { account } = useSession();
  const [vote, setVote] = useState<VoteState>({ kind: "idle" });
  const [goneIds, setGoneIds] = useState<readonly number[]>([]);
  const [openedAt] = useState(() => new Date());

  const { kind, point, existingFacts } = draft;
  const confirmed = vote.kind === "confirmed" ? vote.fact : null;
  const shown = useMemo(() => (existingFacts ?? []).filter((item) => !goneIds.includes(item.fact.id)), [existingFacts, goneIds]);

  const scene = useMemo<MapScene>(() => {
    const plain: MapScene = { ...EMPTY_MAP_SCENE, label: t("report.map.existing"), mapSize: "short" };
    if (point === null) {
      return plain;
    }
    const facts = confirmed !== null ? [confirmed] : shown.map((item) => item.fact);
    const factMarkers = facts.map((fact) => ({ ...buildFactMarker(fact, confirmed !== null, false, t, language), isPressable: false }));
    return {
      ...plain,
      markers: confirmed !== null ? factMarkers : [buildPointMarker(point, t("report.marker.point")), ...factMarkers],
      zones: buildFactZones(facts),
      hasSampleData: facts.some((fact) => fact.is_sample),
      camera: buildPointCamera("existing", point, EXISTING_ZOOM),
    };
  }, [t, language, point, shown, confirmed]);
  useMapScene(scene);

  const open = findOpenStep(draft, "existing");
  if (open !== "existing" || kind === null) {
    return <Navigate to={REPORT_PATHS[open === "existing" ? "kind" : open]} replace />;
  }

  const isSaving = vote.kind === "saving";

  /**
   * Confirms an existing fact in place of a new report, remembers the vote on the device,
   * and asks for a shown route to be planned again.
   */
  const confirmSame = async (fact: Fact) => {
    setVote({ kind: "saving" });
    try {
      const after = await castVote(fact.id, "confirm");
      rememberConfirmation(fact.id, account?.pseudonym ?? null);
      markStale();
      setVote({ kind: "confirmed", fact: after });
    } catch (caught) {
      const error = toApiError(caught);
      if (error.code === "vote_too_soon") {
        setVote({ kind: "too_soon", repeatAllowedAt: error.repeatAllowedAt });
      } else if (error.code === "fact_not_found") {
        setGoneIds((ids) => [...ids, fact.id]);
        setVote({ kind: "failed", textKey: "fact.gone" });
      } else {
        setVote({ kind: "failed", textKey: error.code === "network_error" ? "state.offline" : "vote.failed" });
      }
    }
  };

  /**
   * Starts a new report from the first step. The draft is cleared in the same change of the screen as the address.
   */
  const reportAgain = () => {
    startTransition(clear);
    void navigate(REPORT_PATHS.kind, { replace: true });
  };

  return (
    <Panel labelledBy={REPORT_HEADING_ID}>
      <ReportStepHead
        counter={confirmed === null ? t("report.step", { n: findStepNumber("existing", kind), total: countSteps(kind) }) : null}
        title={t(confirmed === null ? "report.existing.title" : "report.existing.confirmed")}
        hasCancel={confirmed === null}
        focusKey={confirmed === null ? `asking-${goneIds.length}` : "confirmed"}
      />
      {confirmed === null ? <p className={PANEL_TEXT}>{t("report.existing.body")}</p> : null}
      <output className="block">
        {isSaving ? <p className={`${HINT} mt-2`}>{t("vote.saving")}</p> : null}
        {vote.kind === "too_soon" ? <Note className="mt-2">{t("vote.too_soon", { day: formatDay(vote.repeatAllowedAt ?? startOfNextDay(openedAt), language) })}</Note> : null}
        {confirmed !== null ? <Note className="mt-2">{t("vote.saved", { status: t(`status.${confirmed.status}`) })}</Note> : null}
      </output>
      {vote.kind === "failed" ? (
        <Note kind="strong" announce="alert" className="mt-2">
          {t(vote.textKey)}
        </Note>
      ) : null}
      {confirmed !== null ? (
        <ReportFactLine fact={confirmed} />
      ) : (
        <ul className="mt-2.5">
          {shown.map((item) => {
            const sameId = `report-existing-${item.fact.id}-same`;
            const titleId = `report-existing-${item.fact.id}-title`;
            const distanceId = `report-existing-${item.fact.id}-distance`;
            return (
              <li key={item.fact.id} className="border-t border-line">
                <ReportFactLine fact={item.fact} titleId={titleId} aside={t("report.existing.distance", { n: item.distance_m })} asideId={distanceId}>
                  <Button id={sameId} isSmall disabled={isSaving} aria-labelledby={`${sameId} ${titleId} ${distanceId}`} onClick={() => void confirmSame(item.fact)}>
                    {t("report.existing.same")}
                  </Button>
                </ReportFactLine>
              </li>
            );
          })}
        </ul>
      )}
      {confirmed !== null ? (
        <div className={ACTIONS}>
          <Button onClick={reportAgain}>{t("report.again")}</Button>
          <Button look="primary" to={readLastMapPath()}>
            {t("report.to_map")}
          </Button>
        </div>
      ) : (
        <div className={ACTIONS}>
          <Button to={REPORT_PATHS.details}>{t("action.back")}</Button>
          <Button look="primary" disabled={isSaving} onClick={() => void navigate(REPORT_PATHS.summary)}>
            {t("report.existing.other")}
          </Button>
        </div>
      )}
    </Panel>
  );
}
