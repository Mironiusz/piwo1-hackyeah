import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { logIn as requestLogIn, onSessionEnd, readOwnAccount } from "../api/client.ts";
import { toApiError, type ApiError } from "../api/errors.ts";
import type { Account } from "../api/types.ts";
import { isText, readStored, removeStored, STORAGE_KEYS } from "./storage.ts";

interface SessionContextValue {
  account: Account | null;
  isChecking: boolean;
  checkError: ApiError | null;
  hasEnded: boolean;
  logIn: (pseudonym: string, password: string) => Promise<Account>;
  logOut: () => void;
  refresh: () => void;
  dismissEnded: () => void;
}

const SessionContext = createContext<SessionContextValue | null>(null);

/**
 * Tells whether the device keeps a session token.
 */
function hasKeptToken(): boolean {
  return readStored(STORAGE_KEYS.session, isText) !== null;
}

/**
 * Keeps the account of the session for the whole application.
 * A token kept on the device is checked once at the start, and while that check runs the account is not known yet.
 * When the check gets no answer of the service about the token, the token stays and the error of the check is kept,
 * so a view can say that the account is not known in place of treating the person as logged out.
 * A session the service ended shows its notice once.
 */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [isChecking, setIsChecking] = useState(hasKeptToken);
  const [checkError, setCheckError] = useState<ApiError | null>(null);
  const [hasEnded, setHasEnded] = useState(false);
  const checkNumber = useRef(0);

  const check = useCallback(() => {
    checkNumber.current += 1;
    const number = checkNumber.current;
    readOwnAccount().then(
      (own) => {
        if (checkNumber.current === number) {
          setAccount(own);
          setCheckError(null);
          setIsChecking(false);
        }
      },
      (caught: unknown) => {
        if (checkNumber.current === number) {
          setCheckError(hasKeptToken() ? toApiError(caught) : null);
          setIsChecking(false);
        }
      },
    );
  }, []);

  useEffect(() => {
    const removeListener = onSessionEnd(() => {
      setAccount(null);
      setCheckError(null);
      setHasEnded(true);
    });
    if (hasKeptToken()) {
      check();
    }
    return () => {
      checkNumber.current += 1;
      removeListener();
    };
  }, [check]);

  const logIn = useCallback(async (pseudonym: string, password: string) => {
    const own = await requestLogIn(pseudonym, password);
    checkNumber.current += 1;
    setAccount(own);
    setCheckError(null);
    setIsChecking(false);
    setHasEnded(false);
    return own;
  }, []);

  const logOut = useCallback(() => {
    removeStored(STORAGE_KEYS.session);
    checkNumber.current += 1;
    setAccount(null);
    setCheckError(null);
    setIsChecking(false);
    setHasEnded(false);
  }, []);

  const refresh = useCallback(() => {
    if (!hasKeptToken()) {
      return;
    }
    setCheckError(null);
    setIsChecking(true);
    check();
  }, [check]);

  const dismissEnded = useCallback(() => {
    setHasEnded(false);
  }, []);

  const value = useMemo<SessionContextValue>(
    () => ({ account, isChecking, checkError, hasEnded, logIn, logOut, refresh, dismissEnded }),
    [account, isChecking, checkError, hasEnded, logIn, logOut, refresh, dismissEnded],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

/**
 * Returns the account of the session, whether the kept token is being checked, the error of a check that got no answer about the token,
 * the actions that start and end the session, the action that reads the account again, for when the service says
 * the role of the account changed or after a check that failed, and the notice of an ended session.
 */
export function useSession(): SessionContextValue {
  const value = useContext(SessionContext);
  if (value === null) {
    throw new Error("useSession is used outside SessionProvider");
  }
  return value;
}
