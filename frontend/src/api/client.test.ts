import { afterEach, beforeEach, describe, expect, it, vi, type Mock } from "vitest";

import { isText, readStored, removeStored, STORAGE_KEYS, writeStored } from "../state/storage.ts";
import { createMemoryStorage } from "../testing/memoryStorage.ts";
import {
  castVote,
  createAccount,
  createFact,
  deleteOwnAccount,
  findNearbyFacts,
  flagFact,
  hideFact,
  listFactsInArea,
  listFlaggedFacts,
  logIn,
  onSessionEnd,
  planRoute,
  readFact,
  readOsmCopy,
  readOwnAccount,
  restoreFact,
  searchAddress,
} from "./client.ts";
import { ApiError } from "./errors.ts";
import type { Account, AddressMatch, CreateFactRequest, Fact, FlaggedFact, PlanRouteRequest, PlanRouteResponse, Point } from "./types.ts";

const START: Point = { lat: 50.0645, lon: 19.9837 };
const DESTINATION: Point = { lat: 50.0678, lon: 19.9914 };
const PSEUDONYM = "Wózek_KRK";
const PASSWORD = "five or more characters";
const KEPT_TOKEN = "token-kept";
const RENEWED_TOKEN = "token-renewed";
const LATER_TOKEN = "token-of-a-later-session";

const ROUTE_REQUEST: PlanRouteRequest = { start: START, destination: DESTINATION, avoid: ["stairs", "high_kerb"], need: ["ramp"] };

const REPORT: CreateFactRequest = {
  idempotency_key: "6f1c2a9e-0b8d-4c55-9a51-3e2f7d1b9c40",
  type: "stairs",
  point: DESTINATION,
  description: "Three steps at the side entrance",
  step_count: 3,
  geozone_radius_m: null,
};

const FACT: Fact = {
  id: 1042,
  type: "stairs",
  point: DESTINATION,
  geozone_radius_m: null,
  description: null,
  step_count: 3,
  source: "openstreetmap",
  status: "confirmed",
  is_removed_from_osm: false,
  osm_edited_on: "2026-09-14",
  last_confirmed_on: "2026-10-03",
  is_sample: false,
  can_be_flagged: false,
};

const ACCOUNT: Account = { pseudonym: PSEUDONYM, is_moderator: false };

const FLAGGED_FACT: FlaggedFact = { fact: FACT, flagged_on: "2026-10-03", is_hidden: false };

const ADDRESS_MATCH: AddressMatch = { label: "Tauron Arena Kraków, Stanisława Lema 7, Czyżyny, 31-571 Kraków", point: DESTINATION };

const ROUTE_ANSWER: PlanRouteResponse = {
  osm_copy_date: "2026-10-02",
  barrier_free_route_exists: true,
  route: {
    length_m: 14,
    segments: [
      {
        line: [
          [19.9837, 50.0645],
          [19.9839, 50.0646],
        ],
        length_m: 14,
        state: "no_data",
        missing_attributes: ["kerbs", "surface"],
        is_marked_wheelchair_no: false,
      },
    ],
    profile_barriers: [],
    additional_barriers: [],
    amenities: [],
  },
  alternative: null,
};

interface Operation {
  name: string;
  run: () => Promise<unknown>;
  method: "GET" | "POST" | "DELETE";
  path: string;
  body: unknown;
  takesToken: boolean;
}

/**
 * The sixteen operations of docs/product/api_contract.md: the method, the path and the body each one sends,
 * and whether the contract lets it carry the session token.
 */
