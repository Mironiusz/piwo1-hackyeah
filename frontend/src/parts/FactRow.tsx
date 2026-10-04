import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import type { Fact } from "../api/types.ts";
import { formatDistance } from "../format/format.ts";
import { useLanguage } from "../i18n/index.ts";
import { nameFact } from "./factText.ts";
import { Icon } from "./Icon.tsx";
import { findFactIcon } from "./iconPaths.ts";
import { SampleMark } from "./SampleMark.tsx";
import { SourceDate } from "./SourceDate.tsx";
import { StatusMark } from "./StatusMark.tsx";

interface FactRowProps {
  fact: Fact;
  to: string;
  distanceM?: number | null;
  isFirst?: boolean;
}

/**
 * One fact as a row of a list: its type, its distance from the start on a route, its status, its source with the day,
 * and the sample data mark. The whole row is the link that opens the detail of the fact.
 * A row names no street, because the service gives none.
 */
export function FactRow({ fact, to, distanceM = null, isFirst = false }: FactRowProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  return (
    <li className={isFirst ? "" : "border-t border-line"}>
      <Link to={to} className="grid grid-cols-[24px_1fr_auto] gap-x-2.5 py-[11px] text-ink no-underline -outline-offset-[3px]">
        <Icon name={findFactIcon(fact.type, fact.geozone_radius_m !== null)} className="mt-px" />
        <span className="font-semibold">{nameFact(fact, t, language)}</span>
        <span className="text-right text-[14px] font-bold whitespace-nowrap tabular-nums">{distanceM !== null ? formatDistance(distanceM, language) : ""}</span>
        <span className="col-span-2 col-start-2 mt-1.5 flex flex-wrap items-center gap-x-2.5 gap-y-1.5 text-[12.5px]">
          <StatusMark status={fact.status} />
          <SourceDate fact={fact} />
          {fact.is_sample ? <SampleMark /> : null}
        </span>
      </Link>
    </li>
  );
}
