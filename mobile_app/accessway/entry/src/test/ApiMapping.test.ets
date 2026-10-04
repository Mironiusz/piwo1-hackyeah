import { describe, it, expect } from '@ohos/hypium';
import { dayToMs, factFromApi, kindFromApi, kindToApi, planFromApi, routeFactFromApi } from '../main/ets/data/ApiMapping';
import { ApiFact, ApiPlanRouteResponse, ApiRouteFact } from '../main/ets/data/ApiTypes';
import { Lang, setLang } from '../main/ets/model/I18n';
import { EdgeState, FactCategory, FactKind, FactSource, FactStatus } from '../main/ets/model/Types';

function apiFact(id: number, type: string, source: string): ApiFact {
  return {
    id: id, type: type, point: { lat: 50.0678, lon: 19.9914 }, geozone_radius_m: null, description: null,
    step_count: type === 'stairs' ? 3 : null, source: source, status: 'confirmed', is_removed_from_osm: false,
    osm_edited_on: source === 'openstreetmap' ? '2026-09-14' : null, last_confirmed_on: '2026-10-03',
    is_sample: false, can_be_flagged: source !== 'openstreetmap'
  };
}

function routeFact(id: number, type: string, at: number, overruled: boolean): ApiRouteFact {
  const f = apiFact(id, type, 'user_report');
  return {
    id: f.id, type: f.type, point: f.point, geozone_radius_m: f.geozone_radius_m, description: f.description,
    step_count: f.step_count, source: f.source, status: 'unverified', is_removed_from_osm: false,
    osm_edited_on: null, last_confirmed_on: f.last_confirmed_on, is_sample: true, can_be_flagged: true,
    distance_from_start_m: at, is_overruled_by_osm: overruled
  };
}

function response(): ApiPlanRouteResponse {
  return {
    osm_copy_date: '2026-10-02',
    barrier_free_route_exists: false,
    route: {
      length_m: 1000,
      segments: [
        { line: [[19.98, 50.06], [19.981, 50.06]], length_m: 20, state: 'no_data', missing_attributes: ['kerbs', 'steps'],
          is_marked_wheelchair_no: false },
        { line: [[19.981, 50.06], [19.99, 50.065]], length_m: 600, state: 'no_barrier', missing_attributes: [],
          is_marked_wheelchair_no: false },
        { line: [[19.99, 50.065], [19.995, 50.067]], length_m: 380, state: 'partial_data', missing_attributes: ['width'],
          is_marked_wheelchair_no: true }
      ],
      profile_barriers: [routeFact(7, 'high_kerb', 400, true)],
      additional_barriers: [routeFact(8, 'steep_incline', 300, false)],
      amenities: [routeFact(9, 'ramp', 900, false)]
    },
    alternative: {
      route: { length_m: 1180, segments: [], profile_barriers: [], additional_barriers: [], amenities: [] },
      avoided_barriers: [routeFact(7, 'high_kerb', 400, true)]
    }
  };
}

export default function apiMappingTest() {
  describe('ApiMapping', () => {
    it('kind_codes_round_trip', 0, () => {
      expect(kindToApi(FactKind.KERB)).assertEqual('high_kerb');
      expect(kindToApi(FactKind.REST_SPOT)).assertEqual('rest_place');
      expect(kindFromApi('handrail_at_stairs')).assertEqual(FactKind.HANDRAIL);
      expect(kindFromApi(kindToApi(FactKind.ROUGH_SURFACE))).assertEqual(FactKind.ROUGH_SURFACE);
    });
    it('fact_from_contract_example', 0, () => {
      const f = factFromApi(apiFact(1042, 'stairs', 'openstreetmap'));
      expect(f.id).assertEqual('1042');
      expect(f.kind).assertEqual(FactKind.STEPS);
      expect(f.source).assertEqual(FactSource.OSM);
      expect(f.status).assertEqual(FactStatus.CONFIRMED);
      expect(f.stepCount).assertEqual(3);
      expect(f.date).assertEqual(dayToMs('2026-09-14'));
      const zone = apiFact(5, 'narrow_passage', 'user_report');
      zone.geozone_radius_m = 50;
      expect(factFromApi(zone).category).assertEqual(FactCategory.AREA);
    });
    it('overruled_report_becomes_conflict', 0, () => {
      expect(routeFactFromApi(routeFact(7, 'high_kerb', 400, true)).conflictKind).assertEqual(FactKind.LOWERED_KERB);
    });
    it('plan_from_route_response', 0, () => {
      setLang(Lang.PL);
      const r = response();
      const plan = planFromApi(r.route, r.barrier_free_route_exists, true, r);
      expect(plan.barrierFree).assertFalse();
      expect(plan.lengthM).assertEqual(1000);
      expect(plan.segments.length).assertEqual(3);
      expect(plan.segments[1].state).assertEqual(EdgeState.CLEAR);
      expect(plan.segments[2].fromM).assertEqual(620);
      expect(plan.segments[0].pts[0]).assertEqual(50.06);
      expect(plan.noDataM).assertEqual(20);
      expect(plan.gaps.length).assertEqual(2);
      expect(plan.gaps[0].isStart).assertTrue();
      expect(plan.gaps[0].missing.join(',')).assertEqual('krawężniki,stopnie');
      expect(plan.gaps[1].missing.length).assertEqual(2);
      expect(plan.facts.map((it) => it.atM).join(',')).assertEqual('300,400,900');
      expect(plan.alternatives.length).assertEqual(1);
      expect(plan.alternatives[0].factId).assertEqual('7');
      expect(plan.alternatives[0].extraM).assertEqual(180);
    });
    it('unrated_plan_without_gaps', 0, () => {
      const r = response();
      const plan = planFromApi(r.route, r.barrier_free_route_exists, false, r);
      expect(plan.rated).assertFalse();
      expect(plan.barrierFree).assertTrue();
      expect(plan.gaps.length).assertEqual(0);
    });
  });
}
