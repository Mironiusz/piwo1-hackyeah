/**
 * Generates the two style files of the base map, one with Polish labels and one with English ones.
 *
 * Usage: node frontend/scripts/generate_base_map_style.mjs [--check]
 *
 * Without an argument it writes both files. With --check it writes nothing and ends with an error when a
 * committed file differs from what it generates or breaks a rule of the style. A color is changed here,
 * never in a generated file. The rules are described in docs/setup/MAP_SETUP.md.
 */

import { realpathSync } from "node:fs";
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import { layers, namedFlavor } from "@protomaps/basemaps";
import prettier from "prettier";

const SOURCE_NAME = "protomaps";
const ARCHIVE_URL = "pmtiles:///tiles/krakow.pmtiles";
const GLYPHS_URL = "/map/fonts/{fontstack}/{range}.pbf";
const ATTRIBUTION = '<a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>';

const LANGUAGES = ["pl", "en"];
const ALLOWED_FONTS = ["Noto Sans Regular", "Noto Sans Medium", "Noto Sans Italic"];
const REMOVED_LAYER_IDS = ["roads_oneway", "roads_shields"];
const ICON_PROPERTY_PREFIX = "icon-";

const GROUND = "#ECECE3";
const GREEN = "#D3E1CB";
const LAND_USE = "#E6E6DC";
const WATER = "#C5D6DF";
const BUILDINGS = "#DDDDD2";
const ROAD = "#FFFFFF";
const TUNNEL = "#F4F5F2";
const CASING = "#D5D8DC";
const RAIL = "#B9BDC4";
const LABEL = "#4B5058";

const GREEN_KEYS = ["park_a", "park_b", "wood_a", "wood_b", "scrub_a", "scrub_b", "zoo"];
const LAND_USE_KEYS = ["hospital", "industrial", "school", "pedestrian", "glacier", "sand", "beach", "aerodrome", "runway", "military", "pier"];
const ROAD_KEYS = ["other", "minor_service", "minor_a", "minor_b", "link", "major", "highway", "bridges_other", "bridges_minor", "bridges_link", "bridges_major", "bridges_highway"];
const TUNNEL_KEYS = ["tunnel_other", "tunnel_minor", "tunnel_link", "tunnel_major", "tunnel_highway"];
const CASING_SUFFIXES = ["_casing", "_casing_early", "_casing_late"];
const LABEL_KEYS = ["roads_label_minor", "roads_label_major", "ocean_label", "subplace_label", "city_label", "state_label", "country_label", "address_label"];
const ROAD_HALO_KEYS = ["roads_label_minor_halo", "roads_label_major_halo", "address_label_halo"];
const PLACE_HALO_KEYS = ["subplace_label_halo", "city_label_halo", "state_label_halo"];
const OPTIONAL_KEYS_LEFT_OUT = ["pois", "regular", "bold", "italic"];

const FORBIDDEN_CODE_POINTS = [0x2014, 0x2013, 0x2212, 0x201c, 0x201d, 0x2018, 0x2019, 0x02bc, 0x2026, 0x00b7, 0x2192, 0x2190, 0x2194, 0x00d7, 0x0430, 0x037e, 0x2215];
const EMOJI_PATTERN = /\p{Extended_Pictographic}/u;

/**
 * Returns the colors of the base map: the named flavor "light" of the style package with the values of the
 * design direction, the land cover in the same colors, and without the points of interest, which the base
 * map does not draw. A key the package does not know stops the run, so that a renamed key is noticed.
 */
export function buildFlavor() {
  const base = namedFlavor("light");
  const flavor = { ...base };
  const assign = (keys, value) => {
    for (const key of keys) {
      if (!(key in base)) {
        throw new Error(`The style package has no flavor key ${key}`);
      }
      flavor[key] = value;
    }
  };

  assign(["background", "earth"], GROUND);
  assign(GREEN_KEYS, GREEN);
  assign(LAND_USE_KEYS, LAND_USE);
  assign(["water"], WATER);
  assign(["buildings"], BUILDINGS);
  assign(ROAD_KEYS, ROAD);
  assign(TUNNEL_KEYS, TUNNEL);
  assign(
    Object.keys(base).filter((key) => CASING_SUFFIXES.some((suffix) => key.endsWith(suffix))),
    CASING,
  );
  assign(["railway", "boundaries"], RAIL);
  assign(LABEL_KEYS, LABEL);
  assign(ROAD_HALO_KEYS, ROAD);
  assign(PLACE_HALO_KEYS, GROUND);

  flavor.landcover = { barren: GROUND, farmland: GROUND, forest: GREEN, glacier: GROUND, grassland: GREEN, scrub: GREEN, urban_area: GROUND };
  for (const key of OPTIONAL_KEYS_LEFT_OUT) {
    delete flavor[key];
  }
  return flavor;
}

/**
 * Returns the style of the base map with labels in the given language, "pl" or "en". The layers come from
 * the style package and are changed so that none needs a sprite: the arrows of one-way streets and the road
 * shields are removed, and the names of localities keep their text and lose their icon.
 */
