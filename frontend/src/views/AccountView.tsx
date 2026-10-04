import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { createAccount, deleteOwnAccount } from "../api/client.ts";
import { errorTextKey, toApiError } from "../api/errors.ts";
import { Button } from "../parts/Button.tsx";
import { Field } from "../parts/Field.tsx";
import { Note } from "../parts/Note.tsx";
import { ACTIONS, ACTIONS_ONE, HINT, KEY_VALUE_KEY, KEY_VALUE_VALUE, PAGE_HEADING, PAGE_LEAD, PAGE_TEXT, PAGE_TITLE, TEXT_LIST, TEXT_LIST_ITEM } from "../parts/styles.ts";
import { useSession } from "../state/session.tsx";
import {
  ACCOUNT_FIELD_RULES,
  checkAccountForm,
  describeAccountFailure,
  findFirstInvalidField,
  NO_ACCOUNT_FIELD_ERRORS,
  trimPseudonym,
  type AccountField,
  type AccountFieldErrors,
} from "./accountForm.ts";
import { PageBack } from "./PageBack.tsx";
import { useFocusRequest } from "./useFocusRequest.ts";

type Mode = "main" | "create" | "delete";

type Screen = "login" | "create" | "in" | "delete";

type Notice = "account.logged_out" | "account.deleted" | "account.created";

const TITLE_ID = "account-title";

const FIELD_IDS: Record<AccountField, string> = { pseudonym: "account-pseudonym", password: "account-password" };

const SUBMIT_ID = "account-submit";

const DELETE_ID = "account-delete";

/**
 * The look of the two actions that delete the account, drawn in the red of a barrier as the mocks draw them.
 * The button part has no such look, so the classes stand here.
 */
const DANGER_BUTTON =
  "inline-flex min-h-[46px] items-center justify-center gap-1.5 rounded-panel border-[1.5px] border-barrier bg-barrier px-4 text-[14.5px] font-bold text-white disabled:cursor-not-allowed disabled:border-line disabled:bg-off disabled:text-off-ink";

const DANGER_LINK = "inline-flex min-h-11 items-center gap-1.5 px-0.5 text-[14px] font-semibold text-barrier underline underline-offset-[3px]";

interface CredentialsFormProps {
  isCreating: boolean;
  pseudonym: string;
  password: string;
  fieldErrors: AccountFieldErrors;
  failure: string | null;
  isBusy: boolean;
  onEdit: (field: AccountField, value: string) => void;
  onSubmit: () => void;
}

/**
 * The form with the pseudonym and the password, for logging in and for creating an account.
 * Creating an account shows the rule of each field and says that a forgotten password cannot be recovered.
 * A message about one field stands next to it, and every other message stands above the button.
 */
function CredentialsForm({ isCreating, pseudonym, password, fieldErrors, failure, isBusy, onEdit, onSubmit }: CredentialsFormProps) {
  const { t } = useTranslation();

  /**
   * Returns the hint of a field: its rule while an account is created, unless the same rule already stands there as the message.
   */
  const findHint = (field: AccountField) => (isCreating && fieldErrors[field] !== ACCOUNT_FIELD_RULES[field] ? t(ACCOUNT_FIELD_RULES[field]) : undefined);

  /**
   * Returns the message next to a field in the language of the interface, or null for a field without one.
   */
  const findError = (field: AccountField) => {
    const key = fieldErrors[field];
    return key !== null ? t(key) : null;
  };

  return (
    <form
      noValidate
      aria-labelledby={TITLE_ID}
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <Field
        id={FIELD_IDS.pseudonym}
        label={t("account.pseudonym")}
        value={pseudonym}
        onChange={(value) => onEdit("pseudonym", value)}
        autoComplete="username"
        hint={findHint("pseudonym")}
        error={findError("pseudonym")}
        className=""
      />
      <Field
        id={FIELD_IDS.password}
        label={t("account.password")}
        type="password"
        value={password}
        onChange={(value) => onEdit("password", value)}
        autoComplete={isCreating ? "new-password" : "current-password"}
        hint={findHint("password")}
        error={findError("password")}
      />
      {isCreating ? (
        <Note kind="strong" title={t("account.no_recovery.title")} className="mt-3.5">
          <p>{t("account.no_recovery.body")}</p>
        </Note>
      ) : null}
      {failure !== null ? (
        <Note kind="strong" announce="alert" className={isCreating ? "mt-2" : "mt-3.5"}>
          <p>{t(failure)}</p>
        </Note>
      ) : null}
      <div className={ACTIONS_ONE}>
        <Button id={SUBMIT_ID} type="submit" look="primary" disabled={isBusy}>
          {t(isCreating ? "account.create" : "account.log_in")}
        </Button>
      </div>
    </form>
  );
}

