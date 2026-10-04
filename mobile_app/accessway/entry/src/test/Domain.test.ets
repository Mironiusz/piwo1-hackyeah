import { describe, it, expect } from '@ohos/hypium';
import { pseudonymValid } from '../main/ets/data/Repository';
import { assessAll, edgeIssues, edgeState, indexBarriers } from '../main/ets/domain/EdgeRules';
import { buildFacts, sameKindNearby } from '../main/ets/domain/Facts';
import { formatKm, formatKmRange } from '../main/ets/domain/Geo';
import { emptyNeeds, needsConstraints, Preset, presetNeeds, toggleKind } from '../main/ets/domain/Needs';
import { buildDataset, OsmFact, OverpassElement, OverpassResponse, searchPlaces } from '../main/ets/domain/OsmMapping';
import { buildPlan } from '../main/ets/domain/Plan';
import { RouteFactItem, RouteSegment } from '../main/ets/data/Repository';
import { factStatus } from '../main/ets/domain/Trust';
import { Lang, setLang } from '../main/ets/model/I18n';
import { countBarriers, factTitle, formatDate, plural, streetLabel } from '../main/ets/model/Labels';
import {
  Barrier,
  EdgeState,
  Fact,
  FactCategory,
  FactKind,
  FactSource,
  FactStatus,
  Vote
} from '../main/ets/model/Types';

const NOW: number = 1790000000000;

function node(id: number, lat: number, lon: number, tags?: Record<string, string>): OverpassElement {
  const el: OverpassElement = { type: 'node', id: id, lat: lat, lon: lon };
  if (tags !== undefined) {
    el.tags = tags;
  }
  return el;
}

function way(id: number, nodes: number[], tags: Record<string, string>): OverpassElement {
  return { type: 'way', id: id, nodes: nodes, tags: tags };
}

/**
 * Siatka testowa: 1-2-3 to krótka droga przez schody (2-3), 1-4-5-3 to objazd po asfalcie, 3-6 nie ma danych
 * o nawierzchni, 3-7-8 to stroma ścieżka z wysokim krawężnikiem w 7, jedyna droga do 8.
 */
function grid(): OverpassResponse {
  return {
    osm3s: { timestamp_osm_base: '2026-10-01T00:00:00Z' },
    elements: [
      node(1, 50.0600, 19.9300),
      node(2, 50.0600, 19.9310),
      node(3, 50.0600, 19.9320),
      node(4, 50.0610, 19.9300),
      node(5, 50.0610, 19.9320),
      node(6, 50.0590, 19.9320),
      node(7, 50.0600, 19.9330, { 'barrier': 'kerb', 'kerb': 'raised' }),
      node(8, 50.0600, 19.9340),
      node(9, 50.0611, 19.9301, { 'kerb': 'lowered' }),
      node(100, 50.0601, 19.9341, { 'name': 'Muzeum Testowe', 'tourism': 'museum', 'addr:street': 'Testowa',
        'addr:housenumber': '1' }),
      node(101, 50.0611, 19.9301, { 'name': 'Kawiarnia Łódź', 'amenity': 'cafe' }),
      way(10, [1, 2], { 'highway': 'footway', 'surface': 'asphalt', 'name': 'Prosta' }),
      way(11, [2, 3], { 'highway': 'steps', 'step_count': '4', 'name': 'Prosta' }),
      way(12, [1, 4, 5, 3], { 'highway': 'footway', 'surface': 'asphalt', 'incline': '1%', 'width': '2',
        'name': 'aleja Objazdowa' }),
      way(13, [3, 6], { 'highway': 'footway' }),
      way(14, [3, 7, 8], { 'highway': 'footway', 'surface': 'sett', 'incline': '9%', 'name': 'Stroma' })
    ]
  };
}

function vote(id: string, value: number, weight: number): Vote {
  return { voterId: id, value: value, weight: weight, at: NOW };
}

function report(id: string, kind: FactKind, lat: number, lon: number, votes: Vote[]): Barrier {
  return {
    id: id, kind: kind, lat: lat, lon: lon, radiusM: 0, isArea: false, stepCount: 0, description: '', street: '',
    createdAt: NOW, isSample: false, votes: votes, hidden: false, flagged: false
  };
}

function noVotes(): Map<string, Vote[]> {
  return new Map<string, Vote[]>();
}

function stepsFact(facts: OsmFact[]): OsmFact {
  return facts.filter((f: OsmFact) => f.kind === FactKind.STEPS)[0];
}

function countKind(items: RouteFactItem[], k: FactKind): number {
  return items.filter((it: RouteFactItem) => it.fact.kind === k).length;
}

