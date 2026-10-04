import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useOutletContext, useParams } from "react-router";

import { castVote, flagFact, readFact } from "../api/client.ts";
import { toApiError } from "../api/errors.ts";
import type { Fact, RouteFact, Verdict } from "../api/types.ts";
import { formatDay, formatDistance } from "../format/format.ts";
import { useRequest } from "../hooks/useRequest.ts";
import { useLanguage } from "../i18n/index.ts";
import { Button } from "../parts/Button.tsx";
import { findFactKind, nameFact } from "../parts/factText.ts";
import { Icon } from "../parts/Icon.tsx";
import { Note } from "../parts/Note.tsx";
import { Panel } from "../parts/Panel.tsx";
import { SampleMark } from "../parts/SampleMark.tsx";
import { StatusMark } from "../parts/StatusMark.tsx";
import { HINT, KEY_VALUE_KEY, KEY_VALUE_LIST, KEY_VALUE_VALUE, PANEL_TEXT, PANEL_TITLE } from "../parts/styles.ts";
import { canVoteNow, readOwnVote, saveOwnVote, startOfNextDay, toDeviceDay } from "../state/ownVotes.ts";
import { usePlannedRoute } from "../state/plannedRoute.tsx";
import type { FactDetailContext } from "./factDetail.ts";

type VoteState = { kind: "idle" } | { kind: "saving" } | { kind: "saved"; status: Fact["status"] } | { kind: "too_soon"; repeatAllowedAt: string | null } | { kind: "failed"; textKey: string };

type FlagState = "idle" | "asking" | "saving" | "done" | "failed";

interface FactBodyProps {
  fact: Fact;
  routeFact: RouteFact | null;
  vote: VoteState;
  flag: FlagState;
  openedAt: Date;
  onVote: (verdict: Verdict) => void;
  onFlagStep: (step: FlagState) => void;
  onFlag: () => void;
}

/**
 * The content of the detail of a loaded fact: the sample data mark, the source with its days and the status,
 * the notes of an outdated fact and of a contradiction with the map data, the two votes with the own vote, and the flag.
 */