export function buildStyle(language) {
  if (!LANGUAGES.includes(language)) {
    throw new Error(`Unknown language of the labels: ${language}`);
  }
  const styleLayers = layers(SOURCE_NAME, buildFlavor(), { lang: language })
    .filter((layer) => !REMOVED_LAYER_IDS.includes(layer.id))
    .map((layer) => {
      if (!layer.layout) {
        return layer;
      }
      const layout = Object.fromEntries(Object.entries(layer.layout).filter(([property]) => !property.startsWith(ICON_PROPERTY_PREFIX)));
      return { ...layer, layout };
    });

  return {
    version: 8,
    sources: { [SOURCE_NAME]: { type: "vector", url: ARCHIVE_URL, attribution: ATTRIBUTION } },
    glyphs: GLYPHS_URL,
    layers: styleLayers,
  };
}

/**
 * Returns the font names a value of the property text-font uses. The value is a plain list of names, or an
 * expression that holds such lists under "literal"; the other strings of an expression are operators and
 * property names and are not fonts.
 */
function collectFontNames(value) {
  if (!Array.isArray(value)) {
    return [];
  }
  if (value[0] === "literal" && Array.isArray(value[1])) {
    return value[1];
  }
  if (value.every((item) => typeof item === "string")) {
    return value;
  }
  return value.flatMap((item) => collectLiteralFontNames(item));
}

/**
 * Returns the font names held under "literal" anywhere inside a part of an expression.
 */
function collectLiteralFontNames(value) {
  if (!Array.isArray(value)) {
    return [];
  }
  if (value[0] === "literal" && Array.isArray(value[1])) {
    return value[1];
  }
  return value.flatMap((item) => collectLiteralFontNames(item));
}

/**
 * Returns a list of texts, one for each rule of the base map style that the given style breaks, and an empty
 * list for a style that keeps them all: no sprite, no icon, only the three committed fonts, only the two
 * addresses of the project, no other address, and no character the repository forbids.
 */
export function findStyleViolations(style) {
  const violations = [];

  if ("sprite" in style) {
    violations.push("the style has the key sprite");
  }
  if (style.glyphs !== GLYPHS_URL) {
    violations.push(`the glyphs address is ${style.glyphs}, expected ${GLYPHS_URL}`);
  }
  const source = style.sources?.[SOURCE_NAME];
  if (!source || source.url !== ARCHIVE_URL) {
    violations.push(`the source ${SOURCE_NAME} does not point at ${ARCHIVE_URL}`);
  }
  if (Object.keys(style.sources ?? {}).length !== 1) {
    violations.push("the style has a source other than the tile archive");
  }

  for (const layer of style.layers ?? []) {
    const layout = layer.layout ?? {};
    for (const property of Object.keys(layout)) {
      if (property.startsWith(ICON_PROPERTY_PREFIX)) {
        violations.push(`the layer ${layer.id} has the layout property ${property}, which needs a sprite`);
      }
    }
    for (const font of collectFontNames(layout["text-font"])) {
      if (!ALLOWED_FONTS.includes(font)) {
        violations.push(`the layer ${layer.id} uses the font ${font}, which is not committed`);
      }
    }
  }

  const withoutKnownAddresses = JSON.stringify({ ...style, sources: { [SOURCE_NAME]: { ...source, url: "", attribution: "" } } });
  if (withoutKnownAddresses.includes("://")) {
    violations.push("the style holds an address outside the tile archive and the attribution");
  }

  const text = JSON.stringify(style);
  for (const character of text) {
    if (FORBIDDEN_CODE_POINTS.includes(character.codePointAt(0)) || EMOJI_PATTERN.test(character)) {
      violations.push(`the style holds the forbidden character U+${character.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`);
    }
  }
  return violations;
}

/**
 * Returns the text of a style file: the style as JSON, formatted with the prettier configuration of the
 * repository, so that the committed file stays unchanged under the format check.
 */
async function renderStyleFile(style, filePath) {
  const options = (await prettier.resolveConfig(filePath)) ?? {};
  return prettier.format(JSON.stringify(style), { ...options, parser: "json" });
}

/**
 * Writes the two style files, or with --check compares them with what is generated. Prints every broken
 * rule and every difference, and returns 0 when there is none and 1 otherwise.
 */
export async function main(argv) {
  const unknownArguments = argv.filter((argument) => argument !== "--check");
  if (unknownArguments.length > 0) {
    console.error(`Unknown argument: ${unknownArguments.join(" ")}`);
    return 1;
  }
  const isCheck = argv.includes("--check");
  let problemCount = 0;

  for (const language of LANGUAGES) {
    const filePath = fileURLToPath(new URL(`../public/map/style-${language}.json`, import.meta.url));
    const style = buildStyle(language);
    const violations = findStyleViolations(style);
    for (const violation of violations) {
      console.error(`style-${language}.json: ${violation}`);
    }
    problemCount += violations.length;

    const expected = await renderStyleFile(style, filePath);
    if (!isCheck) {
      await writeFile(filePath, expected, "utf8");
      console.log(`Written style-${language}.json with ${style.layers.length} layers`);
      continue;
    }
    const committed = await readFile(filePath, "utf8").catch(() => null);
    if (committed !== expected) {
      console.error(`style-${language}.json differs from what the generator writes. Run the generator without --check.`);
      problemCount += 1;
    }
  }

  if (isCheck && problemCount === 0) {
    console.log("Both style files are up to date and keep every rule.");
  }
  return problemCount === 0 ? 0 : 1;
}

/**
 * Says whether this file was started with node, as opposed to being imported by another file. Both paths are
 * compared after links are resolved, so that a start through a linked directory still runs the generator.
 */
function isStartedDirectly() {
  if (!process.argv[1]) {
    return false;
  }
  return realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
}

if (isStartedDirectly()) {
  process.exitCode = await main(process.argv.slice(2));
}
