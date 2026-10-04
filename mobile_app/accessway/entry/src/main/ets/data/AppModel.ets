import { common } from '@kit.AbilityKit';
import { i18n } from '@kit.LocalizationKit';
import { copyNeeds, emptyNeeds, Needs } from '../domain/Needs';
import { Dataset } from '../domain/OsmMapping';
import { getLang, Lang, langFromSystem, setLang, tr } from '../model/I18n';
import { Fact } from '../model/Types';
import { readApiSettings } from './ApiConfig';
import { tileStore } from './Tiles';
import { ApiRepository } from './ApiRepository';
import { LocalRepository } from './LocalRepository';
import { Account, Area, DataInfo, RepoError, Repository, RoutePlan } from './Repository';
import { readFileText, writeFileText } from './Storage';

const PREFS_FILE: string = 'ui_prefs.json';

/** Product name in the app header and on the start screen. */
export const PRODUCT_NAME: string = 'EnableMe';

interface Prefs {
  lang?: string;
  needs: Needs;
  needsDone: boolean;
}

export interface Endpoint {
  lat: number;
  lon: number;
  label: string;
}

export enum ListFilter {
  NEEDS = 'needs',
  ALL = 'all'
}

/** Error message from the repository in the current language. */
export function errorText(e: Object): string {
  if (e instanceof RepoError) {
    return e.message;
  }
  if (e instanceof Error) {
    return e.message;
  }
  return tr('Coś poszło nie tak.', 'Something went wrong.');
}

/**
 * UI state: needs and language (only on the device), route points, the latest plan and facts. It gets data
 * only through the Repository interface, so swapping LocalRepository for the API client leaves the screens as is.
 * The base map (streets, buildings, greenery) comes from data bundled with the app.
 */
export class AppModel {
  ctx: common.Context | null = null;
  local: LocalRepository = new LocalRepository();
  repo: Repository = this.local;
  ready: boolean = false;
  loadError: string = '';
  needs: Needs = emptyNeeds();
  needsDone: boolean = false;
  langChosen: boolean = false;
  facts: Fact[] = [];
  factsTruncated: boolean = false;
  apiBaseUrl: string = '';
  account: Account | null = null;
  start: Endpoint | null = null;
  dest: Endpoint | null = null;
  plan: RoutePlan | null = null;
  planError: string = '';
  avoidFactIds: string[] = [];
  listFilter: ListFilter = ListFilter.NEEDS;
  mapLat: number = 0;
  mapLon: number = 0;
  mapScale: number = 0;
  fitBox: number[] = [];

  init(ctx: common.Context): void {
    this.ctx = ctx;
    try {
      setLang(langFromSystem(i18n.System.getSystemLanguage()));
    } catch (e) {
      setLang(Lang.PL);
    }
    this.loadPrefs();
    this.local.core.init(ctx);
    const api = readApiSettings(ctx);
    this.apiBaseUrl = api.base_url;
    tileStore.configure(api.tiles_url ?? '');
    if (api.base_url.length > 0) {
      this.repo = new ApiRepository(ctx, api);
    }
    this.loadError = this.local.core.loadError;
    this.ready = this.loadError.length === 0;
    if (this.ready) {
      const ds = this.mapBase();
      this.fitTo((ds.minLat + ds.maxLat) / 2, (ds.minLon + ds.maxLon) / 2, 260);
    }
  }

  mapBase(): Dataset {
    return this.local.core.ds;
  }

  info(): DataInfo {
    return this.repo.facts.info();
  }

  private prefsPath(): string {
    return `${(this.ctx as common.Context).filesDir}/${PREFS_FILE}`;
  }

  private loadPrefs(): void {
    const raw = readFileText(this.prefsPath());
    if (raw === null) {
      return;
    }
    try {
      const p = JSON.parse(raw) as Prefs;
      this.needs = copyNeeds(p.needs);
      this.needsDone = p.needsDone;
      if (p.lang === Lang.PL || p.lang === Lang.EN) {
        setLang(p.lang as Lang);
        this.langChosen = true;
      }
    } catch (e) {
      this.needs = emptyNeeds();
    }
  }

