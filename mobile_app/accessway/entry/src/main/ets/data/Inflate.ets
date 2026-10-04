const LEN_BASE: number[] = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163,
  195, 227, 258];
const LEN_EXTRA: number[] = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0];
const DIST_BASE: number[] = [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049,
  3073, 4097, 6145, 8193, 12289, 16385, 24577];
const DIST_EXTRA: number[] = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13];
const CL_ORDER: number[] = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15];
const FAST_BITS: number = 9;

/**
 * Canonical Huffman code of DEFLATE: a lookup table of the first FAST_BITS bits (symbol and length packed as
 * symbol * 16 + length) and, for longer codes, the counts and symbols for decoding bit by bit.
 */
class Huffman {
  counts: Int32Array = new Int32Array(16);
  symbols: Int32Array;
  fast: Int32Array = new Int32Array(1 << FAST_BITS);

  constructor(lengths: Uint8Array | number[], n: number) {
    this.symbols = new Int32Array(n);
    for (let i = 0; i < n; i++) {
      this.counts[lengths[i]]++;
    }
    this.counts[0] = 0;
    const offs = new Int32Array(16);
    for (let len = 1; len < 16; len++) {
      offs[len] = offs[len - 1] + this.counts[len - 1];
    }
    for (let i = 0; i < n; i++) {
      if (lengths[i] !== 0) {
        this.symbols[offs[lengths[i]]++] = i;
      }
    }
    this.fast.fill(-1);
    let code = 0;
    let index = 0;
    for (let len = 1; len <= FAST_BITS; len++) {
      for (let k = 0; k < this.counts[len]; k++) {
        let rev = 0;
        for (let b = 0; b < len; b++) {
          rev |= ((code >> b) & 1) << (len - 1 - b);
        }
        for (let fill = rev; fill < (1 << FAST_BITS); fill += (1 << len)) {
          this.fast[fill] = this.symbols[index] * 16 + len;
        }
        code++;
        index++;
      }
      code <<= 1;
    }
  }
}

/** Bit reader and output of one inflate run. */
class InflateState {
  src: Uint8Array;
  pos: number;
  bitBuf: number = 0;
  bitCnt: number = 0;
  out: Uint8Array;
  outPos: number = 0;

  constructor(src: Uint8Array, pos: number, sizeHint: number) {
    this.src = src;
    this.pos = pos;
    this.out = new Uint8Array(Math.max(sizeHint, 1024));
  }

  need(n: number): void {
    while (this.bitCnt < n) {
      const b = this.pos < this.src.length ? this.src[this.pos] : 0;
      this.pos++;
      this.bitBuf |= b << this.bitCnt;
      this.bitCnt += 8;
    }
  }

  bits(n: number): number {
    if (n === 0) {
      return 0;
    }
    this.need(n);
    const v = this.bitBuf & ((1 << n) - 1);
    this.bitBuf >>>= n;
    this.bitCnt -= n;
    return v;
  }

  decode(h: Huffman): number {
    this.need(FAST_BITS);
    const hit = h.fast[this.bitBuf & ((1 << FAST_BITS) - 1)];
    if (hit >= 0) {
      const len = hit & 15;
      this.bitBuf >>>= len;
      this.bitCnt -= len;
      return hit >> 4;
    }
    let code = 0;
    let first = 0;
    let index = 0;
    for (let len = 1; len < 16; len++) {
      code |= this.bits(1);
      const count = h.counts[len];
      if (code - count < first) {
        return h.symbols[index + (code - first)];
      }
      index += count;
      first += count;
      first <<= 1;
      code <<= 1;
    }
    throw new Error('inflate: bad Huffman code');
  }

  ensure(extra: number): void {
    if (this.outPos + extra <= this.out.length) {
      return;
    }
    let size = this.out.length * 2;
    while (size < this.outPos + extra) {
      size *= 2;
    }
    const next = new Uint8Array(size);
    next.set(this.out.subarray(0, this.outPos));
    this.out = next;
  }
}

let fixedLit: Huffman | null = null;
let fixedDist: Huffman | null = null;

function fixedTables(): Huffman[] {
  if (fixedLit === null || fixedDist === null) {
    const l: number[] = [];
    for (let i = 0; i < 288; i++) {
      l.push(i < 144 ? 8 : (i < 256 ? 9 : (i < 280 ? 7 : 8)));
    }
    const d: number[] = [];
    for (let i = 0; i < 30; i++) {
      d.push(5);
    }
    fixedLit = new Huffman(l, 288);
    fixedDist = new Huffman(d, 30);
  }
  return [fixedLit as Huffman, fixedDist as Huffman];
}

