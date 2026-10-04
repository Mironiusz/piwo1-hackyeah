export enum Lang {
  PL = 'pl',
  EN = 'en'
}

let current: Lang = Lang.PL;

export function setLang(l: Lang): void {
  current = l;
}

export function getLang(): Lang {
  return current;
}

/** Picks the text in the current UI language. */
export function tr(pl: string, en: string): string {
  return current === Lang.PL ? pl : en;
}

/** Startup language from the system settings: Polish for Polish settings, English for all others. */
export function langFromSystem(systemLanguage: string): Lang {
  return systemLanguage.toLowerCase().startsWith('pl') ? Lang.PL : Lang.EN;
}

export function decimal(v: number, digits: number): string {
  const s = v.toFixed(digits);
  return current === Lang.PL ? s.replace('.', ',') : s;
}
