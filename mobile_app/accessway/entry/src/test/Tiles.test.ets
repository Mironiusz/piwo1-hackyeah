import { describe, it, expect } from '@ohos/hypium';
import { gunzip, inflateRaw } from '../main/ets/data/Inflate';
import { decodeMvt, utf8 } from '../main/ets/data/Mvt';
import { findEntry, parseDirectory, parseHeader, zxyToTileId } from '../main/ets/data/Pmtiles';

const SAMPLE_PMTILES: string[] = [
  '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'
];
const GZIP_TEXT: string = 'H4sIAAAAAAAC//MuSsw+vLlcISm1SiEpsSgztUhHwXtUbFRsVAwsdqT1yMyjs4+0H91zdNfhzUebFAwMjYxNTM3MLSwB7NHZlzsDAAA=';
const RAW_FIXED: string = 'S0xKToQhhYzUnJx8CAkA';
const RAW_STORED: string = 'AREA7v9zdG9yZWQgYmxvY2sgZGF0YQ==';
const B64: string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

function fromBase64(s: string): Uint8Array {
  const clean = s.replace(/=+$/, '');
  const out = new Uint8Array(Math.floor(clean.length * 3 / 4));
  let bits = 0;
  let acc = 0;
  let o = 0;
  for (let i = 0; i < clean.length; i++) {
    acc = (acc << 6) | B64.indexOf(clean.charAt(i));
    bits += 6;
    if (bits >= 8) {
      bits -= 8;
      out[o++] = (acc >> bits) & 0xff;
    }
  }
  return out;
}

function text(b: Uint8Array): string {
  return utf8(b, 0, b.length);
}

export default function tilesTest() {
  describe('Tiles', () => {
    it('hilbert_tile_ids_match_the_spec', 0, () => {
      expect([zxyToTileId(0, 0, 0), zxyToTileId(1, 1, 0), zxyToTileId(3, 5, 2), zxyToTileId(12, 2275, 1387),
        zxyToTileId(15, 18204, 11103)].join(',')).assertEqual('0,4,76,19873333,1271893338');
    });
    it('inflate_dynamic_fixed_and_stored_blocks', 0, () => {
      const t = text(gunzip(fromBase64(GZIP_TEXT)));
      expect(t.length).assertEqual(779);
      expect(t.endsWith('ąęśćżźół 0123456789')).assertTrue();
      expect(text(inflateRaw(fromBase64(RAW_FIXED), 0, 8))).assertEqual('abcabcabcabc hello hello');
      expect(text(inflateRaw(fromBase64(RAW_STORED), 0, 8))).assertEqual('stored block data');
    });
    it('archive_header_directory_and_tile', 0, () => {
      const all = fromBase64(SAMPLE_PMTILES.join(''));
      const h = parseHeader(all);
      expect(h.minZoom).assertEqual(12);
      expect(h.maxZoom).assertEqual(15);
      const root = parseDirectory(gunzip(all.subarray(h.rootOffset, h.rootOffset + h.rootLength)));
      expect(root.ids.length).assertEqual(35);
      expect(findEntry(root, zxyToTileId(14, 0, 0)) === null).assertTrue();
      const e = findEntry(root, zxyToTileId(14, 9102, 5551));
      expect(e !== null && !e.leaf).assertTrue();
      if (e === null) {
        return;
      }
      const raw = all.subarray(h.dataOffset + e.offset, h.dataOffset + e.offset + e.length);
      const t = decodeMvt(gunzip(raw), 14, 9102, 5551);
      expect(t.extent).assertEqual(512);
      expect(t.fills.green.length).assertEqual(1);
      expect(t.fills.building.length).assertEqual(6);
      expect(t.lines.path.length).assertEqual(11);
      expect(t.lines.minor.length).assertEqual(1);
      expect(t.labels.length).assertEqual(1);
    });
    it('low_zoom_drops_paths_and_buildings', 0, () => {
      const all = fromBase64(SAMPLE_PMTILES.join(''));
      const h = parseHeader(all);
      const root = parseDirectory(gunzip(all.subarray(h.rootOffset, h.rootOffset + h.rootLength)));
      const e = findEntry(root, zxyToTileId(13, 4551, 2775));
      if (e === null) {
        expect(false).assertTrue();
        return;
      }
      const t = decodeMvt(gunzip(all.subarray(h.dataOffset + e.offset, h.dataOffset + e.offset + e.length)), 13, 4551, 2775);
      expect(t.fills.building.length).assertEqual(0);
      expect(t.lines.path.length).assertEqual(0);
      expect(t.lines.minor.length).assertEqual(1);
    });
  });
}
