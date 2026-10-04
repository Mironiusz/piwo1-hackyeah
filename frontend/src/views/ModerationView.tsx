import { useState } from "react";
import { useTranslation } from "react-i18next";

import { hideFact, listFlaggedFacts, restoreFact } from "../api/client.ts";
import { errorTextKey, toApiError } from "../api/errors.ts";
import type { FlaggedFact } from "../api/types.ts";
import { formatDay } from "../format/format.ts";
import { useRequest } from "../hooks/useRequest.ts";
import { useLanguage } from "../i18n/index.ts";
import { Button } from "../parts/Button.tsx";
import { nameFact } from "../parts/factText.ts";
import { Note } from "../parts/Note.tsx";
import { SampleMark } from "../parts/SampleMark.tsx";
import { SourceDate } from "../parts/SourceDate.tsx";
import { StatusMark } from "../parts/StatusMark.tsx";
import { ACTIONS_ONE, HINT, PAGE_HEADING, PAGE_LEAD, PAGE_TEXT, PAGE_TITLE } from "../parts/styles.ts";
import { useSession } from "../state/session.tsx";
import { isText, readStored, STORAGE_KEYS } from "../state/storage.ts";
import { buildItemActionId, buildItemTitleId, findNeighbour, isModeratorRefusal, keepChangedFact, splitFlaggedFacts } from "./moderationLists.ts";
import { PageBack } from "./PageBack.tsx";
import { useFocusRequest } from "./useFocusRequest.ts";

interface ActionFailure {
  factId: number;
  textKey: string;
}

interface Announcement {
  count: number;
  item: FlaggedFact;
}

const FLAGGED_HEADING_ID = "moderation-flagged";

const HIDDEN_HEADING_ID = "moderation-hidden";

/**
 * The empty list of flagged facts: what stands in place of an answer that is not there, and what a person without access is given.
 */
const NO_FLAGGED_FACTS: FlaggedFact[] = [];

const COUNT = "font-medium text-muted";

const META_ROW = "flex flex-wrap items-center gap-x-2.5 gap-y-1.5 text-[12.5px]";

const HIDDEN_MARK = "inline-block rounded-control border border-line bg-bg px-[7px] py-px text-[11.5px] font-semibold text-ink";

interface FlaggedItemProps {
  item: FlaggedFact;
  failure: string | null;
  isOff: boolean;
  onAct: (item: FlaggedFact) => void;
}

/**
 * One flagged fact with what a fact shows: its title, its description as plain text, its status, its source with the day
 * and the sample data mark. Under them stands what moderation adds: the day the fact was flagged and, for a hidden fact, its mark.
 * Nothing about an author is shown. An item that is not hidden leads to its place on the map and can be hidden,
 * and a hidden item can be restored. The message of a failed action stands under the buttons of the item.
 */
function FlaggedItem({ item, failure, isOff, onAct }: FlaggedItemProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  const { fact } = item;
  const titleId = buildItemTitleId(fact.id);
  return (
    <li className="mb-2.5 rounded-panel border border-line p-3">
      <h3 id={titleId} tabIndex={-1} className="font-semibold wrap-anywhere">
        {nameFact(fact, t, language)}
      </h3>
      {fact.description !== null ? (
        <p className="mt-1.5 text-[14px] wrap-anywhere whitespace-pre-line">
          {t("fact.description")}: {fact.description}
        </p>
      ) : null}
      <p className={`${META_ROW} mt-2`}>
        <StatusMark status={fact.status} />
        <SourceDate fact={fact} />
        {fact.is_sample ? <SampleMark /> : null}
      </p>
      <p className={`${META_ROW} mt-1.5 text-muted`}>
        {item.is_hidden ? <span className={HIDDEN_MARK}>{t("moderation.hidden.mark")}</span> : null}
        <span>{t("moderation.flagged_on", { date: formatDay(item.flagged_on, language) })}</span>
      </p>
      <div className={`mt-3 grid gap-2.5 ${item.is_hidden ? "grid-cols-1" : "grid-cols-2"}`}>
        {item.is_hidden ? null : <Button to={`/fact/${fact.id}`}>{t("moderation.on_map")}</Button>}
        <Button id={buildItemActionId(fact.id)} look={item.is_hidden ? "outline" : "primary"} aria-describedby={titleId} disabled={isOff} onClick={() => onAct(item)}>
          {t(item.is_hidden ? "moderation.restore" : "moderation.hide")}
        </Button>
      </div>
      {failure !== null ? (
        <Note kind="strong" announce="alert" className="mt-2.5">
          <p>{t(failure)}</p>
        </Note>
      ) : null}
    </li>
  );
}

interface FlaggedListProps {
  headingId: string;
  items: readonly FlaggedFact[];
  failure: ActionFailure | null;
  isOff: boolean;
  onAct: (item: FlaggedFact) => void;
}

/**
 * One of the two lists of the moderation view, named by its heading.
 */
function FlaggedList({ headingId, items, failure, isOff, onAct }: FlaggedListProps) {
  return (
    <ul aria-labelledby={headingId}>
      {items.map((item) => (
        <FlaggedItem key={item.fact.id} item={item} failure={failure !== null && failure.factId === item.fact.id ? failure.textKey : null} isOff={isOff} onAct={onAct} />
      ))}
    </ul>
  );
}

/**
 * Moderation, a page for an account with the moderator role: the flagged content that is not hidden, and the hidden content.
 * Hiding and restoring move an item between the two lists from the answer of the service, without asking for the list again.
 * A person without an account, an account without the role and a request the service refuses for the role all see that the view
 * is only for a moderator. A failed action shows a plain message and changes nothing.
 * While the session kept on the device is still being checked, the service decides: the list is asked for with the kept token.
 */
