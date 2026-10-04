/** A street label of a tile: the name and its lines in tile pixels. */
export interface TileLabel {
  name: string;
  geom: number[][];
}

/** Polygons of one draw class; every part is a flat list [x, y, ...] in tile pixels. */
export interface TileFills {
  green: number[][];
  water: number[][];
  building: number[][];
}

/** Street lines by rank, in tile pixels. */
export interface TileLines {
  path: number[][];
  minor: number[][];
  major: number[][];
}

/**
 * One tile ready to draw: geometry simplified to about one screen pixel, grouped by draw class and stored in
 * integer tile pixels 0..extent. One scale and one offset per tile put it on the screen.
 */
export interface TileData {
  z: number;
  x: number;
  y: number;
  extent: number;
  fills: TileFills;
  lines: TileLines;
  labels: TileLabel[];
}

/** An empty tile, used for a tile the archive does not hold. */
export function emptyTile(z: number, x: number, y: number): TileData {
  return {
    z: z, x: x, y: y, extent: 512,
    fills: { green: [], water: [], building: [] },
    lines: { path: [], minor: [], major: [] },
    labels: []
  };
}
