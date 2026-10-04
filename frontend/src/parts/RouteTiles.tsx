import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import type { Route } from "../api/types.ts";
import { formatDistance } from "../format/format.ts";
import { useLanguage } from "../i18n/index.ts";
import { measureNoData } from "./routeSummary.ts";

interface RouteTilesProps {
  route: Route;
  isAssessed: boolean;
}

const TILE = "rounded-panel border-[1.5px] px-2.5 py-2";
const NUMBER = "block font-num text-[26px] leading-none font-bold whitespace-nowrap tabular-nums";
const LABEL = "text-[12px] text-white/90";

/**
 * One tile: a number with the words that say what it counts. The frame repeats the meaning of the number.
 * The words come first for a screen reader and stand under the number on the screen.
 */
function Tile({ frame, numberColor, value, label }: { frame: string; numberColor: string; value: ReactNode; label: string }) {
  return (
    <div className={`${TILE} flex flex-col-reverse justify-end ${frame}`}>
      <dt className={LABEL}>{label}</dt>
      <dd className={`${NUMBER} ${numberColor}`}>{value}</dd>
    </div>
  );
}

/**
 * The three numbers a person reads before any scrolling: the barriers of the needs on the route in a yellow frame,
 * the distance without data in a dashed frame, and the length of the route. Facts and unknowns stand side by side, without a verdict.
 * For a route that is not assessed the first two give way to one tile that says so.
 */
export function RouteTiles({ route, isAssessed }: RouteTilesProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  const length = <Tile frame="border-white/50" numberColor="text-white" value={formatDistance(route.length_m, language)} label={t("route.tile.length")} />;

  if (!isAssessed) {
    return (
      <dl className="grid grid-cols-[2.3fr_1fr] gap-2">
        <Tile frame="border-dashed border-white/50" numberColor="text-white" value={t("route.tile.not_assessed")} label={t("route.tile.not_assessed.why")} />
        {length}
      </dl>
    );
  }

  const barrierCount = route.profile_barriers.length;
  return (
    <dl className="grid grid-cols-[1fr_1.3fr_1fr] gap-2">
      <Tile frame="border-yellow" numberColor="text-yellow" value={barrierCount} label={t("route.tile.barriers", { count: barrierCount })} />
      <Tile frame="border-dashed border-white/50" numberColor="text-white" value={formatDistance(measureNoData(route), language)} label={t("route.tile.no_data")} />
      {length}
    </dl>
  );
}
