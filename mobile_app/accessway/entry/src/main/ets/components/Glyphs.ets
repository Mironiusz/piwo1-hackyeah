import { FactCategory, FactKind } from '../model/Types';

/**
 * Liniowe znaki rodzajów faktów z makiet, rysowane na Canvas w polu 24 x 24 przeskalowanym do `size`.
 * Ten sam rysunek służy w wierszach list, w zgłaszaniu i w znacznikach na mapie.
 */
export function drawKind(c: CanvasRenderingContext2D, kind: FactKind, category: FactCategory, cx: number, cy: number,
  size: number, color: string): void {
  const k = size / 24;
  const x = (v: number): number => cx + (v - 12) * k;
  const y = (v: number): number => cy + (v - 12) * k;
  c.save();
  c.strokeStyle = color;
  c.fillStyle = color;
  c.lineWidth = Math.max(1.4, 2 * k);
  c.lineCap = 'round';
  c.lineJoin = 'round';
  c.setLineDash([]);
  const poly = (pts: number[]): void => {
    c.beginPath();
    c.moveTo(x(pts[0]), y(pts[1]));
    for (let i = 2; i < pts.length; i += 2) {
      c.lineTo(x(pts[i]), y(pts[i + 1]));
    }
    c.stroke();
  };
  if (category === FactCategory.AREA) {
    c.beginPath();
    c.arc(cx, cy, 8 * k, 0, Math.PI * 2);
    c.stroke();
    c.beginPath();
    c.arc(cx, cy, 2.6 * k, 0, Math.PI * 2);
    c.fill();
    c.restore();
    return;
  }
  if (kind === FactKind.STEPS) {
    poly([4, 19, 9, 19, 9, 14, 14, 14, 14, 9, 19, 9, 19, 5]);
  } else if (kind === FactKind.KERB) {
    poly([3, 16, 11, 16, 11, 9, 21, 9]);
  } else if (kind === FactKind.ROUGH_SURFACE) {
    c.beginPath();
    c.moveTo(x(3), y(12));
    c.quadraticCurveTo(x(5.5), y(8), x(8), y(12));
    c.quadraticCurveTo(x(10.5), y(16), x(13), y(12));
    c.quadraticCurveTo(x(15.5), y(8), x(18), y(12));
    c.quadraticCurveTo(x(19.5), y(14.4), x(21), y(13));
    c.stroke();
    poly([3, 17.5, 21, 17.5]);
  } else if (kind === FactKind.STEEP_SLOPE) {
    poly([3, 18, 21, 18, 21, 7, 3, 18]);
  } else if (kind === FactKind.NARROW_PASSAGE) {
    poly([9, 5, 9, 19]);
    poly([15, 5, 15, 19]);
    poly([3, 12, 6.5, 12]);
    poly([17.5, 12, 21, 12]);
  } else if (kind === FactKind.ELEVATOR) {
    c.beginPath();
    c.rect(x(5.5), y(3.5), 13 * k, 17 * k);
    c.stroke();
    poly([9, 10, 12, 7, 15, 10]);
    poly([9, 14, 12, 17, 15, 14]);
  } else if (kind === FactKind.RAMP) {
    poly([3, 18, 21, 18, 21, 12, 3, 18]);
  } else if (kind === FactKind.LOWERED_KERB) {
    c.beginPath();
    c.moveTo(x(3), y(9));
    c.lineTo(x(8), y(9));
    c.bezierCurveTo(x(11), y(9), x(12), y(15), x(15), y(15));
    c.lineTo(x(21), y(15));
    c.stroke();
  } else if (kind === FactKind.ACCESSIBLE_TOILET) {
    poly([6, 4, 6, 13]);
    c.beginPath();
    c.moveTo(x(4), y(11));
    c.lineTo(x(20), y(11));
    c.bezierCurveTo(x(20), y(16), x(16), y(18), x(12), y(18));
    c.bezierCurveTo(x(8), y(18), x(5), y(16), x(4), y(11));
    c.stroke();
    poly([10, 18, 10, 21, 15, 21, 15, 18]);
  } else if (kind === FactKind.REST_SPOT) {
    poly([4, 7, 20, 7]);
    poly([4, 12, 20, 12]);
    poly([6, 12, 6, 18]);
    poly([18, 12, 18, 18]);
  } else {
    poly([4, 20, 8, 20, 8, 16, 12, 16, 12, 12, 16, 12, 16, 8, 20, 8]);
    poly([3, 12, 19, 3]);
  }
  c.restore();
}

/** Znak rodzaju jako mały element interfejsu, na przykład w wierszu listy. */
@Component
export struct KindIcon {
  kind: FactKind = FactKind.STEPS;
  category: FactCategory = FactCategory.BARRIER;
  iconSize: number = 22;
  color: string = '#111418';
  private settings: RenderingContextSettings = new RenderingContextSettings(true);
  private ctx: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.settings);

  build() {
    Canvas(this.ctx)
      .width(this.iconSize)
      .height(this.iconSize)
      .accessibilityLevel('no')
      .onReady(() => {
        this.ctx.clearRect(0, 0, this.iconSize, this.iconSize);
        drawKind(this.ctx, this.kind, this.category, this.iconSize / 2, this.iconSize / 2, this.iconSize, this.color);
      })
  }
}
