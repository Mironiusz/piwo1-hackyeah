import { useTranslation } from "react-i18next";

/**
 * The mark of sample data, shown on every fact the demo added for the show.
 */
export function SampleMark() {
  const { t } = useTranslation();
  return <span className="inline-block rounded-control border border-line bg-bg px-[7px] py-px text-[11.5px] font-semibold text-ink">{t("sample.mark")}</span>;
}
