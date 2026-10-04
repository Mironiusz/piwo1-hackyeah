/**
 * Runs the platform-independent unit tests (accessway/entry/src/test/*.test.ets) on Node.js.
 * Sources are transpiled with the TypeScript fork shipped in the OpenHarmony SDK (ets-loader),
 * and @ohos/hypium is replaced by a tiny compatible shim. Device tests still run with hvigor.
 *
 * Usage: node tools/run-unit-tests.js <path-to-sdk-ets-dir> [app-dir, default accessway]
 *   e.g. node tools/run-unit-tests.js ~/setup-ohos-sdk/linux/20/ets
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const sdkEts = process.argv[2];
if (!sdkEts) {
  console.error('Usage: node tools/run-unit-tests.js <sdk ets dir>');
  process.exit(2);
}
const ts = require(path.join(sdkEts, 'build-tools/ets-loader/node_modules/typescript'));
const entryDir = path.resolve(__dirname, '..', process.argv[3] || 'accessway', 'entry', 'src');
const out = fs.mkdtempSync(path.join(os.tmpdir(), 'accessway-ut-'));

function walk(dir, acc) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) walk(p, acc);
    else if (f.endsWith('.ets') || f.endsWith('.ts')) acc.push(p);
  }
  return acc;
}

const sources = walk(path.join(entryDir, 'main', 'ets'), []).concat(walk(path.join(entryDir, 'test'), []));
for (const src of sources) {
  const rel = path.relative(entryDir, src).replace(/\.e?ts$/, '.js');
  const dst = path.join(out, rel);
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  let code = fs.readFileSync(src, 'utf8');
  if (/^\s*@(Entry|Component|Observed)/m.test(code) || code.includes('@kit.')) {
    continue;
  }
  const res = ts.transpileModule(code, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2021 } });
  fs.writeFileSync(dst, res.outputText);
}

const hyp = path.join(out, 'node_modules', '@ohos', 'hypium');
fs.mkdirSync(hyp, { recursive: true });
fs.writeFileSync(path.join(hyp, 'index.js'), `
const suites = [];
let current = null;
function describe(name, fn) { current = { name, tests: [] }; suites.push(current); fn(); }
function it(name, _filter, fn) { current.tests.push({ name, fn }); }
function fail(msg) { throw new Error(msg); }
function expect(actual) {
  return {
    assertEqual: (e) => { if (actual !== e) fail('expected ' + JSON.stringify(e) + ' but got ' + JSON.stringify(actual)); },
    assertTrue: () => { if (actual !== true) fail('expected true but got ' + JSON.stringify(actual)); },
    assertFalse: () => { if (actual !== false) fail('expected false but got ' + JSON.stringify(actual)); },
    assertContain: (e) => { if (String(actual).indexOf(e) < 0) fail('expected to contain ' + JSON.stringify(e)); }
  };
}
module.exports = { describe, it, expect, suites, beforeAll() {}, beforeEach() {}, afterEach() {}, afterAll() {} };
`);

let failed = 0;
let passed = 0;
for (const f of fs.readdirSync(path.join(out, 'test')).filter((f) => f.endsWith('.test.js'))) {
  const mod = require(path.join(out, 'test', f));
  if (typeof mod.default === 'function') mod.default();
}
const { suites } = require(hyp);
for (const s of suites) {
  for (const t of s.tests) {
    try {
      t.fn();
      passed++;
      console.log('  ok   ' + s.name + ' > ' + t.name);
    } catch (e) {
      failed++;
      console.log('  FAIL ' + s.name + ' > ' + t.name + ': ' + e.message);
    }
  }
}
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
