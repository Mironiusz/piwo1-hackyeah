import { common } from '@kit.AbilityKit';
import { util } from '@kit.ArkTS';
import { NearbyFact } from '../domain/Facts';
import { Fact, FactKind, FactStatus } from '../model/Types';
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
const DAY: number = 24 * 60 * 60 * 1000;

interface StoredVote {
  id: string;
  stillThere: boolean;
  at: number;
}

/** Stan wspólny klienta API: połączenie, ostatnia data kopii OSM i własne głosy z ostatniej doby. */
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
    this.votes = this.votes.filter((v: StoredVote) => v.id !== id && now - v.at < DAY);
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

/** Fakt nieaktualny nie jest nigdzie pokazywany (makieta System), więc lista go pomija. */
function visible(list: ApiFact[]): Fact[] {
  const out: Fact[] = [];
  for (const a of list) {
    if (!knownKind(a.type)) {
      continue;
    }
    const f = factFromApi(a);
    if (f.status !== FactStatus.OUTDATED) {
      out.push(f);
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

  /** `find_nearby_facts`: `POST /api/facts/nearby`. Geostref serwer nie porównuje, więc dla obszaru lista jest pusta. */
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

  /** Kontrakt nie zwraca własnego głosu, więc aplikacja pamięta głosy oddane z tego urządzenia w ostatniej dobie. */
  async myVote(id: string): Promise<MyVote | null> {
    const now = Date.now();
    for (const v of this.core.votes) {
      if (v.id === id && now - v.at < DAY) {
        return { stillThere: v.stillThere, at: v.at };
      }
    }
    return null;
  }

  /** `cast_vote`: `POST /api/facts/{id}/votes` z `confirm` albo `deny`. */
  async vote(id: string, stillThere: boolean): Promise<MyVote> {
    const body: ApiVoteRequest = { verdict: stillThere ? 'confirm' : 'deny' };
    await this.core.json<ApiFactResponse>('POST', `/api/facts/${factId(id)}/votes`, JSON.stringify(body), Auth.OPTIONAL);
    const at = Date.now();
    this.core.rememberVote(id, stillThere, at);
    return { stillThere: stillThere, at: at };
  }

  /** `create_fact`: `POST /api/facts`, z kluczem idempotencji tworzonym raz na zatwierdzone podsumowanie. */
  async report(input: NewReport): Promise<Fact> {
    const desc = input.description.trim();
    const body: ApiCreateFactRequest = {
      idempotency_key: util.generateRandomUUID(true),
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
   * `plan_route`: `POST /api/routes`, bez tokenu. Gdy osoba wybiera trasę alternatywną, aplikacja nie pyta
   * serwera drugi raz, tylko pokazuje alternatywę z ostatniej odpowiedzi dla tych samych punktów i potrzeb.
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

  /** `search_address`: `POST /api/address-search`; tekst idzie tylko w treści żądania. */
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

  /** Kontrakt nie ma odwrotnego wyszukiwania, więc punkt z mapy zostaje bez nazwy ulicy. */
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

  /** `read_own_account`: `GET /api/accounts/me`; wygasła sesja kończy się wylogowaniem bez błędu. */
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

  /** `log_in`: `POST /api/sessions`; token przychodzi w nagłówku `Session-Token`. */
  async login(pseudonym: string, password: string): Promise<Account> {
    const body: ApiCredentials = { pseudonym: pseudonym, password: password };
    return this.view(await this.core.json<ApiAccountResponse>('POST', '/api/sessions', JSON.stringify(body), Auth.NONE));
  }

  /** `create_account`: `POST /api/accounts`, a po nim `log_in`, bo założenie konta nie loguje. */
  async signup(pseudonym: string, password: string): Promise<Account> {
    const body: ApiCredentials = { pseudonym: pseudonym, password: password };
    await this.core.json<ApiAccountResponse>('POST', '/api/accounts', JSON.stringify(body), Auth.NONE);
    return this.login(pseudonym, password);
  }

  /** Wylogowanie to usunięcie tokenu z urządzenia; kontrakt nie ma do tego operacji. */
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

  /** `list_flagged_facts`: `GET /api/moderation/flagged-facts`, bez ukrytych. */
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

/** Repozytorium nad API zespołu (`docs/product/api_contract.md`), używane, gdy `config/api.json` podaje adres. */
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
