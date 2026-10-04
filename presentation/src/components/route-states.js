/**
 * A route of four segments from A to B, one per segment state of the app: a barrier from the needs, no barriers with
 * full data, partial data and no data (specification M7). Every state carries a color, an icon in a badge and the
 * line pattern the app draws it in, so the states stay apart in grayscale, the same rule the app follows.
 * Styles: `.rs-*` in `src/styles/components.css`.
 */

export const STATE_KEYS = ['barrier', 'clear', 'partial', 'nodata'];

const BEND = [0, -1, 0.6, -0.65, 0.3];

/** The geometry of the two sizes of the route. The small one has no badges. The strokes are set by the styles. */
const SIZES = {
  large: { bend: 34, end: 27, badge: 32, lift: 72, letter: 10 },
  small: { bend: 15, end: 17, badge: 0, lift: 0, letter: 7 },
};

/** The states whose pattern is a second line drawn over the first: the white stripes and the dark dashes. */
const OVERLAID = new Set(['barrier', 'partial']);

const ICONS = {
  barrier: (x, y) => `<path class="rs-icon" d="M${x - 11} ${y - 11} l22 22 M${x + 11} ${y - 11} l-22 22" />`,
  clear: (x, y) => `<path class="rs-icon" d="M${x - 14} ${y + 1} l9 10 l18 -22" />`,
  partial: (x, y) => `<path class="rs-icon-fill" d="M${x} ${y - 14} a14 14 0 0 1 0 28 z" /><circle class="rs-icon" cx="${x}" cy="${y}" r="14" />`,
  nodata: (x, y) => `<text class="rs-icon-text" x="${x}" y="${y + 14}">?</text>`,
};

/**
 * Returns the SVG markup of the route as one `<g>` placed at (x, y), `width` wide, in the size `large` or `small`.
 * Each segment is a `<g class="rs-seg is-<state>" data-state="<state>">`, so a slide can animate the segments one by one.
 */
export function routeStates({ x = 0, y = 0, width = 1200, size = 'large' } = {}) {
  const shape = SIZES[size];
  const step = width / STATE_KEYS.length;
  const points = BEND.map((factor, i) => ({ x: x + i * step, y: y + factor * shape.bend }));
  const segments = STATE_KEYS.map((state, i) => {
    const a = points[i];
    const b = points[i + 1];
    const d = `M${a.x} ${a.y} L${b.x} ${b.y}`;
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2 - shape.lift;
    const over = OVERLAID.has(state) ? `<path class="rs-over" d="${d}" />` : '';
    const badge = shape.badge ? `<circle class="rs-badge" cx="${mx}" cy="${my}" r="${shape.badge}" />${ICONS[state](mx, my)}` : '';
    return `<g class="rs-seg is-${state}" data-state="${state}">
      <path class="rs-line" d="${d}" />
      ${over}
      ${badge}
    </g>`;
  });
  const ends = [
    [points[0], 'A'],
    [points[points.length - 1], 'B'],
  ]
    .map(([p, letter]) => `<circle class="rs-end" cx="${p.x}" cy="${p.y}" r="${shape.end}" /><text class="rs-end-text" x="${p.x}" y="${p.y + shape.letter}">${letter}</text>`)
    .join('');
  return `<g class="route-states is-${size}">${segments.join('')}${ends}</g>`;
}
