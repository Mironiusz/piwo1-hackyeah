import { getLang, Lang, tr } from './I18n';
import { AMENITY_KINDS, EdgeState, FactCategory, FactKind, FactStatus } from './Types';

interface Pair {
  pl: string;
  en: string;
}

function pick(map: Record<string, Pair>, key: string): string {
  const v = map[key];
  if (v === undefined) {
    return key;
  }
  return getLang() === Lang.PL ? v.pl : v.en;
}

const SURFACES: Record<string, Pair> = {
  'asphalt': { pl: 'asfalt', en: 'asphalt' },
  'concrete': { pl: 'beton', en: 'concrete' },
  'concrete:plates': { pl: 'płyty betonowe', en: 'concrete plates' },
  'paving_stones': { pl: 'kostka brukowa', en: 'paving stones' },
  'sett': { pl: 'kostka kamienna (bruk)', en: 'stone setts' },
  'cobblestone': { pl: 'kocie łby', en: 'cobblestones' },
  'unhewn_cobblestone': { pl: 'kocie łby', en: 'cobblestones' },
  'gravel': { pl: 'żwir', en: 'gravel' },
  'fine_gravel': { pl: 'drobny żwir', en: 'fine gravel' },
  'compacted': { pl: 'utwardzona', en: 'compacted' },
  'ground': { pl: 'grunt', en: 'ground' },
  'dirt': { pl: 'ziemia', en: 'dirt' },
  'grass': { pl: 'trawa', en: 'grass' },
  'sand': { pl: 'piasek', en: 'sand' },
  'paved': { pl: 'utwardzona', en: 'paved' },
  'unpaved': { pl: 'nieutwardzona', en: 'unpaved' },
  'wood': { pl: 'drewno', en: 'wood' },
  'metal': { pl: 'metal', en: 'metal' },
  'bricks': { pl: 'cegła', en: 'bricks' }
};

export function surfaceName(s: string): string {
  return pick(SURFACES, s);
}

const KINDS: Record<string, Pair> = {
  'steps': { pl: 'Schody', en: 'Stairs' },
  'kerb': { pl: 'Wysoki krawężnik', en: 'High kerb' },
  'rough_surface': { pl: 'Zła nawierzchnia', en: 'Poor surface' },
  'steep_slope': { pl: 'Strome nachylenie', en: 'Steep incline' },
  'narrow_passage': { pl: 'Wąskie przejście', en: 'Narrow passage' },
  'elevator': { pl: 'Winda', en: 'Elevator' },
  'ramp': { pl: 'Rampa', en: 'Ramp' },
  'lowered_kerb': { pl: 'Obniżony krawężnik', en: 'Lowered kerb' },
  'accessible_toilet': { pl: 'Dostępna toaleta', en: 'Accessible toilet' },
  'rest_spot': { pl: 'Miejsce odpoczynku', en: 'Rest place' },
  'handrail': { pl: 'Poręcz przy schodach', en: 'Handrail on stairs' }
};

/** Name of the fact kind, as shown in the needs lists and in reporting. */
export function kindLabel(k: FactKind): string {
  return pick(KINDS, k);
}

const SHORT: Record<string, Pair> = {
  'steps': { pl: 'schody', en: 'stairs' },
  'kerb': { pl: 'krawężnik', en: 'kerb' },
  'rough_surface': { pl: 'nawierzchnia', en: 'surface' },
  'steep_slope': { pl: 'nachylenie', en: 'incline' },
  'narrow_passage': { pl: 'przejście', en: 'passage' },
  'elevator': { pl: 'winda', en: 'elevator' },
  'ramp': { pl: 'rampa', en: 'ramp' },
  'lowered_kerb': { pl: 'obniżony krawężnik', en: 'lowered kerb' },
  'accessible_toilet': { pl: 'toaleta', en: 'toilet' },
  'rest_spot': { pl: 'miejsce odpoczynku', en: 'rest place' },
  'handrail': { pl: 'poręcz', en: 'handrail' }
};

/** Short lowercase name: the stop label on the route diagram and the type in the report summary. */
export function kindShort(k: FactKind): string {
  return pick(SHORT, k);
}

