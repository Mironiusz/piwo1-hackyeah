import { errorTextKey, type ApiError } from "../api/errors.ts";

export type AccountField = "pseudonym" | "password";

/**
 * The key of the text shown next to each field of the account form, or null for a field without a message.
 */
export type AccountFieldErrors = Record<AccountField, string | null>;

/**
 * What the account form shows after a request failed: the messages next to its fields, and the key of the text of a message
 * that belongs to no field, or null when every message stands next to a field.
 */
export interface AccountFailure {
  fieldErrors: AccountFieldErrors;
  failure: string | null;
}

/**
 * The fields of the account form in the order they stand in it.
 */
export const ACCOUNT_FIELDS: readonly AccountField[] = ["pseudonym", "password"];

/**
 * The key of the text that states the rule of each field.
 */
export const ACCOUNT_FIELD_RULES: Record<AccountField, string> = {
  pseudonym: "account.pseudonym.rule",
  password: "account.password.rule",
};

/**
 * The account form without a message next to a field.
 */
export const NO_ACCOUNT_FIELD_ERRORS: AccountFieldErrors = { pseudonym: null, password: null };

const PSEUDONYM_PATTERN = /^[A-Za-ząćęłńóśźżĄĆĘŁŃÓŚŹŻ0-9_-]{3,30}$/;

const PASSWORD_MIN_LENGTH = 5;

/**
 * Returns a pseudonym as the service keeps it: without its leading and trailing spaces.
 */
export function trimPseudonym(pseudonym: string): string {
  return pseudonym.trim();
}

/**
 * Tells whether a pseudonym keeps its rule: after its leading and trailing spaces are removed it has 3 to 30 characters
 * of the 26 Latin letters and the nine Polish letters, each in both cases, the digits 0 to 9, the underscore and the hyphen.
 * A letter of another alphabet and a Polish letter written as a letter with a separate mark are refused, as the service refuses them.
 */
export function isPseudonymValid(pseudonym: string): boolean {
  return PSEUDONYM_PATTERN.test(trimPseudonym(pseudonym));
}

/**
 * Tells whether a password keeps its rule: at least 5 characters, each of them a Unicode code point, spaces included.
 */
export function isPasswordValid(password: string): boolean {
  return [...password].length >= PASSWORD_MIN_LENGTH;
}

/**
 * Checks the two fields of the account form before a request is sent.
 * A field that breaks its rule gets the key of the text of that rule.
 */
export function checkAccountForm(pseudonym: string, password: string): AccountFieldErrors {
  return {
    pseudonym: isPseudonymValid(pseudonym) ? null : ACCOUNT_FIELD_RULES.pseudonym,
    password: isPasswordValid(password) ? null : ACCOUNT_FIELD_RULES.password,
  };
}

/**
 * Returns the first field that has a message, in the order of the form, or null when no field has one.
 */
export function findFirstInvalidField(fieldErrors: AccountFieldErrors): AccountField | null {
  return ACCOUNT_FIELDS.find((field) => fieldErrors[field] !== null) ?? null;
}

/**
 * Turns the refusal of creating an account or of logging in into what the form shows.
 * A taken pseudonym stands next to the pseudonym, and a field the service names as breaking its rule gets the text of that rule.
 * Every other refusal, also a refused request that names neither field, is one message of the form.
 */
export function describeAccountFailure(error: ApiError): AccountFailure {
  if (error.code === "pseudonym_taken") {
    return { fieldErrors: { ...NO_ACCOUNT_FIELD_ERRORS, pseudonym: errorTextKey(error.code) }, failure: null };
  }
  if (error.code === "invalid_request") {
    const fieldErrors: AccountFieldErrors = {
      pseudonym: error.fields.includes("pseudonym") ? ACCOUNT_FIELD_RULES.pseudonym : null,
      password: error.fields.includes("password") ? ACCOUNT_FIELD_RULES.password : null,
    };
    if (findFirstInvalidField(fieldErrors) !== null) {
      return { fieldErrors, failure: null };
    }
  }
  return { fieldErrors: NO_ACCOUNT_FIELD_ERRORS, failure: errorTextKey(error.code) };
}
