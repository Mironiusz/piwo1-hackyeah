import { describe, expect, it } from "vitest";

import { ApiError } from "../api/errors.ts";
import { en } from "../i18n/en.ts";
import { pl } from "../i18n/pl.ts";
import {
  ACCOUNT_FIELD_RULES,
  ACCOUNT_FIELDS,
  checkAccountForm,
  describeAccountFailure,
  findFirstInvalidField,
  isPasswordValid,
  isPseudonymValid,
  NO_ACCOUNT_FIELD_ERRORS,
  trimPseudonym,
} from "./accountForm.ts";

const PSEUDONYM_RULE = "account.pseudonym.rule";
const PASSWORD_RULE = "account.password.rule";

describe("isPseudonymValid", () => {
  it.each([
    ["three letters", "abc"],
    ["thirty characters", "a".repeat(30)],
    ["Polish letters", "Wózek_Żółć"],
    ["digits, the underscore and the hyphen", "wozek_krk-2026"],
    ["only digits", "123"],
    ["spaces around a pseudonym that keeps the rule", "  wozek_krk  "],
    ["three letters outside the basic plane, each one character", "\u{1D400}\u{1D401}\u{1D402}"],
  ])("accepts %s", (_name, pseudonym) => {
    expect(isPseudonymValid(pseudonym)).toBe(true);
  });

  it.each([
    ["an empty text", ""],
    ["only spaces", "     "],
    ["two characters", "ab"],
    ["two characters between spaces", "  ab  "],
    ["thirty one characters", "a".repeat(31)],
    ["a space inside", "wozek krk"],
    ["a dot", "wozek.krk"],
    ["an at sign", "wozek@krk"],
    ["a line break inside", "wozek\nkrk"],
  ])("refuses %s", (_name, pseudonym) => {
    expect(isPseudonymValid(pseudonym)).toBe(false);
  });
});

describe("trimPseudonym", () => {
  it("removes the leading and trailing spaces and keeps the letter case", () => {
    expect(trimPseudonym("  Wozek_KRK ")).toBe("Wozek_KRK");
  });
});

describe("isPasswordValid", () => {
  it.each([
    ["five characters", "abcde"],
    ["five spaces", "     "],
    ["a long sentence with spaces", "five or more characters"],
    ["five characters outside the basic plane", "\u{1D400}\u{1D401}\u{1D402}\u{1D403}\u{1D404}"],
  ])("accepts %s", (_name, password) => {
    expect(isPasswordValid(password)).toBe(true);
  });

  it.each([
    ["an empty text", ""],
    ["four characters", "abcd"],
    ["four characters outside the basic plane, which are eight code units", "\u{1D400}\u{1D401}\u{1D402}\u{1D403}"],
  ])("refuses %s", (_name, password) => {
    expect(isPasswordValid(password)).toBe(false);
  });
});

describe("checkAccountForm", () => {
  it("gives no message when both fields keep their rules", () => {
    expect(checkAccountForm("wozek_krk", "secret123")).toEqual(NO_ACCOUNT_FIELD_ERRORS);
  });

  it("gives the rule of the pseudonym for a pseudonym that breaks it", () => {
    expect(checkAccountForm("ab", "secret123")).toEqual({ pseudonym: PSEUDONYM_RULE, password: null });
  });

  it("gives the rule of the password for a password that breaks it", () => {
    expect(checkAccountForm("wozek_krk", "abcd")).toEqual({ pseudonym: null, password: PASSWORD_RULE });
  });

  it("gives both rules when both fields are empty", () => {
    expect(checkAccountForm("", "")).toEqual({ pseudonym: PSEUDONYM_RULE, password: PASSWORD_RULE });
  });
});

describe("findFirstInvalidField", () => {
  it("returns null when no field has a message", () => {
    expect(findFirstInvalidField(NO_ACCOUNT_FIELD_ERRORS)).toBeNull();
  });

  it("returns the pseudonym when both fields have a message", () => {
    expect(findFirstInvalidField({ pseudonym: PSEUDONYM_RULE, password: PASSWORD_RULE })).toBe("pseudonym");
  });

  it("returns the password when only the password has a message", () => {
    expect(findFirstInvalidField({ pseudonym: null, password: PASSWORD_RULE })).toBe("password");
  });
});

describe("describeAccountFailure", () => {
  it("puts a taken pseudonym next to the pseudonym", () => {
    expect(describeAccountFailure(new ApiError("pseudonym_taken"))).toEqual({ fieldErrors: { pseudonym: "account.pseudonym.taken", password: null }, failure: null });
  });

  it("puts the rule next to the field the service refused", () => {
    expect(describeAccountFailure(new ApiError("invalid_request", ["password"]))).toEqual({ fieldErrors: { pseudonym: null, password: PASSWORD_RULE }, failure: null });
  });

  it("puts both rules next to both fields the service refused", () => {
    expect(describeAccountFailure(new ApiError("invalid_request", ["pseudonym", "password"]))).toEqual({ fieldErrors: { pseudonym: PSEUDONYM_RULE, password: PASSWORD_RULE }, failure: null });
  });

  it("turns a refused request that names neither field into the message that something failed", () => {
    expect(describeAccountFailure(new ApiError("invalid_request", []))).toEqual({ fieldErrors: NO_ACCOUNT_FIELD_ERRORS, failure: "state.failed" });
  });

  it.each([
    ["invalid_credentials", "account.invalid_credentials"],
    ["network_error", "state.offline"],
    ["internal_error", "state.failed"],
    ["not_found", "state.failed"],
  ] as const)("turns the code %s into one message of the form", (code, key) => {
    expect(describeAccountFailure(new ApiError(code))).toEqual({ fieldErrors: NO_ACCOUNT_FIELD_ERRORS, failure: key });
  });
});

describe("the texts of the account form", () => {
  it.each(ACCOUNT_FIELDS)("has the rule of the field %s in both dictionaries", (field) => {
    const key = ACCOUNT_FIELD_RULES[field];

    expect(pl[key]).toBeTypeOf("string");
    expect(en[key]).toBeTypeOf("string");
  });
});
