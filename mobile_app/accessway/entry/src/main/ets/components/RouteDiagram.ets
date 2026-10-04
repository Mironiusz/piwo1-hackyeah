import { RouteSegment } from '../data/Repository';
import { EdgeState } from '../model/Types';
import { FONT_B, fs, P } from './Theme';

export interface DiagramStop {
  atM: number;
  label: string;
}

/**
 * Schemat trasy z nagłówka wyniku: wyprostowana linia w stanach odcinków, przystanek dla każdej bariery
 * z potrzeb i nazwy startu i celu pod końcami. Trasa bez oceny to granatowy kontur z białym środkiem.
 */
@Component
export struct RouteDiagram {
  segments: RouteSegment[] = [];
  stops: DiagramStop[] = [];
  totalM: number = 1;
  rated: boolean = true;
  startName: string = '';
  endName: string = '';
  private settings: RenderingContextSettings = new RenderingContextSettings(true);
  private ctx: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.settings);

  private fill(c: CanvasRenderingContext2D, s: EdgeState, x0: number, x1: number, y: number, h: number): void {
    const pal = P();
    if (s === EdgeState.CLEAR) {
      c.fillStyle = pal.clear;
      c.fillRect(x0, y, x1 - x0, h);
      return;
    }
    if (s === EdgeState.BARRIER) {
      c.fillStyle = pal.barrier;
      for (let x = x0; x < x1; x += 6) {
        c.fillRect(x, y, Math.min(3.6, x1 - x), h);
      }
      return;
    }
    if (s === EdgeState.PARTIAL) {
      c.fillStyle = pal.partialLine;
      c.fillRect(x0, y, x1 - x0, h);
      c.fillStyle = pal.text;
      for (let x = x0 + 1; x < x1; x += 9) {
        c.fillRect(x, y + h / 2 - 1, Math.min(5, x1 - x), 2);
      }
      return;
    }
    c.fillStyle = pal.noData;
    for (let x = x0 + 1; x < x1; x += 8) {
      c.fillRect(x, y + 1, Math.min(3.5, x1 - x), h - 2);
    }
  }

  private stop(c: CanvasRenderingContext2D, x: number, y: number): void {
    c.beginPath();
    c.arc(x, y, 6.5, 0, Math.PI * 2);
    c.fillStyle = '#FFFFFF';
    c.fill();
    c.lineWidth = 2.6;
    c.strokeStyle = P().text;
    c.stroke();
  }

  private draw(): void {
    const c = this.ctx;
    const w = c.width;
    if (w <= 0) {
      return;
    }
    c.clearRect(0, 0, w, c.height);
    const x0 = 9;
    const x1 = w - 9;
    const y = 28;
    const h = 8;
    const total = Math.max(1, this.totalM);
    if (!this.rated) {
      c.beginPath();
      c.moveTo(x0, y);
      c.lineTo(x1, y);
      c.lineCap = 'round';
      c.strokeStyle = P().primary;
      c.lineWidth = 8;
      c.stroke();
      c.strokeStyle = '#FFFFFF';
      c.lineWidth = 4;
      c.stroke();
    } else {
      for (const s of this.segments) {
        const a = x0 + (x1 - x0) * s.fromM / total;
        const b = x0 + (x1 - x0) * Math.min(total, s.toM) / total;
        if (b - a >= 0.5) {
          this.fill(c, s.state, a, b, y - h / 2, h);
        }
      }
    }
    this.stop(c, x0, y);
    this.stop(c, x1, y);
    c.font = `${fs(12)}vp sans-serif`;
    c.textAlign = 'center';
    for (const st of this.stops) {
      const x = Math.max(x0 + 22, Math.min(x1 - 22, x0 + (x1 - x0) * st.atM / total));
      this.stop(c, x, y);
      c.fillStyle = P().text;
      c.fillText(st.label, x, y - 13);
    }
    c.textAlign = 'left';
  }

  build() {
    Column({ space: 2 }) {
      Canvas(this.ctx)
        .width('100%')
        .height(40)
        .accessibilityLevel('no')
        .onReady(() => this.draw())
        .onAreaChange(() => this.draw())
      Row() {
        Text(this.startName).fontFamily(FONT_B).fontSize(fs(13)).fontColor(P().text).maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis }).layoutWeight(1)
        Text(this.endName).fontFamily(FONT_B).fontSize(fs(13)).fontColor(P().text).maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis }).layoutWeight(1).textAlign(TextAlign.End)
      }
      .width('100%')
    }
    .width('100%')
  }
}