  savePrefs(): void {
    if (this.ctx === null) {
      return;
    }
    const p: Prefs = { lang: this.langChosen ? getLang() : undefined, needs: this.needs, needsDone: this.needsDone };
    try {
      writeFileText(this.prefsPath(), JSON.stringify(p));
    } catch (e) {
      this.loadError = tr('Nie udało się zapisać ustawień na urządzeniu', 'Could not save the settings on the device');
    }
  }

  setLang(l: Lang): void {
    setLang(l);
    this.langChosen = true;
    this.savePrefs();
  }

  setNeeds(n: Needs): void {
    this.needs = copyNeeds(n);
    this.savePrefs();
  }

  usesApi(): boolean {
    return this.apiBaseUrl.length > 0;
  }

  /** Rectangle around the map center, at least 1.5 km in each direction, from which we fetch facts. */
  factsArea(): Area {
    const ds = this.mapBase();
    let lat = this.mapLat;
    let lon = this.mapLon;
    if (this.mapScale <= 0 || (lat === 0 && lon === 0)) {
      lat = (ds.minLat + ds.maxLat) / 2;
      lon = (ds.minLon + ds.maxLon) / 2;
    }
    const spanPx = 400;
    const halfM = Math.max(1500, this.mapScale > 0 ? spanPx / this.mapScale : 1500);
    const dLat = halfM / 111320;
    const dLon = halfM / (111320 * Math.cos(lat * Math.PI / 180));
    return { south: lat - dLat, west: lon - dLon, north: lat + dLat, east: lon + dLon };
  }

  async refreshFacts(): Promise<void> {
    const page = await this.repo.facts.listFacts(this.factsArea());
    this.facts = page.facts;
    this.factsTruncated = page.truncated;
  }

  async refreshInfo(): Promise<void> {
    await this.repo.facts.refreshInfo();
  }

  accountName(): string {
    return this.account !== null ? (this.account as Account).pseudonym : '';
  }

  isModerator(): boolean {
    return this.account !== null && (this.account as Account).moderator;
  }

  async refreshAccount(): Promise<void> {
    this.account = await this.repo.accounts.current();
  }

  /** Computes the route for the current needs; a service error stays in `planError` and the old plan is cleared. */
  async computeRoute(): Promise<boolean> {
    if (this.start === null || this.dest === null) {
      return false;
    }
    this.planError = '';
    try {
      this.plan = await this.repo.routing.route({
        from: { lat: this.start.lat, lon: this.start.lon },
        to: { lat: this.dest.lat, lon: this.dest.lon },
        needs: this.needs,
        avoidFactIds: this.avoidFactIds
      });
      this.fitBox = [this.plan.minLat, this.plan.maxLat, this.plan.minLon, this.plan.maxLon];
      return true;
    } catch (e) {
      this.plan = null;
      this.planError = errorText(e as Object);
      return false;
    }
  }

  fitTo(lat: number, lon: number, spanM: number): void {
    const dLat = spanM / 111320;
    const dLon = spanM / (111320 * Math.cos(lat * Math.PI / 180));
    this.fitBox = [lat - dLat, lat + dLat, lon - dLon, lon + dLon];
  }

  factById(id: string): Fact | null {
    for (const f of this.facts) {
      if (f.id === id) {
        return f;
      }
    }
    if (this.plan !== null) {
      for (const it of this.plan.facts) {
        if (it.fact.id === id) {
          return it.fact;
        }
      }
    }
    return null;
  }

  /** Distance of the fact from the route start if it lies on the current route, or -1. */
  routePosition(id: string): number {
    if (this.plan === null) {
      return -1;
    }
    for (const it of this.plan.facts) {
      if (it.fact.id === id) {
        return it.atM;
      }
    }
    return -1;
  }
}

export const appModel: AppModel = new AppModel();
