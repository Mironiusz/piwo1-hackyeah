import { gunzip, isGzip } from './Inflate';
import { decodeMvt } from './Mvt';
import { TileData } from './TileTypes';

/**
 * Unpacks and decodes one tile of the archive off the UI thread: gzip when the archive compresses its tiles,
 * then the vector tile into the draw classes of the map.
 */
@Concurrent
export function decodeTileTask(raw: ArrayBuffer, z: number, x: number, y: number): TileData {
  const bytes = new Uint8Array(raw);
  return decodeMvt(isGzip(bytes) ? gunzip(bytes) : bytes, z, x, y);
}
