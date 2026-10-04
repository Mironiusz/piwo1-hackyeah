import { KeyCode } from '@kit.InputKit';
import { appModel } from '../data/AppModel';
import { latToTileY, lonToTileX, TileData, tileStore, tileXToLon, tileYToLat } from '../data/Tiles';
import { RouteSegment } from '../data/Repository';
import { tr } from '../model/I18n';
import { factTitle, isAmenity, streetLabel } from '../model/Labels';
import { EdgeState, Fact, FactCategory } from '../model/Types';
import { drawKind } from './Glyphs';
import { edgeStyle, FONT_B, FONT, fs, LineStyle, P, RADIUS_CTRL } from './Theme';
import { Icon } from './Ui';

const M_PER_DEG: number = 111320;
const MARKER: number = 26;
const WATER: string = '#CFDDE6';
const MAX_TILES: number = 36;
const BASE_MARGIN: number = 0.4;

export enum MapMode {
  PLAIN = 'plain',
  PICK = 'pick'
}

/**
 * Mapa z makiet rysowana na Canvas: beżowe tło, budynki, zieleń, białe ulice z podpisami, trasa w stanach,
 * kwadratowe znaczniki faktów i punkty A i B. W trybie wskazywania punktu środek mapy oznacza krzyżyk,
 * a mapę przesuwa się palcem albo strzałkami na klawiaturze.
 */
