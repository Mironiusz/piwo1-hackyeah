"""
PMTiles v3 reader and writer plus a Mapbox Vector Tile decoder and encoder, standard library only.

The mock backend uses the reader to report the zoom range of the archive it serves, the decoder is kept to inspect tiles by hand,
and the sample tile generator uses the writer and encoder. Specifications followed:
https://github.com/protomaps/PMTiles/blob/main/spec/v3/spec.md and https://github.com/mapbox/vector-tile-spec.
"""

import gzip
import math
import struct

COMPRESSION_NONE = 1
COMPRESSION_GZIP = 2
TILE_TYPE_MVT = 1
HEADER_LEN = 127


def zxy_to_tileid(z, x, y):
    """Hilbert tile id of PMTiles v3, the same algorithm as go-pmtiles ZxyToID."""
    if z == 0:
        return 0
    acc = ((1 << (z * 2)) - 1) // 3
    s = 1 << (z - 1)
    while s > 0:
        rx = s & x
        ry = s & y
        acc += ((3 * rx) ^ ry) * s
        if ry == 0:
            if rx != 0:
                x = s - 1 - x
                y = s - 1 - y
            x, y = y, x
        s >>= 1
    return acc


def read_varint(buf, pos):
    result = 0
    shift = 0
    while True:
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if b < 0x80:
            return result, pos
        shift += 7


def write_varint(out, v):
    while v >= 0x80:
        out.append((v & 0x7F) | 0x80)
        v >>= 7
    out.append(v)


def decompress(data, kind):
    if kind == COMPRESSION_GZIP:
        return gzip.decompress(data)
    if kind in (0, COMPRESSION_NONE):
        return data
    raise ValueError("unsupported compression %d (only none and gzip)" % kind)


def deserialize_directory(raw):
    n, pos = read_varint(raw, 0)
    ids = []
    last = 0
    for _ in range(n):
        d, pos = read_varint(raw, pos)
        last += d
        ids.append(last)
    runs = []
    for _ in range(n):
        v, pos = read_varint(raw, pos)
        runs.append(v)
    lens = []
    for _ in range(n):
        v, pos = read_varint(raw, pos)
        lens.append(v)
    offs = []
    for i in range(n):
        v, pos = read_varint(raw, pos)
        if v == 0 and i > 0:
            offs.append(offs[i - 1] + lens[i - 1])
        else:
            offs.append(v - 1)
    return list(zip(ids, runs, lens, offs))


def serialize_directory(entries):
    out = bytearray()
    write_varint(out, len(entries))
    last = 0
    for e in entries:
        write_varint(out, e[0] - last)
        last = e[0]
    for e in entries:
        write_varint(out, e[1])
    for e in entries:
        write_varint(out, e[2])
    for i, e in enumerate(entries):
        if i > 0 and e[3] == entries[i - 1][3] + entries[i - 1][2]:
            write_varint(out, 0)
        else:
            write_varint(out, e[3] + 1)
    return bytes(out)


class PMTilesReader:
    """Random access to one archive file; directories are cached after the first read."""

    def __init__(self, path):
        self.f = open(path, "rb")
        h = self.f.read(HEADER_LEN)
        if h[:7] != b"PMTiles" or h[7] != 3:
            raise ValueError("not a PMTiles v3 archive")
        (self.root_off, self.root_len, self.meta_off, self.meta_len, self.leaf_off, self.leaf_len,
         self.data_off, self.data_len, _, _, _) = struct.unpack_from("<11Q", h, 8)
        (self.clustered, self.internal_comp, self.tile_comp, self.tile_type, self.min_zoom,
         self.max_zoom) = struct.unpack_from("<6B", h, 96)
        (self.min_lon, self.min_lat, self.max_lon, self.max_lat) = [v / 1e7 for v in struct.unpack_from("<4i", h, 102)]
        self.center_zoom = h[118]
        self.center_lon, self.center_lat = [v / 1e7 for v in struct.unpack_from("<2i", h, 119)]
        self._dirs = {}

    def _read(self, off, length):
        self.f.seek(off)
        return self.f.read(length)

    def _dir(self, off, length):
        key = (off, length)
        if key not in self._dirs:
            self._dirs[key] = deserialize_directory(decompress(self._read(off, length), self.internal_comp))
        return self._dirs[key]

    def metadata(self):
        import json
        if self.meta_len == 0:
            return {}
        return json.loads(decompress(self._read(self.meta_off, self.meta_len), self.internal_comp))

    def get(self, z, x, y):
        """Raw (still compressed) tile bytes, or None when the archive has no such tile."""
        tid = zxy_to_tileid(z, x, y)
        off, length = self.root_off, self.root_len
        for _ in range(4):
            entries = self._dir(off, length)
            lo, hi = 0, len(entries) - 1
            found = None
            while lo <= hi:
                mid = (lo + hi) // 2
                if entries[mid][0] <= tid:
                    found = entries[mid]
                    lo = mid + 1
                else:
                    hi = mid - 1
            if found is None:
                return None
            eid, run, elen, eoff = found
            if run == 0:
                off, length = self.leaf_off + eoff, elen
                continue
            if tid < eid + run:
                return self._read(self.data_off + eoff, elen)
            return None
        return None

    def tile(self, z, x, y):
        raw = self.get(z, x, y)
        if raw is None:
            return None
        return decompress(raw, self.tile_comp)