const OPERATIONS: Operation[] = [
  { name: "plan_route", run: () => planRoute(ROUTE_REQUEST), method: "POST", path: "/api/routes", body: ROUTE_REQUEST, takesToken: false },
  { name: "search_address", run: () => searchAddress("Tauron Arena"), method: "POST", path: "/api/address-search", body: { text: "Tauron Arena" }, takesToken: false },
  { name: "read_osm_copy", run: () => readOsmCopy(), method: "GET", path: "/api/osm-copy", body: undefined, takesToken: true },
  { name: "list_facts_in_area", run: () => listFactsInArea(START, DESTINATION), method: "POST", path: "/api/facts/in-area", body: { south_west: START, north_east: DESTINATION }, takesToken: true },
  { name: "read_fact", run: () => readFact(1042), method: "GET", path: "/api/facts/1042", body: undefined, takesToken: true },
  { name: "find_nearby_facts", run: () => findNearbyFacts("high_kerb", START), method: "POST", path: "/api/facts/nearby", body: { type: "high_kerb", point: START }, takesToken: true },
  { name: "create_fact", run: () => createFact(REPORT), method: "POST", path: "/api/facts", body: REPORT, takesToken: true },
  { name: "cast_vote", run: () => castVote(1042, "confirm"), method: "POST", path: "/api/facts/1042/votes", body: { verdict: "confirm" }, takesToken: true },
  { name: "flag_fact", run: () => flagFact(1042), method: "POST", path: "/api/facts/1042/flag", body: undefined, takesToken: true },
  { name: "create_account", run: () => createAccount(PSEUDONYM, PASSWORD), method: "POST", path: "/api/accounts", body: { pseudonym: PSEUDONYM, password: PASSWORD }, takesToken: false },
  { name: "log_in", run: () => logIn(PSEUDONYM, PASSWORD), method: "POST", path: "/api/sessions", body: { pseudonym: PSEUDONYM, password: PASSWORD }, takesToken: false },
  { name: "read_own_account", run: () => readOwnAccount(), method: "GET", path: "/api/accounts/me", body: undefined, takesToken: true },
  { name: "delete_own_account", run: () => deleteOwnAccount(), method: "DELETE", path: "/api/accounts/me", body: undefined, takesToken: true },
  { name: "list_flagged_facts", run: () => listFlaggedFacts(), method: "GET", path: "/api/moderation/flagged-facts", body: undefined, takesToken: true },
  { name: "hide_fact", run: () => hideFact(1042), method: "POST", path: "/api/moderation/flagged-facts/1042/hide", body: undefined, takesToken: true },
  { name: "restore_fact", run: () => restoreFact(1042), method: "POST", path: "/api/moderation/flagged-facts/1042/restore", body: undefined, takesToken: true },
];

const fetchStandIn = vi.fn<typeof fetch>();
const listenerRemovals: (() => void)[] = [];

/**
 * Builds an answer of the service with a JSON body.
 */
function buildJsonAnswer(status: number, body: unknown, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", ...headers } });
}

/**
 * Builds the answer without a body that the contract gives with the status 204.
 */
function buildEmptyAnswer(headers: Record<string, string> = {}): Response {
  return new Response(null, { status: 204, headers });
}

/**
 * Makes the stand-in of fetch answer every request with a new answer of the given function.
 */
function answerWith(build: () => Response): void {
  fetchStandIn.mockImplementation(() => Promise.resolve(build()));
}

/**
 * Makes the stand-in of fetch keep every request waiting, as a slow network does.
 * Returns the function that gives its answer to the request that has waited longest.
 */
function holdAnswers(): (answer: Response) => void {
  const waiting: ((answer: Response) => void)[] = [];
  fetchStandIn.mockImplementation(
    () =>
      new Promise<Response>((resolve) => {
        waiting.push(resolve);
      }),
  );
  return (answer) => {
    const resolve = waiting.shift();
    if (resolve === undefined) {
      throw new Error("No request is waiting for an answer");
    }
    resolve(answer);
  };
}

/**
 * Returns what the latest call of the stand-in of fetch sent: the address, the method, the headers and the body read from JSON.
 */
function readLatestRequest(): { url: string; method: string | undefined; headers: Headers; body: unknown } {
  const call = fetchStandIn.mock.calls.at(-1);
  if (call === undefined) {
    throw new Error("The stand-in of fetch was not called");
  }
  const [input, init] = call;
  const body: unknown = typeof init?.body === "string" ? JSON.parse(init.body) : init?.body;
  return { url: String(input), method: init?.method, headers: new Headers(init?.headers), body };
}

/**
 * Runs a request that is expected to fail and returns what it threw.
 */
async function catchFailure(run: () => Promise<unknown>): Promise<unknown> {
  try {
    await run();
  } catch (error) {
    return error;
  }
  throw new Error("The request was expected to fail");
}

/**
 * Registers a listener of an ended session, which the end of the test removes.
 */
function listenForSessionEnd(): Mock<() => void> {
  const listener = vi.fn<() => void>();
  listenerRemovals.push(onSessionEnd(listener));
  return listener;
}

/**
 * Returns the session token the device keeps, or null.
 */
function readKeptToken(): string | null {
  return readStored(STORAGE_KEYS.session, isText);
}

