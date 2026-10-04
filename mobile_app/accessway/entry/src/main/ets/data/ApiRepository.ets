import { common } from '@kit.AbilityKit';
import { NearbyFact } from '../domain/Facts';
import { sameDay } from '../domain/Trust';
import { Fact, FactKind } from '../model/Types';
import { ApiSettings } from './ApiConfig';
import { ApiClient, Auth } from './ApiClient';
import { dayToMs, factFromApi, kindToApi, knownKind, planFromApi } from './ApiMapping';
import {
  ApiAccountResponse,
  ApiAreaRequest,
  ApiCreateFactRequest,
  ApiCredentials,
  ApiFact,
  ApiFactResponse,
  ApiFactsResponse,
  ApiFlaggedItem,
  ApiFlaggedResponse,
  ApiNearbyItem,
  ApiNearbyRequest,
  ApiNearbyResponse,
  ApiOsmCopy,
  ApiPlanRouteRequest,
  ApiPlanRouteResponse,
  ApiSearchRequest,
  ApiSearchResponse,
  ApiVoteRequest
} from './ApiTypes';
import {
  Account,
  AccountRepository,
  Area,
  DataInfo,
  ErrorCode,
  FactsPage,
  FactsRepository,
  GeocodeResult,
  GeocodingRepository,
  ModerationRepository,
  MyVote,
  NewReport,
  RepoError,
  Repository,
  RoutePlan,
  RouteRequest,
  RoutingRepository
} from './Repository';
import { readFileText, writeFileText } from './Storage';

const VOTES_FILE: string = 'api_my_votes.json';

interface StoredVote {
  id: string;
  stillThere: boolean;
  at: number;
}

/** Shared state of the API client: the connection, the latest OSM copy date and own votes from the last day. */
class ApiCore {
  client: ApiClient;
  ctx: common.Context;
  info: DataInfo = { osmDate: 0, isSample: false };
  votes: StoredVote[] = [];
  lastPlan: ApiPlanRouteResponse | null = null;
  lastPlanKey: string = '';

  constructor(ctx: common.Context, settings: ApiSettings) {
    this.ctx = ctx;
    this.client = new ApiClient(ctx, settings);
    const raw = readFileText(`${ctx.filesDir}/${VOTES_FILE}`);
    if (raw !== null) {
      try {
        this.votes = JSON.parse(raw) as StoredVote[];
      } catch (e) {
        this.votes = [];
      }
    }
  }

  async json<T>(m: string, path: string, body: string, auth: Auth): Promise<T> {
    const res = await this.client.send(m, path, body, auth);
    return JSON.parse(res.body) as T;
  }

  rememberVote(id: string, stillThere: boolean, at: number): void {
    const now = Date.now();
    this.votes = this.votes.filter((v: StoredVote) => v.id !== id && sameDay(v.at, now));
    this.votes.push({ id: id, stillThere: stillThere, at: at });
    try {
      writeFileText(`${this.ctx.filesDir}/${VOTES_FILE}`, JSON.stringify(this.votes));
    } catch (e) {
      return;
    }
  }
}

function factId(id: string): number {
  const n = parseInt(id, 10);
  if (isNaN(n)) {
    throw new RepoError(ErrorCode.NOT_FOUND, 'not found');
  }
  return n;
}

/**
 * Facts of the types the app knows. An outdated fact stays on the map with its status, so that people can judge
 * it and confirm it again (specification M4, version 7; `list_facts_in_area`); the service already leaves out the
 * facts removed in OpenStreetMap and the hidden ones.
 */
function visible(list: ApiFact[]): Fact[] {
  const out: Fact[] = [];
  for (const a of list) {
    if (knownKind(a.type)) {
      out.push(factFromApi(a));
    }
  }
  return out;
}

class ApiFacts implements FactsRepository {
  core: ApiCore;

  constructor(core: ApiCore) {
    this.core = core;
  }

  info(): DataInfo {
    return this.core.info;
  }

  /** `read_osm_copy`: `GET /api/osm-copy`. */
  async refreshInfo(): Promise<DataInfo> {
    const r = await this.core.json<ApiOsmCopy>('GET', '/api/osm-copy', '', Auth.OPTIONAL);
    this.core.info = { osmDate: dayToMs(r.date), isSample: this.core.info.isSample };
    return this.core.info;
  }

  /** `list_facts_in_area`: `POST /api/facts/in-area`. */
  async listFacts(area: Area): Promise<FactsPage> {
    const body: ApiAreaRequest = {
      south_west: { lat: area.south, lon: area.west },
      north_east: { lat: area.north, lon: area.east }
    };
    const r = await this.core.json<ApiFactsResponse>('POST', '/api/facts/in-area', JSON.stringify(body), Auth.OPTIONAL);
    const facts = visible(r.facts);
    for (const f of facts) {
      if (f.isSample) {
        this.core.info.isSample = true;
      }
    }
    return { facts: facts, truncated: r.is_truncated };
  }