function FactBody({ fact, routeFact, vote, flag, openedAt, onVote, onFlagStep, onFlag }: FactBodyProps) {
  const { t } = useTranslation();
  const language = useLanguage();
  const kind = findFactKind(fact);
  const ownVote = readOwnVote(fact.id);
  const canVote = canVoteNow(fact.id, openedAt);
  const isVoteOpen = canVote && vote.kind !== "saving" && vote.kind !== "too_soon";

  return (
    <>
      {fact.is_sample ? (
        <p className="mt-2">
          <SampleMark />
        </p>
      ) : null}

      <dl className={KEY_VALUE_LIST}>
        <dt className={KEY_VALUE_KEY}>{t("fact.source")}</dt>
        <dd className={KEY_VALUE_VALUE}>{t(fact.source === "user_report" ? "source.user_report.full" : "source.openstreetmap")}</dd>
        {fact.osm_edited_on !== null ? (
          <>
            <dt className={KEY_VALUE_KEY}>{t("fact.edited_on")}</dt>
            <dd className={KEY_VALUE_VALUE}>{formatDay(fact.osm_edited_on, language)}</dd>
          </>
        ) : null}
        {fact.last_confirmed_on !== null ? (
          <>
            <dt className={KEY_VALUE_KEY}>{t("fact.confirmed_on")}</dt>
            <dd className={KEY_VALUE_VALUE}>{formatDay(fact.last_confirmed_on, language)}</dd>
          </>
        ) : null}
        <dt className={KEY_VALUE_KEY}>{t("fact.status")}</dt>
        <dd className={KEY_VALUE_VALUE}>
          <StatusMark status={fact.status} />
        </dd>
        {fact.type === "stairs" && fact.step_count !== null ? (
          <>
            <dt className={KEY_VALUE_KEY}>{t("fact.steps")}</dt>
            <dd className={KEY_VALUE_VALUE}>{fact.step_count}</dd>
          </>
        ) : null}
        {fact.geozone_radius_m !== null ? (
          <>
            <dt className={KEY_VALUE_KEY}>{t("fact.radius")}</dt>
            <dd className={KEY_VALUE_VALUE}>{`${fact.geozone_radius_m} m`}</dd>
          </>
        ) : null}
        {fact.description !== null ? (
          <>
            <dt className={KEY_VALUE_KEY}>{t("fact.description")}</dt>
            <dd className="break-words whitespace-pre-line">{fact.description}</dd>
          </>
        ) : null}
      </dl>

      {fact.status === "outdated" ? <Note className="mb-3">{t(fact.is_removed_from_osm ? "fact.removed" : "fact.outdated")}</Note> : null}
      {routeFact?.is_overruled_by_osm === true ? (
        <Note kind="strong" className="mb-3">
          {t("fact.contradiction")}
        </Note>
      ) : null}

      <output className="block">
        {vote.kind === "saved" ? <Note className="mb-2">{t("vote.saved", { status: t(`status.${vote.status}`) })}</Note> : null}
        {vote.kind === "saving" ? <p className={`${HINT} mb-2`}>{t("vote.saving")}</p> : null}
        {vote.kind === "too_soon" ? <Note className="mb-2">{t("vote.too_soon", { day: formatDay(vote.repeatAllowedAt ?? startOfNextDay(openedAt), language) })}</Note> : null}
      </output>
      {vote.kind === "failed" ? (
        <Note kind="strong" announce="alert" className="mb-2">
          {t(vote.textKey)}
        </Note>
      ) : null}
      {ownVote !== null && !canVote ? (
        <Note className="mb-2.5">
          <p>
            <b className="font-bold">{t(ownVote.verdict === "confirm" ? "vote.own.confirm" : "vote.own.deny")}</b> {t("vote.own.saved", { date: formatDay(ownVote.votedOn, language) })}
          </p>
        </Note>
      ) : null}

      <p id="vote-question" className="mb-2 text-[13.5px] font-semibold">
        {t(`vote.question.${kind}`)}
      </p>
      <fieldset aria-labelledby="vote-question" className="m-0 grid min-w-0 grid-cols-2 gap-2.5 border-0 p-0">
        <Button disabled={!isVoteOpen} onClick={() => onVote("confirm")}>
          {t("vote.confirm")}
        </Button>
        <Button disabled={!isVoteOpen} onClick={() => onVote("deny")}>
          {t("vote.deny")}
        </Button>
      </fieldset>

      {fact.can_be_flagged ? (
        <div className="mt-2">
          {flag === "idle" || flag === "failed" ? (
            <Button look="link" onClick={() => onFlagStep("asking")}>
              {t("flag.action")}
            </Button>
          ) : null}
          {flag === "asking" || flag === "saving" ? (
            <Note className="mt-1">
              <p className="font-semibold">{t("flag.confirm")}</p>
              <div className="mt-2 flex gap-2.5">
                <Button isSmall look="primary" disabled={flag === "saving"} onClick={onFlag}>
                  {t("flag.yes")}
                </Button>
                <Button isSmall disabled={flag === "saving"} onClick={() => onFlagStep("idle")}>
                  {t("action.cancel")}
                </Button>
              </div>
            </Note>
          ) : null}
          <output className="block">{flag === "done" ? <Note className="mt-1">{t("flag.done")}</Note> : null}</output>
          {flag === "failed" ? (
            <Note kind="strong" announce="alert" className="mt-1">
              {t("flag.failed")}
            </Note>
          ) : null}
        </div>
      ) : null}
    </>
  );
}

/**
 * The detail of a fact, a panel over the map: its type, source, days and status, the sample data mark and the description,
 * the two equal votes with the own latest vote of the person, which the device remembers, and the flag for moderation
 * where the service allows one. An outdated fact keeps both votes, so it can be confirmed again.
 * The heading stays the same element while the fact loads, so the focus that moved to it stays on it.
 */
