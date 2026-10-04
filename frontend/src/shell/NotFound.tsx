import { useTranslation } from "react-i18next";

import { Button } from "../parts/Button.tsx";
import { PAGE_TITLE } from "../parts/styles.ts";

/**
 * The message for an address that is no view, with the way back to the map.
 */
export function NotFound() {
  const { t } = useTranslation();
  return (
    <>
      <h1 className={PAGE_TITLE}>{t("notfound.title")}</h1>
      <div className="mt-4">
        <Button look="primary" to="/">
          {t("report.to_map")}
        </Button>
      </div>
    </>
  );
}
