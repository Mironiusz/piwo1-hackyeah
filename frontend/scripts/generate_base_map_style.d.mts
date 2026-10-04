/**
 * The types of generate_base_map_style.mjs for the TypeScript code that imports it, which is its test.
 * The script itself stays plain JavaScript, so that node runs it without a build.
 */

/**
 * One layer of the style of the base map, as the style package builds it.
 */
export interface BaseMapLayer {
  id: string;
  type: string;
  source?: string;
  layout?: Record<string, unknown>;
  paint?: Record<string, unknown>;
  [property: string]: unknown;
}

/**
 * A source of a style. The base map has one, the tile archive with its attribution.
 */
export interface BaseMapSource {
  type: string;
  url: string;
  attribution?: string;
}

/**
 * The style of the base map that the generator writes into a file. It never has a sprite: the key stands here
 * only so that the check of the rules can be given a style that breaks that rule.
 */
export interface BaseMapStyle {
  version: number;
  sources: Record<string, BaseMapSource>;
  glyphs: string;
  layers: BaseMapLayer[];
  sprite?: string;
}

/**
 * Returns the colors of the base map: the flavor of the style package with the values of the design direction,
 * without the points of interest.
 */
export function buildFlavor(): Record<string, unknown>;

/**
 * Returns the style of the base map with labels in the given language, "pl" or "en", and throws for another one.
 */
export function buildStyle(language: string): BaseMapStyle;

/**
 * Returns a list of texts, one for each rule of the base map style that the given style breaks,
 * and an empty list for a style that keeps them all.
 */
export function findStyleViolations(style: Partial<BaseMapStyle>): string[];

/**
 * Writes the two style files, or with --check compares them with what is generated.
 * Returns 0 when there is no problem and 1 otherwise.
 */
export function main(argv: string[]): Promise<number>;