beforeEach(() => {
  fetchStandIn.mockReset();
  vi.stubGlobal("fetch", fetchStandIn);
  vi.stubGlobal("localStorage", createMemoryStorage());
});

afterEach(() => {
  for (const remove of listenerRemovals.splice(0)) {
    remove();
  }
  vi.unstubAllGlobals();
});

describe("the request of an operation", () => {
  it("covers each of the sixteen operations of the contract once", () => {
    expect(OPERATIONS).toHaveLength(16);
    expect(new Set(OPERATIONS.map((operation) => `${operation.method} ${operation.path}`)).size).toBe(16);
  });

  it.each(OPERATIONS)("$name sends $method to $path of the host of the page, with its body", async ({ run, method, path, body }) => {
    answerWith(() => buildJsonAnswer(200, {}));

    await run();

    const request = readLatestRequest();
    expect(fetchStandIn).toHaveBeenCalledTimes(1);
    expect(request.url).toBe(path);
    expect(request.method).toBe(method);
    expect(request.body).toEqual(body);
  });

  it.each(OPERATIONS)("$name names JSON as the type of its body only when it sends one", async ({ run, body }) => {
    answerWith(() => buildJsonAnswer(200, {}));

    await run();

    expect(readLatestRequest().headers.get("Content-Type")).toBe(body === undefined ? null : "application/json");
  });

  it.each(OPERATIONS.filter((operation) => !operation.takesToken))("$name sends no Authorization header even when a token is kept", async ({ run }) => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(200, {}));

    await run();

    expect(readLatestRequest().headers.has("Authorization")).toBe(false);
  });

  it.each(OPERATIONS.filter((operation) => operation.takesToken))("$name sends the kept token in the Authorization header", async ({ run }) => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(200, {}));

    await run();

    expect(readLatestRequest().headers.get("Authorization")).toBe(`Bearer ${KEPT_TOKEN}`);
  });

  it.each(OPERATIONS)("$name sends no Authorization header when no token is kept", async ({ run }) => {
    answerWith(() => buildJsonAnswer(200, {}));

    await run();

    expect(readLatestRequest().headers.has("Authorization")).toBe(false);
  });

  it("lets exactly the four operations of the contract travel without a token", () => {
    const names = OPERATIONS.filter((operation) => !operation.takesToken).map((operation) => operation.name);

    expect(names).toEqual(["plan_route", "search_address", "create_account", "log_in"]);
  });
});

