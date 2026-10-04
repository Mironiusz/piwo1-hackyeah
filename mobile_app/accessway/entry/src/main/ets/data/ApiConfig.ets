import { common } from '@kit.AbilityKit';
import { readRawText } from './Storage';

/**
 * API server address. One place to change: the file `entry/src/main/resources/rawfile/config/api.json`,
 * field `base_url`, for example `http://203.0.113.10` or `http://10.0.2.2:8000` for a server on the computer
 * that runs the emulator. An empty address means working without a server, on device data (LocalRepository).
 * The client appends the operation paths (`/api/...`), so give the address without `/api` and no trailing slash.
 * Field `tiles_url` is the full address of the PMTiles archive of Kraków served next to the API, for example
 * `http://10.0.2.2:8090/krakow.pmtiles`; empty means the sample base map bundled in the app.
 */
export interface ApiSettings {
  base_url: string;
  timeout_ms?: number;
  tiles_url?: string;
}

export const DEFAULT_TIMEOUT_MS: number = 15000;

export function readApiSettings(ctx: common.Context): ApiSettings {
  const raw = readRawText(ctx, 'config/api.json');
  if (raw === null) {
    return { base_url: '' };
  }
  try {
    const s = JSON.parse(raw) as ApiSettings;
    let url = (s.base_url ?? '').trim();
    while (url.endsWith('/')) {
      url = url.substring(0, url.length - 1);
    }
    if (url.endsWith('/api')) {
      url = url.substring(0, url.length - 4);
    }
    return { base_url: url, timeout_ms: s.timeout_ms, tiles_url: (s.tiles_url ?? '').trim() };
  } catch (e) {
    return { base_url: '' };
  }
}