export function FactDetailPanel() {
  const { t } = useTranslation();
  const language = useLanguage();
  const params = useParams();
  const factId = Number(params.factId);
  const { closePath, routeFacts, onLoad, onChange } = useOutletContext<FactDetailContext>();
  const { markStale } = usePlannedRoute();
  const loaded = useRequest(() => readFact(factId), [factId]);
  const [changed, setChanged] = useState<Fact | null>(null);
  const [vote, setVote] = useState<VoteState>({ kind: "idle" });
  const [flag, setFlag] = useState<FlagState>("idle");
  const [isGone, setIsGone] = useState(false);
  const [shownId, setShownId] = useState(factId);
  const [openedAt] = useState(() => new Date());

  if (shownId !== factId) {
    setShownId(factId);
    setChanged(null);
    setVote({ kind: "idle" });
    setFlag("idle");
    setIsGone(false);
  }

  const loadedFact = loaded.data;
  const isMissing = isGone || loaded.error?.code === "fact_not_found" || Number.isNaN(factId);
  const fact = isMissing ? null : changed !== null && changed.id === factId ? changed : loadedFact;
  const routeFact = fact === null ? null : (routeFacts.find((candidate) => candidate.id === fact.id) ?? null);

  useEffect(() => {
    if (loadedFact !== null) {
      onLoad(loadedFact);
    }
  }, [loadedFact, onLoad]);

  const sendVote = async (verdict: Verdict) => {
    setVote({ kind: "saving" });
    try {
      const after = await castVote(factId, verdict);
      const now = new Date();
      saveOwnVote(factId, verdict, toDeviceDay(now), startOfNextDay(now));
      setChanged(after);
      setVote({ kind: "saved", status: after.status });
      markStale();
      onChange(after);
    } catch (caught) {
      const error = toApiError(caught);
      if (error.code === "vote_too_soon") {
        setVote({ kind: "too_soon", repeatAllowedAt: error.repeatAllowedAt });
      } else if (error.code === "fact_not_found") {
        setIsGone(true);
      } else {
        setVote({ kind: "failed", textKey: error.code === "network_error" ? "state.offline" : "vote.failed" });
      }
    }
  };

  const sendFlag = async () => {
    setFlag("saving");
    try {
      await flagFact(factId);
      setFlag("done");
    } catch (caught) {
      if (toApiError(caught).code === "fact_not_found") {
        setIsGone(true);
      } else {
        setFlag("failed");
      }
    }
  };

  return (
    <Panel>
      <div className="flex items-start gap-2">
        <div className="min-w-0 flex-1">
          <h1 tabIndex={-1} className={`${PANEL_TITLE} outline-none`}>
            {fact !== null ? nameFact(fact, t, language) : t("fact.title")}
          </h1>
          {routeFact !== null ? <p className={PANEL_TEXT}>{t("route.from_start", { distance: formatDistance(routeFact.distance_from_start_m, language) })}</p> : null}
        </div>
        <Link to={closePath} aria-label={t("fact.close")} className="inline-flex size-11 flex-none items-center justify-center rounded-panel text-ink">
          <Icon name="close" />
        </Link>
      </div>

      {isMissing ? (
        <Note announce="status" className="mt-2">
          {t("fact.gone")}
        </Note>
      ) : null}
      {!isMissing && fact === null && loaded.state === "failed" ? (
        <Note kind="strong" announce="alert" className="mt-2">
          <p>{t(loaded.error?.code === "network_error" ? "state.offline" : "state.failed")}</p>
          <div className="mt-2">
            <Button isSmall onClick={loaded.retry}>
              {t("action.retry")}
            </Button>
          </div>
        </Note>
      ) : null}
      <output className="block">{!isMissing && fact === null && loaded.state === "loading" ? <span className={`${HINT} mt-2 block`}>{t("state.loading")}</span> : null}</output>

      {fact !== null ? (
        <FactBody fact={fact} routeFact={routeFact} vote={vote} flag={flag} openedAt={openedAt} onVote={(verdict) => void sendVote(verdict)} onFlagStep={setFlag} onFlag={() => void sendFlag()} />
      ) : null}
    </Panel>
  );
}
