import { isText, readStored, removeStored, STORAGE_KEYS, writeStored } from "../state/storage.ts";
import { ApiError } from "./errors.ts";
import type { Account, AddressMatch, ApiErrorCode, CreateFactRequest, Fact, FactsInArea, FactType, FlaggedFact, NearbyFact, PlanRouteRequest, PlanRouteResponse, Point, Verdict } from "./types.ts";

const API_PREFIX = "/api";
const SESSION_TOKEN_HEADER = "Session-Token";

type Method = "GET" | "POST" | "DELETE";

interface RequestOptions {
  body?: unknown;
  sendsToken: boolean;
}

type SessionEndListener = () => void;

const sessionEndListeners = new Set<SessionEndListener>();

/**
 * Registers a listener called when the service answers that the session ended. Returns the function that removes it.
 */
export function onSessionEnd(listener: SessionEndListener): () => void {
  sessionEndListeners.add(listener);
  return () => {
    sessionEndListeners.delete(listener);
  };
}

/**
 * Reads the error body of the contract. An answer that is not such a body is an internal error.
 */
async function readError(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as { error?: { code?: ApiErrorCode; fields?: string[]; repeat_allowed_at?: string } };
    const error = body.error;
    if (error !== undefined && typeof error.code === "string") {
      return new ApiError(error.code, Array.isArray(error.fields) ? error.fields : [], error.repeat_allowed_at ?? null);
    }
  } catch {
    return new ApiError("internal_error");
  }
  return new ApiError("internal_error");
}

/**
 * Sends one request to the origin of the page under /api.
 * The token travels only where the contract takes one, the renewed token replaces the kept one,
 * every failure is thrown as ApiError, and an ended session removes the kept token.
 * A renewed token is kept only while the token the request carried is still the kept one,
 * so an answer that arrives after the person logged out does not log them in again.
 * For the same reason an answer that a session expired ends only the session the request belonged to.
 */
async function request<T>(method: Method, path: string, options: RequestOptions): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  const sentToken = options.sendsToken ? readStored(STORAGE_KEYS.session, isText) : null;
  if (sentToken !== null) {
    headers.Authorization = `Bearer ${sentToken}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_PREFIX}${path}`, {
      method,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    throw new ApiError("network_error");
  }

  const renewedToken = response.headers.get(SESSION_TOKEN_HEADER);
  const isSameSession = options.sendsToken ? sentToken !== null && readStored(STORAGE_KEYS.session, isText) === sentToken : true;
  if (renewedToken !== null && renewedToken !== "" && isSameSession) {
    writeStored(STORAGE_KEYS.session, renewedToken);
  }

  if (!response.ok) {
    const error = await readError(response);
    if (error.code === "session_expired" && sentToken !== null && readStored(STORAGE_KEYS.session, isText) === sentToken) {
      removeStored(STORAGE_KEYS.session);
      for (const listener of sessionEndListeners) {
        listener();
      }
    }
    throw error;
  }

  if (response.status === 204) {
    return undefined as T;
  }
  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError("internal_error");
  }
}

/**
 * plan_route: the route between two points for the needs. It carries no token.
 */
export function planRoute(body: PlanRouteRequest): Promise<PlanRouteResponse> {
  return request("POST", "/routes", { body, sendsToken: false });
}

/**
 * search_address: the places in Kraków that match a text. It carries no token.
 */
export async function searchAddress(text: string): Promise<AddressMatch[]> {
  const answer = await request<{ matches: AddressMatch[] }>("POST", "/address-search", { body: { text }, sendsToken: false });
  return answer.matches;
}

/**
 * read_osm_copy: the day of the map data in use, or null before the first copy exists.
 */
export async function readOsmCopy(): Promise<string | null> {
  const answer = await request<{ date: string | null }>("GET", "/osm-copy", { sendsToken: true });
  return answer.date;
}

/**
 * list_facts_in_area: the facts of a rectangle of the map, at most 1000.
 */
export function listFactsInArea(southWest: Point, northEast: Point): Promise<FactsInArea> {
  return request("POST", "/facts/in-area", { body: { south_west: southWest, north_east: northEast }, sendsToken: true });
}

/**
 * read_fact: one fact that is not hidden, in any status.
 */
export async function readFact(factId: number): Promise<Fact> {
  const answer = await request<{ fact: Fact }>("GET", `/facts/${factId}`, { sendsToken: true });
  return answer.fact;
}

/**
 * find_nearby_facts: the facts of the same type within 15 m of a point, nearest first.
 */
export async function findNearbyFacts(type: FactType, point: Point): Promise<NearbyFact[]> {
  const answer = await request<{ facts: NearbyFact[] }>("POST", "/facts/nearby", { body: { type, point }, sendsToken: true });
  return answer.facts;
}

/**
 * create_fact: saves a point report or an area. The key of the body makes a repeated attempt safe.
 */
export async function createFact(body: CreateFactRequest): Promise<Fact> {
  const answer = await request<{ fact: Fact }>("POST", "/facts", { body, sendsToken: true });
  return answer.fact;
}

/**
 * cast_vote: confirms or denies a fact and returns it with its status after the vote.
 */
export async function castVote(factId: number, verdict: Verdict): Promise<Fact> {
  const answer = await request<{ fact: Fact }>("POST", `/facts/${factId}/votes`, { body: { verdict }, sendsToken: true });
  return answer.fact;
}

/**
 * flag_fact: flags a fact for moderation.
 */
export function flagFact(factId: number): Promise<void> {
  return request("POST", `/facts/${factId}/flag`, { sendsToken: true });
}

/**
 * create_account: creates an account. It does not log in and carries no token.
 */
export async function createAccount(pseudonym: string, password: string): Promise<Account> {
  const answer = await request<{ account: Account }>("POST", "/accounts", { body: { pseudonym, password }, sendsToken: false });
  return answer.account;
}

/**
 * log_in: starts a session. The token of the answer is kept by the request itself.
 */
export async function logIn(pseudonym: string, password: string): Promise<Account> {
  const answer = await request<{ account: Account }>("POST", "/sessions", { body: { pseudonym, password }, sendsToken: false });
  return answer.account;
}

/**
 * read_own_account: the account of the session.
 */
export async function readOwnAccount(): Promise<Account> {
  const answer = await request<{ account: Account }>("GET", "/accounts/me", { sendsToken: true });
  return answer.account;
}

/**
 * delete_own_account: removes the account of the session, and then the kept token.
 */
export async function deleteOwnAccount(): Promise<void> {
  await request<void>("DELETE", "/accounts/me", { sendsToken: true });
  removeStored(STORAGE_KEYS.session);
}

/**
 * list_flagged_facts: every flagged fact, hidden ones included. For a moderator.
 */
export async function listFlaggedFacts(): Promise<FlaggedFact[]> {
  const answer = await request<{ facts: FlaggedFact[] }>("GET", "/moderation/flagged-facts", { sendsToken: true });
  return answer.facts;
}

/**
 * hide_fact: hides a flagged fact from everybody. For a moderator.
 */
export function hideFact(factId: number): Promise<FlaggedFact> {
  return request("POST", `/moderation/flagged-facts/${factId}/hide`, { sendsToken: true });
}

/**
 * restore_fact: brings a hidden fact back with the votes it has. For a moderator.
 */
export function restoreFact(factId: number): Promise<FlaggedFact> {
  return request("POST", `/moderation/flagged-facts/${factId}/restore`, { sendsToken: true });
}
