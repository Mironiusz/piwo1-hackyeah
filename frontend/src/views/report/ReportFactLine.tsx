import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import type { Fact } from "../../api/types.ts";
import { useLanguage } from "../../i18n/index.ts";
import { nameFact } from "../../parts/factText.ts";
import { Icon } from "../../parts/Icon.tsx";
import { findFactIcon } from "../../parts/iconPaths.ts";
import { SampleMark } from "../../parts/SampleMark.tsx";
import { SourceDate } from "../../parts/SourceDate.tsx";
import { StatusMark } from "../../parts/StatusMark.tsx";

interface ReportFactLineProps {
  fact: Fact;
  titleId?: string;
  aside?: string | null;
  asideId?: string;
  children?: ReactNode;
}

/**
 * One fact as the flow of a report shows it: its type, its status, its source with the day, the sample data mark
 * and its description, all as the service gave them. Next to the title stands a short text, the distance from the point
 * of the report, and under the fact the answer a person can give about it.
 */
export function ReportFactLine({ fact, titleId, aside = null, asideId, children }: ReportFactLineProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  return (
    <div className="grid grid-cols-[24px_1fr_auto] gap-x-2.5 py-[11px]">
      <Icon name={findFactIcon(fact.type, fact.geozone_radius_m !== null)} className="mt-px" />
      <span id={titleId} className="font-semibold">
        {nameFact(fact, t, language)}
      </span>
      <span id={asideId} className="text-right text-[14px] font-bold whitespace-nowrap tabular-nums">
        {aside ?? ""}
      </span>
      <span className="col-span-2 col-start-2 mt-1.5 flex flex-wrap items-center gap-x-2.5 gap-y-1.5 text-[12.5px]">
        <StatusMark status={fact.status} />
        <SourceDate fact={fact} />
        {fact.is_sample ? <SampleMark /> : null}
      </span>
      {fact.description !== null ? <p className="col-span-2 col-start-2 mt-1.5 text-[13.5px] break-words whitespace-pre-line">{fact.description}</p> : null}
      {children !== undefined ? <div className="col-span-2 col-start-2 mt-2.5">{children}</div> : null}
    </div>
  );
}
