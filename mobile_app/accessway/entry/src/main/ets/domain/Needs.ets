import { tr } from '../model/I18n';
import { AMENITY_KINDS, BARRIER_KINDS, Constraints, FactKind, NO_LIMIT, Roughness } from '../model/Types';

/** Needs from the "Twoje potrzeby" (Your needs) screen: what I avoid and what I need. They stay on the device only. */
export interface Needs {
  avoid: FactKind[];
  need: FactKind[];
}

export const KERB_LIMIT_CM: number = 3;
export const INCLINE_LIMIT_PCT: number = 6;
export const WIDTH_LIMIT_M: number = 0.9;

export enum Preset {
  WHEELCHAIR = 'wheelchair',
  STROLLER = 'stroller',
  WALKING = 'walking'
}

export const PRESETS: Preset[] = [Preset.WHEELCHAIR, Preset.STROLLER, Preset.WALKING];

export function presetLabel(p: Preset): string {
  if (p === Preset.WHEELCHAIR) {
    return tr('Poruszam się na wózku', 'I use a wheelchair');
  }
  if (p === Preset.STROLLER) {
    return tr('Chodzę z wózkiem dziecięcym', 'I walk with a baby stroller');
  }
  return tr('Chodzenie sprawia mi trudność', 'Walking is difficult for me');
}

export function presetIcon(p: Preset): string {
  if (p === Preset.WHEELCHAIR) {
    return 'accessible';
  }
  if (p === Preset.STROLLER) {
    return 'stroller';
  }
  return 'elderly';
}

/** A preset checks boxes on the list; the person can change them afterwards. */
export function presetNeeds(p: Preset): Needs {
  if (p === Preset.WHEELCHAIR) {
    return {
      avoid: [FactKind.STEPS, FactKind.KERB, FactKind.ROUGH_SURFACE, FactKind.NARROW_PASSAGE],
      need: [FactKind.ELEVATOR, FactKind.RAMP, FactKind.LOWERED_KERB]
    };
  }
  if (p === Preset.STROLLER) {
    return {
      avoid: [FactKind.STEPS, FactKind.KERB, FactKind.NARROW_PASSAGE],
      need: [FactKind.ELEVATOR, FactKind.RAMP, FactKind.LOWERED_KERB]
    };
  }
  return {
    avoid: [FactKind.STEPS, FactKind.ROUGH_SURFACE, FactKind.STEEP_SLOPE],
    need: [FactKind.REST_SPOT, FactKind.HANDRAIL, FactKind.ACCESSIBLE_TOILET]
  };
}

export function emptyNeeds(): Needs {
  return { avoid: [], need: [] };
}

export function copyNeeds(n: Needs): Needs {
  return { avoid: n.avoid.slice(), need: n.need.slice() };
}

/** Keeps the order of the kind lists so that saving and comparisons are stable. */
export function toggleKind(list: FactKind[], k: FactKind): FactKind[] {
  const on = list.indexOf(k) < 0;
  const order = BARRIER_KINDS.indexOf(k) >= 0 ? BARRIER_KINDS : AMENITY_KINDS;
  const out: FactKind[] = [];
  for (const x of order) {
    if ((x === k && on) || (x !== k && list.indexOf(x) >= 0)) {
      out.push(x);
    }
  }
  return out;
}

export function hasBarriers(n: Needs): boolean {
  return n.avoid.length > 0;
}

/** Route constraints from the list of barriers the person avoids. Without any barrier, segments are not assessed. */
export function needsConstraints(n: Needs): Constraints {
  const has = (k: FactKind): boolean => n.avoid.indexOf(k) >= 0;
  return {
    avoidSteps: has(FactKind.STEPS),
    maxKerbCm: has(FactKind.KERB) ? KERB_LIMIT_CM : NO_LIMIT,
    maxInclinePct: has(FactKind.STEEP_SLOPE) ? INCLINE_LIMIT_PCT : NO_LIMIT,
    maxRoughness: has(FactKind.ROUGH_SURFACE) ? Roughness.MODERATE : Roughness.ROUGH,
    minWidthM: has(FactKind.NARROW_PASSAGE) ? WIDTH_LIMIT_M : NO_LIMIT
  };
}

export function inNeeds(n: Needs, k: FactKind): boolean {
  return n.avoid.indexOf(k) >= 0 || n.need.indexOf(k) >= 0;
}
