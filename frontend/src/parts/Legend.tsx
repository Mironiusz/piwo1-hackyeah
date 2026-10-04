import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { formatDay } from "../format/format.ts";
import { useLanguage } from "../i18n/index.ts";
import type { MapMarker } from "../map/mapScene.ts";
import { MARK_LOOKS } from "../map/markLooks.ts";
import { ROUTE_COLORS, type DrawnState } from "../map/routeLayers.ts";
import { Icon } from "./Icon.tsx";
import type { IconName } from "./iconPaths.ts";

export type LegendMarker = "barrier" | "amenity" | "area" | "overruled" | "outdated";

interface LegendProps {
  segments: "four" | "neutral" | "none";
  markers?: readonly LegendMarker[];
  osmCopyDate: string | null;
}

const FOUR_STATES: readonly { state: Exclude<DrawnState, "neutral">; text: string }[] = [
  { state: "barrier", text: "segment.barrier" },
  { state: "no_barrier", text: "segment.no_barrier" },
  { state: "partial_data", text: "segment.partial_data" },
  { state: "no_data", text: "segment.no_data" },
];

const MARKERS: Record<LegendMarker, { look: MapMarker["look"]; icon: IconName; text: string }> = {
  barrier: { look: "barrier", icon: "high_kerb", text: "kind.barrier" },
  amenity: { look: "amenity", icon: "lowered_kerb", text: "kind.amenity" },
  area: { look: "barrier", icon: "area", text: "kind.area" },
  overruled: { look: "overruled", icon: "stairs", text: "legend.overruled" },
  outdated: { look: "outdated", icon: "high_kerb", text: "legend.outdated" },
};

/**
 * The sample of a line in one drawn state, with the same color and the same pattern as the route on the map.
 */
function Sample({ state }: { state: DrawnState }) {
  const line = { x1: 2, y1: 6, x2: 34, y2: 6 };
  return (
    <svg aria-hidden="true" focusable="false" viewBox="0 0 36 12" width={36} height={12} className="flex-none">
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
      {state === "neutral" ? (
        <>
          <line {...line} x1={5} x2={31} stroke={ROUTE_COLORS.neutral} strokeWidth={8} strokeLinecap="round" />
          <line {...line} x1={5} x2={31} stroke={ROUTE_COLORS.casing} strokeWidth={4} strokeLinecap="round" />
        </>
      ) : null}
    </svg>
  );
}

/**
 * The legend of a map view: the four segment states of a route with their line patterns and their names,
 * or the one neutral style of a route that is not assessed; the kinds of markers the map of the view can show;
 * and the day of the map data with the way to the page about the data.
 * On the map of facts, which shows no route, the segment states are absent.
 */
export function Legend({ segments, markers = [], osmCopyDate }: LegendProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  return (
    <>
      {segments === "four" ? (
        <ul aria-label={t("aria.legend")} className="grid grid-cols-2 gap-x-3 gap-y-[7px] px-4 pt-2 pb-2.5 text-[12.5px]">
          {FOUR_STATES.map((item) => (
            <li key={item.state} className="flex items-center gap-2">
              <Sample state={item.state} />
              {t(item.text)}
            </li>
          ))}
        </ul>
      ) : null}
      {segments === "neutral" ? (
        <ul aria-label={t("aria.legend")} className="px-4 pt-2 pb-2.5 text-[12.5px]">
          <li className="flex items-center gap-2">
            <Sample state="neutral" />
            {t("segment.not_assessed")}
          </li>
        </ul>
      ) : null}
      {markers.length > 0 ? (
        <ul aria-label={t("legend.markers")} className="flex flex-wrap gap-x-3.5 gap-y-[7px] px-4 pb-2.5 text-[12.5px]">
          {markers.map((marker) => (
            <li key={marker} className="flex items-center gap-1.5">
              <span aria-hidden="true" className={`flex size-[18px] flex-none items-center justify-center ${MARK_LOOKS[MARKERS[marker].look]}`}>
                <Icon name={MARKERS[marker].icon} size={11} strokeWidth={2.4} />
              </span>
              {t(MARKERS[marker].text)}
            </li>
          ))}
        </ul>
      ) : null}
      <p className={`px-4 pb-2.5 text-[12.5px] text-muted ${segments === "none" ? "" : "border-b border-line"}`}>
        {osmCopyDate !== null ? `${t("map.data_date", { date: formatDay(osmCopyDate, language) })} ` : ""}
        <Link to="/about-data" className="font-semibold">
          {t("menu.data")}
        </Link>
      </p>
    </>
  );
}