  /** `find_nearby_facts`: `POST /api/facts/nearby`. The server skips geozones, so an area gets an empty list. */
  async findNearby(kind: FactKind, isArea: boolean, lat: number, lon: number): Promise<NearbyFact[]> {
    if (isArea) {
      return [];
    }
    const body: ApiNearbyRequest = { type: kindToApi(kind), point: { lat: lat, lon: lon } };
    const r = await this.core.json<ApiNearbyResponse>('POST', '/api/facts/nearby', JSON.stringify(body), Auth.OPTIONAL);
    const out: NearbyFact[] = [];
    for (const it of r.facts) {
      if (knownKind(it.fact.type)) {
        out.push({ fact: factFromApi(it.fact), distanceM: it.distance_m });
      }
    }
    return out;
  }

  /** `read_fact`: `GET /api/facts/{id}`. */
  async getFact(id: string): Promise<Fact> {
    const r = await this.core.json<ApiFactResponse>('GET', `/api/facts/${factId(id)}`, '', Auth.OPTIONAL);
    return factFromApi(r.fact);
  }

  /** The contract does not return one's own vote, so the app remembers votes cast from this device today. */
  async myVote(id: string): Promise<MyVote | null> {
    const now = Date.now();
    for (const v of this.core.votes) {
      if (v.id === id && sameDay(v.at, now)) {
        return { stillThere: v.stillThere, at: v.at };
      }
    }
    return null;
  }

  /** `cast_vote`: `POST /api/facts/{id}/votes` with `confirm` or `deny`. */
  async vote(id: string, stillThere: boolean): Promise<MyVote> {
    const body: ApiVoteRequest = { verdict: stillThere ? 'confirm' : 'deny' };
    await this.core.json<ApiFactResponse>('POST', `/api/facts/${factId(id)}/votes`, JSON.stringify(body), Auth.OPTIONAL);
    const at = Date.now();
    this.core.rememberVote(id, stillThere, at);
    return { stillThere: stillThere, at: at };
  }

  /**
   * `create_fact`: `POST /api/facts` with the idempotency key of the approved summary, the same on every attempt
   * of the same save, so a retry after a lost response returns the first saved fact instead of a duplicate.
   */
  async report(input: NewReport): Promise<Fact> {
    const desc = input.description.trim();
    const body: ApiCreateFactRequest = {
      idempotency_key: input.idempotencyKey,
      type: kindToApi(input.kind),
      point: { lat: input.lat, lon: input.lon },
      description: desc.length > 0 ? desc : null,
      step_count: input.kind === FactKind.STEPS && input.stepCount > 0 ? input.stepCount : null,
      geozone_radius_m: input.isArea ? input.radiusM : null
    };
    const r = await this.core.json<ApiFactResponse>('POST', '/api/facts', JSON.stringify(body), Auth.OPTIONAL);
    return factFromApi(r.fact);
  }

  /** `flag_fact`: `POST /api/facts/{id}/flag`. */
  async flagForModeration(id: string): Promise<void> {
    await this.core.client.send('POST', `/api/facts/${factId(id)}/flag`, '', Auth.OPTIONAL);
  }
}

class ApiRouting implements RoutingRepository {
  core: ApiCore;

  constructor(core: ApiCore) {
    this.core = core;
  }

  /**
   * `plan_route`: `POST /api/routes`, without a token. When the person picks the alternative route, the app does not
   * ask the server again, but shows the alternative from the last response for the same points and needs.
   */
  async route(req: RouteRequest): Promise<RoutePlan> {
    const body: ApiPlanRouteRequest = {
      start: { lat: req.from.lat, lon: req.from.lon },
      destination: { lat: req.to.lat, lon: req.to.lon },
      avoid: req.needs.avoid.map((k: FactKind): string => kindToApi(k)),
      need: req.needs.need.map((k: FactKind): string => kindToApi(k))
    };
    const key = JSON.stringify(body);
    const rated = req.needs.avoid.length > 0;
    const cached = this.core.lastPlan;
    if (req.avoidFactIds.length > 0 && cached !== null && this.core.lastPlanKey === key && cached.alternative !== null) {
      return planFromApi(cached.alternative.route, true, rated, null);
    }
    const r = await this.core.json<ApiPlanRouteResponse>('POST', '/api/routes', key, Auth.NONE);
    this.core.lastPlan = r;
    this.core.lastPlanKey = key;
    if (r.osm_copy_date !== null) {
      this.core.info.osmDate = dayToMs(r.osm_copy_date);
    }
    return planFromApi(r.route, r.barrier_free_route_exists, rated, r);
  }
}

class ApiGeocoding implements GeocodingRepository {
  core: ApiCore;

  constructor(core: ApiCore) {
    this.core = core;
  }

