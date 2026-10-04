import { content } from '../lib/lang.js';

/**
 * Symbols missing from the bundled Barlow fonts (arrow, "approximately", check mark, cross).
 * The browser would take them from a system font and they would look different on another computer, so they are drawn in SVG.
 * Size and color follow the text (1em, currentColor). The spoken label comes from `page.icons` of the content file,
 * so a screen reader hears it in the language of the deck.
 */

const LABELS = content.page.icons;

const icon = (body, label) => `<svg class="icon" viewBox="0 0 24 24" width="1em" height="1em" role="img" aria-label="${label}">${body}</svg>`;

export const ARROW = icon('<path d="M3 12h16M13 6l6 6-6 6" />', LABELS.arrow);
export const APPROX = icon('<path d="M4 9.5c2.7-2.6 5.3-2.6 8 0s5.3 2.6 8 0M4 16.5c2.7-2.6 5.3-2.6 8 0s5.3 2.6 8 0" />', LABELS.approx);
export const CHECK = icon('<path d="M4 12.5l5.5 5.5L20 6" />', LABELS.check);
export const CROSS = icon('<path d="M6 6l12 12M18 6L6 18" />', LABELS.cross);

/** An arrow to the right inside an SVG drawing: from (x, y) over the length `w`, at the height of the middle of the text. */
export const svgArrow = (x, y, w = 28, cls = 'svg-arrow') => `<path class="${cls}" d="M${x} ${y} h${w - 6} M${x + w - 12} ${y - 7} l7 7 l-7 7" />`;

/** A downward arrow inside an SVG drawing: from (x, y) over the length `h`. */
export const svgArrowDown = (x, y, h = 28, cls = 'svg-arrow') => `<path class="${cls}" d="M${x} ${y} v${h - 6} M${x - 7} ${y + h - 12} l7 7 l7 -7" />`;

/** A check mark and a cross inside an SVG drawing, centered on the point (x, y). */
export const svgCheck = (x, y, cls = '') => `<path class="svg-check ${cls}" d="M${x - 9} ${y} l6 7 l12 -15" />`;
export const svgCross = (x, y, cls = '') => `<path class="svg-cross ${cls}" d="M${x - 8} ${y - 8} l16 16 M${x + 8} ${y - 8} l-16 16" />`;
