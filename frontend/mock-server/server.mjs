/**
 * The temporary mock of the service, for the development run and the tests of the frontend only.
 * It answers the sixteen operations of docs/product/api_contract.md under /api on 127.0.0.1:8787,
 * from the files of mock-server/data/ and from a state kept in its memory, which a restart clears.
 * It applies no rule of the specification beyond what a screen needs to be drawn, and it never reaches the demo.
 *
 * What steers its answers, so that every state of a view can be reached:
 * - plan_route: a destination within 300 m of "Ogród Doświadczeń" gives the usual route with one alternative,
 *   a destination within 300 m of "Park Lotników" the route with the fewest barriers, and a start or a destination
 *   within 300 m of "Rondo Mogilskie" the refusal routing_unavailable. The address search finds all three places.
 * - search_address: the text "unavailable" gives address_search_unavailable, and a text no label holds gives an empty list.
 * - list_facts_in_area: a rectangle that holds "Rynek Główny" is answered as cut off.
 * - cast_vote: a second vote of the same person on a fact on the same calendar day gives vote_too_soon. The author of a report has voted on it.
 * - create_account: the account named "moderator" holds the moderator role.
 * - every operation that takes a token: the token "expired", and a token the mock does not know, give session_expired.
 * - create_fact: a fact created here is no sample data; every fact of the data files is.
 *
 * Usage: node mock-server/server.mjs
 */

import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { createServer } from "node:http";
import { fileURLToPath } from "node:url";

const HOST = "127.0.0.1";
const PORT = 8787;
const API_PREFIX = "/api";
const DAY_IN_MILLISECONDS = 24 * 60 * 60 * 1000;
const NEARBY_RADIUS_M = 15;
const CURVE_STEPS = 60;
const EXPIRED_TOKEN = "expired";
const MODERATOR_PSEUDONYM = "moderator";
const ANONYMOUS_VOTER = "anonymous";

const BARRIER_TYPES = ["stairs", "high_kerb", "poor_surface", "steep_incline", "narrow_passage"];
const AMENITY_TYPES = ["elevator", "ramp", "lowered_kerb", "accessible_toilet", "rest_place", "handrail_at_stairs"];
const GEOZONE_RADII = [10, 25, 50, 100];
const ALL_ATTRIBUTES = ["kerbs", "surface", "incline", "width", "steps"];

/**
 * Reads one data file of the mock as JSON.
 */
function readData(name) {
  return JSON.parse(readFileSync(fileURLToPath(new URL(`./data/${name}`, import.meta.url)), "utf8"));
}

const factsData = readData("facts.json");
const routesData = readData("routes.json");
const addressesData = readData("addresses.json");

const facts = new Map();
const flags = new Map();
const votes = new Map();
const accounts = new Map();
const sessions = new Map();
const savedKeys = new Map();
let nextFactId = 100;

for (const fact of factsData.facts) {
  facts.set(fact.id, { ...fact, is_removed_from_osm: false, is_sample: true, can_be_flagged: fact.source !== "openstreetmap" });
}

/**
 * A refusal of a request, sent as the error body of the contract.
 */
class Refusal extends Error {
  constructor(status, code, extra = {}) {
    super(code);
    this.status = status;
    this.code = code;
    this.extra = extra;
  }
}

/**
 * Waits a number of milliseconds, so the frontend shows its loading states.
 */
function wait(milliseconds) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

/**
 * Returns the parts of a moment on the clock of the Europe/Warsaw zone.
 */
function readWarsawClock(moment) {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/Warsaw",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
    timeZoneName: "longOffset",
  }).formatToParts(moment);
  const clock = {};
  for (const part of parts) {
    clock[part.type] = part.value;
  }
  return clock;
}

/**
 * Writes a moment as a calendar day of the Europe/Warsaw zone.
 */
function toDay(moment) {
  const clock = readWarsawClock(moment);
  return `${clock.year}-${clock.month}-${clock.day}`;
}

/**
 * Returns the instant at which the next calendar day of the Europe/Warsaw zone starts, from which the next vote
 * of a person on a fact is accepted.
 */
function findStartOfNextDay(moment) {
  const nextDay = new Date(moment.getTime() + DAY_IN_MILLISECONDS);
  const offset = readWarsawClock(nextDay).timeZoneName.replace("GMT", "") || "+00:00";
  return `${toDay(nextDay)}T00:00:00.000${offset}`;
}

/**
 * Returns the distance in metres between two points of the contract.
 */