  /** `search_address`: `POST /api/address-search`; the text goes only in the request body. */
  async search(text: string): Promise<GeocodeResult[]> {
    const body: ApiSearchRequest = { text: text };
    const r = await this.core.json<ApiSearchResponse>('POST', '/api/address-search', JSON.stringify(body), Auth.NONE);
    const out: GeocodeResult[] = [];
    for (let i = 0; i < r.matches.length; i++) {
      const m = r.matches[i];
      const cut = m.label.indexOf(',');
      out.push({
        id: `${i}`,
        name: cut > 0 ? m.label.substring(0, cut) : m.label,
        address: cut > 0 ? m.label.substring(cut + 1).trim() : '',
        lat: m.point.lat,
        lon: m.point.lon
      });
    }
    return out;
  }

  /** The contract has no reverse search, so a point from the map stays without a street name. */
  async streetAt(lat: number, lon: number): Promise<string> {
    return '';
  }
}

class ApiAccounts implements AccountRepository {
  core: ApiCore;

  constructor(core: ApiCore) {
    this.core = core;
  }

  private view(r: ApiAccountResponse): Account {
    return { pseudonym: r.account.pseudonym, moderator: r.account.is_moderator };
  }

  /** `read_own_account`: `GET /api/accounts/me`; an expired session ends in a sign-out without an error. */
  async current(): Promise<Account | null> {
    if (!this.core.client.hasToken()) {
      return null;
    }
    try {
      return this.view(await this.core.json<ApiAccountResponse>('GET', '/api/accounts/me', '', Auth.REQUIRED));
    } catch (e) {
      if (e instanceof RepoError && (e as RepoError).code === ErrorCode.SESSION_EXPIRED) {
        return null;
      }
      throw e as Error;
    }
  }

  /** `log_in`: `POST /api/sessions`; the token comes in the `Session-Token` header. */
  async login(pseudonym: string, password: string): Promise<Account> {
    const body: ApiCredentials = { pseudonym: pseudonym, password: password };
    return this.view(await this.core.json<ApiAccountResponse>('POST', '/api/sessions', JSON.stringify(body), Auth.NONE));
  }

  /** `create_account`: `POST /api/accounts`, then `log_in`, because creating an account does not sign in. */
  async signup(pseudonym: string, password: string): Promise<Account> {
    const body: ApiCredentials = { pseudonym: pseudonym, password: password };
    await this.core.json<ApiAccountResponse>('POST', '/api/accounts', JSON.stringify(body), Auth.NONE);
    return this.login(pseudonym, password);
  }

  /** Signing out means removing the token from the device; the contract has no operation for it. */
  async logout(): Promise<void> {
    this.core.client.clearToken();
  }

  /** `delete_own_account`: `DELETE /api/accounts/me`. */
  async deleteAccount(): Promise<void> {
    await this.core.client.send('DELETE', '/api/accounts/me', '', Auth.REQUIRED);
    this.core.client.clearToken();
  }
}

class ApiModeration implements ModerationRepository {
  core: ApiCore;

  constructor(core: ApiCore) {
    this.core = core;
  }

  private async items(): Promise<ApiFlaggedItem[]> {
    const r = await this.core.json<ApiFlaggedResponse>('GET', '/api/moderation/flagged-facts', '', Auth.REQUIRED);
    return r.facts.filter((it: ApiFlaggedItem) => knownKind(it.fact.type));
  }

  private toFact(it: ApiFlaggedItem): Fact {
    const f = factFromApi(it.fact);
    f.flagged = true;
    f.hidden = it.is_hidden;
    return f;
  }

  /** `list_flagged_facts`: `GET /api/moderation/flagged-facts`, without hidden ones. */
  async flagged(): Promise<Fact[]> {
    return (await this.items()).filter((it: ApiFlaggedItem) => !it.is_hidden).map((it: ApiFlaggedItem): Fact => this.toFact(it));
  }

  async hiddenFacts(): Promise<Fact[]> {
    return (await this.items()).filter((it: ApiFlaggedItem) => it.is_hidden).map((it: ApiFlaggedItem): Fact => this.toFact(it));
  }

  /** `hide_fact`: `POST /api/moderation/flagged-facts/{id}/hide`. */
  async hide(id: string): Promise<void> {
    await this.core.client.send('POST', `/api/moderation/flagged-facts/${factId(id)}/hide`, '', Auth.REQUIRED);
  }

  /** `restore_fact`: `POST /api/moderation/flagged-facts/{id}/restore`. */
  async restore(id: string): Promise<void> {
    await this.core.client.send('POST', `/api/moderation/flagged-facts/${factId(id)}/restore`, '', Auth.REQUIRED);
  }
}

/** Repository over the team's API (`docs/product/api_contract.md`), used when `config/api.json` gives an address. */
export class ApiRepository implements Repository {
  facts: FactsRepository;
  routing: RoutingRepository;
  geocoding: GeocodingRepository;
  accounts: AccountRepository;
  moderation: ModerationRepository;

  constructor(ctx: common.Context, settings: ApiSettings) {
    const core = new ApiCore(ctx, settings);
    this.facts = new ApiFacts(core);
    this.routing = new ApiRouting(core);
    this.geocoding = new ApiGeocoding(core);
    this.accounts = new ApiAccounts(core);
    this.moderation = new ApiModeration(core);
  }
}
