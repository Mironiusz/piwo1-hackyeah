import { EdgeState } from '../model/Types';

/**
 * Tokeny z artboardu "System: tokeny i części wspólne": granat nagłówka i akcji, żółty akcji Zgłoś i wejścia do
 * potrzeb, tusz tekstu, tekst drugi, linie, tło i powierzchnie oraz kolory stanów.
 */
export class Palette {
  primary: string = '#12306B';
  onPrimary: string = '#FFFFFF';
  yellow: string = '#FFD400';
  onYellow: string = '#111418';
  background: string = '#F4F5F2';
  card: string = '#FFFFFF';
  text: string = '#111418';
  textVar: string = '#4B5058';
  outline: string = '#111418';
  outlineVar: string = '#D5D8DC';
  clear: string = '#1E7A46';
  barrier: string = '#C8321E';
  partialLine: string = '#E0A100';
  noData: string = '#6F7480';
  disputed: string = '#8A5A00';
  gray: string = '#EEF0EC';
  grayText: string = '#4B5058';
  chipBg: string = '#EEF0EC';
  mapBg: string = '#ECEBE3';
  mapBuilding: string = '#DEDDD3';
  mapGreen: string = '#D8E6D2';
  mapStreet: string = '#FFFFFF';
  mapLabel: string = '#4B5058';
  scrim: string = '#99F4F5F2';
}

const NORMAL: Palette = new Palette();

export function P(): Palette {
  return NORMAL;
}

export const FONT: string = 'BarlowSC';
export const FONT_B: string = 'BarlowSCSemi';
export const FONT_NUM: string = 'BarlowNum';
export const FONT_TITLE: string = 'BarlowSCBold';

/** Rozmiar tekstu w fp, więc aplikacja respektuje systemowe powiększenie czcionki. */
export function fs(base: number): number {
  return base;
}

export const TOUCH: number = 48;
export const RADIUS: number = 6;
export const RADIUS_CTRL: number = 4;
export const RADIUS_SHEET: number = 16;
export const PAD: number = 16;

export interface LineStyle {
  color: string;
  width: number;
  dash: number[];
  overColor: string;
  overWidth: number;
  overDash: number[];
}

/**
 * Linie stanów z makiety: bariera to czerwone kreski z białymi przerwami, bez barier to ciągła zieleń, dane
 * niepełne to żółta linia z czarnymi kreskami, brak danych to szare kropki. Wzory odróżniają stany bez koloru.
 */
export function edgeStyle(s: EdgeState, k: number): LineStyle {
  const p = P();
  if (s === EdgeState.CLEAR) {
    return { color: p.clear, width: 5 * k, dash: [], overColor: '', overWidth: 0, overDash: [] };
  }
  if (s === EdgeState.PARTIAL) {
    return { color: p.partialLine, width: 5 * k, dash: [], overColor: p.text, overWidth: 1.6 * k, overDash: [5 * k, 4 * k] };
  }
  if (s === EdgeState.NO_DATA) {
    return { color: p.noData, width: 3.2 * k, dash: [3.2 * k, 4.8 * k], overColor: '', overWidth: 0, overDash: [] };
  }
  return { color: p.barrier, width: 5 * k, dash: [3.6 * k, 2.4 * k], overColor: '', overWidth: 0, overDash: [] };
}