def write_pmtiles(path, tiles, min_zoom, max_zoom, bounds, center, metadata):
    """Writes an archive from {(z, x, y): mvt bytes}; tiles are gzip compressed, one root directory."""
    import json
    items = sorted(((zxy_to_tileid(*k), v) for k, v in tiles.items()), key=lambda t: t[0])
    data = bytearray()
    entries = []
    for tid, mvt in items:
        blob = gzip.compress(mvt, mtime=0)
        entries.append((tid, 1, len(blob), len(data)))
        data += blob
    root = gzip.compress(serialize_directory(entries), mtime=0)
    meta = gzip.compress(json.dumps(metadata).encode("utf-8"), mtime=0)
    root_off = HEADER_LEN
    meta_off = root_off + len(root)
    data_off = meta_off + len(meta)
    header = bytearray(b"PMTiles") + bytes([3])
    header += struct.pack("<11Q", root_off, len(root), meta_off, len(meta), data_off, 0, data_off, len(data),
                          len(entries), len(entries), len(entries))
    header += struct.pack("<6B", 1, COMPRESSION_GZIP, COMPRESSION_GZIP, TILE_TYPE_MVT, min_zoom, max_zoom)
    header += struct.pack("<4i", *[int(round(v * 1e7)) for v in bounds])
    header += struct.pack("<B2i", center[2], int(round(center[0] * 1e7)), int(round(center[1] * 1e7)))
    assert len(header) == HEADER_LEN
    with open(path, "wb") as f:
        f.write(header)
        f.write(root)
        f.write(meta)
        f.write(data)


def _fields(buf):
    pos = 0
    n = len(buf)
    while pos < n:
        key, pos = read_varint(buf, pos)
        field, wire = key >> 3, key & 7
        if wire == 0:
            v, pos = read_varint(buf, pos)
            yield field, wire, v
        elif wire == 2:
            ln, pos = read_varint(buf, pos)
            yield field, wire, buf[pos:pos + ln]
            pos += ln
        elif wire == 1:
            yield field, wire, buf[pos:pos + 8]
            pos += 8
        elif wire == 5:
            yield field, wire, buf[pos:pos + 4]
            pos += 4
        else:
            raise ValueError("unsupported wire type %d" % wire)


def _packed(buf):
    out = []
    pos = 0
    while pos < len(buf):
        v, pos = read_varint(buf, pos)
        out.append(v)
    return out


def _zigzag(v):
    return (v >> 1) ^ -(v & 1)


def _value(buf):
    for field, wire, v in _fields(buf):
        if field == 1:
            return bytes(v).decode("utf-8", "replace")
        if field == 2:
            return struct.unpack("<f", v)[0]
        if field == 3:
            return struct.unpack("<d", v)[0]
        if field in (4, 5):
            return v
        if field == 6:
            return _zigzag(v)
        if field == 7:
            return bool(v)
    return None


def _geometry(cmds):
    """Command stream to a list of parts, each a list of (x, y) in tile pixels."""
    parts = []
    cur = None
    x = y = 0
    i = 0
    while i < len(cmds):
        c = cmds[i]
        i += 1
        cid, count = c & 7, c >> 3
        if cid == 1:
            for _ in range(count):
                x += _zigzag(cmds[i])
                y += _zigzag(cmds[i + 1])
                i += 2
                cur = [(x, y)]
                parts.append(cur)
        elif cid == 2:
            for _ in range(count):
                x += _zigzag(cmds[i])
                y += _zigzag(cmds[i + 1])
                i += 2
                if cur is not None:
                    cur.append((x, y))
        elif cid == 7:
            if cur:
                cur.append(cur[0])
    return parts


