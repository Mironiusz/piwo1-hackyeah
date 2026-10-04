import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate } from "react-router";

import { findNearbyFacts } from "../../api/client.ts";
import { errorTextKey, toApiError } from "../../api/errors.ts";
import type { FactType } from "../../api/types.ts";
import { formatDistance } from "../../format/format.ts";
import { useLanguage } from "../../i18n/index.ts";
import { EMPTY_MAP_SCENE, useMapScene, type MapScene } from "../../map/mapScene.ts";
import { Button } from "../../parts/Button.tsx";
import { Field } from "../../parts/Field.tsx";
import { Icon } from "../../parts/Icon.tsx";
import { Note } from "../../parts/Note.tsx";
import { Panel } from "../../parts/Panel.tsx";
import { ACTIONS, HINT } from "../../parts/styles.ts";
import { Switch } from "../../parts/Switch.tsx";
import { listTypesOfKind, useReportDraft } from "../../state/reportDraft.tsx";
import { buildPointCamera, buildPointMarker, buildReportZone, buildZoneCamera } from "./reportMap.ts";
import { ReportStepHead } from "./ReportStepHead.tsx";
import { countSteps, DESCRIPTION_MAX_LENGTH, findOpenStep, findStepNumber, GEOZONE_RADII, readStepCount, REPORT_HEADING_ID, REPORT_PATHS } from "./reportSteps.ts";
import { useIsMounted } from "./useIsMounted.ts";

const RADIUS_LABEL_ID = "report-radius-label";
const TYPE_ERROR_ID = "report-type-error";
const FIELD_ERROR = "text-[13px] font-semibold text-barrier";

type CheckState = { kind: "idle" } | { kind: "checking" } | { kind: "failed"; textKey: string };

interface TypeOptionsProps {
  types: readonly FactType[];
  chosen: FactType | null;
  onChoose: (type: FactType) => void;
}

/**
 * The closed list of fact types of a kind as radio buttons, each with its icon and its name.
 */
function TypeOptions({ types, chosen, onChoose }: TypeOptionsProps) {
  const { t } = useTranslation();
  return (
    <ul className="border-b border-line">
      {types.map((type) => (
        <li key={type} className="border-t border-line">
          <label className="flex min-h-12 items-center gap-3 py-1.5">
            <input type="radio" name="report-type" checked={chosen === type} onChange={() => onChoose(type)} className="m-0 size-[22px] flex-none accent-shell" />
            <Icon name={type} className="text-muted" />
            <span>{t(`type.${type}`)}</span>
          </label>
        </li>
      ))}
    </ul>
  );
}

/**
 * The details of a report. For a barrier or an amenity: the type from the closed list of the kind, an optional description,
 * and for stairs an optional number of steps. For an area: the radius from the list, the barrier type and the description.
 * When the details of a barrier or an amenity are approved, the step asks the service for existing facts of the same type
 * near the point, and leads to them, or straight to the summary when there are none.
 */
