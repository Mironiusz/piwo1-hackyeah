import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { logIn as requestLogIn, onSessionEnd, readOwnAccount } from "../api/client.ts";
import type { Account } from "../api/types.ts";
import { isText, readStored, removeStored, STORAGE_KEYS } from "./storage.ts";

interface SessionContextValue {
  account: Account | null;
  isChecking: boolean;
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
 * A session the service ended shows its notice once.
 */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [isChecking, setIsChecking] = useState(hasKeptToken);
  const [hasEnded, setHasEnded] = useState(false);

  useEffect(() => {
    const removeListener = onSessionEnd(() => {
      setAccount(null);
      setHasEnded(true);
    });
    let isCurrent = true;
    if (hasKeptToken()) {
      readOwnAccount().then(
        (own) => {
          if (isCurrent) {
            setAccount(own);
            setIsChecking(false);
          }
        },
        () => {
          if (isCurrent) {
            setIsChecking(false);
          }
        },
      );
    }
    return () => {
      isCurrent = false;
      removeListener();
    };
  }, []);

  const logIn = useCallback(async (pseudonym: string, password: string) => {
    const own = await requestLogIn(pseudonym, password);
    setAccount(own);
    setIsChecking(false);
    setHasEnded(false);
    return own;
  }, []);

  const logOut = useCallback(() => {
    removeStored(STORAGE_KEYS.session);
    setAccount(null);
    setIsChecking(false);
    setHasEnded(false);
  }, []);

  const refresh = useCallback(() => {
    if (!hasKeptToken()) {
      return;
    }
    readOwnAccount().then(setAccount, () => undefined);
  }, []);

  const dismissEnded = useCallback(() => {
    setHasEnded(false);
  }, []);

  const value = useMemo<SessionContextValue>(() => ({ account, isChecking, hasEnded, logIn, logOut, refresh, dismissEnded }), [account, isChecking, hasEnded, logIn, logOut, refresh, dismissEnded]);

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

/**
 * Returns the account of the session, whether the kept token is still being checked, the actions that start and end the session,
 * the action that reads the account again, for when the service says the role of the account changed,
 * and the notice of an ended session.
 */
export function useSession(): SessionContextValue {
  const value = useContext(SessionContext);
  if (value === null) {
    throw new Error("useSession is used outside SessionProvider");
  }
  return value;
}
