import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { readOsmCopy } from "../api/client.ts";
import { formatDay } from "../format/format.ts";
import { useRequest } from "../hooks/useRequest.ts";
import { changeLanguage, useLanguage, type Language } from "../i18n/index.ts";
import { Icon } from "../parts/Icon.tsx";
import type { IconName } from "../parts/iconPaths.ts";
import { Switch } from "../parts/Switch.tsx";
import { useSession } from "../state/session.tsx";

const ROW = "flex min-h-[52px] w-full items-center gap-3 py-1.5 text-left font-semibold text-ink no-underline";

interface MenuLinkProps {
  to: string;
  icon: IconName;
  name: string;
  detail: string | null;
  onPress: () => void;
}

/**
 * One row of the menu that leads to a page, with its icon, its name and a line of detail under the name.
 */
function MenuLink({ to, icon, name, detail, onPress }: MenuLinkProps) {
  return (
    <Link to={to} onClick={onPress} className={`${ROW} -outline-offset-[3px]`}>
      <Icon name={icon} />
      <span>
        {name}
        {detail !== null ? <small className="block text-[12.5px] font-normal text-muted">{detail}</small> : null}
      </span>
      <span className="flex-1" />
      <Icon name="chevron" />
    </Link>
  );
}

/**
 * One item of the list of the menu, with the line that parts it from the item above.
 */
function MenuItem({ isFirst = false, children }: { isFirst?: boolean; children: ReactNode }) {
  return <li className={isFirst ? "" : "border-t border-line"}>{children}</li>;
}

/**
 * The menu under the header: the account, the language switch, the privacy information, the page about the data,
 * and moderation for an account with the moderator role only.
 */
export function Menu({ onClose }: { onClose: () => void }) {
  const { t } = useTranslation();
  const language = useLanguage();
  const { account } = useSession();
  const osmCopy = useRequest(readOsmCopy, []);
  const languages: readonly { value: Language; label: string }[] = [
    { value: "pl", label: t("language.pl") },
    { value: "en", label: t("language.en") },
  ];
  return (
    <>
      <button type="button" tabIndex={-1} aria-hidden="true" onClick={onClose} className="absolute inset-0 z-10 cursor-default bg-bg/55" />
      <nav id="menu" aria-label={t("menu.open")} className="absolute inset-x-0 top-0 z-20 rounded-b-[12px] bg-surface px-4 pt-1 pb-2.5 shadow-menu">
        <ul>
          <MenuItem isFirst>
            <MenuLink
              to="/account"
              icon="account"
              name={t("menu.account")}
              detail={account !== null ? t("menu.account.in", { pseudonym: account.pseudonym }) : t("menu.account.out")}
              onPress={onClose}
            />
          </MenuItem>
          <MenuItem>
            <div className={ROW}>
              <Icon name="language" />
              <span id="menu-language">{t("menu.language")}</span>
              <span className="flex-1" />
              <Switch labelledBy="menu-language" options={languages} value={language} onChange={changeLanguage} className="w-[170px]" />
            </div>
          </MenuItem>
          <MenuItem>
            <MenuLink to="/privacy" icon="privacy" name={t("menu.privacy")} detail={null} onPress={onClose} />
          </MenuItem>
          <MenuItem>
            <MenuLink to="/about-data" icon="info" name={t("menu.data")} detail={osmCopy.data !== null ? t("menu.data.date", { date: formatDay(osmCopy.data, language) }) : null} onPress={onClose} />
          </MenuItem>
          {account?.is_moderator === true ? (
            <MenuItem>
              <MenuLink to="/moderation" icon="moderation" name={t("menu.moderation")} detail={null} onPress={onClose} />
            </MenuItem>
          ) : null}
        </ul>
      </nav>
    </>
  );
}
