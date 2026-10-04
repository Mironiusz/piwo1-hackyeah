import { useTranslation } from "react-i18next";

import { changeLanguage, useLanguage } from "../i18n/index.ts";
import { Icon } from "../parts/Icon.tsx";

interface HeaderProps {
  isMenuOpen: boolean;
  onToggleMenu: () => void;
  showsLanguage: boolean;
}

/**
 * The header of every view: the name of the product and the button of the menu.
 * On the first opening it also carries the language switch, which later lives in the menu.
 */
export function Header({ isMenuOpen, onToggleMenu, showsLanguage }: HeaderProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  const other = language === "pl" ? "en" : "pl";
  return (
    <header className="flex min-h-[52px] flex-none items-center gap-2.5 bg-shell py-1 pr-1.5 pl-4 text-white">
      <span className="text-[17px] font-bold">{t("app.name")}</span>
      <span className="flex-1" />
      {showsLanguage ? (
        <button
          type="button"
          lang={other}
          aria-label={t("aria.language")}
          onClick={() => changeLanguage(other)}
          className="inline-flex min-h-9 items-center rounded-control border border-white/85 px-2.5 text-[13px] font-semibold text-white focus-visible:outline-yellow"
        >
          {t(`language.${other}`)}
        </button>
      ) : null}
      <button
        id="menu-button"
        type="button"
        aria-label={isMenuOpen ? t("menu.close") : t("menu.open")}
        aria-expanded={isMenuOpen}
        aria-controls="menu"
        onClick={onToggleMenu}
        className="inline-flex size-11 items-center justify-center rounded-panel focus-visible:outline-yellow"
      >
        <Icon name={isMenuOpen ? "close" : "menu"} />
      </button>
    </header>
  );
}