def decode_mvt(data):
    """MVT bytes to {layer name: (extent, [ {type, props, parts} ])}."""
    layers = {}
    for field, _, lbuf in _fields(data):
        if field != 3:
            continue
        name = ""
        extent = 4096
        keys, values, feats = [], [], []
        for lf, _, v in _fields(lbuf):
            if lf == 1:
                name = bytes(v).decode("utf-8")
            elif lf == 2:
                feats.append(v)
            elif lf == 3:
                keys.append(bytes(v).decode("utf-8"))
            elif lf == 4:
                values.append(_value(v))
            elif lf == 5:
                extent = v
        out = []
        for fbuf in feats:
            ftype, tags, geom = 0, [], []
            for ff, _, v in _fields(fbuf):
                if ff == 2:
                    tags = _packed(v)
                elif ff == 3:
                    ftype = v
                elif ff == 4:
                    geom = _packed(v)
            props = {}
            for k in range(0, len(tags) - 1, 2):
                if tags[k] < len(keys) and tags[k + 1] < len(values):
                    props[keys[tags[k]]] = values[tags[k + 1]]
            out.append({"type": ftype, "props": props, "parts": _geometry(geom)})
        layers[name] = (extent, out)
    return layers


def tile_to_lonlat(z, x, y, px, py, extent):
    n = 1 << z
    wx = (x + px / extent) / n
    wy = (y + py / extent) / n
    lon = wx * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * wy))))
    return lon, lat


def lonlat_to_tile_px(z, x, y, lon, lat, extent):
    n = 1 << z
    wx = (lon + 180.0) / 360.0
    s = math.sin(math.radians(lat))
    wy = 0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)
    return int(round((wx * n - x) * extent)), int(round((wy * n - y) * extent))


def lonlat_to_tile(z, lon, lat):
    n = 1 << z
    s = math.sin(math.radians(lat))
    wy = 0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)
    return int((lon + 180.0) / 360.0 * n), int(wy * n)


def _write_field_bytes(out, field, data):
    write_varint(out, (field << 3) | 2)
    write_varint(out, len(data))
    out += data


def _write_field_varint(out, field, v):
    write_varint(out, field << 3)
    write_varint(out, v)


def _zz(v):
    return (v << 1) if v >= 0 else ((-v) << 1) - 1


def encode_mvt(layers, extent=4096):
    """{layer name: [ {type 1|2|3, props {str: str}, parts [[(x, y), ...]]} ]} to MVT bytes."""
    tile = bytearray()
    for name, feats in layers.items():
        keys, values = [], []
        layer = bytearray()
        _write_field_varint(layer, 15, 2)
        _write_field_bytes(layer, 1, name.encode("utf-8"))
        for f in feats:
            tags = []
            for k, v in f["props"].items():
                if k not in keys:
                    keys.append(k)
                if v not in values:
                    values.append(v)
                tags += [keys.index(k), values.index(v)]
            geom = []
            cx = cy = 0
            for part in f["parts"]:
                pts = part[:-1] if f["type"] == 3 and len(part) > 1 and part[0] == part[-1] else part
                if not pts:
                    continue
                geom.append((1 & 7) | (1 << 3))
                geom += [_zz(pts[0][0] - cx), _zz(pts[0][1] - cy)]
                cx, cy = pts[0]
                if f["type"] != 1 and len(pts) > 1:
                    geom.append((2 & 7) | ((len(pts) - 1) << 3))
                    for px, py in pts[1:]:
                        geom += [_zz(px - cx), _zz(py - cy)]
                        cx, cy = px, py
                if f["type"] == 3:
                    geom.append((7 & 7) | (1 << 3))
            feat = bytearray()
            if tags:
                packed = bytearray()
                for t in tags:
                    write_varint(packed, t)
                _write_field_bytes(feat, 2, bytes(packed))
            _write_field_varint(feat, 3, f["type"])
            packed = bytearray()
            for g in geom:
                write_varint(packed, g)
            _write_field_bytes(feat, 4, bytes(packed))
            _write_field_bytes(layer, 2, bytes(feat))
        for k in keys:
            _write_field_bytes(layer, 3, k.encode("utf-8"))
        for v in values:
            val = bytearray()
            _write_field_bytes(val, 1, str(v).encode("utf-8"))
            _write_field_bytes(layer, 4, bytes(val))
        _write_field_varint(layer, 5, extent)
        _write_field_bytes(tile, 3, bytes(layer))
    return bytes(tile)
