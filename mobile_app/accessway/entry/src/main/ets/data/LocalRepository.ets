import { common } from '@kit.AbilityKit';
import { cryptoFramework } from '@kit.CryptoArchitectureKit';
import { util } from '@kit.ArkTS';
import { buildFacts, NearbyFact, reportFact, sameKindNearby } from '../domain/Facts';
import { buildDataset, Dataset, nearestStreet, OverpassResponse, searchPlaces } from '../domain/OsmMapping';
import { buildPlan } from '../domain/Plan';
import { recentVote, voteWeight } from '../domain/Trust';
import { tr } from '../model/I18n';
import { Barrier, DAY_MS, Fact, FactKind, Place, Vote } from '../model/Types';
import { demoReports } from './DemoSeed';
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
  passwordValid,
  pseudonymValid,
  RepoError,
  Repository,
  RoutePlan,
  RouteRequest,
  RoutingRepository
} from './Repository';
import { readFileText, readRawText, writeFileText } from './Storage';

const STATE_FILE: string = 'local_repository.json';
const SESSION_MS: number = DAY_MS;
/** In the local version the account with this nickname gets the moderator role; in the API the server grants it. */
export const LOCAL_MODERATOR: string = 'moderator';

interface StoredAccount {
  pseudonym: string;
  salt: string;
  hash: string;
  moderator: boolean;
}

interface StoredSession {
  pseudonym: string;
  lastUsed: number;
}

interface StoredState {
  version: number;
  deviceId: string;
  reports: Barrier[];
  osmVotes: Record<string, Vote[]>;
  accounts: StoredAccount[];
  session?: StoredSession;
}

function randomId(prefix: string): string {
  return `${prefix}-${Date.now().toString(36)}-${Math.floor(Math.random() * 1e9).toString(36)}`;
}

function sha256Hex(text: string): string {
  const md = cryptoFramework.createMd('SHA256');
  const bytes = new util.TextEncoder().encodeInto(text);
  md.updateSync({ data: bytes });
  const out = md.digestSync().data;
  let hex = '';
  for (let i = 0; i < out.length; i++) {
    const h = out[i].toString(16);
    hex += h.length === 1 ? '0' + h : h;
  }
  return hex;
}

/** Shared state of the local version: walking network from a file, plus reports, votes and accounts on the device. */
export class LocalCore {
  ctx: common.Context | null = null;
  ds: Dataset = new Dataset();
  deviceId: string = '';
  reports: Barrier[] = [];
  osmVotes: Map<string, Vote[]> = new Map<string, Vote[]>();
  accounts: StoredAccount[] = [];
  session: StoredSession | null = null;
  loadError: string = '';
  private factsCache: Fact[] | null = null;

  init(ctx: common.Context): void {
    this.ctx = ctx;
    this.loadDataset();
    this.loadState();
  }

  private path(): string {
    return `${(this.ctx as common.Context).filesDir}/${STATE_FILE}`;
  }

  private loadDataset(): void {
    const ctx = this.ctx as common.Context;
    let raw = readRawText(ctx, 'data/osm_krakow.json');
    if (raw === null) {
      raw = readRawText(ctx, 'data/osm_sample.json');
    }
    if (raw === null) {
      this.loadError = tr('Brak danych mapy w aplikacji', 'No map data in the app');
      return;
    }
    try {
      this.ds = buildDataset(JSON.parse(raw) as OverpassResponse);
    } catch (e) {
      this.loadError = tr('Uszkodzony plik danych mapy', 'Damaged map data file');
    }
  }

  private loadState(): void {
    const raw = readFileText(this.path());
    if (raw !== null) {
      try {
        const st = JSON.parse(raw) as StoredState;
        this.deviceId = st.deviceId;
        this.reports = st.reports;
        this.accounts = st.accounts;
        this.session = st.session ?? null;
        this.osmVotes = new Map<string, Vote[]>();
        const keys = Object.keys(st.osmVotes);
        for (const k of keys) {
          this.osmVotes.set(k, st.osmVotes[k]);
        }
      } catch (e) {
        this.deviceId = '';
      }
    }
    if (this.deviceId.length === 0) {
      this.deviceId = randomId('dev');
      this.reports = demoReports(Date.now());
      this.save();
    }
  }

