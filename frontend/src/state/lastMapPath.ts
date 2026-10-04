let lastMapPath = "/";

/**
 * Remembers the address of the map view a person was on last, until the page closes.
 */
export function rememberLastMapPath(path: string): void {
  lastMapPath = path;
}

/**
 * Returns the address of the map view a person was on last, so a page or a flow can lead back to the map
 * in the mode it was left in: the facts, route planning or the route result.
 */
export function readLastMapPath(): string {
  return lastMapPath;
}
