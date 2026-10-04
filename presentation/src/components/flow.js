/**
 * Flow diagrams: rectangles joined by arrows, vertical or horizontal, for example the architecture diagram.
 * Shared by every slide with a flow, so they all have the same rhythm and the same gaps.
 *
 * Node: `{ label, sub, cls, w, h, plain }`. `plain` draws the label alone, without a frame.
 * The returned `boxes` carry ready geometry (x, y, w, h, cx, cy) for attaching animations
 * and for drawing custom links. Styles: `.fl-*` in `src/styles/components.css`.
 * The color of a node is picked by `cls`, by meaning: `is-primary`, `is-accent`, `is-barrier`, `is-clear`,
 * `is-partial`, `is-nodata`, `is-disputed`, `is-dim` (MODULE.md, section Main records and contracts).
 */

export const FLOW = { w: 320, h: 64, gap: 38 };

function renderNode(node, i) {
  const labelY = node.y + node.h / 2 + (node.sub ? -2 : 9);
  return `<g class="fl-node ${node.cls ?? ''}" data-i="${i}">
    ${node.plain ? '' : `<rect class="fl-box" x="${node.x}" y="${node.y}" width="${node.w}" height="${node.h}" rx="10" />`}
    <text class="fl-label" x="${node.cx}" y="${labelY}" text-anchor="middle">${node.label}</text>
    ${node.sub ? `<text class="fl-sub" x="${node.cx}" y="${node.y + node.h / 2 + 24}" text-anchor="middle">${node.sub}</text>` : ''}
  </g>`;
}

/** A downward arrow from `y1` to `y2` (the head ends exactly at `y2`). */
export const vArrow = (x, y1, y2, cls = '') => `<g class="fl-arrow ${cls}"><path class="fl-link" d="M${x} ${y1} V${y2 - 11}" /><path class="fl-head" d="M${x} ${y2} l-7 -12 h14 z" /></g>`;

/** An upward arrow from `yBottom` to `yTop` (the head at the top). */
export const vArrowUp = (x, yBottom, yTop, cls = '') =>
  `<g class="fl-arrow ${cls}"><path class="fl-link" d="M${x} ${yBottom} V${yTop + 11}" /><path class="fl-head" d="M${x} ${yTop} l-7 12 h14 z" /></g>`;

/** An arrow to the right from `x1` to `x2`. */
export const hArrow = (x1, x2, y, cls = '') => `<g class="fl-arrow ${cls}"><path class="fl-link" d="M${x1} ${y} H${x2 - 11}" /><path class="fl-head" d="M${x2} ${y} l-12 -7 v14 z" /></g>`;

function place(nodes, step, geom) {
  return nodes.map((node, i) => {
    const w = node.w ?? geom.w;
    const h = node.h ?? geom.h;
    return { ...node, ...step(i, w, h), w, h };
  });
}

/** A column of boxes centered on `cx`, going down from `top`. */
export function flowColumn(nodes, { cx = 0, top = 0, w = FLOW.w, h = FLOW.h, gap = FLOW.gap } = {}) {
  let y = top;
  const boxes = place(
    nodes,
    (i, bw, bh) => {
      const box = { x: cx - bw / 2, y, cx, cy: y + bh / 2 };
      y += bh + gap;
      return box;
    },
    { w, h },
  );
  const svg = boxes.map((b, i) => (i > 0 ? vArrow(cx, boxes[i - 1].y + boxes[i - 1].h + 6, b.y - 4) : '') + renderNode(b, i)).join('');
  return { svg, boxes, bottom: y - gap };
}

/** A row of boxes at the height `cy`, going right from `left`. */
export function flowRow(nodes, { left = 0, cy = 0, w = FLOW.w, h = FLOW.h, gap = FLOW.gap } = {}) {
  let x = left;
  const boxes = place(
    nodes,
    (i, bw, bh) => {
      const box = { x, y: cy - bh / 2, cx: x + bw / 2, cy };
      x += bw + gap;
      return box;
    },
    { w, h },
  );
  const svg = boxes.map((b, i) => (i > 0 ? hArrow(boxes[i - 1].x + boxes[i - 1].w + 6, b.x - 4, cy) : '') + renderNode(b, i)).join('');
  return { svg, boxes, right: x - gap };
}
