import { useTranslation } from "react-i18next";

import { readOsmCopy } from "../api/client.ts";
import type { FactStatus, SegmentState } from "../api/types.ts";
import { formatDay } from "../format/format.ts";
import { useRequest } from "../hooks/useRequest.ts";
import { useLanguage } from "../i18n/index.ts";
import { ROUTE_COLORS } from "../map/routeLayers.ts";
import { Note } from "../parts/Note.tsx";
import { SampleMark } from "../parts/SampleMark.tsx";
import { StatusMark } from "../parts/StatusMark.tsx";
import { PAGE_HEADING, PAGE_LEAD, PAGE_TEXT, PAGE_TITLE, TEXT_LIST, TEXT_LIST_ITEM } from "../parts/styles.ts";
import { LeadItem } from "./LeadItem.tsx";
import { PageBack } from "./PageBack.tsx";
import { splitAroundPart, splitLeadSentence } from "./textParts.ts";

const STATUSES: readonly FactStatus[] = ["unverified", "confirmed", "disputed", "outdated"];

const SEGMENT_STATES: readonly SegmentState[] = ["barrier", "no_barrier", "partial_data", "no_data"];

/**
 * The sample of a line in one of the four segment states, with the same color and the same pattern as the legend
 * and the route on the map draw it. It is decoration: the text next to it names the state.
 */
function SegmentSample({ state }: { state: SegmentState }) {
  const line = { x1: 2, y1: 6, x2: 34, y2: 6 };
  return (
    <svg aria-hidden="true" focusable="false" viewBox="0 0 36 12" width={36} height={12} className="mt-1 flex-none">
      {state === "barrier" ? (
        <>
          <line {...line} stroke={ROUTE_COLORS.barrier} strokeWidth={7} />
          <line {...line} stroke={ROUTE_COLORS.casing} strokeWidth={7} strokeDasharray="2.5 5" />
        </>
      ) : null}
      {state === "no_barrier" ? <line {...line} stroke={ROUTE_COLORS.no_barrier} strokeWidth={7} /> : null}
      {state === "partial_data" ? (
        <>
          <line {...line} stroke={ROUTE_COLORS.partial_data} strokeWidth={7} />
          <line {...line} stroke={ROUTE_COLORS.ink} strokeWidth={2.5} strokeDasharray="7 7" />
        </>
      ) : null}
      {state === "no_data" ? <line {...line} x1={3} stroke={ROUTE_COLORS.no_data} strokeWidth={4} strokeDasharray="2 8" strokeLinecap="round" /> : null}
    </svg>
  );
}

/**
 * One segment state explained: its line sample in place of the list mark, its name in bold, and what the state means.
 */
function SegmentItem({ state }: { state: SegmentState }) {
  const { t } = useTranslation();
  const { lead, rest } = splitLeadSentence(t(`data.segment.${state}`));
  return (
    <li className="grid grid-cols-[36px_1fr] gap-x-2.5 text-[14.5px]">
      <SegmentSample state={state} />
      <span>
        {lead !== "" ? <b className="font-bold">{lead}</b> : null}
        {rest}
      </span>
    </li>
  );
}

/**
 * The page about the data, a page of text in the language of the interface: where the facts come from and from which day
 * the map data are, what the statuses and the four segment states mean, what the sample data mark means,
 * how an error is corrected, and the licence of the map.
 * The day of the map data is the one the service gives. While it is not known, the sentence about the map data stands without a day.
 */
export function AboutDataView() {
  const { t } = useTranslation();
  const language = useLanguage();
  const osmCopy = useRequest(readOsmCopy, []);
  const mapSource = osmCopy.data !== null ? t("data.sources.map", { date: formatDay(osmCopy.data, language) }) : t("data.sources.map.no_date");
  const sampleText = t("data.sample.body");
  const sampleParts = splitAroundPart(sampleText, t("sample.mark"));

  return (
    <>
      <PageBack />
      <h1 className={PAGE_TITLE}>{t("menu.data")}</h1>
      <p className={PAGE_LEAD}>{t("data.intro")}</p>

      <h2 className={`${PAGE_HEADING} mt-1!`}>{t("data.sources")}</h2>
      <ul className={TEXT_LIST}>
        <LeadItem text={mapSource} />
        <LeadItem text={t("data.sources.reports")} />
      </ul>

      <h2 className={PAGE_HEADING}>{t("data.statuses")}</h2>
      <ul className={TEXT_LIST}>
        {STATUSES.map((status) => (
          <li key={status} className={TEXT_LIST_ITEM}>
            <StatusMark status={status} />: {t(`data.status.${status}`)}
          </li>
        ))}
      </ul>
      <p className={`${PAGE_TEXT} mt-2`}>{t("data.status.time")}</p>

      <h2 className={PAGE_HEADING}>{t("data.segments")}</h2>
      <ul className={TEXT_LIST}>
        {SEGMENT_STATES.map((state) => (
          <SegmentItem key={state} state={state} />
        ))}
      </ul>
      <Note kind="strong" className="mt-2">
        <p>{t("data.missing")}</p>
      </Note>

      <h2 className={PAGE_HEADING}>{t("data.sample")}</h2>
      <p className={PAGE_TEXT}>
        {sampleParts === null ? (
          sampleText
        ) : (
          <>
            {sampleParts.before}
            <SampleMark />
            {sampleParts.after}
          </>
        )}
      </p>

      <h2 className={PAGE_HEADING}>{t("data.fix")}</h2>
      <p className={PAGE_TEXT}>{t("data.fix.body")}</p>

      <h2 className={PAGE_HEADING}>{t("data.licence")}</h2>
      <p className={PAGE_TEXT}>{t("data.licence.body")}</p>
    </>
  );
}
