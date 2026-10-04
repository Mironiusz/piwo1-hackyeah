import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from "react";

import { planRoute } from "../api/client.ts";
import { ApiError, toApiError } from "../api/errors.ts";
import type { PlanRouteResponse, Point, Route } from "../api/types.ts";
import { isRouteAssessed } from "../parts/routeSummary.ts";
import { needsSignature, useNeeds } from "./needs.tsx";

export type RouteEndName = "start" | "destination";

/**
 * One end of a route: its point, the way the person gave it, and the label of the address when it came from the search.
 */
export interface RouteEnd {
  point: Point;
  kind: "location" | "address" | "map";
  label: string | null;
}

export type ShownRoute = "first" | "alternative";

export type PlanState = "idle" | "loading" | "ready" | "failed";

interface PlannedRouteContextValue {
  start: RouteEnd | null;
  destination: RouteEnd | null;
  setEnd: (name: RouteEndName, end: RouteEnd | null) => void;
  state: PlanState;
  answer: PlanRouteResponse | null;
  error: ApiError | null;
  isAssessed: boolean;
  isStale: boolean;
  shown: ShownRoute;
  shownRoute: Route | null;
  show: (which: ShownRoute) => void;
  plan: () => Promise<boolean>;
  planAgain: () => void;
  markStale: () => void;
}

interface Planned {
  answer: PlanRouteResponse;
  signature: string;
  isAssessed: boolean;
}

const PlannedRouteContext = createContext<PlannedRouteContextValue | null>(null);

/**
 * Keeps the two ends of a route and the answer of the service for the whole application, so the route survives
 * a change of the view and of the language. Nothing here is written to the device.
 * A request for the same two points and the same needs as the one that is running is not sent a second time.
 * A change of an end drops the answer planned for the ends before it, and the answer of a request that is still running.
 * Whether a route is assessed is read from its answer. An end the service refuses as lying outside Kraków is removed,
 * and the error stays, so the view says why.
 */
export function PlannedRouteProvider({ children }: { children: ReactNode }) {
  const { needs } = useNeeds();
  const [start, setStart] = useState<RouteEnd | null>(null);
  const [destination, setDestination] = useState<RouteEnd | null>(null);
  const [state, setState] = useState<PlanState>("idle");
  const [planned, setPlanned] = useState<Planned | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [shown, setShown] = useState<ShownRoute>("first");
  const [isMarkedStale, setIsMarkedStale] = useState(false);
  const latestRequest = useRef(0);
  const running = useRef<{ key: string; promise: Promise<boolean> } | null>(null);

  const signature = needsSignature(needs);

  const setEnd = useCallback((name: RouteEndName, end: RouteEnd | null) => {
    if (name === "start") {
      setStart(end);
    } else {
      setDestination(end);
    }
    latestRequest.current += 1;
    running.current = null;
    setPlanned(null);
    setError(null);
    setIsMarkedStale(false);
    setState("idle");
  }, []);

  const plan = useCallback(() => {
    if (start === null || destination === null) {
      return Promise.resolve(false);
    }
    const key = `${start.point.lat},${start.point.lon}|${destination.point.lat},${destination.point.lon}|${signature}`;
    if (running.current !== null && running.current.key === key) {
      return running.current.promise;
    }
    const requestNumber = latestRequest.current + 1;
    latestRequest.current = requestNumber;
    setState("loading");
    setError(null);
    const promise = planRoute({ start: start.point, destination: destination.point, avoid: needs.avoid, need: needs.need }).then(
      (answer) => {
        if (latestRequest.current !== requestNumber) {
          return false;
        }
        running.current = null;
        setPlanned({ answer, signature, isAssessed: isRouteAssessed(answer.route) });
        setShown("first");
        setIsMarkedStale(false);
        setState("ready");
        return true;
      },
      (caught: unknown) => {
        if (latestRequest.current !== requestNumber) {
          return false;
        }
        running.current = null;
        const failure = toApiError(caught);
        if (failure.points.includes("start")) {
          setStart(null);
        }
        if (failure.points.includes("destination")) {
          setDestination(null);
        }
        setPlanned(null);
        setError(failure);
        setIsMarkedStale(false);
        setState("failed");
        return false;
      },
    );
    running.current = { key, promise };
    return promise;
  }, [start, destination, needs.avoid, needs.need, signature]);

  const planAgain = useCallback(() => {
    void plan();
  }, [plan]);

  const markStale = useCallback(() => {
    setIsMarkedStale(true);
  }, []);

  const value = useMemo<PlannedRouteContextValue>(() => {
    const answer = planned?.answer ?? null;
    const shownRoute = answer === null ? null : shown === "alternative" && answer.alternative !== null ? answer.alternative.route : answer.route;
    return {
      start,
      destination,
      setEnd,
      state,
      answer,
      error,
      isAssessed: planned?.isAssessed ?? true,
      isStale: planned !== null && (isMarkedStale || planned.signature !== signature),
      shown,
      shownRoute,
      show: setShown,
      plan,
      planAgain,
      markStale,
    };
  }, [start, destination, setEnd, state, planned, error, isMarkedStale, signature, shown, plan, planAgain, markStale]);

  return <PlannedRouteContext.Provider value={value}>{children}</PlannedRouteContext.Provider>;
}

/**
 * Returns the two ends of the route, the answer of the service, which of its routes is shown,
 * and the actions that plan it. A route is stale when the needs changed or a vote or a report was saved after it was planned.
 */
export function usePlannedRoute(): PlannedRouteContextValue {
  const value = useContext(PlannedRouteContext);
  if (value === null) {
    throw new Error("usePlannedRoute is used outside PlannedRouteProvider");
  }
  return value;
}