  save(): void {
    this.factsCache = null;
    if (this.ctx === null) {
      return;
    }
    const votes: Record<string, Vote[]> = {};
    this.osmVotes.forEach((v: Vote[], k: string) => {
      votes[k] = v;
    });
    const st: StoredState = {
      version: 2,
      deviceId: this.deviceId,
      reports: this.reports,
      osmVotes: votes,
      accounts: this.accounts,
      session: this.session ?? undefined
    };
    writeFileText(this.path(), JSON.stringify(st));
  }

  facts(): Fact[] {
    if (this.factsCache === null) {
      this.factsCache = buildFacts(this.ds, this.reports, this.osmVotes);
    }
    return this.factsCache;
  }

  /** The active account or null; the session expires a day after the app was last used. */
  account(): StoredAccount | null {
    const s = this.session;
    if (s === null) {
      return null;
    }
    const now = Date.now();
    if (now - s.lastUsed > SESSION_MS) {
      this.session = null;
      this.save();
      return null;
    }
    for (const a of this.accounts) {
      if (a.pseudonym === s.pseudonym) {
        s.lastUsed = now;
        return a;
      }
    }
    this.session = null;
    return null;
  }

  voterId(): string {
    const a = this.account();
    return a !== null ? `acc:${a.pseudonym}` : `dev:${this.deviceId}`;
  }

  findReport(id: string): Barrier | null {
    for (const b of this.reports) {
      if (b.id === id) {
        return b;
      }
    }
    return null;
  }

  votesOf(id: string): Vote[] {
    const b = this.findReport(id);
    if (b !== null) {
      return b.votes;
    }
    return this.osmVotes.get(id) ?? [];
  }

  findFact(id: string): Fact | null {
    for (const f of this.facts()) {
      if (f.id === id) {
        return f;
      }
    }
    const b = this.findReport(id);
    return b !== null ? reportFact(b) : null;
  }
}

class LocalFacts implements FactsRepository {
  core: LocalCore;

  constructor(core: LocalCore) {
    this.core = core;
  }

  info(): DataInfo {
    return { osmDate: this.core.ds.sourceDate, isSample: this.core.ds.isSample };
  }

  async refreshInfo(): Promise<DataInfo> {
    return this.info();
  }

  /** The local version knows all facts at once, so it returns all of them regardless of the rectangle. */
  async listFacts(area: Area): Promise<FactsPage> {
    return { facts: this.core.facts(), truncated: false };
  }

  async findNearby(kind: FactKind, isArea: boolean, lat: number, lon: number): Promise<NearbyFact[]> {
    return sameKindNearby(this.core.facts(), kind, isArea, lat, lon);
  }

  async getFact(id: string): Promise<Fact> {
    const f = this.core.findFact(id);
    if (f === null) {
      throw new RepoError(ErrorCode.NOT_FOUND, tr('Nie ma takiego faktu', 'No such fact'));
    }
    return f;
  }

  async myVote(id: string): Promise<MyVote | null> {
    const v = recentVote(this.core.votesOf(id), this.core.voterId(), Date.now());
    return v === null ? null : { stillThere: v.value > 0, at: v.at };
  }

  async vote(id: string, stillThere: boolean): Promise<MyVote> {
    const core = this.core;
    const now = Date.now();
    const voter = core.voterId();
    if (core.findFact(id) === null) {
      throw new RepoError(ErrorCode.NOT_FOUND, tr('Nie ma takiego faktu', 'No such fact'));
    }
    if (recentVote(core.votesOf(id), voter, now) !== null) {
      throw new RepoError(ErrorCode.VOTE_TOO_SOON,
        tr('Na ten fakt głosowałeś już dzisiaj. Kolejny głos będzie możliwy jutro.', 'You already voted on this fact today. You can vote again tomorrow.'));
    }
    const v: Vote = { voterId: voter, value: stillThere ? 1 : -1, weight: voteWeight(core.account() !== null), at: now };
    const b = core.findReport(id);
    if (b !== null) {
      b.votes.push(v);
    } else {
      const list = core.osmVotes.get(id) ?? [];
      list.push(v);
      core.osmVotes.set(id, list);
    }
    core.save();
    return { stillThere: stillThere, at: now };
  }

