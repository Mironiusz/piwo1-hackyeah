import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { Icon } from "../parts/Icon.tsx";

interface BottomBarProps {
  current: "map" | "report" | "needs" | "other";
  mapPath: string;
}

const TAB = "flex min-h-12 flex-col items-center justify-center gap-0.5 rounded-panel text-[11.5px] font-semibold no-underline";

/**
 * The bottom bar of every view: Map, Report as the main action, and Needs.
 * Map leads back to the map in the mode it was left in.
 */
export function BottomBar({ current, mapPath }: BottomBarProps) {
  const { t } = useTranslation();
  return (
    <nav aria-label={t("aria.nav")} className="grid flex-none grid-cols-[1fr_1.3fr_1fr] items-center gap-1.5 border-t border-line bg-surface px-2.5 py-2">
      <Link to={current === "map" ? "/" : mapPath} aria-current={current === "map" ? "page" : undefined} className={`${TAB} ${current === "map" ? "text-shell" : "text-muted"}`}>
        <Icon name="map" />
        {t("nav.map")}
      </Link>
      <Link
        to="/report"
        aria-current={current === "report" ? "page" : undefined}
        className="flex min-h-12 flex-row items-center justify-center gap-2 rounded-panel bg-yellow text-[14.5px] font-bold text-ink no-underline"
      >
        <Icon name="report" />
        {t("nav.report")}
      </Link>
      <Link to="/needs" aria-current={current === "needs" ? "page" : undefined} className={`${TAB} ${current === "needs" ? "text-shell" : "text-muted"}`}>
        <Icon name="needs" />
        {t("nav.needs")}
      </Link>
    </nav>
  );
}
