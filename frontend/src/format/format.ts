import type { Language } from "../i18n/index.ts";

const ENGLISH_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] as const;

const DAY_PATTERN = /^(\d{4})-(\d{2})-(\d{2})/;

/**
 * Writes a calendar day of the service, YYYY-MM-DD, in the form of the language: 3.10.2026 and 12.05.2025, or 3 Oct 2026.
 * The Polish form keeps the two digits of the month and drops the leading zero of the day, as the mocks write it.
 * An instant of the service is written as its day: the day is taken from its text, so no time zone is converted.
 * A text that is not a day is returned unchanged.
 */
export function formatDay(day: string, language: Language): string {
  const parts = DAY_PATTERN.exec(day);
  if (parts === null) {
    return day;
  }
  const year = parts[1];
  const month = Number(parts[2]);
  const dayOfMonth = Number(parts[3]);
  if (language === "pl") {
    return `${dayOfMonth}.${parts[2]}.${year}`;
  }
  return `${dayOfMonth} ${ENGLISH_MONTHS[month - 1] ?? parts[2]} ${year}`;
}

/**
 * Writes a distance in whole metres: in metres under 1000 m, and in kilometres with one decimal place from 1000 m.
 */
export function formatDistance(metres: number, language: Language): string {
  const whole = Math.round(metres);
  if (whole < 1000) {
    return `${whole} m`;
  }
  const kilometres = (whole / 1000).toFixed(1);
  return `${language === "pl" ? kilometres.replace(".", ",") : kilometres} km`;
}