describe("the answer of an operation", () => {
  it("planRoute returns the answer as it is", async () => {
    answerWith(() => buildJsonAnswer(200, ROUTE_ANSWER));

    await expect(planRoute(ROUTE_REQUEST)).resolves.toEqual(ROUTE_ANSWER);
  });

  it("searchAddress returns the matches", async () => {
    answerWith(() => buildJsonAnswer(200, { matches: [ADDRESS_MATCH] }));

    await expect(searchAddress("Tauron Arena")).resolves.toEqual([ADDRESS_MATCH]);
  });

  it("searchAddress returns an empty list when nothing is found", async () => {
    answerWith(() => buildJsonAnswer(200, { matches: [] }));

    await expect(searchAddress("no such place")).resolves.toEqual([]);
  });

  it("readOsmCopy returns the day of the map data", async () => {
    answerWith(() => buildJsonAnswer(200, { date: "2026-10-02" }));

    await expect(readOsmCopy()).resolves.toBe("2026-10-02");
  });

  it("readOsmCopy returns null before the first copy exists", async () => {
    answerWith(() => buildJsonAnswer(200, { date: null }));

    await expect(readOsmCopy()).resolves.toBeNull();
  });

  it("listFactsInArea returns the facts and whether the answer was cut", async () => {
    answerWith(() => buildJsonAnswer(200, { facts: [FACT], is_truncated: true }));

    await expect(listFactsInArea(START, DESTINATION)).resolves.toEqual({ facts: [FACT], is_truncated: true });
  });

  it("readFact returns the fact", async () => {
    answerWith(() => buildJsonAnswer(200, { fact: FACT }));

    await expect(readFact(1042)).resolves.toEqual(FACT);
  });

  it("findNearbyFacts returns the facts with their distances", async () => {
    answerWith(() => buildJsonAnswer(200, { facts: [{ fact: FACT, distance_m: 8 }] }));

    await expect(findNearbyFacts("stairs", DESTINATION)).resolves.toEqual([{ fact: FACT, distance_m: 8 }]);
  });

  it("createFact returns the new fact of an answer with the status 201", async () => {
    answerWith(() => buildJsonAnswer(201, { fact: FACT }));

    await expect(createFact(REPORT)).resolves.toEqual(FACT);
  });

  it("castVote returns the fact with its status after the vote", async () => {
    answerWith(() => buildJsonAnswer(201, { fact: { ...FACT, status: "disputed" } }));

    await expect(castVote(1042, "deny")).resolves.toEqual({ ...FACT, status: "disputed" });
  });

  it("flagFact resolves for an answer with the status 204, which has no body", async () => {
    answerWith(() => buildEmptyAnswer());

    await expect(flagFact(1042)).resolves.toBeUndefined();
  });

  it("createAccount returns the account", async () => {
    answerWith(() => buildJsonAnswer(201, { account: ACCOUNT }));

    await expect(createAccount(PSEUDONYM, PASSWORD)).resolves.toEqual(ACCOUNT);
  });

  it("logIn returns the account", async () => {
    answerWith(() => buildJsonAnswer(200, { account: ACCOUNT }, { "Session-Token": RENEWED_TOKEN }));

    await expect(logIn(PSEUDONYM, PASSWORD)).resolves.toEqual(ACCOUNT);
  });

  it("readOwnAccount returns the account", async () => {
    answerWith(() => buildJsonAnswer(200, { account: { ...ACCOUNT, is_moderator: true } }));

    await expect(readOwnAccount()).resolves.toEqual({ ...ACCOUNT, is_moderator: true });
  });

  it("deleteOwnAccount resolves for an answer with the status 204 and removes the kept token", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildEmptyAnswer());

    await expect(deleteOwnAccount()).resolves.toBeUndefined();
    expect(readKeptToken()).toBeNull();
  });

  it("deleteOwnAccount keeps the token when the service refuses to delete", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(500, { error: { code: "internal_error" } }));

    await catchFailure(() => deleteOwnAccount());

    expect(readKeptToken()).toBe(KEPT_TOKEN);
  });

  it("listFlaggedFacts returns the flagged facts", async () => {
    answerWith(() => buildJsonAnswer(200, { facts: [FLAGGED_FACT] }));

    await expect(listFlaggedFacts()).resolves.toEqual([FLAGGED_FACT]);
  });

  it("hideFact returns the item of the fact, hidden", async () => {
    answerWith(() => buildJsonAnswer(200, { ...FLAGGED_FACT, is_hidden: true }));

    await expect(hideFact(1042)).resolves.toEqual({ ...FLAGGED_FACT, is_hidden: true });
  });

  it("restoreFact returns the item of the fact, not hidden", async () => {
    answerWith(() => buildJsonAnswer(200, FLAGGED_FACT));

    await expect(restoreFact(1042)).resolves.toEqual(FLAGGED_FACT);
  });
});

