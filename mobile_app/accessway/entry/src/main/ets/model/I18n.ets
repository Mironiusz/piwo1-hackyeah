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

/** Wybiera tekst w bieżącym języku interfejsu. */
export function tr(pl: string, en: string): string {
  return current === Lang.PL ? pl : en;
}

/** Język startowy z ustawień systemu: polski dla polskich ustawień, angielski dla pozostałych. */
export function langFromSystem(systemLanguage: string): Lang {
  return systemLanguage.toLowerCase().startsWith('pl') ? Lang.PL : Lang.EN;
}

export function decimal(v: number, digits: number): string {
  const s = v.toFixed(digits);
  return current === Lang.PL ? s.replace('.', ',') : s;
}
