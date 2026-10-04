import { describe, expect, it } from "vitest";

import { en } from "../i18n/en.ts";
import { pl } from "../i18n/pl.ts";
import { splitAroundPart, splitLeadSentence } from "./textParts.ts";

/**
 * The texts whose first sentence the privacy information and the page about the data set in bold.
 */
const LEAD_TEXT_KEYS = [
  "privacy.kept.account",
  "privacy.kept.vote",
  "privacy.not_kept.needs",
  "privacy.not_kept.location",
  "privacy.not_kept.email",
  "privacy.not_kept.disability",
  "data.sources.map",
  "data.sources.map.no_date",
  "data.sources.reports",
  "data.segment.barrier",
  "data.segment.no_barrier",
  "data.segment.partial_data",
  "data.segment.no_data",
];

describe("splitLeadSentence", () => {
  it("cuts a text after its first sentence and keeps the space with the rest", () => {
    expect(splitLeadSentence("An email address. We do not ask for one.")).toEqual({ lead: "An email address.", rest: " We do not ask for one." });
  });

  it("cuts only after the first sentence of a text of three", () => {
    expect(splitLeadSentence("One. Two. Three.")).toEqual({ lead: "One.", rest: " Two. Three." });
  });

  it("returns a text of one sentence whole as the rest", () => {
    expect(splitLeadSentence("This cannot be undone.")).toEqual({ lead: "", rest: "This cannot be undone." });
  });

  it("returns an empty text as an empty rest", () => {
    expect(splitLeadSentence("")).toEqual({ lead: "", rest: "" });
  });

  it.each(LEAD_TEXT_KEYS)("finds a lead and a rest in both languages of the text %s", (key) => {
    for (const dictionary of [pl, en]) {
      const text = dictionary[key] ?? "";
      const split = splitLeadSentence(text);

      expect(split.lead.endsWith(".")).toBe(true);
      expect(split.rest.startsWith(" ")).toBe(true);
      expect(split.lead + split.rest).toBe(text);
    }
  });
});

describe("splitAroundPart", () => {
  it("cuts a text around the part it holds", () => {
    expect(splitAroundPart("Each one carries the mark sample data.", "sample data")).toEqual({ before: "Each one carries the mark ", after: "." });
  });

  it("cuts around the first place of a part that stands twice", () => {
    expect(splitAroundPart("a mark and a mark", "mark")).toEqual({ before: "a ", after: " and a mark" });
  });

  it("returns null for a text without the part", () => {
    expect(splitAroundPart("Each one carries the mark.", "sample data")).toBeNull();
  });

  it("returns null for an empty part", () => {
    expect(splitAroundPart("Each one carries the mark.", "")).toBeNull();
  });

  it("finds the name of the sample data mark in the text about sample data, in both languages", () => {
    for (const dictionary of [pl, en]) {
      expect(splitAroundPart(dictionary["data.sample.body"] ?? "", dictionary["sample.mark"] ?? "")).not.toBeNull();
    }
  });
});