  async report(input: NewReport): Promise<Fact> {
    const core = this.core;
    const now = Date.now();
    const b: Barrier = {
      id: randomId('r'),
      kind: input.kind,
      lat: input.lat,
      lon: input.lon,
      radiusM: input.isArea ? input.radiusM : 0,
      isArea: input.isArea,
      stepCount: input.stepCount,
      description: input.description.trim(),
      street: nearestStreet(core.ds, input.lat, input.lon),
      createdAt: now,
      isSample: false,
      votes: [{ voterId: core.voterId(), value: 1, weight: voteWeight(core.account() !== null), at: now }],
      hidden: false,
      flagged: false
    };
    core.reports.push(b);
    core.save();
    return reportFact(b);
  }

  async flagForModeration(id: string): Promise<void> {
    const b = this.core.findReport(id);
    if (b === null) {
      throw new RepoError(ErrorCode.NOT_FOUND, tr('Do moderacji można zgłosić tylko zgłoszenie użytkownika',
        'Only a user report can be sent to moderation'));
    }
    b.flagged = true;
    this.core.save();
  }
}

class LocalRouting implements RoutingRepository {
  core: LocalCore;

  constructor(core: LocalCore) {
    this.core = core;
  }

  async route(req: RouteRequest): Promise<RoutePlan> {
    return buildPlan(this.core.ds, this.core.facts(), this.core.reports, req);
  }
}

function addressOf(p: Place): string {
  const t = p.tags;
  const street = t['addr:street'] !== undefined ? `${t['addr:street']} ${t['addr:housenumber'] ?? ''}`.trim() : '';
  const city = `${t['addr:postcode'] ?? ''} ${t['addr:city'] ?? 'Kraków'}`.trim();
  const parts: string[] = [];
  for (const s of [street, t['addr:suburb'] ?? '', city]) {
    if (s.length > 0) {
      parts.push(s);
    }
  }
  return parts.join(', ');
}

class LocalGeocoding implements GeocodingRepository {
  core: LocalCore;

  constructor(core: LocalCore) {
    this.core = core;
  }

  async search(text: string): Promise<GeocodeResult[]> {
    const out: GeocodeResult[] = [];
    for (const p of searchPlaces(this.core.ds, text, 8)) {
      out.push({ id: p.id, name: p.name, address: addressOf(p), lat: p.lat, lon: p.lon });
    }
    return out;
  }

  async streetAt(lat: number, lon: number): Promise<string> {
    return nearestStreet(this.core.ds, lat, lon);
  }
}

class LocalAccounts implements AccountRepository {
  core: LocalCore;

  constructor(core: LocalCore) {
    this.core = core;
  }

  private view(a: StoredAccount): Account {
    return { pseudonym: a.pseudonym, moderator: a.moderator };
  }

  async current(): Promise<Account | null> {
    const a = this.core.account();
    if (a !== null) {
      this.core.save();
    }
    return a === null ? null : this.view(a);
  }

  async login(pseudonym: string, password: string): Promise<Account> {
    const p = pseudonym.trim();
    for (const a of this.core.accounts) {
      if (a.pseudonym.toLowerCase() === p.toLowerCase() && a.hash === sha256Hex(a.salt + password)) {
        this.core.session = { pseudonym: a.pseudonym, lastUsed: Date.now() };
        this.core.save();
        return this.view(a);
      }
    }
    throw new RepoError(ErrorCode.BAD_CREDENTIALS,
      tr('Pseudonim i hasło do siebie nie pasują. Sprawdź oba i spróbuj ponownie.',
        'The nickname and password do not match. Check both and try again.'));
  }