export function ReportDetailsStep() {
  const { t } = useTranslation();
  const language = useLanguage();
  const navigate = useNavigate();
  const isMounted = useIsMounted();
  const { draft, setType, setDescription, setStepCount, setRadius, keepExistingFacts } = useReportDraft();
  const [stepsText, setStepsText] = useState(draft.stepCount === null ? "" : String(draft.stepCount));
  const [wasApproved, setWasApproved] = useState(false);
  const [check, setCheck] = useState<CheckState>({ kind: "idle" });

  const { kind, point, type, radiusM } = draft;
  const isArea = kind === "area";
  const zoneRadius = isArea ? radiusM : null;

  const scene = useMemo<MapScene>(() => {
    const plain: MapScene = { ...EMPTY_MAP_SCENE, label: t("report.map.point"), mapSize: "short" };
    if (point === null) {
      return plain;
    }
    return {
      ...plain,
      markers: [buildPointMarker(point, t("report.marker.point"))],
      zones: zoneRadius === null ? [] : [buildReportZone(point, zoneRadius)],
      camera: zoneRadius === null ? buildPointCamera("details", point, null) : buildZoneCamera("details", point, zoneRadius),
    };
  }, [t, point, zoneRadius]);
  useMapScene(scene);

  const open = findOpenStep(draft, "details");
  if (open !== "details" || kind === null || point === null) {
    return <Navigate to={REPORT_PATHS[open === "details" ? "kind" : open]} replace />;
  }

  const hasSteps = !isArea && type === "stairs";
  const areStepsInvalid = hasSteps && readStepCount(stepsText) === "invalid";
  const isRadiusMissing = isArea && radiusM === null;
  const isChecking = check.kind === "checking";
  const showsTypeError = wasApproved && type === null;

  /**
   * Keeps the text of the number of steps as it is typed, and its number in the draft once the text is one.
   */
  const changeSteps = (text: string) => {
    setStepsText(text);
    const count = readStepCount(text);
    setStepCount(count === "invalid" ? null : count);
  };

  /**
   * Sets the radius of the area to the one of the pressed button.
   */
  const chooseRadius = (value: string) => {
    const radius = GEOZONE_RADII.find((candidate) => String(candidate) === value);
    if (radius !== undefined) {
      setRadius(radius);
    }
  };

  /**
   * Approves the details. What is missing or wrong is named and the step stays. An area goes to its summary.
   * A barrier or an amenity is first checked against the existing facts near its point.
   */
  const approve = async () => {
    setWasApproved(true);
    if (type === null || isRadiusMissing || areStepsInvalid) {
      return;
    }
    if (isArea) {
      void navigate(REPORT_PATHS.summary);
      return;
    }
    setCheck({ kind: "checking" });
    try {
      const facts = await findNearbyFacts(type, point);
      if (!isMounted()) {
        return;
      }
      keepExistingFacts(facts);
      void navigate(facts.length > 0 ? REPORT_PATHS.existing : REPORT_PATHS.summary);
    } catch (caught) {
      if (isMounted()) {
        setCheck({ kind: "failed", textKey: errorTextKey(toApiError(caught).code) });
      }
    }
  };

  const typeOptions = <TypeOptions types={listTypesOfKind(kind)} chosen={type} onChoose={setType} />;

  return (
    <Panel labelledBy={REPORT_HEADING_ID}>
      <ReportStepHead counter={t("report.step", { n: findStepNumber("details", kind), total: countSteps(kind) })} title={t(isArea ? "report.area.title" : `report.type.${kind}`)} />
      {isArea ? (
        <>
          <p id={RADIUS_LABEL_ID} className="mt-2.5 mb-1.5 text-[13.5px] font-semibold">
            {t("report.area.radius")}
          </p>
          <Switch
            labelledBy={RADIUS_LABEL_ID}
            options={GEOZONE_RADII.map((radius) => ({ value: String(radius), label: formatDistance(radius, language) }))}
            value={radiusM === null ? "" : String(radiusM)}
            onChange={chooseRadius}
          />
          {wasApproved && isRadiusMissing ? (
            <p role="alert" className={`${FIELD_ERROR} mt-1.5`}>
              {t("report.area.radius.missing")}
            </p>
          ) : null}
          <fieldset aria-describedby={showsTypeError ? TYPE_ERROR_ID : undefined} className="m-0 mt-4 min-w-0 border-0 p-0">
            <legend className="mb-0.5 p-0 text-[13.5px] font-semibold">{t("report.area.type")}</legend>
            {typeOptions}
          </fieldset>
        </>
      ) : (
        <fieldset aria-labelledby={REPORT_HEADING_ID} aria-describedby={showsTypeError ? TYPE_ERROR_ID : undefined} disabled={isChecking} className="m-0 mt-2 min-w-0 border-0 p-0">
          {typeOptions}
        </fieldset>
      )}
      {showsTypeError ? (
        <p id={TYPE_ERROR_ID} role="alert" className={`${FIELD_ERROR} mt-1.5`}>
          {t("report.type.missing")}
        </p>
      ) : null}
      {hasSteps ? (
        <Field
          id="report-steps"
          label={t("fact.steps")}
          value={stepsText}
          onChange={changeSteps}
          isOptional
          inputMode="numeric"
          autoComplete="off"
          error={wasApproved && areStepsInvalid ? t("report.steps.invalid") : null}
          className="mt-3.5 max-w-[220px]"
        />
      ) : null}
      <Field
        id="report-description"
        label={t("fact.description")}
        value={draft.description}
        onChange={setDescription}
        isOptional
        isMultiline
        maxLength={DESCRIPTION_MAX_LENGTH}
        hint={t("report.description.hint")}
      />
      <output className="block">{isChecking ? <p className={`${HINT} mt-3`}>{t("report.existing.checking")}</p> : null}</output>
      {check.kind === "failed" ? (
        <Note kind="strong" announce="alert" className="mt-3">
          {t(check.textKey)}
        </Note>
      ) : null}
      <div className={ACTIONS}>
        <Button to={REPORT_PATHS.place}>{t("action.back")}</Button>
        <Button look="primary" disabled={isChecking} onClick={() => void approve()}>
          {t("action.next")}
        </Button>
      </div>
    </Panel>
  );
}