function measure(first, second) {
  const toRadians = Math.PI / 180;
  const latitudeStep = (second.lat - first.lat) * toRadians;
  const longitudeStep = (second.lon - first.lon) * toRadians;
  const half = Math.sin(latitudeStep / 2) ** 2 + Math.cos(first.lat * toRadians) * Math.cos(second.lat * toRadians) * Math.sin(longitudeStep / 2) ** 2;
  return 2 * 6_371_000 * Math.asin(Math.sqrt(half));
}

/**
 * Tells whether a value is a point of the contract.
 */
function isPoint(value) {
  return typeof value === "object" && value !== null && typeof value.lat === "number" && typeof value.lon === "number";
}

/**
 * Tells whether a point lies within the radius of one of the named places that steer the answers of the mock.
 */
function isNear(point, placeName) {
  return measure(point, routesData.places[placeName].point) <= routesData.place_radius_m;
}

/**
 * Returns a text without diacritics and in small letters, for matching a search text.
 */
function fold(text) {
  return text
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/ł/g, "l")
    .replace(/Ł/g, "L")
    .toLowerCase();
}

/**
 * Returns the point of a route at a share of its way from the start to the destination.
 * The route bends to one side, so it is not a straight line.
 */
function findRoutePoint(start, destination, bend, share) {
  const scale = Math.cos((start.lat * Math.PI) / 180);
  const east = (destination.lon - start.lon) * scale;
  const north = destination.lat - start.lat;
  const swing = Math.sin(Math.PI * share) * bend;
  return {
    lat: start.lat + north * share + east * swing,
    lon: start.lon + (east * share - north * swing) / scale,
  };
}

/**
 * Returns the line of a route between two shares of its way, as pairs of longitude and latitude.
 */
function buildLine(start, destination, bend, fromShare, toShare) {
  const shares = [fromShare];
  for (let step = 1; step < CURVE_STEPS; step += 1) {
    const share = step / CURVE_STEPS;
    if (share > fromShare && share < toShare) {
      shares.push(share);
    }
  }
  shares.push(toShare);
  return shares.map((share) => {
    const point = findRoutePoint(start, destination, bend, share);
    return [Number(point.lon.toFixed(7)), Number(point.lat.toFixed(7))];
  });
}

/**
 * Returns the length of a line in metres.
 */
function measureLine(line) {
  let length = 0;
  for (let index = 1; index < line.length; index += 1) {
    length += measure({ lon: line[index - 1][0], lat: line[index - 1][1] }, { lon: line[index][0], lat: line[index][1] });
  }
  return length;
}

/**
 * Puts a fact of a route into the facts of the mock at its place on this route and returns it as a route fact.
 * A fact that is already kept holds its status, so a vote on it survives the next route.
 */
function placeRouteFact(key, point, distance) {
  const template = routesData.route_facts[key];
  const kept = facts.get(template.id);
  const fact = {
    id: template.id,
    type: template.type,
    point: { lat: Number(point.lat.toFixed(7)), lon: Number(point.lon.toFixed(7)) },
    geozone_radius_m: null,
    description: null,
    step_count: template.step_count,
    source: template.source,
    status: kept?.status ?? template.status,
    is_removed_from_osm: false,
    osm_edited_on: template.osm_edited_on,
    last_confirmed_on: kept?.last_confirmed_on ?? template.last_confirmed_on,
    is_sample: true,
    can_be_flagged: template.source !== "openstreetmap",
  };
  facts.set(fact.id, fact);
  return { ...fact, distance_from_start_m: Math.round(distance), is_overruled_by_osm: template.is_overruled_by_osm && fact.status !== "confirmed" };
}

/**
 * Builds one route of the answer from a template of routes.json, between the two points of the request and for its needs.
 */
