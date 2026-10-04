import { useTranslation } from "react-i18next";

import { Note } from "../parts/Note.tsx";
import { PAGE_HEADING, PAGE_LEAD, PAGE_TITLE, TEXT_LIST, TEXT_LIST_ITEM } from "../parts/styles.ts";
import { LeadItem } from "./LeadItem.tsx";
import { PageBack } from "./PageBack.tsx";

const KEPT_TEXTS = ["privacy.kept.account", "privacy.kept.vote", "privacy.kept.route_log"] as const;

const NOT_KEPT_TEXTS = ["privacy.not_kept.needs", "privacy.not_kept.location", "privacy.not_kept.email", "privacy.not_kept.disability"] as const;

const OTHERS_TEXTS = ["privacy.others.server", "privacy.others.search", "privacy.others.users"] as const;

/**
 * The privacy information, a page of text in the language of the interface: what the application keeps, for what purpose
 * and for how long, what it does not keep, who else sees the data, and the day the demo and all its data are deleted.
 * It asks the service for nothing.
 */
export function PrivacyView() {
  const { t } = useTranslation();
  return (
    <>
      <PageBack />
      <h1 className={PAGE_TITLE}>{t("menu.privacy")}</h1>
      <p className={PAGE_LEAD}>{t("privacy.intro")}</p>

      <h2 className={`${PAGE_HEADING} mt-1!`}>{t("privacy.kept")}</h2>
      <ul className={TEXT_LIST}>
        {KEPT_TEXTS.map((key) => (
          <LeadItem key={key} text={t(key)} />
        ))}
      </ul>

      <h2 className={PAGE_HEADING}>{t("privacy.not_kept")}</h2>
      <ul className={TEXT_LIST}>
        {NOT_KEPT_TEXTS.map((key) => (
          <LeadItem key={key} text={t(key)} />
        ))}
      </ul>

      <h2 className={PAGE_HEADING}>{t("privacy.others")}</h2>
      <ul className={TEXT_LIST}>
        {OTHERS_TEXTS.map((key) => (
          <li key={key} className={TEXT_LIST_ITEM}>
            {t(key)}
          </li>
        ))}
      </ul>

      <h2 className={PAGE_HEADING}>{t("privacy.demo")}</h2>
      <Note kind="strong">
        <p>{t("privacy.demo.body")}</p>
      </Note>
    </>
  );
}
