import { useTranslation } from "react-i18next";

import type { Fact } from "../api/types.ts";
import { formatDay } from "../format/format.ts";
import { useLanguage } from "../i18n/index.ts";
import { findFactDay } from "./factText.ts";

/**
 * The source of a fact and its day, as the service gave them: map data with the day of the last edit,
 * or a report with the day of the last confirmation.
 */
export function SourceDate({ fact }: { fact: Pick<Fact, "source" | "osm_edited_on" | "last_confirmed_on"> }) {
  const { t } = useTranslation();
  const language = useLanguage();
  const day = findFactDay(fact);
  return (
    <span className="text-muted">
      {t(`source.${fact.source}`)}
      {day !== null ? `, ${formatDay(day, language)}` : ""}
    </span>
  );
}