function buildRoute(template, start, destination, avoid, need) {
  const totalLength = measureLine(buildLine(start, destination, template.bend, 0, 1));
  const segments = [];
  const profileBarriers = [];
  const additionalBarriers = [];
  const amenities = [];
  const bounds = [];
  let fromShare = 0;

  /**
   * Sorts a fact of the route into the group of the list it belongs to and tells whether it is a barrier of the needs.
   */
  const sortFact = (key, share) => {
    const point = findRoutePoint(start, destination, template.bend, share);
    const type = routesData.route_facts[key].type;
    if (hiddenIds().has(routesData.route_facts[key].id)) {
      return false;
    }
    if (BARRIER_TYPES.includes(type)) {
      const routeFact = placeRouteFact(key, point, totalLength * share);
      if (avoid.includes(type)) {
        profileBarriers.push(routeFact);
        return true;
      }
      additionalBarriers.push(routeFact);
      return false;
    }
    if (need.includes(type)) {
      amenities.push(placeRouteFact(key, point, totalLength * share));
    }
    return false;
  };

  template.stretches.forEach((stretch, index) => {
    const toShare = index === template.stretches.length - 1 ? 1 : fromShare + stretch.share;
    const line = buildLine(start, destination, template.bend, fromShare, toShare);
    let state = stretch.state;
    if (stretch.fact !== null && sortFact(stretch.fact, (fromShare + toShare) / 2)) {
      state = "barrier";
    }
    bounds.push({ fromShare, toShare });
    segments.push({
      line,
      length_m: Math.round(measureLine(line)),
      state,
      missing_attributes: state === "no_data" ? ALL_ATTRIBUTES : state === "partial_data" ? ["surface", "incline"] : [],
      is_marked_wheelchair_no: template.wheelchair_no_stretch === index,
    });
    fromShare = toShare;
  });

  for (const other of template.others) {
    if (sortFact(other.fact, other.at)) {
      const index = bounds.findIndex((bound) => other.at >= bound.fromShare && other.at <= bound.toShare);
      if (index !== -1) {
        segments[index].state = "barrier";
        segments[index].missing_attributes = [];
      }
    }
  }

  const byDistance = (first, second) => first.distance_from_start_m - second.distance_from_start_m;
  return {
    length_m: segments.reduce((sum, segment) => sum + segment.length_m, 0),
    segments,
    profile_barriers: profileBarriers.sort(byDistance),
    additional_barriers: additionalBarriers.sort(byDistance),
    amenities: amenities.sort(byDistance),
  };
}

/**
 * Returns the identifiers of the facts a moderator has hidden.
 */
function hiddenIds() {
  const hidden = new Set();
  for (const [id, flag] of flags) {
    if (flag.is_hidden) {
      hidden.add(id);
    }
  }
  return hidden;
}

/**
 * Returns a fact that is kept and not hidden, or refuses the request as the contract does.
 */
function findVisibleFact(id) {
  const fact = facts.get(id);
  if (fact === undefined || hiddenIds().has(id)) {
    throw new Refusal(404, "fact_not_found");
  }
  return fact;
}

/**
 * Returns the account of the contract for a kept account.
 */
function describeAccount(account) {
  return { pseudonym: account.pseudonym, is_moderator: account.pseudonym.toLowerCase() === MODERATOR_PSEUDONYM };
}

/**
 * Returns the item of the moderation list for a flagged fact.
 */
function describeFlagged(id) {
  const flag = flags.get(id);
  return { fact: facts.get(id), flagged_on: flag.flagged_on, is_hidden: flag.is_hidden };
}

/**
 * Refuses a request whose body lacks a field or holds a value of a wrong form.
 */
function requireFields(checks) {
  const fields = Object.entries(checks)
    .filter(([, isValid]) => !isValid)
    .map(([field]) => field);
  if (fields.length > 0) {
    throw new Refusal(422, "invalid_request", { fields });
  }
}

/**
 * Tells whether a list holds only values of a closed list, each at most once.
 */
function isListOf(value, allowed) {
  return Array.isArray(value) && value.every((item) => allowed.includes(item)) && new Set(value).size === value.length;
}