describe("the session token", () => {
  it("is kept from the header Session-Token of the answer to logIn", async () => {
    answerWith(() => buildJsonAnswer(200, { account: ACCOUNT }, { "Session-Token": RENEWED_TOKEN }));

    await logIn(PSEUDONYM, PASSWORD);

    expect(readKeptToken()).toBe(RENEWED_TOKEN);
  });

  it("is replaced by the renewed token of the header Session-Token", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(200, { fact: FACT }, { "Session-Token": RENEWED_TOKEN }));

    await readFact(1042);

    expect(readKeptToken()).toBe(RENEWED_TOKEN);
  });

  it("travels renewed with the next request", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(200, { fact: FACT }, { "Session-Token": RENEWED_TOKEN }));

    await readFact(1042);
    await readFact(1042);

    expect(readLatestRequest().headers.get("Authorization")).toBe(`Bearer ${RENEWED_TOKEN}`);
  });

  it("is replaced by the renewed token of an answer that is an error", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(409, { error: { code: "vote_too_soon", repeat_allowed_at: "2026-10-04T09:12:44.120+02:00" } }, { "Session-Token": RENEWED_TOKEN }));

    await catchFailure(() => castVote(1042, "confirm"));

    expect(readKeptToken()).toBe(RENEWED_TOKEN);
  });

  it("stays as it is when the answer carries no Session-Token", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(200, { fact: FACT }));

    await readFact(1042);

    expect(readKeptToken()).toBe(KEPT_TOKEN);
  });

  it("stays as it is when the answer carries an empty Session-Token", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(200, { fact: FACT }, { "Session-Token": "" }));

    await readFact(1042);

    expect(readKeptToken()).toBe(KEPT_TOKEN);
  });

  /**
   * The rule of the renewed token: it is kept only while the token the request carried is still the kept one.
   * Logging out is the client deleting its token, so the answer to a request that left before the logout
   * must not log the person in again.
   */
  it("does not bring back a token that was removed while the request was on its way", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const answer = holdAnswers();

    const request = readFact(1042);
    removeStored(STORAGE_KEYS.session);
    answer(buildJsonAnswer(200, { fact: FACT }, { "Session-Token": RENEWED_TOKEN }));

    await expect(request).resolves.toEqual(FACT);
    expect(readKeptToken()).toBeNull();
  });

  it("leaves the token of a later session in place when the answer to a request of the earlier one arrives", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const answer = holdAnswers();

    const request = readFact(1042);
    writeStored(STORAGE_KEYS.session, LATER_TOKEN);
    answer(buildJsonAnswer(200, { fact: FACT }, { "Session-Token": RENEWED_TOKEN }));

    await expect(request).resolves.toEqual(FACT);
    expect(readKeptToken()).toBe(LATER_TOKEN);
  });

  it("keeps a renewed token of the session when two of its requests are answered one after another", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const answer = holdAnswers();

    const first = readFact(1042);
    const second = readOsmCopy();
    answer(buildJsonAnswer(200, { fact: FACT }, { "Session-Token": "token-renewed-first" }));
    await first;
    answer(buildJsonAnswer(200, { date: "2026-10-02" }, { "Session-Token": "token-renewed-second" }));
    await second;

    expect(["token-renewed-first", "token-renewed-second"]).toContain(readKeptToken());
  });

  it("is replaced by the token of the answer to logIn, a request that carries none", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    answerWith(() => buildJsonAnswer(200, { account: ACCOUNT }, { "Session-Token": RENEWED_TOKEN }));

    await logIn(PSEUDONYM, PASSWORD);

    expect(readKeptToken()).toBe(RENEWED_TOKEN);
  });

  it("is removed when the service answers session_expired, and the listener of onSessionEnd is called", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const listener = listenForSessionEnd();
    answerWith(() => buildJsonAnswer(401, { error: { code: "session_expired" } }));

    const error = await catchFailure(() => readOwnAccount());

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code: "session_expired" });
    expect(readKeptToken()).toBeNull();
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it("ends for every listener of onSessionEnd", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const first = listenForSessionEnd();
    const second = listenForSessionEnd();
    answerWith(() => buildJsonAnswer(401, { error: { code: "session_expired" } }));

    await catchFailure(() => castVote(1042, "confirm"));

    expect(first).toHaveBeenCalledTimes(1);
    expect(second).toHaveBeenCalledTimes(1);
  });

  it("does not call a listener that was removed", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const listener = vi.fn<() => void>();
    const remove = onSessionEnd(listener);
    remove();
    answerWith(() => buildJsonAnswer(401, { error: { code: "session_expired" } }));

    await catchFailure(() => readOwnAccount());

    expect(listener).not.toHaveBeenCalled();
    expect(readKeptToken()).toBeNull();
  });

  it("does not end a later session when the answer to a request of the earlier one says that its session expired", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const listener = listenForSessionEnd();
    const answer = holdAnswers();

    const request = catchFailure(() => readOwnAccount());
    writeStored(STORAGE_KEYS.session, LATER_TOKEN);
    answer(buildJsonAnswer(401, { error: { code: "session_expired" } }));

    expect(await request).toMatchObject({ code: "session_expired" });
    expect(readKeptToken()).toBe(LATER_TOKEN);
    expect(listener).not.toHaveBeenCalled();
  });

  it("stays and ends for no listener when the answer is another error", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const listener = listenForSessionEnd();
    answerWith(() => buildJsonAnswer(403, { error: { code: "moderator_role_required" } }));

    await catchFailure(() => listFlaggedFacts());

    expect(readKeptToken()).toBe(KEPT_TOKEN);
    expect(listener).not.toHaveBeenCalled();
  });

  it("stays and ends for no listener when an answer is read without an error", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const listener = listenForSessionEnd();
    answerWith(() => buildJsonAnswer(200, { account: ACCOUNT }));

    await readOwnAccount();

    expect(readKeptToken()).toBe(KEPT_TOKEN);
    expect(listener).not.toHaveBeenCalled();
  });
});

