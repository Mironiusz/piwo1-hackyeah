import { useCallback, useEffect, useRef, useState } from "react";

import { toApiError, type ApiError } from "../api/errors.ts";

export type RequestState = "loading" | "ready" | "failed";

export interface RequestResult<T> {
  state: RequestState;
  data: T | null;
  error: ApiError | null;
  retry: () => void;
}

interface Settled<T> {
  key: string;
  data: T | null;
  error: ApiError | null;
}

interface Tracked {
  dependencies: readonly unknown[];
  version: number;
}

/**
 * Tells whether two lists of dependencies differ in length or in any value.
 */
function hasChanged(previous: readonly unknown[], next: readonly unknown[]): boolean {
  return previous.length !== next.length || next.some((value, index) => !Object.is(value, previous[index]));
}

/**
 * Runs a request when the view appears and again when a dependency changes or retry is called.
 * While a request runs the state is loading and data holds the last answer, so a view can keep it on the screen.
 * An answer that arrives after a newer request started is dropped.
 */
export function useRequest<T>(run: () => Promise<T>, dependencies: readonly unknown[]): RequestResult<T> {
  const [tracked, setTracked] = useState<Tracked>({ dependencies, version: 0 });
  const [attempt, setAttempt] = useState(0);
  const [settled, setSettled] = useState<Settled<T> | null>(null);
  const latestRun = useRef(run);

  if (hasChanged(tracked.dependencies, dependencies)) {
    setTracked({ dependencies, version: tracked.version + 1 });
  }

  const requestKey = `${tracked.version}:${attempt}`;

  useEffect(() => {
    latestRun.current = run;
  });

  useEffect(() => {
    let isCurrent = true;
    latestRun.current().then(
      (data) => {
        if (isCurrent) {
          setSettled({ key: requestKey, data, error: null });
        }
      },
      (caught: unknown) => {
        if (isCurrent) {
          setSettled({ key: requestKey, data: null, error: toApiError(caught) });
        }
      },
    );
    return () => {
      isCurrent = false;
    };
  }, [requestKey]);

  const retry = useCallback(() => {
    setAttempt((current) => current + 1);
  }, []);

  if (settled === null || settled.key !== requestKey) {
    return { state: "loading", data: settled?.data ?? null, error: null, retry };
  }
  if (settled.error !== null) {
    return { state: "failed", data: null, error: settled.error, retry };
  }
  return { state: "ready", data: settled.data, error: null, retry };
}