const operations = [
  {
    name: "plan_route",
    method: "POST",
    path: /^\/routes$/,
    actor: "none",
    delay: 700,
    run: ({ body }) => {
      requireFields({
        start: isPoint(body.start),
        destination: isPoint(body.destination),
        avoid: isListOf(body.avoid, BARRIER_TYPES),
        need: isListOf(body.need, AMENITY_TYPES),
      });
      if (isNear(body.start, "routing_unavailable") || isNear(body.destination, "routing_unavailable")) {
        throw new Refusal(503, "routing_unavailable");
      }
      const hasNoFreeRoute = isNear(body.destination, "no_barrier_free_route");
      const route = buildRoute(routesData.routes[hasNoFreeRoute ? "fewest_barriers" : "usual"], body.start, body.destination, body.avoid, body.need);
      const kept = route.profile_barriers.filter((fact) => fact.status === "unverified" || fact.status === "disputed");
      const alternative =
        !hasNoFreeRoute && isNear(body.destination, "usual_with_alternative") && kept.length > 0
          ? { route: buildRoute(routesData.routes.alternative, body.start, body.destination, body.avoid, body.need), avoided_barriers: kept }
          : null;
      return {
        status: 200,
        body: {
          osm_copy_date: factsData.osm_copy_date,
          barrier_free_route_exists: !(hasNoFreeRoute && route.profile_barriers.length > 0),
          route,
          alternative,
        },
      };
    },
  },
  {
    name: "search_address",
    method: "POST",
    path: /^\/address-search$/,
    actor: "none",
    delay: 400,
    run: ({ body }) => {
      requireFields({ text: typeof body.text === "string" });
      const text = body.text
        .replace(/\bul\.|\bulica\b/giu, " ")
        .replace(/\s+/g, " ")
        .trim();
      if ([...body.text].length > 200 || text === "") {
        throw new Refusal(422, "invalid_search_text");
      }
      if (text.toLowerCase() === "unavailable") {
        throw new Refusal(503, "address_search_unavailable");
      }
      const wanted = fold(text);
      return { status: 200, body: { matches: addressesData.matches.filter((match) => fold(match.label).includes(wanted)).slice(0, 10) } };
    },
  },
  {
    name: "read_osm_copy",
    method: "GET",
    path: /^\/osm-copy$/,
    actor: "optional",
    delay: 80,
    run: () => ({ status: 200, body: { date: factsData.osm_copy_date } }),
  },
  {
    name: "list_facts_in_area",
    method: "POST",
    path: /^\/facts\/in-area$/,
    actor: "optional",
    delay: 250,
    run: ({ body }) => {
      requireFields({ south_west: isPoint(body.south_west), north_east: isPoint(body.north_east) });
      requireFields({ south_west: body.south_west.lat < body.north_east.lat && body.south_west.lon < body.north_east.lon });
      const isInside = (point) => point.lat >= body.south_west.lat && point.lat <= body.north_east.lat && point.lon >= body.south_west.lon && point.lon <= body.north_east.lon;
      const hidden = hiddenIds();
      return {
        status: 200,
        body: {
          facts: [...facts.values()].filter((fact) => !hidden.has(fact.id) && !fact.is_removed_from_osm && isInside(fact.point)),
          is_truncated: isInside(routesData.places.too_many_facts.point),
        },
      };
    },
  },
  {
    name: "find_nearby_facts",
    method: "POST",
    path: /^\/facts\/nearby$/,
    actor: "optional",
    delay: 250,
    run: ({ body }) => {
      requireFields({ type: [...BARRIER_TYPES, ...AMENITY_TYPES].includes(body.type), point: isPoint(body.point) });
      const hidden = hiddenIds();
      const nearby = [...facts.values()]
        .filter((fact) => fact.type === body.type && !hidden.has(fact.id))
        .map((fact) => ({ fact, distance_m: Math.round(measure(fact.point, body.point)) }))
        .filter((item) => item.distance_m <= NEARBY_RADIUS_M)
        .sort((first, second) => first.distance_m - second.distance_m);
      return { status: 200, body: { facts: nearby } };
    },
  },
  {
    name: "create_fact",
    method: "POST",
    path: /^\/facts$/,
    actor: "optional",
    delay: 500,
    run: ({ body, voter }) => {
      const isGeozone = body.geozone_radius_m !== null && body.geozone_radius_m !== undefined;
      const description = typeof body.description === "string" ? body.description.trim() : null;
      requireFields({
        idempotency_key: typeof body.idempotency_key === "string" && body.idempotency_key !== "",
        type: (isGeozone ? BARRIER_TYPES : [...BARRIER_TYPES, ...AMENITY_TYPES]).includes(body.type),
        point: isPoint(body.point),
        description: body.description === null || body.description === undefined || (typeof body.description === "string" && [...description].length <= 500),
        step_count: body.step_count === null || body.step_count === undefined || (body.type === "stairs" && Number.isInteger(body.step_count) && body.step_count >= 1 && body.step_count <= 999),
        geozone_radius_m: !isGeozone || GEOZONE_RADII.includes(body.geozone_radius_m),
      });
      const content = JSON.stringify([body.type, body.point, description, body.step_count ?? null, body.geozone_radius_m ?? null]);
      const saved = savedKeys.get(body.idempotency_key);
      if (saved !== undefined) {
        if (saved.content !== content) {
          throw new Refusal(409, "idempotency_key_reused");
        }
        return { status: 200, body: { fact: facts.get(saved.factId) } };
      }
      const now = new Date();
      const fact = {
        id: nextFactId,
        type: body.type,
        point: body.point,
        geozone_radius_m: body.geozone_radius_m ?? null,
        description: description === "" ? null : description,
        step_count: body.step_count ?? null,
        source: "user_report",
        status: "unverified",
        is_removed_from_osm: false,
        osm_edited_on: null,
        last_confirmed_on: toDay(now),
        is_sample: false,
        can_be_flagged: true,
      };
      nextFactId += 1;
      facts.set(fact.id, fact);
      votes.set(`${voter}:${fact.id}`, toDay(now));
      savedKeys.set(body.idempotency_key, { content, factId: fact.id });
      return { status: 201, body: { fact } };
    },
  },
  {
    name: "cast_vote",
    method: "POST",
    path: /^\/facts\/(\d+)\/votes$/,
    actor: "optional",
    delay: 400,
    run: ({ body, voter, id }) => {
      requireFields({ verdict: body.verdict === "confirm" || body.verdict === "deny" });
      const fact = findVisibleFact(id);
      const now = new Date();
      if (votes.get(`${voter}:${id}`) === toDay(now)) {
        throw new Refusal(409, "vote_too_soon", { repeat_allowed_at: findStartOfNextDay(now) });
      }
      votes.set(`${voter}:${id}`, toDay(now));
      if (body.verdict === "confirm") {
        fact.status = "confirmed";
        fact.last_confirmed_on = toDay(now);
      } else {
        fact.status = fact.status === "confirmed" ? "disputed" : "outdated";
      }
      return { status: 201, body: { fact } };
    },
  },
  {
    name: "flag_fact",
    method: "POST",
    path: /^\/facts\/(\d+)\/flag$/,
    actor: "optional",
    delay: 300,
    run: ({ id }) => {
      const fact = findVisibleFact(id);
      if (!fact.can_be_flagged) {
        throw new Refusal(409, "fact_not_flaggable");
      }
      flags.set(id, { flagged_on: toDay(new Date()), is_hidden: false });
      return { status: 204, body: null };
    },
  },
  {
    name: "read_fact",
    method: "GET",
    path: /^\/facts\/(\d+)$/,
    actor: "optional",
    delay: 200,
    run: ({ id }) => ({ status: 200, body: { fact: findVisibleFact(id) } }),
  },
  {
    name: "create_account",
    method: "POST",
    path: /^\/accounts$/,
    actor: "none",
    delay: 400,
    run: ({ body }) => {
      const pseudonym = typeof body.pseudonym === "string" ? body.pseudonym.trim() : "";
      const pseudonymLength = [...pseudonym].length;
      const passwordLength = typeof body.password === "string" ? [...body.password].length : 0;
      requireFields({
        pseudonym: pseudonymLength >= 3 && pseudonymLength <= 30 && !/\p{Cc}/u.test(pseudonym),
        password: passwordLength >= 5 && passwordLength <= 128,
      });
      if (accounts.has(pseudonym.toLowerCase())) {
        throw new Refusal(409, "pseudonym_taken");
      }
      const account = { pseudonym, password: body.password };
      accounts.set(pseudonym.toLowerCase(), account);
      return { status: 201, body: { account: describeAccount(account) } };
    },
  },
  {
    name: "log_in",
    method: "POST",
    path: /^\/sessions$/,
    actor: "none",
    delay: 400,
    run: ({ body }) => {
      requireFields({ pseudonym: typeof body.pseudonym === "string", password: typeof body.password === "string" });
      const key = body.pseudonym.trim().toLowerCase();
      const account = accounts.get(key);
      if (account === undefined || account.password !== body.password) {
        throw new Refusal(401, "invalid_credentials");
      }
      const token = randomUUID();
      sessions.set(token, key);
      return { status: 200, body: { account: describeAccount(account) }, token };
    },
  },
  {
    name: "read_own_account",
    method: "GET",
    path: /^\/accounts\/me$/,
    actor: "required",
    delay: 150,
    run: ({ account }) => ({ status: 200, body: { account: describeAccount(account) } }),
  },
  {
    name: "delete_own_account",
    method: "DELETE",
    path: /^\/accounts\/me$/,
    actor: "required",
    delay: 400,
    run: ({ account }) => {
      const key = account.pseudonym.toLowerCase();
      accounts.delete(key);
      for (const [token, owner] of sessions) {
        if (owner === key) {
          sessions.delete(token);
        }
      }
      return { status: 204, body: null, token: null };
    },
  },
  {
    name: "list_flagged_facts",
    method: "GET",
    path: /^\/moderation\/flagged-facts$/,
    actor: "moderator",
    delay: 250,
    run: () => ({ status: 200, body: { facts: [...flags.keys()].reverse().map(describeFlagged) } }),
  },
  {
    name: "hide_fact",
    method: "POST",
    path: /^\/moderation\/flagged-facts\/(\d+)\/hide$/,
    actor: "moderator",
    delay: 300,
    run: ({ id }) => {
      if (!flags.has(id)) {
        throw new Refusal(409, "fact_not_flagged");
      }
      flags.get(id).is_hidden = true;
      return { status: 200, body: describeFlagged(id) };
    },
  },
  {
    name: "restore_fact",
    method: "POST",
    path: /^\/moderation\/flagged-facts\/(\d+)\/restore$/,
    actor: "moderator",
    delay: 300,
    run: ({ id }) => {
      if (!flags.has(id)) {
        throw new Refusal(409, "fact_not_flagged");
      }
      flags.get(id).is_hidden = false;
      return { status: 200, body: describeFlagged(id) };
    },
  },
];