  async signup(pseudonym: string, password: string): Promise<Account> {
    const p = pseudonym.trim();
    if (!pseudonymValid(p)) {
      throw new RepoError(ErrorCode.INVALID_PSEUDONYM,
        tr('Pseudonim musi mieć od 3 do 30 znaków: litery, cyfry, podkreślenie i myślnik.',
          'A nickname needs 3 to 30 characters: letters, digits, underscore and hyphen.'));
    }
    if (!passwordValid(password)) {
      throw new RepoError(ErrorCode.INVALID_PASSWORD,
        tr('Hasło musi mieć co najmniej 5 znaków.', 'The password needs at least 5 characters.'));
    }
    for (const a of this.core.accounts) {
      if (a.pseudonym.toLowerCase() === p.toLowerCase()) {
        throw new RepoError(ErrorCode.TAKEN, tr('Ten pseudonim jest już zajęty. Wybierz inny.',
          'This nickname is already taken. Choose another one.'));
      }
    }
    const salt = randomId('s');
    const acc: StoredAccount = { pseudonym: p, salt: salt, hash: sha256Hex(salt + password),
      moderator: p.toLowerCase() === LOCAL_MODERATOR };
    this.core.accounts.push(acc);
    this.core.session = { pseudonym: p, lastUsed: Date.now() };
    this.core.save();
    return this.view(acc);
  }

  async logout(): Promise<void> {
    this.core.session = null;
    this.core.save();
  }

  /** Deletes the account and nickname; votes stay and still count, but are unlinked from the person. */
  async deleteAccount(): Promise<void> {
    const a = this.core.account();
    if (a === null) {
      return;
    }
    const oldVoter = `acc:${a.pseudonym}`;
    const newVoter = randomId('gone');
    const relink = (list: Vote[]): void => {
      for (const v of list) {
        if (v.voterId === oldVoter) {
          v.voterId = newVoter;
        }
      }
    };
    for (const b of this.core.reports) {
      relink(b.votes);
    }
    this.core.osmVotes.forEach((list: Vote[]) => relink(list));
    this.core.accounts = this.core.accounts.filter((x: StoredAccount) => x.pseudonym !== a.pseudonym);
    this.core.session = null;
    this.core.save();
  }
}

class LocalModeration implements ModerationRepository {
  core: LocalCore;

  constructor(core: LocalCore) {
    this.core = core;
  }

  private requireModerator(): void {
    const a = this.core.account();
    if (a === null || !a.moderator) {
      throw new RepoError(ErrorCode.FORBIDDEN, tr('To konto nie ma roli moderatora.', 'This account is not a moderator.'));
    }
  }

  async flagged(): Promise<Fact[]> {
    this.requireModerator();
    const out: Fact[] = [];
    for (const b of this.core.reports) {
      if (b.flagged && !b.hidden) {
        out.push(reportFact(b));
      }
    }
    return out;
  }

  async hiddenFacts(): Promise<Fact[]> {
    this.requireModerator();
    const out: Fact[] = [];
    for (const b of this.core.reports) {
      if (b.hidden) {
        out.push(reportFact(b));
      }
    }
    return out;
  }

  async hide(id: string): Promise<void> {
    this.requireModerator();
    const b = this.core.findReport(id);
    if (b !== null) {
      b.hidden = true;
      this.core.save();
    }
  }

  async restore(id: string): Promise<void> {
    this.requireModerator();
    const b = this.core.findReport(id);
    if (b !== null) {
      b.hidden = false;
      this.core.save();
    }
  }
}

/** Repository that runs entirely on the device; it stands in for the team's API until that is connected. */
export class LocalRepository implements Repository {
  core: LocalCore = new LocalCore();
  facts: FactsRepository = new LocalFacts(this.core);
  routing: RoutingRepository = new LocalRouting(this.core);
  geocoding: GeocodingRepository = new LocalGeocoding(this.core);
  accounts: AccountRepository = new LocalAccounts(this.core);
  moderation: ModerationRepository = new LocalModeration(this.core);
}
