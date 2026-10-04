import { Barrier, DAY_MS, FactKind, Vote } from '../model/Types';

const LAT0: number = 50.0676;
const LON0: number = 19.9914;
const M_LAT: number = 111320;
const M_LON: number = 111320 * Math.cos(LAT0 * Math.PI / 180);

function vote(voter: string, value: number, weight: number, at: number): Vote {
  return { voterId: voter, value: value, weight: weight, at: at };
}

function sample(id: string, kind: FactKind, x: number, y: number, radius: number, steps: number, desc: string,
  street: string, created: number, votes: Vote[]): Barrier {
  return {
    id: id,
    kind: kind,
    lat: LAT0 + y / M_LAT,
    lon: LON0 + x / M_LON,
    radiusM: radius,
    isArea: radius > 0,
    stepCount: steps,
    description: desc,
    street: street,
    createdAt: created,
    isSample: true,
    votes: votes,
    hidden: false,
    flagged: false
  };
}

/**
 * Sample reports around Tauron Arena, placed on the schematic network sample (tools/accessway_sample.py).
 * Each one has the "dane przykładowe" (sample data) mark. A few are already flagged for moderation or hidden,
 * to show the moderation screen.
 */
export function demoReports(now: number): Barrier[] {
  const d = (days: number): number => now - days * DAY_MS;
  const kerb = sample('demo-kerb-lema', FactKind.KERB, 400, 0, 0, 0, '', 'Stanisława Lema', d(0.2),
    [vote('sample-a', 1, 1, d(0.2)), vote('sample-b', 1, 1, d(0.1))]);
  const stairs = sample('demo-stairs-pokoju', FactKind.STEPS, 1115, 415, 0, 4, 'Brak poręczy po prawej stronie.',
    'aleja Pokoju', d(1), [vote('sample-c', 1, 1, d(1))]);
  const ramp = sample('demo-ramp-park', FactKind.RAMP, 1190, 470, 0, 0, '', 'aleja Pokoju', d(2),
    [vote('sample-a', 1, 1, d(2)), vote('sample-d', 1, 1, d(1.5))]);
  const area = sample('demo-area-surface', FactKind.ROUGH_SURFACE, 600, 185, 25, 0, 'Remont chodnika, rozkopana nawierzchnia.',
    'aleja Pokoju', d(2), [vote('sample-e', 1, 1, d(2)), vote('sample-f', -1, 1, d(1))]);
  const conflict = sample('demo-kerb-medweckiego', FactKind.KERB, -150, 0, 0, 0, '', 'Stanisława Lema', d(0.3),
    [vote('sample-g', 1, 1, d(0.3))]);
  const flaggedStairs = sample('demo-flag-stairs', FactKind.STEPS, 400, -80, 0, 3,
    'Schody pod domem pana [nazwisko], zawsze zastawione jego autem.', 'Stanisława Lema', d(0.1),
    [vote('sample-h', 1, 1, d(0.1))]);
  flaggedStairs.flagged = true;
  const flaggedArea = sample('demo-flag-area', FactKind.NARROW_PASSAGE, -150, 120, 50, 0,
    'Rusztowanie na całej szerokości chodnika.', 'Medweckiego', d(1),
    [vote('sample-i', 1, 1, d(1)), vote('sample-j', -1, 1, d(0.5))]);
  flaggedArea.flagged = true;
  const hidden = sample('demo-hidden-kerb', FactKind.KERB, 100, 0, 0, 0, 'tekst z numerem telefonu, ukryty.',
    'Stanisława Lema', d(2), [vote('sample-k', 1, 1, d(2))]);
  hidden.hidden = true;
  hidden.flagged = true;
  return [kerb, stairs, ramp, area, conflict, flaggedStairs, flaggedArea, hidden];
}
