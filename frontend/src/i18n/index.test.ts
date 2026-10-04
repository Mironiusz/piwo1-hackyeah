import i18next from "i18next";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { STORAGE_KEYS } from "../state/storage.ts";
import { createMemoryStorage, type MemoryStorage } from "../testing/memoryStorage.ts";
import { en } from "./en.ts";
import { changeLanguage, detectLanguage, initI18n, isLanguage, LANGUAGES, readLanguage } from "./index.ts";
import { pl } from "./pl.ts";

const PLURAL_SUFFIXES = ["_one", "_few", "_many", "_other"];
const PLURAL_SUFFIX_PATTERN = /_(one|few|many|other)$/;
const REQUIRED_PLURAL_SUFFIX_PATTERN = /_(one|other)$/;
const PLACEHOLDER_PATTERN = /\{([^{}]+)\}/g;
const POLISH_PLURAL_SUFFIXES = ["_one", "_few", "_many", "_other"];
const ENGLISH_PLURAL_SUFFIXES = ["_one", "_other"];
const PSEUDONYM = "Wózek_KRK";

interface PageStandIn {
  documentElement: { lang: string };
}

let storage: MemoryStorage;

/**
 * Sets the languages the browser reports, the first being the one the person prefers.
 */
function stubBrowserLanguages(languages: string[]): void {
  vi.stubGlobal("navigator", { languages, language: languages[0] ?? "" });
}

/**
 * Puts a stand-in of the page in place, because Node.js has no document, and returns it.
 */
function stubPage(): PageStandIn {
  const page: PageStandIn = { documentElement: { lang: "" } };
  vi.stubGlobal("document", page);
  return page;
}

/**
 * Returns a text of a dictionary with every placeholder replaced by its value, as the catalogue of texts writes a placeholder:
 * a name in single braces. The Polish texts stand only in the Polish dictionary, so a test reads them from there.
 */
function fillText(dictionary: Record<string, string>, key: string, values: Record<string, string | number> = {}): string {
  const text = dictionary[key];
  if (text === undefined) {
    throw new Error(`The dictionary has no text under the key ${key}`);
  }
  return text.replace(PLACEHOLDER_PATTERN, (_placeholder, name: string) => String(values[name]));
}

/**
 * Lists the names of the plural texts of a dictionary: the names that have the form for one or the form for the other numbers,
 * which both languages require. A key that only ends like a plural form, such as facts.too_many, is a text of its own.
 */
function listPluralNames(dictionary: Record<string, string>): string[] {
  const names = Object.keys(dictionary)
    .filter((key) => REQUIRED_PLURAL_SUFFIX_PATTERN.test(key))
    .map((key) => key.replace(REQUIRED_PLURAL_SUFFIX_PATTERN, ""));
  return [...new Set(names)].sort();
}

/**
 * Lists the suffixes of the forms a dictionary holds for a plural text, in the order one, few, many, other.
 */
function listPluralSuffixes(dictionary: Record<string, string>, name: string): string[] {
  return PLURAL_SUFFIXES.filter((suffix) => `${name}${suffix}` in dictionary);
}

/**
 * Groups the texts of a dictionary by the name of their text: a plain key holds its one text,
 * and the name of a plural text holds every form of it.
 */
function groupTexts(dictionary: Record<string, string>): Map<string, string[]> {
  const pluralNames = new Set(listPluralNames(dictionary));
  const groups = new Map<string, string[]>();
  for (const [key, text] of Object.entries(dictionary)) {
    const base = key.replace(PLURAL_SUFFIX_PATTERN, "");
    const name = pluralNames.has(base) ? base : key;
    groups.set(name, [...(groups.get(name) ?? []), text]);
  }
  return groups;
}

/**
 * Lists the names of the texts of a dictionary, each once, with the forms of a plural text under its one name.
 */
function listTextNames(dictionary: Record<string, string>): string[] {
  return [...groupTexts(dictionary).keys()].sort();
}

/**
 * Lists the placeholders of the given texts, each once.
 */
function listPlaceholders(texts: string[]): string[] {
  return [...new Set(texts.flatMap((text) => [...text.matchAll(PLACEHOLDER_PATTERN)].map((match) => match[1])))].sort();
}

