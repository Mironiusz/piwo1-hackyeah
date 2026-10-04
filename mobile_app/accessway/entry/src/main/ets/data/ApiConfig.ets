import { common } from '@kit.AbilityKit';
import { readRawText } from './Storage';

/**
 * Adres serwera API. Jedno miejsce do zmiany: plik `entry/src/main/resources/rawfile/config/api.json`,
 * pole `base_url`, na przykład `http://203.0.113.10` albo `http://10.0.2.2:8000` dla serwera na komputerze,
 * na którym działa emulator. Pusty adres oznacza pracę bez serwera, na danych z urządzenia (LocalRepository).
 * Ścieżki operacji (`/api/...`) dokleja klient, więc adres podaje się bez `/api` i bez ukośnika na końcu.
 * Pole `tiles_url` to adres serwera kafelków mapy (`/tiles/...`); pusty oznacza podkład z danych w aplikacji.
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
