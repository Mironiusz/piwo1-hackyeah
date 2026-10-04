import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { Icon } from "../../parts/Icon.tsx";
import { PANEL_TITLE, STEP_TEXT } from "../../parts/styles.ts";
import { readLastMapPath } from "../../state/lastMapPath.ts";
import { REPORT_HEADING_ID } from "./reportSteps.ts";
import { useHeadingFocus } from "./useHeadingFocus.ts";

const COUNTER_ID = "report-step-counter";

interface ReportStepHeadProps {
  counter: string | null;
  title: string;
  hasCancel?: boolean;
  focusKey?: string;
}

/**
 * The head of a step of the flow: the step counter, the heading of the view, which takes the focus when the step opens,
 * and the way to cancel the report, which leads back to the map and saves nothing.
 * A finished flow shows the heading alone.
 */
export function ReportStepHead({ counter, title, hasCancel = true, focusKey = "" }: ReportStepHeadProps) {
  const { t } = useTranslation();
  const heading = useHeadingFocus(focusKey);
  return (
    <div className="flex items-start gap-2">
      <div className="min-w-0 flex-1">
        {counter !== null ? (
          <p id={COUNTER_ID} className={STEP_TEXT}>
            {counter}
          </p>
        ) : null}
        <h1 id={REPORT_HEADING_ID} ref={heading} tabIndex={-1} aria-describedby={counter !== null ? COUNTER_ID : undefined} className={`${PANEL_TITLE} outline-none`}>
          {title}
        </h1>
      </div>
      {hasCancel ? (
        <Link to={readLastMapPath()} aria-label={t("report.cancel")} className="inline-flex size-11 flex-none items-center justify-center rounded-panel text-ink">
          <Icon name="close" />
        </Link>
      ) : null}
    </div>
  );
}
