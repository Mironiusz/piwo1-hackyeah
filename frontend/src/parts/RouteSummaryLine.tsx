import { useTranslation } from "react-i18next";

import type { AnsweredSegmentState, Route, RouteFact } from "../api/types.ts";
import { formatDistance } from "../format/format.ts";
import { useLanguage } from "../i18n/index.ts";
import { nameTypeInSentence } from "./factText.ts";
import { joinSummaryStretches, placeSummaryStops } from "./routeSummary.ts";

interface RouteSummaryLineProps {
  route: Route;
  isAssessed: boolean;
  startName: string;
  destinationName: string;
}

const STRETCH_LOOKS: Record<AnsweredSegmentState, string> = {
  not_assessed: "bg-white outline-2 outline-shell",
  no_barrier: "bg-clear",
  barrier: "bg-[repeating-linear-gradient(90deg,var(--color-barrier)_0_3px,var(--color-white)_3px_6px)] outline-2 outline-barrier",
  partial_data: "bg-[repeating-linear-gradient(90deg,var(--color-partial)_0_7px,var(--color-ink)_7px_10px)]",
  no_data: "bg-[repeating-linear-gradient(90deg,var(--color-nodata)_0_3px,transparent_3px_9px)]",
};

const STOP = "absolute top-1/2 -mt-2 -ml-2 size-4 rounded-full border-[3px] border-ink bg-white";

const LABEL_ALIGNS = {
  left: "left-[-4px]",
  center: "left-1/2 -translate-x-1/2",
  right: "right-[-4px]",
} as const;

/**
 * The route as one straightened line: its stretches in the order of the route, each in the pattern of its segment state,
 * a stop for every barrier of the needs, and the names of the start and the destination under its ends.
 * The line itself is a drawing; the same stretches stand next to it as a text in order, which a screen reader reads.
 * A route that is not assessed is one hollow line, which is none of the four states.
 */
export function RouteSummaryLine({ route, isAssessed, startName, destinationName }: RouteSummaryLineProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  const stretches = joinSummaryStretches(route);
  const stops = isAssessed ? placeSummaryStops(route.profile_barriers, route.length_m, (fact: RouteFact) => nameTypeInSentence(fact.type, t, language)) : [];
  const description = isAssessed
    ? t("route.summary.text", {
        stretches: stretches.map((stretch) => t("route.summary.stretch", { distance: formatDistance(stretch.lengthM, language), state: t(`segment.short.${stretch.state}`) })).join(", "),
      })
    : t("route.summary.not_assessed", { distance: formatDistance(route.length_m, language) });

  return (
    <div className="my-3 rounded-panel bg-white px-3.5 pt-2 pb-3 text-ink">
      <div aria-hidden="true" className="relative mx-1 mt-[22px] mb-3.5 flex h-2.5">
        {isAssessed ? (
          stretches.map((stretch, index) => <i key={index} className={`block h-full ${STRETCH_LOOKS[stretch.state]}`} style={{ width: `${(stretch.lengthM / Math.max(1, route.length_m)) * 100}%` }} />)
        ) : (
          <i className="block h-full w-full bg-white outline-2 outline-shell" />
        )}
        <span className={STOP} style={{ left: "0%" }} />
        {stops.map((stop) => (
          <span key={stop.factId} className={STOP} style={{ left: `${stop.share * 100}%` }}>
            {stop.label !== null ? (
              <em className={`absolute bottom-[17px] text-[12px] leading-none font-semibold whitespace-nowrap text-ink not-italic ${LABEL_ALIGNS[stop.align]}`}>{stop.label}</em>
            ) : null}
          </span>
        ))}
        <span className={STOP} style={{ left: "100%" }} />
      </div>
      <p className="sr-only">{description}</p>
      <div className="flex justify-between gap-3 text-[14px] leading-[1.15] font-semibold">
        <span className="min-w-0 break-words">
          <span className="sr-only">{`${t("route.summary.start")}: `}</span>
          {startName}
        </span>
        <span className="min-w-0 text-right break-words">
          <span className="sr-only">{`${t("route.summary.destination")}: `}</span>
          {destinationName}
        </span>
      </div>
    </div>
  );
}
