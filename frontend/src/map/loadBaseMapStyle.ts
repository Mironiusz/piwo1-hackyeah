import type { StyleSpecification } from "maplibre-gl";

import type { Language } from "../i18n/index.ts";

const TILES_PREFIX = "pmtiles://";

/**
 * Loads the style of the base map for a language from the host of the page.
 * The two addresses of the style start with a slash; they are turned into full addresses of the page here,
 * so the map library never has to resolve them itself.
 */
export async function loadBaseMapStyle(language: Language): Promise<StyleSpecification> {
  const response = await fetch(`/map/style-${language}.json`);
  if (!response.ok) {
    throw new Error(`The style of the base map did not load: ${response.status}`);
  }
  const style = (await response.json()) as StyleSpecification;
  const origin = window.location.origin;

  const sources: StyleSpecification["sources"] = {};
  for (const [name, source] of Object.entries(style.sources)) {
    if (source.type === "vector" && typeof source.url === "string" && source.url.startsWith(`${TILES_PREFIX}/`)) {
      sources[name] = { ...source, url: `${TILES_PREFIX}${origin}${source.url.slice(TILES_PREFIX.length)}` };
    } else {
      sources[name] = source;
    }
  }

  const glyphs = typeof style.glyphs === "string" && style.glyphs.startsWith("/") ? `${origin}${style.glyphs}` : style.glyphs;

  return { ...style, sources, glyphs };
}