const SAME: Record<string, Pair> = {
  'steps': { pl: 'te same schody', en: 'the same stairs' },
  'kerb': { pl: 'ten sam krawężnik', en: 'the same kerb' },
  'rough_surface': { pl: 'ta sama nawierzchnia', en: 'the same surface' },
  'steep_slope': { pl: 'to samo nachylenie', en: 'the same incline' },
  'narrow_passage': { pl: 'to samo przejście', en: 'the same passage' },
  'elevator': { pl: 'ta sama winda', en: 'the same elevator' },
  'ramp': { pl: 'ta sama rampa', en: 'the same ramp' },
  'lowered_kerb': { pl: 'ten sam krawężnik', en: 'the same kerb' },
  'accessible_toilet': { pl: 'ta sama toaleta', en: 'the same toilet' },
  'rest_spot': { pl: 'to samo miejsce', en: 'the same place' },
  'handrail': { pl: 'ta sama poręcz', en: 'the same handrail' }
};

const OTHER: Record<string, Pair> = {
  'steps': { pl: 'To inne schody', en: 'These are other stairs' },
  'kerb': { pl: 'To inny krawężnik', en: 'This is another kerb' },
  'rough_surface': { pl: 'To inna nawierzchnia', en: 'This is another surface' },
  'steep_slope': { pl: 'To inne nachylenie', en: 'This is another incline' },
  'narrow_passage': { pl: 'To inne przejście', en: 'This is another passage' },
  'elevator': { pl: 'To inna winda', en: 'This is another elevator' },
  'ramp': { pl: 'To inna rampa', en: 'This is another ramp' },
  'lowered_kerb': { pl: 'To inny krawężnik', en: 'This is another kerb' },
  'accessible_toilet': { pl: 'To inna toaleta', en: 'This is another toilet' },
  'rest_spot': { pl: 'To inne miejsce', en: 'This is another place' },
  'handrail': { pl: 'To inna poręcz', en: 'This is another handrail' }
};

const ALREADY: Record<string, Pair> = {
  'steps': { pl: 'są już zgłoszone schody', en: 'stairs are already reported' },
  'kerb': { pl: 'jest już zgłoszony wysoki krawężnik', en: 'a high kerb is already reported' },
  'rough_surface': { pl: 'jest już zgłoszona zła nawierzchnia', en: 'a poor surface is already reported' },
  'steep_slope': { pl: 'jest już zgłoszone strome nachylenie', en: 'a steep incline is already reported' },
  'narrow_passage': { pl: 'jest już zgłoszone wąskie przejście', en: 'a narrow passage is already reported' },
  'elevator': { pl: 'jest już zgłoszona winda', en: 'an elevator is already reported' },
  'ramp': { pl: 'jest już zgłoszona rampa', en: 'a ramp is already reported' },
  'lowered_kerb': { pl: 'jest już zgłoszony obniżony krawężnik', en: 'a lowered kerb is already reported' },
  'accessible_toilet': { pl: 'jest już zgłoszona dostępna toaleta', en: 'an accessible toilet is already reported' },
  'rest_spot': { pl: 'jest już zgłoszone miejsce odpoczynku', en: 'a rest place is already reported' },
  'handrail': { pl: 'jest już zgłoszona poręcz', en: 'a handrail is already reported' }
};

/** Question from step 4 of reporting, for example "Czy to te same schody?" (Are these the same stairs?). */
export function sameQuestion(k: FactKind): string {
  return tr(`Czy to ${pick(SAME, k)}?`, `Is this ${pick(SAME, k)}?`);
}

export function otherAnswer(k: FactKind): string {
  return pick(OTHER, k);
}

export function alreadyReported(k: FactKind): string {
  return pick(ALREADY, k);
}

export function isAmenity(k: FactKind): boolean {
  return AMENITY_KINDS.indexOf(k) >= 0;
}

/** Numeral inflection: 1 is singular, 2-4 (except 12-14) take the "kilka" (few) form, the rest "wiele" (many). */
export function plural(n: number, one: string, few: string, many: string): string {
  if (n === 1) {
    return one;
  }
  const d = n % 10;
  const dd = n % 100;
  if (d >= 2 && d <= 4 && (dd < 12 || dd > 14)) {
    return few;
  }
  return many;
}