interface LoggedInProps {
  pseudonym: string;
  onLogOut: () => void;
  onAskDelete: () => void;
}

/**
 * The account of a logged in person: the pseudonym, how long the session lasts, that the needs are no part of the account,
 * the action that logs out and the way to deleting the account.
 */
function LoggedIn({ pseudonym, onLogOut, onAskDelete }: LoggedInProps) {
  const { t } = useTranslation();
  return (
    <>
      <output className="my-3 grid grid-cols-[auto_1fr] gap-x-3.5 text-[15px]">
        <span className={KEY_VALUE_KEY}>{t("account.logged_in_as")}</span> <span className={`${KEY_VALUE_VALUE} wrap-anywhere`}>{pseudonym}</span>
      </output>
      <Note>
        <p>{t("account.session")}</p>
      </Note>
      <Note className="mt-2">
        <p>{t("account.needs")}</p>
      </Note>
      <div className={ACTIONS_ONE}>
        <Button onClick={onLogOut}>{t("account.log_out")}</Button>
      </div>

      <h2 className={`${PAGE_HEADING} mt-7!`}>{t("account.delete.section")}</h2>
      <p className={PAGE_TEXT}>{t("account.delete.intro")}</p>
      <button type="button" onClick={onAskDelete} className={DANGER_LINK}>
        {t("account.delete")}
      </button>
    </>
  );
}

