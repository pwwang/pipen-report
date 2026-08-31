// Verify report pages: setter[i] is aligned with deps[i]; every name a setter
// asks must be exported by the chunk it points to.
import fs from 'node:fs';
import path from 'node:path';

const dir = process.argv[2];
const entry = process.argv[3];

function skipString(code, i, q) {
  for (let j = i + 1; j < code.length; j++) {
    if (code[j] === '\\') { j++; continue; }
    if (q === '`' && code[j] === '$' && code[j + 1] === '{') {
      let d = 1;
      for (let k = j + 2; k < code.length; k++) {
        const ch = code[k];
        if (ch === '"' || ch === "'" || ch === '`') { k = skipString(code, k, ch); continue; }
        if (ch === '{') d++;
        else if (ch === '}') { if (--d === 0) { j = k; break; } }
      }
      continue;
    }
    if (code[j] === q) return j;
  }
  return i;
}

function exportNames(file) {
  const code = fs.readFileSync(file, 'utf8');
  // the export function is the register's first parameter (t, e, ...)
  const pm = code.match(/System\.register\(\[[^\]]*\]\s*,\s*function\(([\w$]+)\)/);
  const exp = pm ? pm[1] : 't';
  const names = new Set();
  // per-name exp("name", value) — value may be fn/class/obj/array/string/literal/var
  for (const m of code.matchAll(new RegExp('\\(["\']([A-Za-z_$][\\w$]*)["\']\\s*,\\s*[^),]', 'g'))) {
    names.add(m[1]);
  }
  // exp({key:value,...}) big-object export form: collect every depth-1 identifier key,
  // value type irrelevant (functions, classes, or aliased variables)
  for (let i = 0; i < code.length - 2; i++) {
    if (code[i] !== exp || code[i + 1] !== '(' || code[i + 2] !== '{') continue;
    let depth = 0;
    for (let j = i + 2; j < code.length; j++) {
      const c = code[j];
      if (c === '"' || c === "'" || c === '`') { j = skipString(code, j, c); continue; }
      if (c === '{') depth++;
      else if (c === '}') { if (--depth === 0) break; }
      else if (depth === 1 && c === ':') {
        let k = j - 1;
        while (k > i && /[\w$]/.test(code[k])) k--;
        const key = code.slice(k + 1, j);
        if (/^[\w$]+$/.test(key)) names.add(key);
      }
    }
  }
  return names;
}

function parseChunk(file) {
  const code = fs.readFileSync(file, 'utf8');
  const m = code.match(/System\.register\(\[(.*?)\],/);
  const deps = m && m[1].trim() ? [...m[1].matchAll(/"([^"]+)"/g)].map(x => x[1]) : [];
  // setters are aligned with deps positionally; elements are `function(P){...}`
  // (flat bodies) or `null` — split on top-level commas, not on '},'
  const sm = code.match(/setters:\[(.*)\],execute/s);
  const setters = [];
  if (sm) {
    let depth = 0, cur = '';
    for (const ch of sm[1]) {
      if (ch === '{') depth++;
      else if (ch === '}') depth--;
      else if (ch === ',' && depth === 0) { setters.push(cur.trim()); cur = ''; continue; }
      cur += ch;
    }
    setters.push(cur.trim());
  }
  const requested = setters.map((s) => {
    const fn = s.match(/function\((\w+)\)\{(.*)$/s);
    if (!fn) return []; // null or empty
    return [...fn[2].matchAll(new RegExp(fn[1] + '\\.([A-Za-z_$][\\w$]*)', 'g'))].map(x => x[1]);
  });
  return { deps, requested };
}

const issues = [];
const visited = new Set();
function check(file) {
  const abs = path.resolve(dir, file);
  if (visited.has(abs)) return;
  visited.add(abs);
  if (!fs.existsSync(abs)) { issues.push(`${file}: FILE MISSING`); return; }
  const { deps, requested } = parseChunk(abs);
  for (let i = 0; i < deps.length; i++) {
    const dep = path.relative(dir, path.resolve(path.dirname(abs), deps[i]));
    const depAbs = path.resolve(dir, dep);
    if (!fs.existsSync(depAbs)) { issues.push(`${file}: dep ${deps[i]} MISSING`); continue; }
    if (i >= requested.length) continue;
    const missing = [...new Set(requested[i])].filter(n => !exportNames(depAbs).has(n));
    if (missing.length) issues.push(`${file}: dep ${deps[i]} lacks exports ${missing.join(', ')}`);
    check(dep);
  }
}

check(entry);
if (issues.length) { console.log('ISSUES:\n' + [...new Set(issues)].join('\n')); process.exit(1); }
console.log(`OK: ${entry} — all deps present, all requested names exported (${visited.size} chunks loaded)`);
