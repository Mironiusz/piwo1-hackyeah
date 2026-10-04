import type { ApiErrorCode } from "./types.ts";

/**
 * The one error of every failed request: the code of the contract, the fields the service refused,
 * and for a vote that came too soon the instant from which the next one is accepted.
 */
export class ApiError extends Error {
  readonly code: ApiErrorCode;
  readonly fields: readonly string[];
  readonly repeatAllowedAt: string | null;

  constructor(code: ApiErrorCode, fields: readonly string[] = [], repeatAllowedAt: string | null = null) {
    super(code);
    this.name = "ApiError";
    this.code = code;
    this.fields = fields;
    this.repeatAllowedAt = repeatAllowedAt;
  }
}

const ERROR_TEXT_KEYS: Partial<Record<ApiErrorCode, string>> = {
  routing_unavailable: "plan.unavailable.title",
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
};

/**
 * Returns the key of the text that tells a person about an error code, and state.failed for a code without its own text.
 */
export function errorTextKey(code: ApiErrorCode): string {
  return ERROR_TEXT_KEYS[code] ?? "state.failed";
}

/**
 * Turns anything a request threw into an ApiError, so a view handles one type.
 */
export function toApiError(error: unknown): ApiError {
  return error instanceof ApiError ? error : new ApiError("internal_error");
}