describe("a failed request", () => {
  it("throws an ApiError with the code and the refused fields of the error body", async () => {
    answerWith(() => buildJsonAnswer(422, { error: { code: "invalid_request", fields: ["start.lat", "destination"] } }));

    const error = await catchFailure(() => planRoute(ROUTE_REQUEST));

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code: "invalid_request", fields: ["start.lat", "destination"], repeatAllowedAt: null });
  });

  it("throws an ApiError with the ends of a route that lie outside Kraków", async () => {
    answerWith(() => buildJsonAnswer(422, { error: { code: "point_outside_krakow", points: ["start", "elsewhere", "destination"] } }));

    const error = await catchFailure(() => planRoute(ROUTE_REQUEST));

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code: "point_outside_krakow", fields: [], points: ["start", "destination"] });
  });

  it("throws an ApiError with the instant from which the next vote is accepted", async () => {
    answerWith(() => buildJsonAnswer(409, { error: { code: "vote_too_soon", repeat_allowed_at: "2026-10-04T09:12:44.120+02:00" } }));

    const error = await catchFailure(() => castVote(1042, "confirm"));

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code: "vote_too_soon", fields: [], repeatAllowedAt: "2026-10-04T09:12:44.120+02:00" });
  });

  it.each([
    [503, "routing_unavailable"],
    [422, "invalid_search_text"],
    [503, "address_search_unavailable"],
    [409, "idempotency_key_reused"],
    [409, "fact_not_flaggable"],
    [409, "pseudonym_taken"],
    [401, "invalid_credentials"],
    [401, "authentication_required"],
    [403, "moderator_role_required"],
    [404, "fact_not_found"],
    [404, "not_found"],
    [409, "fact_not_flagged"],
    [500, "internal_error"],
  ])("throws an ApiError with the code of an answer %i %s, without a field and without an instant", async (status, code) => {
    answerWith(() => buildJsonAnswer(status, { error: { code } }));

    const error = await catchFailure(() => readFact(1042));

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code, fields: [], repeatAllowedAt: null });
  });

  it.each([
    ["a page of a proxy in place of JSON", () => new Response("<html>Bad Gateway</html>", { status: 502, headers: { "Content-Type": "text/html" } })],
    ["no body at all", () => new Response(null, { status: 500 })],
    ["JSON without an error", () => buildJsonAnswer(500, { message: "failed" })],
    ["an error without a code", () => buildJsonAnswer(500, { error: { fields: ["start"] } })],
    ["a code that is not a text", () => buildJsonAnswer(500, { error: { code: 500 } })],
    ["the JSON value null", () => buildJsonAnswer(500, null)],
  ])("throws an internal error for a failed answer with %s", async (_name, build) => {
    answerWith(build);

    const error = await catchFailure(() => readFact(1042));

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code: "internal_error", fields: [], repeatAllowedAt: null });
  });

  it("reads fields that are not a list as no field", async () => {
    answerWith(() => buildJsonAnswer(422, { error: { code: "invalid_request", fields: "start.lat" } }));

    const error = await catchFailure(() => planRoute(ROUTE_REQUEST));

    expect(error).toMatchObject({ code: "invalid_request", fields: [] });
  });

  it("throws a network error when fetch is rejected", async () => {
    fetchStandIn.mockRejectedValue(new TypeError("Failed to fetch"));

    const error = await catchFailure(() => planRoute(ROUTE_REQUEST));

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code: "network_error", fields: [], repeatAllowedAt: null });
  });

  it("keeps the token and ends no session when fetch is rejected", async () => {
    writeStored(STORAGE_KEYS.session, KEPT_TOKEN);
    const listener = listenForSessionEnd();
    fetchStandIn.mockRejectedValue(new TypeError("Failed to fetch"));

    await catchFailure(() => readOwnAccount());

    expect(readKeptToken()).toBe(KEPT_TOKEN);
    expect(listener).not.toHaveBeenCalled();
  });

  it("throws an internal error for an answer without an error whose body is not JSON", async () => {
    answerWith(() => new Response("<html>the page of the application</html>", { status: 200, headers: { "Content-Type": "text/html" } }));

    const error = await catchFailure(() => readFact(1042));

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ code: "internal_error" });
  });
});