@Component
export struct MapCanvas {
  mapHeight: number = 250;
  mode: MapMode = MapMode.PLAIN;
  facts: Fact[] = [];
  selectedId: string = '';
  showRoute: boolean = false;
  showA: boolean = false;
  showB: boolean = false;
  pointLat: number = NaN;
  pointLon: number = NaN;
  pointRadiusM: number = 0;
  areaRadiusM: number = 0;
  showLocate: boolean = false;
  onFactTap: (id: string) => void = () => {
  };
  onMoved: () => void = () => {
  };
  onLocate: () => void = () => {
  };
  private settings: RenderingContextSettings = new RenderingContextSettings(true);
  private ctx: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.settings);
  private panLat: number = 0;
  private panLon: number = 0;
  private pinchScale: number = 1;
  private ready: boolean = false;
  private pinching: boolean = false;
  private base: ImageBitmap | null = null;
  private baseLon: number = 0;
  private baseLat: number = 0;
  private baseKx: number = 1;
  private baseKy: number = 1;
  private baseW: number = 0;
  private baseH: number = 0;
  private baseVersion: number = -1;
  private basePal: string = '';

  aboutToDisappear(): void {
    this.ready = false;
    this.dropBase();
  }

  private kx(): number {
    return M_PER_DEG * Math.cos(appModel.mapLat * Math.PI / 180) * appModel.mapScale;
  }

  private ky(): number {
    return M_PER_DEG * appModel.mapScale;
  }

  private applyFit(w: number, h: number): void {
    const f = appModel.fitBox;
    if (f.length === 4) {
      appModel.mapLat = (f[0] + f[1]) / 2;
      appModel.mapLon = (f[2] + f[3]) / 2;
      const mw = (f[3] - f[2]) * M_PER_DEG * Math.cos(appModel.mapLat * Math.PI / 180);
      const mh = (f[1] - f[0]) * M_PER_DEG;
      appModel.mapScale = Math.min(w / Math.max(mw, 60), h / Math.max(mh, 60)) * 0.84;
      appModel.fitBox = [];
      return;
    }
    if (appModel.mapScale <= 0) {
      const ds = appModel.mapBase();
      appModel.mapLat = (ds.minLat + ds.maxLat) / 2;
      appModel.mapLon = (ds.minLon + ds.maxLon) / 2;
      const mw = (ds.maxLon - ds.minLon) * M_PER_DEG * Math.cos(appModel.mapLat * Math.PI / 180);
      const mh = (ds.maxLat - ds.minLat) * M_PER_DEG;
      appModel.mapScale = Math.min(w / Math.max(mw, 60), h / Math.max(mh, 60)) * 0.9;
    }
  }

  private strokeStyle(c: CanvasRenderingContext2D, st: LineStyle): void {
    c.strokeStyle = st.color;
    c.lineWidth = st.width;
    c.setLineDash(st.dash);
    c.stroke();
    if (st.overWidth > 0) {
      c.strokeStyle = st.overColor;
      c.lineWidth = st.overWidth;
      c.setLineDash(st.overDash);
      c.stroke();
    }
    c.setLineDash([]);
  }

  draw(): void {
    if (!this.ready || !appModel.ready) {
      return;
    }
    const c = this.ctx;
    const w = c.width;
    const h = c.height;
    if (w <= 0 || h <= 0) {
      return;
    }
    this.applyFit(w, h);
    const pal = P();
    const ds = appModel.mapBase();
    const kx = this.kx();
    const ky = this.ky();
    const cx = w / 2 - appModel.mapLon * kx;
    const cy = h / 2 + appModel.mapLat * ky;
    const X = (lon: number): number => cx + lon * kx;
    const Y = (lat: number): number => cy - lat * ky;
    const latSpan = h / ky / 2 + 0.001;
    const lonSpan = w / kx / 2 + 0.001;
    const minLat = appModel.mapLat - latSpan;
    const maxLat = appModel.mapLat + latSpan;
    const minLon = appModel.mapLon - lonSpan;
    const maxLon = appModel.mapLon + lonSpan;

    c.clearRect(0, 0, w, h);
    c.fillStyle = pal.mapBg;
    c.fillRect(0, 0, w, h);

    if (!(tileStore.ready && this.drawTiles(c, w, h, kx, ky, X, Y, minLat, maxLat, minLon, maxLon))) {
      for (const a of ds.areas) {
        c.beginPath();
        c.moveTo(X(a.pts[1]), Y(a.pts[0]));
        for (let i = 2; i < a.pts.length; i += 2) {
          c.lineTo(X(a.pts[i + 1]), Y(a.pts[i]));
        }
        c.closePath();
        c.fillStyle = a.kind === 'green' ? pal.mapGreen : pal.mapBuilding;
        c.fill();
      }

      const streetW = Math.max(6, Math.min(14, 4 + appModel.mapScale * 9));
      c.beginPath();
      for (const e of ds.edges) {
        const a = ds.nodes[e.a];
        const b = ds.nodes[e.b];
        if ((a.lat < minLat && b.lat < minLat) || (a.lat > maxLat && b.lat > maxLat) ||
          (a.lon < minLon && b.lon < minLon) || (a.lon > maxLon && b.lon > maxLon)) {
          continue;
        }
        c.moveTo(X(a.lon), Y(a.lat));
        c.lineTo(X(b.lon), Y(b.lat));
      }
      c.strokeStyle = pal.mapStreet;
      c.lineWidth = streetW;
      c.lineCap = 'round';
      c.lineJoin = 'round';
      c.stroke();
      this.drawLabels(c, X, Y, minLat, maxLat, minLon, maxLon);
    }

    if (this.showRoute && appModel.plan !== null) {
      this.drawRoute(c, X, Y);
    }
    for (const f of this.facts) {
      if (f.category === FactCategory.AREA) {
        this.drawArea(c, X(f.lon), Y(f.lat), f.radiusM, f.id === this.selectedId);
      }
    }
    for (const f of this.facts) {
      if (f.category !== FactCategory.AREA) {
        this.drawMarker(c, f, X(f.lon), Y(f.lat));
      }
    }
    if (this.showA && appModel.start !== null) {
      this.drawPin(c, X(appModel.start.lon), Y(appModel.start.lat), 'A');
    }
    if (this.showB && appModel.dest !== null) {
      this.drawPin(c, X(appModel.dest.lon), Y(appModel.dest.lat), 'B');
    }
    if (!isNaN(this.pointLat)) {
      const px = X(this.pointLon);
      const py = Y(this.pointLat);
      if (this.areaRadiusM > 0) {
        this.drawArea(c, px, py, this.areaRadiusM, false);
      }
      if (this.pointRadiusM > 0) {
        c.beginPath();
        c.arc(px, py, Math.max(14, this.pointRadiusM * appModel.mapScale), 0, Math.PI * 2);
        c.strokeStyle = pal.text;
        c.lineWidth = 1.6;
        c.setLineDash([4, 3]);
        c.stroke();
        c.setLineDash([]);
      }
      this.drawPoint(c, px, py);
    }
    if (this.mode === MapMode.PICK) {
      this.drawCrosshair(c, w / 2, h / 2);
    }
  }

  /** Wszystkie części jednej klasy ze wszystkich kafelków jako jedna ścieżka, w punktach bitmapy podkładu. */
  private tileParts(c: CanvasRenderer, tiles: TileData[], pick: (t: TileData) => number[][], close: boolean,
    bx: (lon: number) => number, by: (lat: number) => number): boolean {
    let any = false;
    c.beginPath();
    for (const t of tiles) {
      const parts = pick(t);
      if (parts === undefined || parts.length === 0) {
        continue;
      }
      const ox = bx(tileXToLon(t.x, t.z));
      const oy = by(tileYToLat(t.y, t.z));
      const ext = t.extent > 0 ? t.extent : 512;
      const sx = (bx(tileXToLon(t.x + 1, t.z)) - ox) / ext;
      const sy = (by(tileYToLat(t.y + 1, t.z)) - oy) / ext;
      for (const part of parts) {
        c.moveTo(ox + part[0] * sx, oy + part[1] * sy);
        for (let i = 2; i < part.length; i += 2) {
          c.lineTo(ox + part[i] * sx, oy + part[i + 1] * sy);
        }
        if (close) {
          c.closePath();
        }
        any = true;
      }
    }
    return any;
  }

  private fillClass(c: CanvasRenderer, tiles: TileData[], pick: (t: TileData) => number[][], color: string,
    bx: (lon: number) => number, by: (lat: number) => number): void {
    if (this.tileParts(c, tiles, pick, true, bx, by)) {
      c.fillStyle = color;
      c.fill();
    }
  }

  private strokeClass(c: CanvasRenderer, tiles: TileData[], pick: (t: TileData) => number[][], width: number,
    color: string, bx: (lon: number) => number, by: (lat: number) => number): void {
    if (this.tileParts(c, tiles, pick, false, bx, by)) {
      c.strokeStyle = color;
      c.lineWidth = width;
      c.lineCap = 'round';
      c.lineJoin = 'round';
      c.stroke();
    }
  }

  /** Kafelki potrzebne do pokrycia prostokąta; brakujący zastępuje kafelek nadrzędny z pamięci. */
  private collectTiles(z: number, minLat: number, maxLat: number, minLon: number, maxLon: number): TileData[] | null {
    const x0 = lonToTileX(minLon, z);
    const x1 = lonToTileX(maxLon, z);
    const y0 = latToTileY(maxLat, z);
    const y1 = latToTileY(minLat, z);
    if ((x1 - x0 + 1) * (y1 - y0 + 1) > MAX_TILES) {
      return null;
    }
    const tiles: TileData[] = [];
    const seen: Set<string> = new Set<string>();
    for (let x = x0; x <= x1; x++) {
      for (let y = y0; y <= y1; y++) {
        let t = tileStore.want(z, x, y);
        let pz = z;
        let px = x;
        let py = y;
        while (t === null && pz > tileStore.minZoom && z - pz < 4) {
          pz--;
          px = Math.floor(px / 2);
          py = Math.floor(py / 2);
          t = tileStore.peek(pz, px, py);
        }
        if (t !== null && !seen.has(`${t.z}/${t.x}/${t.y}`)) {
          seen.add(`${t.z}/${t.x}/${t.y}`);
          tiles.push(t);
        }
      }
    }
    return tiles;
  }

  private dropBase(): void {
    if (this.base !== null) {
      this.base.close();
      this.base = null;
    }
  }

  /**
   * Rysuje podkład z kafelków raz do bitmapy większej od ekranu o margines. Przesuwanie i szczypanie mapy tylko
   * przesuwa i skaluje tę bitmapę, więc koszt ruchu nie zależy od liczby ulic i budynków na ekranie. Zwraca false,
   * gdy nie ma jeszcze żadnego kafelka albo widok obejmuje zbyt wiele kafelków.
   */
  private renderBase(w: number, h: number, kx: number, ky: number, palKey: string): boolean {
    const mx = Math.round(w * BASE_MARGIN);
    const my = Math.round(h * BASE_MARGIN);
    const bw = Math.round(w + 2 * mx);
    const bh = Math.round(h + 2 * my);
    const lon0 = appModel.mapLon - (w / 2 + mx) / kx;
    const lat0 = appModel.mapLat + (h / 2 + my) / ky;
    const lon1 = lon0 + bw / kx;
    const lat1 = lat0 - bh / ky;
    const z = tileStore.zoomFor(appModel.mapScale, appModel.mapLat);
    const tiles = this.collectTiles(z, lat1, lat0, lon0, lon1);
    if (tiles === null || tiles.length === 0) {
      return false;
    }
    tiles.sort((a: TileData, b: TileData) => a.z - b.z);
    const bx = (lon: number): number => (lon - lon0) * kx;
    const by = (lat: number): number => (lat0 - lat) * ky;
    const off = new OffscreenCanvas(bw, bh);
    const c = off.getContext('2d', this.settings);
    const pal = P();
    c.fillStyle = pal.mapBg;
    c.fillRect(0, 0, bw, bh);
    this.fillClass(c, tiles, (t: TileData) => t.fills.green, pal.mapGreen, bx, by);
    this.fillClass(c, tiles, (t: TileData) => t.fills.water, WATER, bx, by);
    if (z >= 14) {
      this.fillClass(c, tiles, (t: TileData) => t.fills.building, pal.mapBuilding, bx, by);
    }
    const s = appModel.mapScale;
    const sw = s >= 0.6 ? Math.min(14, 4 + 9 * s) : Math.max(1.5, 9.4 * s / 0.6);
    this.strokeClass(c, tiles, (t: TileData) => t.lines.path, Math.max(1, sw * 0.4), pal.mapStreet, bx, by);
    this.strokeClass(c, tiles, (t: TileData) => t.lines.minor, sw * 0.8, pal.mapStreet, bx, by);
    this.strokeClass(c, tiles, (t: TileData) => t.lines.major, sw * 1.15, pal.mapStreet, bx, by);
    if (sw >= 5) {
      this.tileLabels(c, tiles, bx, by, bw, bh);
    }
    this.dropBase();
    this.base = off.transferToImageBitmap();
    this.baseLon = lon0;
    this.baseLat = lat0;
    this.baseKx = kx;
    this.baseKy = ky;
    this.baseW = bw;
    this.baseH = bh;
    this.baseVersion = tileStore.version;
    this.basePal = palKey;
    return true;
  }

  /** Podkład z kafelków na ekranie; bitmapę rysuje od nowa tylko wtedy, gdy obecna przestała wystarczać. */
  private drawTiles(c: CanvasRenderingContext2D, w: number, h: number, kx: number, ky: number,
    X: (lon: number) => number, Y: (lat: number) => number, minLat: number, maxLat: number, minLon: number,
    maxLon: number): boolean {
    const pal = P();
    const palKey = `${pal.mapBg}${pal.mapStreet}`;
    let need = this.base === null || this.basePal !== palKey;
    if (!need) {
      const r = ky / this.baseKy;
      const lo = this.pinching ? 0.5 : 0.8;
      const hi = this.pinching ? 2 : 1.25;
      const covers = minLon >= this.baseLon && maxLon <= this.baseLon + this.baseW / this.baseKx &&
        maxLat <= this.baseLat && minLat >= this.baseLat - this.baseH / this.baseKy;
      need = r < lo || r > hi || !covers || (this.baseVersion !== tileStore.version && !this.pinching);
    }
    if (need && !this.renderBase(w, h, kx, ky, palKey)) {
      this.dropBase();
      return false;
    }
    const base = this.base;
    if (base === null) {
      return false;
    }
    c.drawImage(base, X(this.baseLon), Y(this.baseLat), this.baseW * kx / this.baseKx, this.baseH * ky / this.baseKy);
    return true;
  }

  private tileLabels(c: CanvasRenderer, tiles: TileData[], bx: (lon: number) => number, by: (lat: number) => number,
    bw: number, bh: number): void {
    const best: Map<string, number[]> = new Map<string, number[]>();
    for (const t of tiles) {
      if (t.labels === undefined || t.labels.length === 0) {
        continue;
      }
      const ox = bx(tileXToLon(t.x, t.z));
      const oy = by(tileYToLat(t.y, t.z));
      const ext = t.extent > 0 ? t.extent : 512;
      const sx = (bx(tileXToLon(t.x + 1, t.z)) - ox) / ext;
      const sy = (by(tileYToLat(t.y + 1, t.z)) - oy) / ext;
      for (const lb of t.labels) {
        for (const part of lb.geom) {
          for (let i = 2; i < part.length; i += 2) {
            const ax = ox + part[i - 2] * sx;
            const ay = oy + part[i - 1] * sy;
            const qx = ox + part[i] * sx;
            const qy = oy + part[i + 1] * sy;
            const mx = (ax + qx) / 2;
            const my = (ay + qy) / 2;
            if (mx < 0 || my < 0 || mx > bw || my > bh) {
              continue;
            }
            const len = Math.sqrt((qx - ax) * (qx - ax) + (qy - ay) * (qy - ay));
            const prev = best.get(lb.name);
            if (prev === undefined || prev[4] < len) {
              best.set(lb.name, [ax, ay, qx, qy, len]);
            }
          }
        }
      }
    }
    c.font = `${fs(11)}vp sans-serif`;
    c.fillStyle = P().mapLabel;
    c.textAlign = 'center';
    best.forEach((v: number[], name: string) => {
      this.streetLabelAt(c, streetLabel(name), v[0], v[1], v[2], v[3]);
    });
    c.textAlign = 'left';
  }

  private streetLabelAt(c: CanvasRenderer, label: string, ax0: number, ay0: number, bx0: number,
    by0: number): void {
    let ax = ax0;
    let ay = ay0;
    let bx = bx0;
    let by = by0;
    if (bx < ax) {
      ax = bx0;
      ay = by0;
      bx = ax0;
      by = ay0;
    }
    const len = Math.sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay));
    if (len < c.measureText(label).width + 24) {
      return;
    }
    c.save();
    c.translate((ax + bx) / 2, (ay + by) / 2);
    c.rotate(Math.atan2(by - ay, bx - ax));
    c.fillText(label, 0, -9);
    c.restore();
  }

  private drawLabels(c: CanvasRenderingContext2D, X: (lon: number) => number, Y: (lat: number) => number,
    minLat: number, maxLat: number, minLon: number, maxLon: number): void {
    const ds = appModel.mapBase();
    const best: Map<string, number> = new Map<string, number>();
    for (const e of ds.edges) {
      if (e.name.length === 0 || e.highway === 'steps') {
        continue;
      }
      const a = ds.nodes[e.a];
      const b = ds.nodes[e.b];
      const mLat = (a.lat + b.lat) / 2;
      const mLon = (a.lon + b.lon) / 2;
      if (mLat < minLat || mLat > maxLat || mLon < minLon || mLon > maxLon) {
        continue;
      }
      const prev = best.get(e.name);
      if (prev === undefined || ds.edges[prev].lengthM < e.lengthM) {
        best.set(e.name, e.index);
      }
    }
    c.font = `${fs(11)}vp sans-serif`;
    c.fillStyle = P().mapLabel;
    c.textAlign = 'center';
    best.forEach((ei: number, name: string) => {
      const e = ds.edges[ei];
      const a = ds.nodes[e.a];
      const b = ds.nodes[e.b];
      let ax = X(a.lon);
      let ay = Y(a.lat);
      let bx = X(b.lon);
      let by = Y(b.lat);
      if (bx < ax) {
        const tx = ax;
        const ty = ay;
        ax = bx;
        ay = by;
        bx = tx;
        by = ty;
      }
      const label = streetLabel(name);
      const len = Math.sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay));
      if (len < c.measureText(label).width + 24) {
        return;
      }
      c.save();
      c.translate((ax + bx) / 2, (ay + by) / 2);
      c.rotate(Math.atan2(by - ay, bx - ax));
      c.fillText(label, 0, -9);
      c.restore();
    });
    for (const ar of ds.areas) {
      if (ar.kind !== 'green' || ar.name.length === 0) {
        continue;
      }
      let sLat = 0;
      let sLon = 0;
      let n = 0;
      for (let i = 0; i < ar.pts.length; i += 2) {
        sLat += ar.pts[i];
        sLon += ar.pts[i + 1];
        n++;
      }
      const lx = X(sLon / n);
      const ly = Y(sLat / n);
      c.fillText(ar.name.replace(' Polskich', ''), lx, ly);
    }
    c.textAlign = 'left';
  }

  private polyline(c: CanvasRenderingContext2D, s: RouteSegment, X: (lon: number) => number,
    Y: (lat: number) => number): void {
    c.beginPath();
    c.moveTo(X(s.pts[1]), Y(s.pts[0]));
    for (let i = 2; i < s.pts.length; i += 2) {
      c.lineTo(X(s.pts[i + 1]), Y(s.pts[i]));
    }
  }

  /** Trasa: biała obwódka i stany odcinków; trasa bez oceny to granatowy kontur z białym środkiem. */
  private drawRoute(c: CanvasRenderingContext2D, X: (lon: number) => number, Y: (lat: number) => number): void {
    const plan = appModel.plan;
    if (plan === null) {
      return;
    }
    c.lineCap = 'round';
    c.lineJoin = 'round';
    if (!plan.rated) {
      for (const s of plan.segments) {
        this.polyline(c, s, X, Y);
        c.strokeStyle = P().primary;
        c.lineWidth = 8;
        c.stroke();
      }
      for (const s of plan.segments) {
        this.polyline(c, s, X, Y);
        c.strokeStyle = '#FFFFFF';
        c.lineWidth = 4;
        c.stroke();
      }
      return;
    }
    for (const s of plan.segments) {
      this.polyline(c, s, X, Y);
      c.strokeStyle = '#FFFFFF';
      c.lineWidth = 10;
      c.stroke();
    }
    c.lineCap = 'butt';
    const order: EdgeState[] = [EdgeState.CLEAR, EdgeState.PARTIAL, EdgeState.NO_DATA, EdgeState.BARRIER];
    for (const st of order) {
      for (const s of plan.segments) {
        if (s.state === st) {
          this.polyline(c, s, X, Y);
          this.strokeStyle(c, edgeStyle(st, 1));
        }
      }
    }
    c.lineCap = 'round';
  }

  private drawArea(c: CanvasRenderingContext2D, x: number, y: number, radiusM: number, selected: boolean): void {
    const r = Math.max(12, radiusM * appModel.mapScale);
    c.beginPath();
    c.arc(x, y, r, 0, Math.PI * 2);
    c.fillStyle = 'rgba(200, 50, 30, 0.18)';
    c.fill();
    c.lineWidth = selected ? 3 : 2;
    c.strokeStyle = selected ? P().text : P().barrier;
    c.setLineDash([5, 4]);
    c.stroke();
    c.setLineDash([]);
  }

  private roundRect(c: CanvasRenderingContext2D, x: number, y: number, s: number, r: number): void {
    c.beginPath();
    c.moveTo(x + r, y);
    c.lineTo(x + s - r, y);
    c.arcTo(x + s, y, x + s, y + r, r);
    c.lineTo(x + s, y + s - r);
    c.arcTo(x + s, y + s, x + s - r, y + s, r);
    c.lineTo(x + r, y + s);
    c.arcTo(x, y + s, x, y + s - r, r);
    c.lineTo(x, y + r);
    c.arcTo(x, y, x + r, y, r);
    c.closePath();
  }

  /**
   * Znaczniki z legendy makiety: bariera to czerwony kwadrat z białym znakiem, udogodnienie to biały kwadrat
   * z zieloną ramką, zgłoszenie sprzeczne z OpenStreetMap ma przerywaną czerwoną ramkę. Wybrany ma czarną obwódkę.
   */
  private drawMarker(c: CanvasRenderingContext2D, f: Fact, x: number, y: number): void {
    const pal = P();
    const s = MARKER;
    const amenity = isAmenity(f.kind);
    const conflict = f.conflictKind.length > 0;
    if (f.id === this.selectedId) {
      this.roundRect(c, x - s / 2 - 4, y - s / 2 - 4, s + 8, 8);
      c.fillStyle = pal.text;
      c.fill();
    }
    this.roundRect(c, x - s / 2, y - s / 2, s, 5);
    let fg = '#FFFFFF';
    if (amenity) {
      c.fillStyle = '#FFFFFF';
      c.fill();
      c.lineWidth = 2;
      c.strokeStyle = pal.clear;
      c.stroke();
      fg = pal.clear;
    } else if (conflict) {
      c.fillStyle = '#FFFFFF';
      c.fill();
      c.lineWidth = 2;
      c.strokeStyle = pal.barrier;
      c.setLineDash([3, 2.5]);
      c.stroke();
      c.setLineDash([]);
      fg = pal.barrier;
    } else {
      c.fillStyle = pal.barrier;
      c.fill();
    }
    drawKind(c, f.kind, f.category, x, y, 18, fg);
  }

  private drawPin(c: CanvasRenderingContext2D, x: number, y: number, label: string): void {
    c.beginPath();
    c.arc(x, y, 11, 0, Math.PI * 2);
    c.fillStyle = '#FFFFFF';
    c.fill();
    c.lineWidth = 2.5;
    c.strokeStyle = P().text;
    c.stroke();
    c.fillStyle = P().text;
    c.font = `bold ${fs(12)}vp sans-serif`;
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(label, x, y + 0.5);
    c.textAlign = 'left';
    c.textBaseline = 'alphabetic';
  }

  private drawPoint(c: CanvasRenderingContext2D, x: number, y: number): void {
    c.beginPath();
    c.arc(x, y, 10, 0, Math.PI * 2);
    c.fillStyle = '#FFFFFF';
    c.fill();
    c.lineWidth = 2.5;
    c.strokeStyle = P().text;
    c.stroke();
    c.beginPath();
    c.arc(x, y, 4.5, 0, Math.PI * 2);
    c.fillStyle = P().text;
    c.fill();
  }

  private drawCrosshair(c: CanvasRenderingContext2D, x: number, y: number): void {
    c.strokeStyle = P().primary;
    c.lineWidth = 2.5;
    c.beginPath();
    c.arc(x, y, 11, 0, Math.PI * 2);
    c.stroke();
    c.beginPath();
    c.moveTo(x - 21, y);
    c.lineTo(x - 11, y);
    c.moveTo(x + 11, y);
    c.lineTo(x + 21, y);
    c.moveTo(x, y - 21);
    c.lineTo(x, y - 11);
    c.moveTo(x, y + 11);
    c.lineTo(x, y + 21);
    c.stroke();
  }

  private hit(x: number, y: number): string {
    const kx = this.kx();
    const ky = this.ky();
    const cx = this.ctx.width / 2 - appModel.mapLon * kx;
    const cy = this.ctx.height / 2 + appModel.mapLat * ky;
    let best = '';
    let bestD = MARKER;
    for (const f of this.facts) {
      const fx = cx + f.lon * kx;
      const fy = cy - f.lat * ky;
      const d = Math.sqrt((fx - x) * (fx - x) + (fy - y) * (fy - y));
      const reach = f.category === FactCategory.AREA ? Math.max(MARKER, f.radiusM * appModel.mapScale) : MARKER;
      if (d <= reach && d < bestD + (f.category === FactCategory.AREA ? 0 : 1)) {
        bestD = d;
        best = f.id;
      }
    }
    return best;
  }

  private pan(dx: number, dy: number): void {
    appModel.mapLon -= dx / this.kx();
    appModel.mapLat += dy / this.ky();
    this.draw();
  }

  private describe(): string {
    if (this.mode === MapMode.PICK) {
      return tr('Mapa. Przesuń mapę, aż krzyżyk na środku wskaże miejsce. Strzałki przesuwają mapę.',
        'Map. Move the map until the cross in the middle points at the place. Arrow keys move the map.');
    }
    const names: string[] = [];
    for (const f of this.facts.slice(0, 6)) {
      names.push(factTitle(f.kind, f.category, f.stepCount, f.radiusM));
    }
    return tr(`Mapa. Fakty na mapie: ${this.facts.length}. ${names.join(', ')}. Ta sama informacja jest na liście poniżej.`,
      `Map. Facts on the map: ${this.facts.length}. ${names.join(', ')}. The same information is in the list below.`);
  }

  build() {
    Stack({ alignContent: Alignment.TopStart }) {
      Canvas(this.ctx)
        .width('100%')
        .height(this.mapHeight)
        .onReady(() => {
          this.ready = true;
          tileStore.onChange = () => this.draw();
          this.draw();
        })
        .onAreaChange(() => this.draw())
        .accessibilityText(this.describe())
        .focusable(this.mode === MapMode.PICK)
        .onKeyEvent((e: KeyEvent) => {
          if (e.type !== KeyType.Down) {
            return;
          }
          if (e.keyCode === KeyCode.KEYCODE_DPAD_LEFT) {
            this.pan(40, 0);
          } else if (e.keyCode === KeyCode.KEYCODE_DPAD_RIGHT) {
            this.pan(-40, 0);
          } else if (e.keyCode === KeyCode.KEYCODE_DPAD_UP) {
            this.pan(0, 40);
          } else if (e.keyCode === KeyCode.KEYCODE_DPAD_DOWN) {
            this.pan(0, -40);
          } else {
            return;
          }
          this.onMoved();
        })
        .gesture(
          GestureGroup(GestureMode.Exclusive,
            PinchGesture({ fingers: 2 })
              .onActionStart(() => {
                this.pinchScale = appModel.mapScale;
                this.pinching = true;
              })
              .onActionUpdate((e: GestureEvent) => {
                appModel.mapScale = Math.max(0.05, Math.min(8, this.pinchScale * e.scale));
                this.draw();
              })
              .onActionEnd(() => {
                this.pinching = false;
                this.draw();
                this.onMoved();
              })
              .onActionCancel(() => {
                this.pinching = false;
                this.draw();
              }),
            PanGesture({ distance: 4 })
              .onActionStart(() => {
                this.panLat = appModel.mapLat;
                this.panLon = appModel.mapLon;
              })
              .onActionUpdate((e: GestureEvent) => {
                appModel.mapLon = this.panLon - e.offsetX / this.kx();
                appModel.mapLat = this.panLat + e.offsetY / this.ky();
                this.draw();
              })
              .onActionEnd(() => this.onMoved())
          )
        )
        .onClick((e: ClickEvent) => {
          const id = this.hit(e.x, e.y);
          if (id.length > 0) {
            this.onFactTap(id);
          }
        })
      if (appModel.info().isSample && this.mode !== MapMode.PICK && this.facts.length > 0) {
        Text(tr('Dane przykładowe', 'Sample data'))
          .fontFamily(FONT_B).fontSize(fs(12)).fontColor(P().text)
          .padding({ left: 9, right: 9, top: 5, bottom: 5 })
          .backgroundColor(P().card).borderRadius(RADIUS_CTRL).border({ width: 1, color: P().outlineVar })
          .margin({ left: 10, top: 10 })
      }
      if (this.showLocate) {
        Button({ type: ButtonType.Normal }) {
          Row({ space: 6 }) {
            Icon({ name: 'crosshair', iconSize: 20, color: P().primary })
            Text(tr('Moja lokalizacja', 'My location')).fontFamily(FONT_B).fontSize(fs(13)).fontColor(P().primary)
          }
          .padding({ left: 10, right: 12 })
        }
        .height(36)
        .backgroundColor(P().card)
        .borderRadius(RADIUS_CTRL)
        .border({ width: 1.5, color: P().primary })
        .position({ right: 10, top: 10 })
        .onClick(() => this.onLocate())
      }
      Text('© OpenStreetMap contributors')
        .fontFamily(FONT).fontSize(fs(9.5)).fontColor('#3A3A3A')
        .padding({ left: 4, right: 4, top: 1, bottom: 1 })
        .backgroundColor('#D9FFFFFF').borderRadius(2)
        .position({ right: 6, bottom: 22 })
    }
    .width('100%')
    .height(this.mapHeight)
    .clip(true)
  }
}

