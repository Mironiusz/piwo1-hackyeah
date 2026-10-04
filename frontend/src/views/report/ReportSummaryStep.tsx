import { startTransition, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate } from "react-router";

import { createFact } from "../../api/client.ts";
import { toApiError } from "../../api/errors.ts";
import { formatDistance } from "../../format/format.ts";
import { useLanguage } from "../../i18n/index.ts";
import { EMPTY_MAP_SCENE, useMapScene, type MapScene } from "../../map/mapScene.ts";
import { Button } from "../../parts/Button.tsx";
import { nameFact, nameTypeInSentence } from "../../parts/factText.ts";
import { Note } from "../../parts/Note.tsx";
import { Panel } from "../../parts/Panel.tsx";
import { ACTIONS, HINT, KEY_VALUE_KEY, KEY_VALUE_LIST, KEY_VALUE_VALUE } from "../../parts/styles.ts";
import { usePlannedRoute } from "../../state/plannedRoute.tsx";
import { useReportDraft } from "../../state/reportDraft.tsx";
import { useSession } from "../../state/session.tsx";
import { buildPointCamera, buildReportMarker, buildReportZone, buildZoneCamera, REPORT_POINT_ZOOM } from "./reportMap.ts";
import { ReportStepHead } from "./ReportStepHead.tsx";
import { buildCreateFactRequest, countSteps, findOpenStep, findStepNumber, hasExistingStep, makeIdempotencyKey, rememberConfirmation, REPORT_HEADING_ID, REPORT_PATHS } from "./reportSteps.ts";
import { useIsMounted } from "./useIsMounted.ts";

type SaveState = "idle" | "saving" | "failed";

/**
 * The summary of a report: its kind, its type, its place and the optional fields, with the point on the map
 * and for an area its circle. Nothing is sent before a person approves it here. The approval makes the key of the save once
 * and keeps it in the draft, so every further attempt of a save that failed sends the same key and nothing is saved twice.
 */
export function ReportSummaryStep() {
  const { t } = useTranslation();
  const language = useLanguage();
  const navigate = useNavigate();
  const isMounted = useIsMounted();
  const { draft, keepIdempotencyKey, dropIdempotencyKey, keepSavedFact } = useReportDraft();
  const { markStale } = usePlannedRoute();
  const { account } = useSession();
  const [save, setSave] = useState<SaveState>("idle");

  const { kind, point, type } = draft;
  const zoneRadius = kind === "area" ? draft.radiusM : null;
  const stepCount = kind !== "area" && type === "stairs" ? draft.stepCount : null;
  const name = type === null ? "" : nameFact({ type, geozone_radius_m: zoneRadius, step_count: stepCount }, t, language);

  const scene = useMemo<MapScene>(() => {
    const plain: MapScene = { ...EMPTY_MAP_SCENE, label: t("report.map.point") };
    if (kind === null || point === null || type === null) {
      return plain;
    }
    return {
      ...plain,
      markers: [buildReportMarker(kind, type, point, name)],
      zones: zoneRadius === null ? [] : [buildReportZone(point, zoneRadius)],
      camera: zoneRadius === null ? buildPointCamera("summary", point, REPORT_POINT_ZOOM) : buildZoneCamera("summary", point, zoneRadius),
    };
  }, [t, kind, point, type, zoneRadius, name]);
  useMapScene(scene);

  const open = findOpenStep(draft, "summary");
  if (open !== "summary" || kind === null || type === null) {
    return <Navigate to={REPORT_PATHS[open === "summary" ? "kind" : open]} replace />;
  }

  const description = draft.description.trim();
  const isSaving = save === "saving";

  /**
   * Saves the report. The key is made at the first approval and stays in the draft until the save succeeds.
   * Only when the service answers that the key already saved another content is it dropped,
   * because a further attempt with it could never succeed.
   * The saved fact goes to the draft also when the person has moved to another step meanwhile, so that step shows the saved state;
   * here the saved fact and the address of the saved state change in one change of the screen.
   * A saved report carries the confirmation of its author, so the device remembers it as the own vote of the person on the new fact.
   */
  const approve = async () => {
    const key = draft.idempotencyKey ?? makeIdempotencyKey();
    const body = buildCreateFactRequest(draft, key);
    if (body === null) {
      return;
    }
    if (draft.idempotencyKey === null) {
      keepIdempotencyKey(key);
    }
    setSave("saving");
    try {
      const fact = await createFact(body);
      rememberConfirmation(fact.id, account?.pseudonym ?? null);
      markStale();
      startTransition(() => keepSavedFact(fact));
      if (isMounted()) {
        void navigate(REPORT_PATHS.saved, { replace: true });
      }
    } catch (caught) {
      if (toApiError(caught).code === "idempotency_key_reused") {
        dropIdempotencyKey();
      }
      if (isMounted()) {
        setSave("failed");
      }
    }
  };

  return (
    <Panel labelledBy={REPORT_HEADING_ID}>
      <ReportStepHead counter={t("report.step", { n: findStepNumber("summary", kind), total: countSteps(kind) })} title={t("report.summary.title")} />
      <dl className={KEY_VALUE_LIST}>
        <dt className={KEY_VALUE_KEY}>{t("report.summary.kind")}</dt>
        <dd className={KEY_VALUE_VALUE}>{t(`kind.${kind}`)}</dd>
        <dt className={KEY_VALUE_KEY}>{t("report.summary.type")}</dt>
        <dd className={KEY_VALUE_VALUE}>{nameTypeInSentence(type, t, language)}</dd>
        {stepCount !== null ? (
          <>
            <dt className={KEY_VALUE_KEY}>{t("fact.steps")}</dt>
            <dd className={KEY_VALUE_VALUE}>{stepCount}</dd>
          </>
        ) : null}
        {zoneRadius !== null ? (
          <>
            <dt className={KEY_VALUE_KEY}>{t("fact.radius")}</dt>
            <dd className={KEY_VALUE_VALUE}>{formatDistance(zoneRadius, language)}</dd>
          </>
        ) : null}
        <dt className={KEY_VALUE_KEY}>{t("report.summary.place")}</dt>
        <dd className={KEY_VALUE_VALUE}>{t("report.summary.point")}</dd>
        {description !== "" ? (
          <>
            <dt className={KEY_VALUE_KEY}>{t("fact.description")}</dt>
            <dd className="break-words whitespace-pre-line">{description}</dd>
          </>
        ) : null}
      </dl>
      <Note>{t("report.summary.note")}</Note>
      <output className="block">{isSaving ? <p className={`${HINT} mt-3`}>{t("report.saving")}</p> : null}</output>
      {save === "failed" ? (
        <Note kind="strong" announce="alert" className="mt-3">
          {t("report.failed")}
        </Note>
      ) : null}
      <div className={ACTIONS}>
        <Button to={hasExistingStep(draft) ? REPORT_PATHS.existing : REPORT_PATHS.details}>{t("action.back")}</Button>
        <Button look="primary" disabled={isSaving} onClick={() => void approve()}>
          {t("report.save")}
        </Button>
      </div>
    </Panel>
  );
}
