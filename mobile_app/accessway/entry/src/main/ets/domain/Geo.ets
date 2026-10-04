import { decimal } from '../model/I18n';

const EARTH_R: number = 6371000;
const DEG: number = Math.PI / 180;

export function distanceM(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const dLat = (lat2 - lat1) * DEG;
  const dLon = (lon2 - lon1) * DEG;
  const s = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * DEG) * Math.cos(lat2 * DEG) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  return 2 * EARTH_R * Math.asin(Math.min(1, Math.sqrt(s)));
}

/** Odległość punktu od odcinka w metrach, w lokalnym rzucie równoodległościowym. */
export function pointSegmentDistanceM(pLat: number, pLon: number, aLat: number, aLon: number,
  bLat: number, bLon: number): number {
  const kx = Math.cos(pLat * DEG) * DEG * EARTH_R;
  const ky = DEG * EARTH_R;
  const ax = (aLon - pLon) * kx;
  const ay = (aLat - pLat) * ky;
  const bx = (bLon - pLon) * kx;
  const by = (bLat - pLat) * ky;
  const dx = bx - ax;
  const dy = by - ay;
  const len2 = dx * dx + dy * dy;
  let t = 0;
  if (len2 > 0) {
    t = Math.max(0, Math.min(1, -(ax * dx + ay * dy) / len2));
  }
  const cx = ax + t * dx;
  const cy = ay + t * dy;
  return Math.sqrt(cx * cx + cy * cy);
}

/** Azymut w stopniach od północy, zgodnie z ruchem wskazówek zegara. */
export function bearingDeg(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const y = Math.sin((lon2 - lon1) * DEG) * Math.cos(lat2 * DEG);
  const x = Math.cos(lat1 * DEG) * Math.sin(lat2 * DEG) -
    Math.sin(lat1 * DEG) * Math.cos(lat2 * DEG) * Math.cos((lon2 - lon1) * DEG);
  const b = Math.atan2(y, x) / DEG;
  return (b + 360) % 360;
}

export function turnAngle(inBearing: number, outBearing: number): number {
  let d = outBearing - inBearing;
  while (d > 180) {
    d -= 360;
  }
  while (d < -180) {
    d += 360;
  }
  return d;
}

export function formatDistance(m: number): string {
  if (m < 1000) {
    return `${Math.max(1, Math.round(m / 10) * 10)} m`;
  }
  return `${decimal(m / 1000, 1)} km`;
}

export const WALK_SPEED_MPS: number = 3.6 * 1000 / 3600;

export function walkMinutes(m: number): number {
  return Math.max(1, Math.round(m / WALK_SPEED_MPS / 60));
}

/** Położenie na trasie zawsze w kilometrach z jednym miejscem po przecinku, jak na makietach: "0,4 km". */
export function formatKm(m: number): string {
  return `${decimal(m / 1000, 1)} km`;
}

/** Przedział na trasie: "0,6-0,8 km". */
export function formatKmRange(a: number, b: number): string {
  const d = b - a < 150 ? 2 : 1;
  return `${decimal(a / 1000, d)}-${decimal(b / 1000, d)} km`;
}
