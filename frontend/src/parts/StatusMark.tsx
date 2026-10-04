import { useTranslation } from "react-i18next";

import type { FactStatus } from "../api/types.ts";
import { Icon } from "./Icon.tsx";
import type { IconName } from "./iconPaths.ts";

const LOOKS: Record<FactStatus, { icon: IconName; color: string }> = {
  confirmed: { icon: "status_confirmed", color: "text-clear" },
  unverified: { icon: "status_unverified", color: "text-ink" },
  disputed: { icon: "status_disputed", color: "text-disputed" },
  outdated: { icon: "status_outdated", color: "text-muted" },
};

/**
 * The status of a fact as a word with its icon, so the status never depends on color alone.
 */
export function StatusMark({ status }: { status: FactStatus }) {
  const { t } = useTranslation();
  const look = LOOKS[status];
  return (
    <span className={`inline-flex items-center gap-[5px] font-semibold ${look.color}`}>
      <Icon name={look.icon} size={16} />
      {t(`status.${status}`)}
    </span>
  );
}
