// In-process replica of check.py gate #1 (inline <script> syntax),
// but without spawning 2044 node subprocesses. One process, vm.Script per chunk.
import { readFileSync, readdirSync, statSync } from 'fs';
import { join } from 'path';
import vm from 'vm';

const ROOT = process.argv[2] || 'dist';
const SCRIPT_TAG = /<script([^>]*)>(.*?)<\/script>/gs;
const JS_TYPES = ['', 'text/javascript', 'application/javascript', 'module'];
const VERIFY_PREFIXES = ['baidu_verify_', 'google', 'yandex_', 'msvalidate', 'sogou_verify_', '360verify', 'bing', 'indexnow'];

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) out.push(...walk(p));
    else if (name.endsWith('.html')) out.push(p);
  }
  return out;
}

const files = walk(ROOT).filter(f => {
  // skip root-level third-party verify files
  const rel = f.slice(ROOT.length + 1);
  if (!rel.includes('/') && VERIFY_PREFIXES.some(v => rel.toLowerCase().startsWith(v))) return false;
  return true;
});

let checked = 0, errors = [];
for (const f of files.sort()) {
  const html = readFileSync(f, 'utf-8');
  let m;
  SCRIPT_TAG.lastIndex = 0;
  let idx = 0;
  while ((m = SCRIPT_TAG.exec(html))) {
    const attrs = m[1], body = m[2];
    if (/\bsrc=/.test(attrs)) continue;
    const tm = attrs.match(/\btype=["']([^"']*)["']/);
    if (tm && !JS_TYPES.includes(tm[1].toLowerCase())) continue;
    if (!body.trim()) continue;
    checked++;
    try {
      new vm.Script(body, { filename: `${f}#${idx}` });
    } catch (e) {
      errors.push(`${f} script#${idx}: ${e.message.split('\n')[0]}`);
    }
    idx++;
  }
}
console.log(`inline scripts checked: ${checked}`);
if (errors.length) {
  console.log(`❌ ${errors.length} syntax errors`);
  for (const e of errors.slice(0, 20)) console.log('  - ' + e);
  process.exit(1);
} else {
  console.log('✅ all inline scripts OK');
}