function dynamicTables(s: InflateState): Huffman[] {
  const nlen = s.bits(5) + 257;
  const ndist = s.bits(5) + 1;
  const ncode = s.bits(4) + 4;
  const cl = new Uint8Array(19);
  for (let i = 0; i < ncode; i++) {
    cl[CL_ORDER[i]] = s.bits(3);
  }
  const clh = new Huffman(cl, 19);
  const lengths = new Uint8Array(nlen + ndist);
  let i = 0;
  while (i < nlen + ndist) {
    const sym = s.decode(clh);
    if (sym < 16) {
      lengths[i++] = sym;
      continue;
    }
    let rep = 0;
    let val = 0;
    if (sym === 16) {
      if (i === 0) {
        throw new Error('inflate: repeat with no previous length');
      }
      val = lengths[i - 1];
      rep = 3 + s.bits(2);
    } else if (sym === 17) {
      rep = 3 + s.bits(3);
    } else {
      rep = 11 + s.bits(7);
    }
    if (i + rep > nlen + ndist) {
      throw new Error('inflate: too many lengths');
    }
    while (rep-- > 0) {
      lengths[i++] = val;
    }
  }
  return [new Huffman(lengths.subarray(0, nlen), nlen), new Huffman(lengths.subarray(nlen), ndist)];
}

function inflateBlock(s: InflateState, lit: Huffman, dist: Huffman): void {
  for (;;) {
    const sym = s.decode(lit);
    if (sym < 256) {
      s.ensure(1);
      s.out[s.outPos++] = sym;
    } else if (sym === 256) {
      return;
    } else {
      const li = sym - 257;
      if (li >= 29) {
        throw new Error('inflate: bad length symbol');
      }
      const len = LEN_BASE[li] + s.bits(LEN_EXTRA[li]);
      const di = s.decode(dist);
      if (di >= 30) {
        throw new Error('inflate: bad distance symbol');
      }
      const d = DIST_BASE[di] + s.bits(DIST_EXTRA[di]);
      if (d > s.outPos) {
        throw new Error('inflate: distance too far back');
      }
      s.ensure(len);
      const o = s.out;
      let p = s.outPos;
      for (let k = 0; k < len; k++) {
        o[p] = o[p - d];
        p++;
      }
      s.outPos = p;
    }
  }
}

/** Inflates raw DEFLATE data (RFC 1951) that starts at `pos` of `src`. */
export function inflateRaw(src: Uint8Array, pos: number, sizeHint: number): Uint8Array {
  const s = new InflateState(src, pos, sizeHint);
  let last = 0;
  while (last === 0) {
    last = s.bits(1);
    const type = s.bits(2);
    if (type === 0) {
      s.pos -= s.bitCnt >> 3;
      s.bitBuf = 0;
      s.bitCnt = 0;
      const len = s.src[s.pos] | (s.src[s.pos + 1] << 8);
      s.pos += 4;
      s.ensure(len);
      s.out.set(s.src.subarray(s.pos, s.pos + len), s.outPos);
      s.outPos += len;
      s.pos += len;
    } else if (type === 1) {
      const t = fixedTables();
      inflateBlock(s, t[0], t[1]);
    } else if (type === 2) {
      const t = dynamicTables(s);
      inflateBlock(s, t[0], t[1]);
    } else {
      throw new Error('inflate: bad block type');
    }
  }
  return s.out.subarray(0, s.outPos);
}

/** True when the bytes start with the gzip magic number. */
export function isGzip(src: Uint8Array): boolean {
  return src.length > 18 && src[0] === 0x1f && src[1] === 0x8b;
}

/** Unpacks one gzip member (RFC 1952), the compression PMTiles uses for directories and tiles. */
export function gunzip(src: Uint8Array): Uint8Array {
  if (!isGzip(src) || src[2] !== 8) {
    throw new Error('gunzip: not gzip data');
  }
  const flg = src[3];
  let pos = 10;
  if ((flg & 4) !== 0) {
    pos += 2 + (src[pos] | (src[pos + 1] << 8));
  }
  if ((flg & 8) !== 0) {
    while (src[pos++] !== 0) {
    }
  }
  if ((flg & 16) !== 0) {
    while (src[pos++] !== 0) {
    }
  }
  if ((flg & 2) !== 0) {
    pos += 2;
  }
  const n = src.length;
  const isize = (src[n - 4] | (src[n - 3] << 8) | (src[n - 2] << 16) | (src[n - 1] << 24)) >>> 0;
  return inflateRaw(src, pos, isize);
}