export function countBarriers(n: number): string {
  return tr(`${n} ${plural(n, 'bariera', 'bariery', 'barier')}`, `${n} ${n === 1 ? 'barrier' : 'barriers'}`);
}

export function countAmenities(n: number): string {
  return tr(`${n} ${plural(n, 'udogodnienie', 'udogodnienia', 'udogodnień')}`,
    `${n} ${n === 1 ? 'amenity' : 'amenities'}`);
}

export function countSegments(n: number): string {
  return tr(`${n} ${plural(n, 'odcinek', 'odcinki', 'odcinków')}`, `${n} ${n === 1 ? 'segment' : 'segments'}`);
}

export function countSteps(n: number): string {
  return tr(`${n} ${plural(n, 'stopień', 'stopnie', 'stopni')}`, `${n} ${n === 1 ? 'step' : 'steps'}`);
}

/** Fact title in a list row: the kind, the number of steps and, for an area, the radius. */
export function factTitle(kind: FactKind, category: FactCategory, stepCount: number, radiusM: number): string {
  if (category === FactCategory.AREA) {
    return tr(`Obszar: ${kindShortArea(kind)}, ${radiusM} m`, `Area: ${kindShortArea(kind)}, ${radiusM} m`);
  }
  if (kind === FactKind.STEPS && stepCount > 0) {
    return `${kindLabel(kind)}, ${countSteps(stepCount)}`;
  }
  return kindLabel(kind);
}

function kindShortArea(kind: FactKind): string {
  return kindLabel(kind).toLowerCase();
}

export function statusLabel(s: FactStatus): string {
  if (s === FactStatus.CONFIRMED) {
    return tr('potwierdzone', 'confirmed');
  }
  if (s === FactStatus.DISPUTED) {
    return tr('sporne', 'disputed');
  }
  if (s === FactStatus.OUTDATED) {
    return tr('nieaktualne', 'outdated');
  }
  return tr('niezweryfikowane', 'unverified');
}

export function categoryLabel(c: FactCategory): string {
  if (c === FactCategory.AMENITY) {
    return tr('udogodnienie', 'amenity');
  }
  if (c === FactCategory.AREA) {
    return tr('obszar', 'area');
  }
  return tr('bariera', 'barrier');
}

export function edgeStateLabel(s: EdgeState): string {
  if (s === EdgeState.CLEAR) {
    return tr('bez barier, dane pełne', 'no barriers, full data');
  }
  if (s === EdgeState.BARRIER) {
    return tr('bariera z potrzeb', 'barrier from your needs');
  }
  if (s === EdgeState.PARTIAL) {
    return tr('dane niepełne', 'incomplete data');
  }
  return tr('brak danych', 'no data');
}

const MONTHS_EN: string[] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** Day date as in the mockups: 3.10.2026 in Polish, 3 Oct 2026 in English. */
export function formatDate(ms: number): string {
  if (ms <= 0) {
    return tr('data nieznana', 'date unknown');
  }
  const d = new Date(ms);
  if (getLang() === Lang.PL) {
    const m = d.getMonth() + 1;
    return `${d.getDate()}.${m < 10 ? '0' + m : '' + m}.${d.getFullYear()}`;
  }
  return `${d.getDate()} ${MONTHS_EN[d.getMonth()]} ${d.getFullYear()}`;
}

const NO_PREFIX: string[] = ['ul.', 'ulica', 'al.', 'plac', 'pl.', 'rondo', 'park', 'osiedle', 'os.', 'most', 'bulwar',
  'rynek', 'skwer', 'tauron', 'centrum', 'kopiec', 'ogród'];

/** Street name as in the mockups: "ul. Stanisława Lema", "al. Pokoju"; squares, parks and markets get no prefix. */
export function streetLabel(name: string): string {
  const n = name.trim();
  if (n.length === 0) {
    return '';
  }
  const lower = n.toLowerCase();
  if (lower.startsWith('aleja ')) {
    return 'al. ' + n.substring(6);
  }
  const first = lower.split(' ')[0];
  if (NO_PREFIX.indexOf(first) >= 0) {
    return n;
  }
  return 'ul. ' + n;
}