/**
 * Reads the body of a request as JSON. A request without a body reads as an empty object.
 */
async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) {
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString("utf8");
  if (text === "") {
    return {};
  }
  try {
    const body = JSON.parse(text);
    if (typeof body !== "object" || body === null || Array.isArray(body)) {
      throw new Refusal(422, "invalid_request", { fields: [] });
    }
    return body;
  } catch {
    throw new Refusal(422, "invalid_request", { fields: [] });
  }
}

/**
 * Finds the account of the token a request carries, by the rules of the section Sessions and actors of the contract.
 * Returns the token with its account, or nulls for a request without a token.
 */
function resolveActor(request, operation) {
  const header = request.headers.authorization;
  if (operation.actor === "none" || header === undefined) {
    if (operation.actor === "required" || operation.actor === "moderator") {
      throw new Refusal(401, "authentication_required");
    }
    return { token: null, account: null };
  }
  const token = header.replace(/^Bearer\s+/i, "");
  const account = accounts.get(sessions.get(token) ?? "");
  if (token === EXPIRED_TOKEN || account === undefined) {
    throw new Refusal(401, "session_expired");
  }
  if (operation.actor === "moderator" && !describeAccount(account).is_moderator) {
    throw new Refusal(403, "moderator_role_required");
  }
  return { token, account };
}

