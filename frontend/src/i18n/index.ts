import i18next from "i18next";
import { initReactI18next, useTranslation } from "react-i18next";

import { readStored, STORAGE_KEYS, writeStored } from "../state/storage.ts";
import { en } from "./en.ts";
import { pl } from "./pl.ts";

export type Language = "pl" | "en";

export const LANGUAGES: readonly Language[] = ["pl", "en"];

/**
 * Tells whether a value is one of the two languages of the interface.
 */
export function isLanguage(value: unknown): value is Language {
  return value === "pl" || value === "en";
}

/**
 * Returns the language of the first opening: the stored one, or else Polish when the first language
 * of the browser is Polish, and English otherwise.
 */
export function detectLanguage(): Language {
  const stored = readStored(STORAGE_KEYS.language, isLanguage);
  if (stored !== null) {
    return stored;
  }
  const preferred = typeof navigator === "undefined" ? "" : (navigator.languages?.[0] ?? navigator.language ?? "");
  return preferred.toLowerCase().startsWith("pl") ? "pl" : "en";
}

/**
 * Sets i18next up with both dictionaries.
 * A key is one flat text with dots in it, and a placeholder is written in single braces, as the catalogue of texts writes them.
 */
export function initI18n(language: Language): void {
  void i18next.use(initReactI18next).init({
    lng: language,
    fallbackLng: "pl",
    supportedLngs: LANGUAGES,
    resources: { pl: { translation: pl }, en: { translation: en } },
    keySeparator: false,
    nsSeparator: false,
    initAsync: false,
    interpolation: { prefix: "{", suffix: "}", escapeValue: false },
    react: { useSuspense: false },
  });
  setPageLanguage(language);
}

/**
 * Switches the language of the interface, keeps the choice on the device and sets the language of the page.
 */
export function changeLanguage(language: Language): void {
  void i18next.changeLanguage(language);
  writeStored(STORAGE_KEYS.language, language);
  setPageLanguage(language);
}

/**
 * Returns the language the interface is shown in now.
 */
export function readLanguage(): Language {
  return isLanguage(i18next.language) ? i18next.language : "pl";
}

/**
 * Sets the language attribute of the page, which a screen reader picks its voice by.
 */
function setPageLanguage(language: Language): void {
  if (typeof document !== "undefined") {
    document.documentElement.lang = language;
  }
}

/**
 * Returns the language the interface is shown in, and renders the component again when it changes.
 */
export function useLanguage(): Language {
  const { i18n } = useTranslation();
  return i18n.language === "en" ? "en" : "pl";
}