interface DeleteConfirmationProps {
  pseudonym: string;
  failure: string | null;
  isBusy: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

/**
 * The one confirmation before an account is deleted: what goes, what stays, and that it cannot be undone.
 * It asks for no password.
 */
function DeleteConfirmation({ pseudonym, failure, isBusy, onCancel, onConfirm }: DeleteConfirmationProps) {
  const { t } = useTranslation();
  return (
    <>
      <h2 className={PAGE_HEADING}>{t("account.delete.goes")}</h2>
      <ul className={TEXT_LIST}>
        <li className={TEXT_LIST_ITEM}>{t("account.delete.goes.account")}</li>
        <li className={`${TEXT_LIST_ITEM} wrap-anywhere`}>{t("account.delete.goes.pseudonym", { pseudonym })}</li>
      </ul>

      <h2 className={PAGE_HEADING}>{t("account.delete.stays")}</h2>
      <ul className={TEXT_LIST}>
        <li className={TEXT_LIST_ITEM}>{t("account.delete.stays.content")}</li>
      </ul>

      <Note kind="strong" className="mt-[18px]">
        <p>{t("account.delete.final")}</p>
      </Note>
      {failure !== null ? (
        <Note kind="strong" announce="alert" className="mt-2">
          <p>{t(failure)}</p>
        </Note>
      ) : null}
      <div className={ACTIONS}>
        <Button onClick={onCancel} disabled={isBusy}>
          {t("action.cancel")}
        </Button>
        <button id={DELETE_ID} type="button" onClick={onConfirm} disabled={isBusy} className={DANGER_BUTTON}>
          {t("account.delete")}
        </button>
      </div>
    </>
  );
}

/**
 * The account, a page with four screens: logging in, creating an account, the account of a logged in person,
 * and the confirmation of deleting it. An account is a pseudonym and a password, and the view asks for no email address.
 * Both fields are checked against their rules before a request is sent, creating an account logs in right after it,
 * and a deleted account is forgotten by the session too. When an action of the person changes the screen, the focus moves to its title.
 * While the session kept on the device is still being checked, the page shows that it is loading in place of the form for logging in.
 * When that check got no answer, the page says so and offers to try again, because the kept session may still be valid.
 */
export function AccountView() {
  const { t } = useTranslation();
  const { account, isChecking: isSessionChecked, checkError, logIn, logOut, refresh } = useSession();
  const [mode, setMode] = useState<Mode>("main");
  const [pseudonym, setPseudonym] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<AccountFieldErrors>(NO_ACCOUNT_FIELD_ERRORS);
  const [failure, setFailure] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const requestFocus = useFocusRequest();
  const isChecking = isSessionChecked && account === null;
  const title = useRef<HTMLHeadingElement | null>(null);
  const movesFocusToTitle = useRef(false);

  if ((account !== null && mode === "create") || (account === null && mode === "delete")) {
    setMode("main");
  }

  const screen: Screen = account !== null ? (mode === "delete" ? "delete" : "in") : mode === "create" ? "create" : "login";

  useEffect(() => {
    if (movesFocusToTitle.current) {
      movesFocusToTitle.current = false;
      title.current?.focus();
    }
  }, [screen]);

  /**
   * Shows another screen of the page and forgets the messages of the one it leaves. A running request keeps the screen.
   */
  const switchMode = (next: Mode) => {
    if (isBusy) {
      return;
    }
    movesFocusToTitle.current = true;
    setFieldErrors(NO_ACCOUNT_FIELD_ERRORS);
    setFailure(null);
    setNotice(null);
    setMode(next);
  };

  /**
   * Reads the account of the kept session again after a check that got no answer.
   * The focus moves to the title, because the control that was pressed leaves the screen.
   */
  const checkAgain = () => {
    title.current?.focus();
    refresh();
  };

  /**
   * Keeps what a person typed into a field and removes the message next to it, which was about the old value.
   */
  const edit = (field: AccountField, value: string) => {
    if (field === "pseudonym") {
      setPseudonym(value);
    } else {
      setPassword(value);
    }
    setFieldErrors((current) => (current[field] === null ? current : { ...current, [field]: null }));
  };

  /**
   * Sends the form: checks both fields first, creates the account when the form is the one for creating, and logs in.
   * A refusal becomes a message next to a field or above the button, and the focus moves to the field with a message.
   * When the account was created and logging in failed, the form for logging in takes over, so the next attempt creates nothing again.
   */
  const submit = async () => {
    if (isBusy) {
      return;
    }
    const isCreating = screen === "create";
    const name = trimPseudonym(pseudonym);
    const found = checkAccountForm(name, password);
    const invalidField = findFirstInvalidField(found);
    setFieldErrors(found);
    setFailure(null);
    setNotice(null);
    if (invalidField !== null) {
      requestFocus(FIELD_IDS[invalidField]);
      return;
    }
    setIsBusy(true);
    movesFocusToTitle.current = true;
    let isCreated = false;
    try {
      if (isCreating) {
        await createAccount(name, password);
        isCreated = true;
      }
      await logIn(name, password);
      setMode("main");
      setPseudonym("");
      setPassword("");
    } catch (caught) {
      const described = describeAccountFailure(toApiError(caught));
      const refusedField = findFirstInvalidField(described.fieldErrors);
      movesFocusToTitle.current = isCreated;
      setFieldErrors(described.fieldErrors);
      setFailure(described.failure);
      if (isCreated) {
        setMode("main");
        setNotice("account.created");
      }
      if (refusedField !== null) {
        requestFocus(FIELD_IDS[refusedField]);
      } else {
        requestFocus(SUBMIT_ID, true);
      }
    } finally {
      setIsBusy(false);
    }
  };

  /**
   * Logs out on this device and says so above the form for logging in.
   */
  const leaveAccount = () => {
    movesFocusToTitle.current = true;
    logOut();
    setMode("main");
    setFieldErrors(NO_ACCOUNT_FIELD_ERRORS);
    setFailure(null);
    setNotice("account.logged_out");
  };

  /**
   * Deletes the account after the one confirmation and makes the session forget it.
   * A session that ended in the meantime is told by the shell, so the view only goes back to logging in.
   * Any other refusal is a plain message, and the account stays.
   */
  const confirmDelete = async () => {
    if (isBusy) {
      return;
    }
    setIsBusy(true);
    setFailure(null);
    movesFocusToTitle.current = true;
    try {
      await deleteOwnAccount();
      logOut();
      setMode("main");
      setNotice("account.deleted");
    } catch (caught) {
      const error = toApiError(caught);
      if (error.code === "session_expired") {
        setMode("main");
      } else if (error.code === "authentication_required") {
        logOut();
        setMode("main");
        setFailure(errorTextKey(error.code));
      } else {
        movesFocusToTitle.current = false;
        setFailure(errorTextKey(error.code));
        requestFocus(DELETE_ID, true);
      }
    } finally {
      setIsBusy(false);
    }
  };

  const titleText = screen === "create" ? t("account.create") : screen === "delete" && account !== null ? t("account.delete.title", { pseudonym: account.pseudonym }) : t("account.title");

  return (
    <>
      <PageBack onBack={screen === "create" || screen === "delete" ? () => switchMode("main") : undefined} />
      <h1 id={TITLE_ID} ref={title} tabIndex={-1} className={`${PAGE_TITLE} wrap-anywhere outline-none`}>
        {titleText}
      </h1>
      {isChecking ? (
        <output className={`${HINT} block`}>{t("state.loading")}</output>
      ) : account === null && checkError !== null ? (
        <Note kind="strong" announce="alert">
          <p>{t(errorTextKey(checkError.code))}</p>
          <div className="mt-2">
            <Button isSmall onClick={checkAgain}>
              {t("action.retry")}
            </Button>
          </div>
        </Note>
      ) : account === null ? (
        <>
          <p className={PAGE_LEAD}>{t(screen === "create" ? "account.create.intro" : "account.intro")}</p>
          {notice !== null ? (
            <Note announce="status" className="mb-3.5">
              <p>{t(notice)}</p>
            </Note>
          ) : null}
          <CredentialsForm
            key={screen}
            isCreating={screen === "create"}
            pseudonym={pseudonym}
            password={password}
            fieldErrors={fieldErrors}
            failure={failure}
            isBusy={isBusy}
            onEdit={edit}
            onSubmit={() => void submit()}
          />
          {screen === "create" ? (
            <div className="mt-2.5">
              <Button look="link" disabled={isBusy} onClick={() => switchMode("main")}>
                {t("account.have_account")}
              </Button>
            </div>
          ) : (
            <>
              <p className={`${PAGE_TEXT} mt-[22px]`}>{t("account.no_account")}</p>
              <Button className="w-full" disabled={isBusy} onClick={() => switchMode("create")}>
                {t("account.create")}
              </Button>
            </>
          )}
        </>
      ) : screen === "delete" ? (
        <DeleteConfirmation pseudonym={account.pseudonym} failure={failure} isBusy={isBusy} onCancel={() => switchMode("main")} onConfirm={() => void confirmDelete()} />
      ) : (
        <LoggedIn pseudonym={account.pseudonym} onLogOut={leaveAccount} onAskDelete={() => switchMode("delete")} />
      )}
    </>
  );
}