/**
 * Answers one request: finds its operation, runs it, and writes the answer or the error body of the contract.
 */
async function answer(request, response) {
  const requestId = randomUUID();
  const send = (status, body, headers = {}) => {
    const text = body === null ? "" : JSON.stringify(body);
    response.writeHead(status, { "X-Request-Id": requestId, ...(body === null ? {} : { "Content-Type": "application/json; charset=utf-8" }), ...headers });
    response.end(text);
  };
  let name = "unknown";
  try {
    const url = new URL(request.url ?? "/", `http://${HOST}:${PORT}`);
    const path = url.pathname.startsWith(API_PREFIX) ? url.pathname.slice(API_PREFIX.length) : null;
    const operation = path === null ? undefined : operations.find((candidate) => candidate.method === request.method && candidate.path.test(path));
    if (operation === undefined || path === null) {
      throw new Refusal(404, "not_found");
    }
    name = operation.name;
    const actor = resolveActor(request, operation);
    const body = await readBody(request);
    await wait(operation.delay);
    const match = operation.path.exec(path);
    const result = operation.run({
      body,
      account: actor.account,
      voter: actor.account === null ? ANONYMOUS_VOTER : actor.account.pseudonym.toLowerCase(),
      id: match !== null && match[1] !== undefined ? Number(match[1]) : null,
    });
    const token = result.token === undefined ? actor.token : result.token;
    send(result.status, result.body, token === null ? {} : { "Session-Token": token });
    console.log(`${name} ${result.status}`);
  } catch (error) {
    if (error instanceof Refusal) {
      send(error.status, { error: { code: error.code, ...error.extra } });
      console.log(`${name} ${error.status} ${error.code}`);
      return;
    }
    send(500, { error: { code: "internal_error" } });
    console.log(`${name} 500 internal_error`);
  }
}

createServer((request, response) => {
  void answer(request, response);
}).listen(PORT, HOST, () => {
  console.log(`The mock of the service answers on http://${HOST}:${PORT}${API_PREFIX}`);
});