export function ModerationView() {
  const { t } = useTranslation();
  const language = useLanguage();
  const { account, refresh } = useSession();
  const hasKeptSession = readStored(STORAGE_KEYS.session, isText) !== null;
  const canAsk = account !== null ? account.is_moderator : hasKeptSession;
  const listed = useRequest(() => (canAsk ? listFlaggedFacts() : Promise.resolve(NO_FLAGGED_FACTS)), [canAsk]);
  const [changed, setChanged] = useState<readonly FlaggedFact[]>(NO_FLAGGED_FACTS);
  const [isBusy, setIsBusy] = useState(false);
  const [failure, setFailure] = useState<ActionFailure | null>(null);
  const [isRefused, setIsRefused] = useState(false);
  const [announcement, setAnnouncement] = useState<Announcement | null>(null);
  const requestFocus = useFocusRequest();

  const isDenied = !canAsk || isRefused || (listed.error !== null && isModeratorRefusal(listed.error.code));
  const lists = splitFlaggedFacts(listed.data ?? NO_FLAGGED_FACTS, changed);

  /**
   * Hides an item that is not hidden, or restores a hidden one, and takes its new place from the answer of the service.
   * The focus then moves to the next item of the list the item left, or to the heading of that list when it is empty.
   * A refusal for the role closes the view and makes the session read its account again, so the menu loses the entry;
   * an ended session is told by the shell, and any other failure is a message under the item.
   */
  const act = async (item: FlaggedFact) => {
    if (isBusy) {
      return;
    }
    const factId = item.fact.id;
    const neighbour = findNeighbour(item.is_hidden ? lists.hidden : lists.flagged, factId);
    const headingId = item.is_hidden ? HIDDEN_HEADING_ID : FLAGGED_HEADING_ID;
    setIsBusy(true);
    setFailure(null);
    try {
      const answered = await (item.is_hidden ? restoreFact(factId) : hideFact(factId));
      setChanged((current) => keepChangedFact(current, answered));
      setAnnouncement((current) => ({ count: (current?.count ?? 0) + 1, item: answered }));
      requestFocus(neighbour !== null ? buildItemTitleId(neighbour.fact.id) : headingId, true);
    } catch (caught) {
      const error = toApiError(caught);
      if (isModeratorRefusal(error.code)) {
        setIsRefused(true);
        refresh();
      } else if (error.code !== "session_expired") {
        setFailure({ factId, textKey: errorTextKey(error.code) });
        requestFocus(buildItemActionId(factId), true);
      }
    } finally {
      setIsBusy(false);
    }
  };

  /**
   * Asks for the list again after it could not be loaded, and forgets the answers of earlier actions, which the new list holds.
   */
  const reload = () => {
    setChanged(NO_FLAGGED_FACTS);
    setFailure(null);
    listed.retry();
  };

  if (isDenied) {
    return (
      <>
        <PageBack />
        <h1 className={PAGE_TITLE}>{t("moderation.title")}</h1>
        <Note kind="strong" announce="alert" className="mt-2">
          <p>{t("moderation.denied")}</p>
        </Note>
        {account === null && !hasKeptSession ? (
          <div className={ACTIONS_ONE}>
            <Button look="primary" to="/account">
              {t("account.log_in")}
            </Button>
          </div>
        ) : null}
      </>
    );
  }

  return (
    <>
      <PageBack />
      <h1 className={PAGE_TITLE}>{t("moderation.title")}</h1>
      <p className={PAGE_LEAD}>{t("moderation.intro")}</p>

      {listed.error !== null ? (
        <>
          <Note kind="strong" announce="alert">
            <p>{t(errorTextKey(listed.error.code))}</p>
          </Note>
          <div className={ACTIONS_ONE}>
            <Button onClick={reload}>{t("action.retry")}</Button>
          </div>
        </>
      ) : listed.state === "loading" ? (
        <output className={`${HINT} block`}>{t("state.loading")}</output>
      ) : lists.flagged.length === 0 && lists.hidden.length === 0 ? (
        <Note announce="status">
          <p>{t("moderation.empty")}</p>
        </Note>
      ) : (
        <>
          <h2 id={FLAGGED_HEADING_ID} tabIndex={-1} className={`${PAGE_HEADING} mt-1!`}>
            {t("moderation.flagged")} <span className={COUNT}>{lists.flagged.length}</span>
          </h2>
          {lists.flagged.length === 0 ? (
            <p className={PAGE_TEXT}>{t("moderation.empty")}</p>
          ) : (
            <>
              <FlaggedList headingId={FLAGGED_HEADING_ID} items={lists.flagged} failure={failure} isOff={isBusy} onAct={(item) => void act(item)} />
              <p className={HINT}>{t("moderation.no_dismiss")}</p>
            </>
          )}

          <h2 id={HIDDEN_HEADING_ID} tabIndex={-1} className={PAGE_HEADING}>
            {t("moderation.hidden")} <span className={COUNT}>{lists.hidden.length}</span>
          </h2>
          {lists.hidden.length > 0 ? <FlaggedList headingId={HIDDEN_HEADING_ID} items={lists.hidden} failure={failure} isOff={isBusy} onAct={(item) => void act(item)} /> : null}
          <p className={HINT}>{t("moderation.hidden.note")}</p>

          <output className="sr-only">
            {announcement !== null ? (
              <span key={announcement.count}>{t(announcement.item.is_hidden ? "moderation.hide.done" : "moderation.restore.done", { title: nameFact(announcement.item.fact, t, language) })}</span>
            ) : null}
          </output>
        </>
      )}
    </>
  );
}
