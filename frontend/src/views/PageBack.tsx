import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router";

import { Icon } from "../parts/Icon.tsx";
import { BACK_LINK } from "../parts/styles.ts";
import { readLastMapPath } from "../state/lastMapPath.ts";

/**
 * The key the router gives the first address of a visit, the one the page was opened with.
 */
const FIRST_LOCATION_KEY = "default";

interface PageBackProps {
  onBack?: () => void;
}

/**
 * The way back at the top of a page without the map. It leads to the view the person came from.
 * A page opened straight from its address has no such view, so there it leads to the map in the mode it was left in.
 * A page that shows a step of its own, such as the confirmation of deleting an account, hands in where its step leads back to.
 */
export function PageBack({ onBack }: PageBackProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();

  /**
   * Leaves the page: one step back in the history of the browser, or to the map when the page is the first address of the visit.
   */
  const leave = () => {
    if (location.key === FIRST_LOCATION_KEY) {
      void navigate(readLastMapPath());
      return;
    }
    void navigate(-1);
  };

  return (
    <button type="button" onClick={onBack ?? leave} className={BACK_LINK}>
      <Icon name="back" />
      {t("action.back")}
    </button>
  );
}
