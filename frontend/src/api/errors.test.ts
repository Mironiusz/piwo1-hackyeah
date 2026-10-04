import { describe, expect, it } from "vitest";

import { en } from "../i18n/en.ts";
import { pl } from "../i18n/pl.ts";
import { ApiError, errorTextKey, toApiError } from "./errors.ts";
import type { ApiErrorCode } from "./types.ts";

const FAILED_TEXT_KEY = "state.failed";

/**
 * The text key of every error code: the codes with a text of their own, and state.failed for the others.
 * The type makes the table name every code, so a new code fails the type check until its text is decided here.
 */
const EXPECTED_TEXT_KEYS: Record<ApiErrorCode, string> = {
  routing_unavailable: "plan.unavailable.title",
  point_outside_krakow: "plan.outside",
  invalid_search_text: "search.invalid",
  address_search_unavailable: "search.unavailable",
  vote_too_soon: "vote.too_soon",
  pseudonym_taken: "account.pseudonym.taken",
  invalid_credentials: "account.invalid_credentials",
  session_expired: "account.session_expired",
  authentication_required: "account.session_expired",
  moderator_role_required: "moderation.denied",
  fact_not_found: "fact.gone",
  network_error: "state.offline",
  invalid_request: FAILED_TEXT_KEY,
  not_found: FAILED_TEXT_KEY,
  internal_error: FAILED_TEXT_KEY,
  idempotency_key_reused: FAILED_TEXT_KEY,
  fact_not_flaggable: FAILED_TEXT_KEY,
  fact_not_flagged: FAILED_TEXT_KEY,
};

const EXPECTED_ROWS = Object.entries(EXPECTED_TEXT_KEYS) as [ApiErrorCode, string][];

describe("errorTextKey", () => {
  it.each(EXPECTED_ROWS.filter(([, key]) => key !== FAILED_TEXT_KEY))("returns the own text of the code %s", (code, key) => {
    expect(errorTextKey(code)).toBe(key);
  });

  it.each(EXPECTED_ROWS.filter(([, key]) => key === FAILED_TEXT_KEY))("returns state.failed for the code %s, which has no text of its own", (code) => {
    expect(errorTextKey(code)).toBe(FAILED_TEXT_KEY);
  });

  it.each(EXPECTED_ROWS)("returns for the code %s a key that both dictionaries hold", (code) => {
    const key = errorTextKey(code);

    expect(pl[key]).toBeTypeOf("string");
    expect(en[key]).toBeTypeOf("string");
  });
});

describe("ApiError", () => {
  it("carries the code, the refused fields and the instant of the next vote", () => {
    const error = new ApiError("vote_too_soon", ["verdict"], "2026-10-04T09:12:44.120+02:00");

    expect(error.code).toBe("vote_too_soon");
    expect(error.fields).toEqual(["verdict"]);
    expect(error.repeatAllowedAt).toBe("2026-10-04T09:12:44.120+02:00");
  });

  it("has no field and no instant when only the code is given", () => {
    const error = new ApiError("internal_error");

    expect(error.fields).toEqual([]);
    expect(error.repeatAllowedAt).toBeNull();
  });

  it("is an error named ApiError with the code as its message", () => {
    const error = new ApiError("routing_unavailable");

    expect(error).toBeInstanceOf(Error);
    expect(error.name).toBe("ApiError");
    expect(error.message).toBe("routing_unavailable");
  });
});

describe("toApiError", () => {
  it("returns an ApiError as it is", () => {
    const error = new ApiError("pseudonym_taken", ["pseudonym"]);

    expect(toApiError(error)).toBe(error);
  });

  it.each([
    ["another error", new TypeError("The answer has no route")],
    ["a text", "failed"],
    ["nothing", undefined],
    ["an empty value", null],
    ["an object that only looks like the error", { code: "vote_too_soon", fields: [], repeatAllowedAt: null }],
  ])("turns %s into an internal error", (_name, thrown) => {
    const error = toApiError(thrown);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.code).toBe("internal_error");
    expect(error.fields).toEqual([]);
    expect(error.repeatAllowedAt).toBeNull();
  });
});
