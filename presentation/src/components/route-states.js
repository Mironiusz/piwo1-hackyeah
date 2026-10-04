/**
 * A route of four segments, one per segment state of the app: a barrier from the needs, no barriers with full data,
 * partial data and no data (specification M7). Every state carries a color, an icon in a badge and a line pattern,
 * so the states stay apart in grayscale, the same rule the app follows. Styles: `.rs-*` in `src/styles/components.css`.
 */

export const STATE_KEYS = ['barrier', 'clear', 'partial', 'nodata'];

const BEND = [0, -46, 28, -30, 14];

const ICONS = {
  barrier: (x, y) => `<path class="rs-icon" d="M${x - 8} ${y - 8} l16 16 M${x + 8} ${y - 8} l-16 16" />`,
  clear: (x, y) => `<path class="rs-icon" d="M${x - 10} ${y + 1} l6 7 l13 -16" />`,
  partial: (x, y) => `<path class="rs-icon-fill" d="M${x} ${y - 11} a11 11 0 0 1 0 22 z" /><circle class="rs-icon" cx="${x}" cy="${y}" r="11" />`,
  nodata: (x, y) => `<text class="rs-icon-text" x="${x}" y="${y + 10}" text-anchor="middle">?</text>`,
};

/**
 * Returns the SVG markup of the route as one `<g>` placed at (x, y), `width` wide. Each segment is a
 * `<g class="rs-seg is-<state>" data-state="<state>">`, so a slide can animate the segments one by one.
 */
export function routeStates({ x = 0, y = 0, width = 1200 } = {}) {
  const step = width / STATE_KEYS.length;
  const points = BEND.map((dy, i) => ({ x: x + i * step, y: y + dy }));
  const segments = STATE_KEYS.map((state, i) => {
    const a = points[i];
    const b = points[i + 1];
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2 - 58;
    return `<g class="rs-seg is-${state}" data-state="${state}">
      <path class="rs-line" d="M${a.x} ${a.y} L${b.x} ${b.y}" />
      <circle class="rs-badge" cx="${mx}" cy="${my}" r="24" />
      ${ICONS[state](mx, my)}
    </g>`;
  });
  const ends = [points[0], points[points.length - 1]].map((p) => `<circle class="rs-end" cx="${p.x}" cy="${p.y}" r="12" />`).join('');
  return `<g class="route-states">${segments.join('')}${ends}</g>`;
}

/** A short sample of one state, a line with its badge, for a legend row. */
export function stateSample(state) {
  return `<svg class="rs-sample" viewBox="0 0 120 60" width="120" height="60" aria-hidden="true">
    <g class="rs-seg is-${state}">
      <path class="rs-line" d="M6 44 H114" />
      <circle class="rs-badge" cx="60" cy="22" r="18" />
      ${ICONS[state](60, 22)}
    </g>
  </svg>`;
}
