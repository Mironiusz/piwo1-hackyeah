import { content } from '../lib/lang.js';

/**
 * The arrow is missing from the bundled Barlow fonts: the browser would take it from a system font and it would look
 * different on another computer, so it is drawn in SVG. Size and color follow the text (1em, currentColor). The spoken
 * label comes from `page.icons` of the content file, so a screen reader hears it in the language of the deck.
 */

const icon = (body, label) => `<svg class="icon" viewBox="0 0 24 24" width="1em" height="1em" role="img" aria-label="${label}">${body}</svg>`;

export const ARROW = icon('<path d="M3 12h16M13 6l6 6-6 6" />', content.page.icons.arrow);
