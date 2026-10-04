import { describe, expect, it } from "vitest";

import { buildFlavor, buildStyle, findStyleViolations, type BaseMapLayer, type BaseMapStyle } from "./generate_base_map_style.mjs";

const LANGUAGES = ["pl", "en"];
const SOURCE_NAME = "protomaps";
const ARCHIVE_ADDRESS = "pmtiles:///tiles/krakow.pmtiles";
const GLYPHS_ADDRESS = "/map/fonts/{fontstack}/{range}.pbf";
const COMMITTED_FONTS = ["Noto Sans Regular", "Noto Sans Medium", "Noto Sans Italic"];
const REMOVED_LAYERS = ["roads_oneway", "roads_shields"];
const EXTRA_LAYER = "extra_label";

/**
 * Builds a label layer over the tile archive with the given layout, to add to a style under test.
 */
function buildLabelLayer(layout: Record<string, unknown>): BaseMapLayer {
  return { id: EXTRA_LAYER, type: "symbol", source: SOURCE_NAME, "source-layer": "places", layout };
}

/**
 * Returns the style with Polish labels and one more layer at its end.
 */
function buildStyleWithLayer(layer: BaseMapLayer): BaseMapStyle {
  const style = buildStyle("pl");
  return { ...style, layers: [...style.layers, layer] };
}

/**
 * Lists the layout properties of every layer of a style, each as the layer and the property.
 */
function listLayoutProperties(style: BaseMapStyle): string[] {
  return style.layers.flatMap((layer) => Object.keys(layer.layout ?? {}).map((property) => `${layer.id}: ${property}`));
}

describe("buildFlavor", () => {
  it("sets the colors of the design direction", () => {
    expect(buildFlavor()).toMatchObject({
      background: "#ECECE3",
      earth: "#ECECE3",
      park_a: "#D3E1CB",
      wood_a: "#D3E1CB",
      school: "#E6E6DC",
      water: "#C5D6DF",
      buildings: "#DDDDD2",
      minor_a: "#FFFFFF",
      major: "#FFFFFF",
      bridges_major: "#FFFFFF",
      tunnel_major: "#F4F5F2",
      major_casing_late: "#D5D8DC",
      railway: "#B9BDC4",
      boundaries: "#B9BDC4",
      city_label: "#4B5058",
      roads_label_major: "#4B5058",
    });
  });

  it("leaves out the points of interest and the fonts of the style package", () => {
    const flavor = buildFlavor();

    expect(flavor).not.toHaveProperty("pois");
    expect(flavor).not.toHaveProperty("regular");
    expect(flavor).not.toHaveProperty("bold");
    expect(flavor).not.toHaveProperty("italic");
  });
});

describe("buildStyle", () => {
  it.each(LANGUAGES)("builds the style with labels in the language %s", (language) => {
    const style = buildStyle(language);

    expect(style.version).toBe(8);
    expect(style.glyphs).toBe(GLYPHS_ADDRESS);
    expect(Object.keys(style.sources)).toEqual([SOURCE_NAME]);
    expect(style.sources[SOURCE_NAME]?.url).toBe(ARCHIVE_ADDRESS);
    expect(style.layers.length).toBeGreaterThan(0);
  });

  it.each(LANGUAGES)("builds a style in the language %s that breaks no rule", (language) => {
    expect(findStyleViolations(buildStyle(language))).toEqual([]);
  });

  it.each(LANGUAGES)("builds the style in the language %s without a sprite and without a layer that draws an icon", (language) => {
    const style = buildStyle(language);

    expect(style).not.toHaveProperty("sprite");
    expect(listLayoutProperties(style).filter((property) => property.includes(": icon-"))).toEqual([]);
    expect(style.layers.map((layer) => layer.id).filter((id) => REMOVED_LAYERS.includes(id))).toEqual([]);
  });

  it.each(LANGUAGES)("writes the labels of the style in the language %s with the three committed fonts", (language) => {
    const text = JSON.stringify(buildStyle(language));

    for (const font of COMMITTED_FONTS) {
      expect(text).toContain(font);
    }
  });

  it.each(LANGUAGES)("draws every layer of the style in the language %s from the tile archive", (language) => {
    const sources = buildStyle(language)
      .layers.filter((layer) => layer.type !== "background")
      .map((layer) => layer.source);

    expect(new Set(sources)).toEqual(new Set([SOURCE_NAME]));
  });

  it.each(LANGUAGES)("keeps the attribution of the map data in the language %s, with its link", (language) => {
    const attribution = buildStyle(language).sources[SOURCE_NAME]?.attribution;

    expect(attribution).toContain("OpenStreetMap");
    expect(attribution).toContain("https://www.openstreetmap.org/copyright");
  });

  it("takes the labels of the Polish style from the Polish names", () => {
    expect(JSON.stringify(buildStyle("pl"))).toContain("name:pl");
  });

  it("takes the labels of the English style from the English names and not from the Polish ones", () => {
    const text = JSON.stringify(buildStyle("en"));

    expect(text).toContain("name:en");
    expect(text).not.toContain("name:pl");
  });

  it("builds the two styles with the same layers, apart from the labels", () => {
    const polish = buildStyle("pl");
    const english = buildStyle("en");

    expect(english.layers.map((layer) => layer.id)).toEqual(polish.layers.map((layer) => layer.id));
    expect(JSON.stringify(english)).not.toBe(JSON.stringify(polish));
  });

  it("refuses a language the interface does not have", () => {
    expect(() => buildStyle("de")).toThrow(/\bde$/);
  });
});