beforeEach(() => {
  storage = createMemoryStorage();
  vi.stubGlobal("localStorage", storage);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("isLanguage", () => {
  it("accepts the two languages of the interface", () => {
    expect(LANGUAGES).toEqual(["pl", "en"]);
    expect(isLanguage("pl")).toBe(true);
    expect(isLanguage("en")).toBe(true);
  });

  it("refuses every other value", () => {
    expect(isLanguage("de")).toBe(false);
    expect(isLanguage("PL")).toBe(false);
    expect(isLanguage("pl-PL")).toBe(false);
    expect(isLanguage("")).toBe(false);
    expect(isLanguage(null)).toBe(false);
    expect(isLanguage(["pl"])).toBe(false);
  });
});

describe("detectLanguage", () => {
  it("returns the stored language, whatever the browser prefers", () => {
    storage.setItem(STORAGE_KEYS.language, JSON.stringify("en"));
    stubBrowserLanguages(["pl-PL", "pl"]);

    expect(detectLanguage()).toBe("en");
  });

  it("returns stored Polish in a browser that prefers English", () => {
    storage.setItem(STORAGE_KEYS.language, JSON.stringify("pl"));
    stubBrowserLanguages(["en-US", "en"]);

    expect(detectLanguage()).toBe("pl");
  });

  it("returns Polish when the first language of the browser is Polish", () => {
    stubBrowserLanguages(["pl-PL", "en-US"]);

    expect(detectLanguage()).toBe("pl");
  });

  it("returns Polish for the plain code of the language", () => {
    stubBrowserLanguages(["pl"]);

    expect(detectLanguage()).toBe("pl");
  });

  it("reads the language of the browser without regard to letter case", () => {
    stubBrowserLanguages(["PL-pl"]);

    expect(detectLanguage()).toBe("pl");
  });

  it("returns English when the first language of the browser is another one", () => {
    stubBrowserLanguages(["en-GB", "en"]);

    expect(detectLanguage()).toBe("en");
  });

  it("returns English when Polish is not the first language of the browser", () => {
    stubBrowserLanguages(["de-DE", "pl-PL"]);

    expect(detectLanguage()).toBe("en");
  });

  it("reads the one language of a browser that reports no list", () => {
    vi.stubGlobal("navigator", { language: "pl-PL" });

    expect(detectLanguage()).toBe("pl");
  });

  it("reads the one language of a browser that reports an empty list", () => {
    vi.stubGlobal("navigator", { languages: [], language: "pl" });

    expect(detectLanguage()).toBe("pl");
  });

  it("returns English where no browser reports a language", () => {
    vi.stubGlobal("navigator", undefined);

    expect(detectLanguage()).toBe("en");
  });

  it("drops a stored value that is not a language and reads the browser", () => {
    storage.setItem(STORAGE_KEYS.language, JSON.stringify("de"));
    stubBrowserLanguages(["pl-PL"]);

    expect(detectLanguage()).toBe("pl");
    expect(storage.getItem(STORAGE_KEYS.language)).toBeNull();
  });

  it("stores nothing itself, because a detected language is not a choice of the person", () => {
    stubBrowserLanguages(["pl-PL"]);

    detectLanguage();

    expect(storage.getItem(STORAGE_KEYS.language)).toBeNull();
  });
});

describe("initI18n", () => {
  it.each([
    [0, "_many"],
    [1, "_one"],
    [2, "_few"],
    [4, "_few"],
    [5, "_many"],
    [12, "_many"],
    [21, "_many"],
    [22, "_few"],
    [25, "_many"],
  ])("writes %i barriers in Polish with the form %s", (count, suffix) => {
    initI18n("pl");

    expect(i18next.t("count.barriers", { count })).toBe(fillText(pl, `count.barriers${suffix}`, { count }));
  });

  it("picks between three Polish forms that differ, each showing its number", () => {
    const forms = ["_one", "_few", "_many"].map((suffix) => fillText(pl, `count.barriers${suffix}`, { count: 7 }));

    expect(new Set(forms).size).toBe(3);
    for (const form of forms) {
      expect(form).toContain("7");
    }
  });

  it.each([
    [0, "_other"],
    [1, "_one"],
    [2, "_other"],
    [25, "_other"],
  ])("writes %i barriers in English with the form %s", (count, suffix) => {
    initI18n("en");

    expect(i18next.t("count.barriers", { count })).toBe(fillText(en, `count.barriers${suffix}`, { count }));
  });

  it("writes one barrier and two barriers in English as a person reads them", () => {
    initI18n("en");

    expect(i18next.t("count.barriers", { count: 1 })).toBe("1 barrier");
    expect(i18next.t("count.barriers", { count: 2 })).toBe("2 barriers");
  });

  it.each([
    [1, "_one"],
    [3, "_few"],
    [7, "_many"],
  ])("picks the Polish form of a plural text without a number for the count %i", (count, suffix) => {
    initI18n("pl");

    expect(i18next.t("route.tile.barriers", { count })).toBe(fillText(pl, `route.tile.barriers${suffix}`));
  });

  it("fills a placeholder written in single braces", () => {
    initI18n("pl");

    expect(pl["menu.account.in"]).toContain("{pseudonym}");
    expect(i18next.t("menu.account.in", { pseudonym: PSEUDONYM })).toBe(fillText(pl, "menu.account.in", { pseudonym: PSEUDONYM }));
  });

  it("fills the same placeholder in English", () => {
    initI18n("en");

    expect(i18next.t("menu.account.in", { pseudonym: PSEUDONYM })).toBe(`logged in as ${PSEUDONYM}`);
  });

  it("fills two placeholders of one text", () => {
    initI18n("en");

    expect(i18next.t("report.step", { n: 2, total: 5 })).toBe("Step 2 of 5");
  });

  it("passes a value on as it is, because the page escapes a text when it shows it", () => {
    initI18n("en");

    expect(i18next.t("menu.account.in", { pseudonym: "<Ala & Ola>" })).toBe("logged in as <Ala & Ola>");
  });

  it("reads a key with dots as one flat name, also when a shorter key starts the same", () => {
    initI18n("pl");

    expect(i18next.t("menu.account")).toBe(pl["menu.account"]);
    expect(i18next.t("menu.account.out")).toBe(pl["menu.account.out"]);
    expect(pl["menu.account.out"]).not.toBe(pl["menu.account"]);
  });

  it("starts in the given language", () => {
    initI18n("en");

    expect(readLanguage()).toBe("en");
    expect(i18next.t("nav.map")).toBe(en["nav.map"]);
    expect(en["nav.map"]).not.toBe(pl["nav.map"]);
  });

  it("starts again in the other language when it is called again", () => {
    initI18n("en");
    initI18n("pl");

    expect(readLanguage()).toBe("pl");
    expect(i18next.t("nav.map")).toBe(pl["nav.map"]);
  });

  it("sets the language of the page", () => {
    const page = stubPage();

    initI18n("en");

    expect(page.documentElement.lang).toBe("en");
  });

  it("stores nothing, because the language it starts in is not a choice of the person", () => {
    initI18n("en");

    expect(storage.getItem(STORAGE_KEYS.language)).toBeNull();
  });
});

describe("changeLanguage", () => {
  it("switches the texts of the interface", () => {
    initI18n("pl");

    changeLanguage("en");

    expect(readLanguage()).toBe("en");
    expect(i18next.t("nav.map")).toBe(en["nav.map"]);
    expect(i18next.t("count.barriers", { count: 2 })).toBe("2 barriers");
  });

  it("stores the choice on the device", () => {
    initI18n("pl");

    changeLanguage("en");

    expect(storage.getItem(STORAGE_KEYS.language)).toBe(JSON.stringify("en"));
  });

  it("stores a choice that the next opening detects, whatever the browser prefers", () => {
    initI18n("pl");
    stubBrowserLanguages(["pl-PL"]);

    changeLanguage("en");

    expect(detectLanguage()).toBe("en");
  });

  it("replaces the choice stored before", () => {
    initI18n("pl");

    changeLanguage("en");
    changeLanguage("pl");

    expect(storage.getItem(STORAGE_KEYS.language)).toBe(JSON.stringify("pl"));
    expect(readLanguage()).toBe("pl");
    expect(i18next.t("nav.map")).toBe(pl["nav.map"]);
  });

  it("sets the language of the page", () => {
    const page = stubPage();
    initI18n("pl");

    changeLanguage("en");

    expect(page.documentElement.lang).toBe("en");
  });
});

describe("the two dictionaries", () => {
  it("have the same keys once the plural suffixes are removed", () => {
    const polish = listTextNames(pl);
    const english = listTextNames(en);

    expect(polish.filter((name) => !english.includes(name))).toEqual([]);
    expect(english.filter((name) => !polish.includes(name))).toEqual([]);
  });

  it("have plural forms for the same texts, the names with a number among them", () => {
    expect(listPluralNames(en)).toEqual(listPluralNames(pl));
    expect(listPluralNames(pl)).toEqual(expect.arrayContaining(["count.amenities", "count.barriers", "count.results", "count.steps"]));
  });

  it("give a plural text its four forms in Polish", () => {
    for (const name of listPluralNames(pl)) {
      expect(listPluralSuffixes(pl, name), name).toEqual(POLISH_PLURAL_SUFFIXES);
    }
  });

  it("give a plural text its two forms in English", () => {
    for (const name of listPluralNames(en)) {
      expect(listPluralSuffixes(en, name), name).toEqual(ENGLISH_PLURAL_SUFFIXES);
    }
  });

  it("write the number of a plural text as count, which picks the form", () => {
    for (const dictionary of [pl, en]) {
      const texts = groupTexts(dictionary);

      for (const name of listPluralNames(dictionary)) {
        expect(listPlaceholders(texts.get(name) ?? []), name).not.toContain("n");
      }
    }
  });

  it("use the same placeholders for a text in both languages", () => {
    const polish = groupTexts(pl);
    const english = groupTexts(en);
    const different = [...polish.keys()].filter((name) => listPlaceholders(polish.get(name) ?? []).join() !== listPlaceholders(english.get(name) ?? []).join());

    expect(different).toEqual([]);
  });

  it("hold no empty text", () => {
    for (const dictionary of [pl, en]) {
      const empty = Object.keys(dictionary).filter((key) => dictionary[key]?.trim() === "");

      expect(empty).toEqual([]);
    }
  });
});