export default function domainTest() {
  describe('Needs', () => {
    it('wheelchair_preset_matches_the_needs_view', 0, () => {
      const n = presetNeeds(Preset.WHEELCHAIR);
      expect(n.avoid.join(',')).assertEqual('steps,kerb,rough_surface,narrow_passage');
      expect(n.need.join(',')).assertEqual('elevator,ramp,lowered_kerb');
    });
    it('toggle_keeps_list_order', 0, () => {
      const a = toggleKind(toggleKind([], FactKind.NARROW_PASSAGE), FactKind.STEPS);
      expect(a.join(',')).assertEqual('steps,narrow_passage');
      expect(toggleKind(a, FactKind.STEPS).join(',')).assertEqual('narrow_passage');
    });
    it('no_barrier_means_no_constraints', 0, () => {
      const c = needsConstraints(emptyNeeds());
      expect(c.avoidSteps).assertFalse();
      expect(c.maxKerbCm).assertEqual(-1);
      expect(c.minWidthM).assertEqual(-1);
    });
  });

  describe('Trust', () => {
    it('statuses_from_votes', 0, () => {
      expect(factStatus([vote('a', 1, 1)])).assertEqual(FactStatus.UNVERIFIED);
      expect(factStatus([vote('a', 1, 1), vote('b', 1, 1)])).assertEqual(FactStatus.CONFIRMED);
      expect(factStatus([vote('a', 1, 1), vote('b', -1, 1)])).assertEqual(FactStatus.DISPUTED);
      expect(factStatus([vote('a', 1, 0.5), vote('b', -1, 1), vote('c', -1, 1), vote('d', -1, 1)]))
        .assertEqual(FactStatus.OUTDATED);
    });
    it('anonymous_votes_weigh_half', 0, () => {
      expect(factStatus([vote('a', 1, 0.5), vote('b', 1, 0.5), vote('c', 1, 0.5)])).assertEqual(FactStatus.UNVERIFIED);
      expect(factStatus([vote('a', 1, 0.5), vote('b', 1, 0.5), vote('c', 1, 1)])).assertEqual(FactStatus.CONFIRMED);
    });
  });

  describe('Dataset', () => {
    it('osm_facts_steps_kerbs_incline', 0, () => {
      const ds = buildDataset(grid());
      const kinds: string[] = ds.osmFacts.map((f: OsmFact): string => f.kind);
      expect(kinds.indexOf(FactKind.STEPS) >= 0).assertTrue();
      expect(kinds.indexOf(FactKind.KERB) >= 0).assertTrue();
      expect(kinds.indexOf(FactKind.LOWERED_KERB) >= 0).assertTrue();
      expect(kinds.indexOf(FactKind.STEEP_SLOPE) >= 0).assertTrue();
      const steps = stepsFact(ds.osmFacts);
      expect(steps.stepCount).assertEqual(4);
      expect(steps.street).assertEqual('Prosta');
    });
    it('search_ignores_polish_diacritics', 0, () => {
      const ds = buildDataset(grid());
      expect(searchPlaces(ds, 'lodz', 5)[0].name).assertEqual('Kawiarnia Łódź');
    });
  });

  describe('EdgeRules', () => {
    it('four_states', 0, () => {
      const ds = buildDataset(grid());
      const c = needsConstraints(presetNeeds(Preset.WHEELCHAIR));
      const states: EdgeState[] = [];
      for (const e of ds.edges) {
        states.push(edgeState(e, c, edgeIssues(e, c, ds.sourceDate, [])));
      }
      expect(states.indexOf(EdgeState.BARRIER) >= 0).assertTrue();
      expect(states.indexOf(EdgeState.CLEAR) >= 0).assertTrue();
      expect(states.indexOf(EdgeState.PARTIAL) >= 0).assertTrue();
      expect(states.indexOf(EdgeState.NO_DATA) >= 0).assertTrue();
    });
    it('unverified_report_does_not_block', 0, () => {
      const ds = buildDataset(grid());
      const c = needsConstraints(presetNeeds(Preset.STROLLER));
      const b = report('r1', FactKind.NARROW_PASSAGE, 50.0610, 19.9310, [vote('a', 1, 1)]);
      const before = assessAll(ds, c, indexBarriers(ds, []));
      const after = assessAll(ds, c, indexBarriers(ds, [b]));
      expect(after.counts[3]).assertEqual(before.counts[3]);
      b.votes.push(vote('b', 1, 1));
      expect(assessAll(ds, c, indexBarriers(ds, [b])).counts[3] > before.counts[3]).assertTrue();
    });
  });

  describe('Facts', () => {
    it('report_conflicting_with_osm_kerb', 0, () => {
      const ds = buildDataset(grid());
      const r = report('r1', FactKind.KERB, 50.06111, 19.93011, [vote('a', 1, 1)]);
      const f = buildFacts(ds, [r], noVotes()).filter((x: Fact) => x.id === 'r1')[0];
      expect(f.conflictKind).assertEqual(FactKind.LOWERED_KERB);
      expect(f.source).assertEqual(FactSource.REPORT);
    });
    it('outdated_and_hidden_are_not_listed', 0, () => {
      const ds = buildDataset(grid());
      const gone = report('r1', FactKind.STEPS, 50.0605, 19.9305, [vote('a', -1, 1), vote('b', -1, 1)]);
      const hidden = report('r2', FactKind.STEPS, 50.0605, 19.9305, [vote('a', 1, 1)]);
      hidden.hidden = true;
      const ids = buildFacts(ds, [gone, hidden], noVotes()).map((f: Fact): string => f.id);
      expect(ids.indexOf('r1')).assertEqual(-1);
      expect(ids.indexOf('r2')).assertEqual(-1);
    });
    it('duplicates_within_15_m', 0, () => {
      const ds = buildDataset(grid());
      const facts = buildFacts(ds, [], noVotes());
      const steps = stepsFact(ds.osmFacts);
      expect(sameKindNearby(facts, FactKind.STEPS, false, steps.lat + 0.00005, steps.lon).length).assertEqual(1);
      expect(sameKindNearby(facts, FactKind.STEPS, false, steps.lat + 0.001, steps.lon).length).assertEqual(0);
    });
  });

  describe('Plan', () => {
    it('route_avoids_osm_stairs_for_wheelchair', 0, () => {
      setLang(Lang.PL);
      const ds = buildDataset(grid());
      const plan = buildPlan(ds, buildFacts(ds, [], noVotes()), [], {
        from: { lat: 50.0600, lon: 19.9300 }, to: { lat: 50.0600, lon: 19.9320 },
        needs: presetNeeds(Preset.WHEELCHAIR), avoidFactIds: []
      });
      expect(plan.rated).assertTrue();
      expect(plan.barrierFree).assertTrue();
      expect(countKind(plan.facts, FactKind.STEPS)).assertEqual(0);
    });
    it('unrated_route_without_barriers_in_needs', 0, () => {
      const ds = buildDataset(grid());
      const plan = buildPlan(ds, buildFacts(ds, [], noVotes()), [], {
        from: { lat: 50.0600, lon: 19.9300 }, to: { lat: 50.0600, lon: 19.9320 },
        needs: emptyNeeds(), avoidFactIds: []
      });
      expect(plan.rated).assertFalse();
      expect(plan.gaps.length).assertEqual(0);
      expect(countKind(plan.facts, FactKind.STEPS)).assertEqual(1);
    });
    it('unverified_report_stays_on_route_with_alternative', 0, () => {
      const ds = buildDataset(grid());
      const r = report('r1', FactKind.NARROW_PASSAGE, 50.0610, 19.9310, [vote('a', 1, 1)]);
      const needs = presetNeeds(Preset.STROLLER);
      const plan = buildPlan(ds, buildFacts(ds, [r], noVotes()), [r], {
        from: { lat: 50.0610, lon: 19.9300 }, to: { lat: 50.0610, lon: 19.9320 }, needs: needs, avoidFactIds: []
      });
      expect(plan.facts.filter((it: RouteFactItem) => it.fact.id === 'r1').length).assertEqual(1);
    });
    it('no_free_route_through_kerb', 0, () => {
      const ds = buildDataset(grid());
      const plan = buildPlan(ds, buildFacts(ds, [], noVotes()), [], {
        from: { lat: 50.0600, lon: 19.9320 }, to: { lat: 50.0600, lon: 19.9340 },
        needs: presetNeeds(Preset.WHEELCHAIR), avoidFactIds: []
      });
      expect(plan.barrierFree).assertFalse();
      expect(plan.segments.filter((s: RouteSegment) => s.state === EdgeState.BARRIER).length > 0).assertTrue();
    });
  });

  describe('Labels', () => {
    it('polish_plurals', 0, () => {
      setLang(Lang.PL);
      expect(countBarriers(1)).assertEqual('1 bariera');
      expect(countBarriers(4)).assertEqual('4 bariery');
      expect(countBarriers(5)).assertEqual('5 barier');
      expect(countBarriers(12)).assertEqual('12 barier');
      expect(countBarriers(22)).assertEqual('22 bariery');
      expect(plural(13, 'a', 'b', 'c')).assertEqual('c');
    });
    it('titles_and_streets', 0, () => {
      setLang(Lang.PL);
      expect(factTitle(FactKind.STEPS, FactCategory.BARRIER, 4, 0)).assertEqual('Schody, 4 stopnie');
      expect(factTitle(FactKind.ROUGH_SURFACE, FactCategory.AREA, 0, 25)).assertEqual('Obszar: zła nawierzchnia, 25 m');
      expect(streetLabel('aleja Pokoju')).assertEqual('al. Pokoju');
      expect(streetLabel('Stanisława Lema')).assertEqual('ul. Stanisława Lema');
      expect(streetLabel('Park Lotników Polskich')).assertEqual('Park Lotników Polskich');
    });
    it('dates_and_distances', 0, () => {
      setLang(Lang.PL);
      expect(formatDate(new Date(2026, 9, 3, 12).getTime())).assertEqual('3.10.2026');
      expect(formatKm(400)).assertEqual('0,4 km');
      expect(formatKmRange(600, 800)).assertEqual('0,6-0,8 km');
      setLang(Lang.EN);
      expect(formatDate(new Date(2026, 9, 3, 12).getTime())).assertEqual('3 Oct 2026');
      setLang(Lang.PL);
    });
    it('pseudonym_rules', 0, () => {
      expect(pseudonymValid('wozek_krk')).assertTrue();
      expect(pseudonymValid('ab')).assertFalse();
      expect(pseudonymValid('a b c')).assertFalse();
      expect(pseudonymValid('łódź-2')).assertTrue();
    });
  });
}