describe("findStyleViolations", () => {
  it("reports a sprite", () => {
    const violations = findStyleViolations({ ...buildStyle("pl"), sprite: "/map/sprite" });

    expect(violations).toEqual([expect.stringContaining("sprite")]);
  });

  it("reports a layer with an icon", () => {
    const violations = findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "icon-image": "townspot" })));

    expect(violations).toEqual([expect.stringContaining("icon-image")]);
    expect(violations[0]).toContain(EXTRA_LAYER);
  });

  it("reports every icon property of a layer", () => {
    const violations = findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "icon-image": "townspot", "icon-size": 0.7 })));

    expect(violations).toEqual([expect.stringContaining("icon-image"), expect.stringContaining("icon-size")]);
  });

  it("reports a font outside the three", () => {
    const violations = findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "text-font": ["Open Sans Bold"] })));

    expect(violations).toEqual([expect.stringContaining("Open Sans Bold")]);
    expect(violations[0]).toContain(EXTRA_LAYER);
  });

  it("reports a font outside the three next to a committed one", () => {
    const violations = findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "text-font": ["Noto Sans Regular", "Open Sans Bold"] })));

    expect(violations).toEqual([expect.stringContaining("Open Sans Bold")]);
  });

  it("reports a font outside the three inside an expression", () => {
    const font = ["case", ["<=", ["get", "min_zoom"], 5], ["literal", ["Open Sans Bold"]], ["literal", ["Noto Sans Regular"]]];
    const violations = findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "text-font": font })));

    expect(violations).toEqual([expect.stringContaining("Open Sans Bold")]);
  });

  it.each(COMMITTED_FONTS)("accepts the committed font %s, as a list and inside an expression", (font) => {
    const expression = ["case", ["<=", ["get", "min_zoom"], 5], ["literal", [font]], ["literal", ["Noto Sans Regular"]]];

    expect(findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "text-font": [font] })))).toEqual([]);
    expect(findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "text-font": expression })))).toEqual([]);
  });

  it("reports an outside address anywhere in the style", () => {
    const layer = { ...buildLabelLayer({ "text-font": ["Noto Sans Regular"] }), metadata: { origin: "https://tiles.example.com/style.json" } };
    const violations = findStyleViolations(buildStyleWithLayer(layer));

    expect(violations).toEqual([expect.stringContaining("address outside")]);
  });

  it("reports fonts taken from an outside address", () => {
    const violations = findStyleViolations({ ...buildStyle("pl"), glyphs: "https://fonts.example.com/{fontstack}/{range}.pbf" });

    expect(violations).toEqual([expect.stringContaining("glyphs"), expect.stringContaining("address outside")]);
  });

  it("reports fonts taken from another address of the page", () => {
    const violations = findStyleViolations({ ...buildStyle("pl"), glyphs: "/fonts/{fontstack}/{range}.pbf" });

    expect(violations).toEqual([expect.stringContaining("glyphs")]);
  });

  it("reports a second source", () => {
    const style = buildStyle("pl");
    const violations = findStyleViolations({ ...style, sources: { ...style.sources, other: { type: "vector", url: "pmtiles:///tiles/other.pmtiles" } } });

    expect(violations).toEqual([expect.stringContaining("a source other than the tile archive")]);
  });

  it("reports a tile archive at another address", () => {
    const style = buildStyle("pl");
    const violations = findStyleViolations({ ...style, sources: { [SOURCE_NAME]: { type: "vector", url: "https://tiles.example.com/krakow.pmtiles" } } });

    expect(violations).toEqual([expect.stringContaining(ARCHIVE_ADDRESS)]);
  });

  it("reports a character the repository forbids, by its code point", () => {
    const emDash = String.fromCodePoint(0x2014);
    const violations = findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "text-field": `Rynek ${emDash} centrum`, "text-font": ["Noto Sans Regular"] })));

    expect(violations).toEqual([expect.stringContaining("U+2014")]);
  });

  it("reports an emoji", () => {
    const emoji = String.fromCodePoint(0x1f600);
    const violations = findStyleViolations(buildStyleWithLayer(buildLabelLayer({ "text-field": emoji, "text-font": ["Noto Sans Regular"] })));

    expect(violations).toEqual([expect.stringContaining("U+1F600")]);
  });

  it("reports each broken rule of a style that breaks several", () => {
    const style = buildStyleWithLayer(buildLabelLayer({ "icon-image": "townspot", "text-font": ["Open Sans Bold"] }));
    const violations = findStyleViolations({ ...style, sprite: "/map/sprite" });

    expect(violations).toEqual([expect.stringContaining("sprite"), expect.stringContaining("icon-image"), expect.stringContaining("Open Sans Bold")]);
  });

  it("reports a style without a source, without fonts and without a layer, and does not fail on it", () => {
    expect(findStyleViolations({}).length).toBeGreaterThanOrEqual(2);
  });
});