/** Próbka linii stanu do legendy, z tym samym wzorem co na mapie. */
@Component
export struct LegendSwatch {
  state: EdgeState = EdgeState.CLEAR;
  unrated: boolean = false;
  private settings: RenderingContextSettings = new RenderingContextSettings(true);
  private ctx: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.settings);

  build() {
    Canvas(this.ctx)
      .width(this.unrated ? 36 : 28)
      .height(12)
      .accessibilityLevel('no')
      .onReady(() => {
        const c = this.ctx;
        const wd = this.unrated ? 36 : 28;
        c.clearRect(0, 0, wd, 12);
        c.beginPath();
        c.moveTo(3, 6);
        c.lineTo(wd - 3, 6);
        if (this.unrated) {
          c.lineCap = 'round';
          c.strokeStyle = P().primary;
          c.lineWidth = 8;
          c.stroke();
          c.strokeStyle = '#FFFFFF';
          c.lineWidth = 4;
          c.stroke();
          return;
        }
        c.lineCap = 'butt';
        const st = edgeStyle(this.state, 1);
        c.strokeStyle = st.color;
        c.lineWidth = st.width;
        c.setLineDash(st.dash);
        c.stroke();
        if (st.overWidth > 0) {
          c.strokeStyle = st.overColor;
          c.lineWidth = st.overWidth;
          c.setLineDash(st.overDash);
          c.stroke();
        }
      })
  }
}
