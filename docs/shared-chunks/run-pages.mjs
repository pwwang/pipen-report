// Mini SystemJS loader: instantiate a page entry against the real chunks with
// stubbed DOM. Any broken import wiring throws (undefined extends, missing fn).
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const baseDir = process.argv[2];
const entry = process.argv[3];

function makeElement() {
  return {
    style: { removeProperty() {}, setProperty() {}, getPropertyValue() { return ''; } },
    dataset: {}, children: [],
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    attributes: {},
    addEventListener() {}, removeEventListener() {},
    appendChild(c) { this.children.push(c); return c; },
    insertBefore(c) { this.children.push(c); return c; },
    removeChild() {}, replaceChildren() { this.children.length = 0; },
    setAttribute(k, v) { this.attributes[k] = String(v); },
    setAttributeNS(_, k, v) { this.attributes[k] = String(v); },
    removeAttribute(k) { delete this.attributes[k]; },
    removeAttributeNS(_, k) { delete this.attributes[k]; },
    getAttribute(k) { return this.attributes[k]; },
    getAttributeNS(_, k) { return this.attributes[k]; },
    hasAttribute(k) { return k in this.attributes; },
    querySelector() { return makeElement(); },
    querySelectorAll() { return []; },
    getBoundingClientRect() {
      return { width: 100, height: 50, top: 0, left: 0, right: 100, bottom: 50 };
    },
    clientWidth: 100, clientHeight: 50, offsetWidth: 100, offsetHeight: 50,
    scrollIntoView() {}, scrollTo() {}, focus() {}, blur() {}, click() {},
    remove() {}, dispatchEvent() { return true; },
    setPointerCapture() {}, releasePointerCapture() {}, hasPointerCapture() { return false; },
    contains() { return false; }, insertAdjacentHTML() {}, insertAdjacentElement() {},
    closest() { return null; }, matches() { return false; },
    textContent: '', innerHTML: '', value: '', checked: false, disabled: false,
    tagName: 'DIV', ownerDocument: null,
    parentNode: null, nextSibling: null, previousSibling: null,
    firstChild: null, lastChild: null, childNodes: [],
  };
}
const body = makeElement();
const document = {
  body, documentElement: body, head: body,
  getElementById() { return makeElement(); },
  getElementsByClassName() { return []; }, getElementsByTagName() { return []; },
  querySelector() { return makeElement(); }, querySelectorAll() { return []; },
  createElement() { return makeElement(); },
  createElementNS() { return makeElement(); },
  createTextNode() { return {}; },
  createDocumentFragment() { return makeElement(); },
  addEventListener() {}, removeEventListener() {},
  readyState: 'complete', visibilityState: 'visible',
  location: { href: 'http://localhost/report/index.html', hash: '' },
};
const windowStub = {
  location: document.location, document,
  addEventListener() {}, removeEventListener() {},
  innerWidth: 1024, innerHeight: 768, devicePixelRatio: 1,
  matchMedia() { return { matches: false, addEventListener() {}, removeEventListener() {} }; },
  requestAnimationFrame: (f) => setTimeout(f, 0),
  cancelAnimationFrame: clearTimeout,
  getComputedStyle() { return { position: 'static', display: 'block' }; },
};
const storage = {
  _d: {}, getItem(k) { return k in this._d ? this._d[k] : null; },
  setItem(k, v) { this._d[k] = String(v); }, removeItem(k) { delete this._d[k]; },
  clear() { this._d = {}; }, key(i) { return Object.keys(this._d)[i] ?? null; },
  get length() { return Object.keys(this._d).length; },
};
const sandbox = vm.createContext({
  localStorage: storage, sessionStorage: storage,
  System: {}, document, window: windowStub, location: document.location,
  navigator: { userAgent: 'node' }, self: windowStub, globalThis: null,
  console, setTimeout, clearTimeout, setInterval, clearInterval,
  EventTarget, Event, CustomEvent, AbortController,
  fetch, Request, Response, Headers,
  MutationObserver: class { observe() {} disconnect() {} takeRecords() { return []; } },
  ResizeObserver: class { observe() {} unobserve() {} disconnect() {} },
  IntersectionObserver: class { observe() {} unobserve() {} disconnect() {} },
  PerformanceObserver: class { observe() {} disconnect() {} },
  Image: class { constructor() { this.style = {}; this.addEventListener = () => {}; } },
  getSelection() { return { removeAllRanges() {}, addRange() {} }; },
  crypto: { getRandomValues: (a) => a, randomUUID: () => 'stub' },
  queueMicrotask: (f) => Promise.resolve().then(f),
  structuredClone: (v) => JSON.parse(JSON.stringify(v)),
  requestAnimationFrame: windowStub.requestAnimationFrame,
  URL: URL, URLSearchParams: URLSearchParams, TextEncoder, TextDecoder,
  Promise, Map, Set, WeakMap, WeakSet, Symbol, Reflect, Proxy, Object, Array,
  Number, String, Boolean, Math, JSON, Date, RegExp, Error, TypeError, RangeError,
  parseInt, parseFloat, isNaN, isFinite, encodeURIComponent, decodeURIComponent,
});
sandbox.globalThis = sandbox;
sandbox.self = sandbox;

const instances = new Map(); // url -> {deps, exports, setters, execute, declare}
const loaded = new Map();    // url -> true when register captured

function resolveDep(fromUrl, dep) {
  const u = new URL(dep, 'file://' + baseDir + '/' + fromUrl);
  return u.pathname.slice(1);
}

function instantiate(url) {
  if (instances.has(url)) return instances.get(url);
  const file = path.join(baseDir, url);
  const code = fs.readFileSync(file, 'utf8');
  let reg = null;
  sandbox.System.register = (deps, declare) => { reg = { deps, declare }; };
  try {
    vm.runInContext(code, sandbox, { filename: url });
  } catch (e) {
    throw new Error(`module eval failed: ${url}: ${e.message}`);
  }
  if (!reg) throw new Error(`no System.register in ${url}`);
  const exports = {};
  const inst = { url, deps: reg.deps.map((d) => resolveDep(url, d)), exports, declare: reg.declare };
  instances.set(url, inst);
  for (const dep of inst.deps) {
    if (!fs.existsSync(path.join(baseDir, dep))) throw new Error(`missing dep ${dep} of ${url}`);
    instantiate(dep);
  }
  return inst;
}

const executed = new Set();
function run(url) {
  if (executed.has(url)) return;
  executed.add(url);
  const inst = instances.get(url);
  const exp = inst.exports;
  const mod = inst.declare((name, value) => {
    if (name && typeof name === 'object') Object.assign(exp, name);
    else exp[name] = value;
    return value; // rollup assigns `const k = _export("globals", ...)`
  });
  for (const dep of inst.deps) run(dep);
  for (let i = 0; i < inst.deps.length; i++) {
    if (mod.setters && mod.setters[i]) mod.setters[i](instances.get(inst.deps[i]).exports);
  }
  try {
    mod.execute();
  } catch (e) {
    throw new Error(`execute failed: ${url}: ${e.message}`);
  }
  if (!Object.keys(exp).length) throw new Error(`no exports from ${url}`);
}

instantiate(entry);
run(entry);
console.log(`OK: ${entry} — loaded and executed (${instances.size} chunks)`);
process.exit(0);
