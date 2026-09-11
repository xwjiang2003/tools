// json-tools.js — JSON format, compress, validate, diff, convert, JSONPath, tree
// ============================================================
// DEMO DATA
// ============================================================
const demoJson = JSON.stringify({"name":"JSON Tools","version":"1.0.0","author":{"name":"Dev","email":"dev@example.com"},"tags":["json","formatter"],"settings":{"theme":"light","indent":4}}, null, 2);
const demoJson2 = JSON.stringify({"name":"JSON Tools Pro","version":"2.0.0","author":{"name":"Dev Team","email":"team@example.com"},"tags":["json","formatter","diff"],"settings":{"theme":"dark","indent":2}}, null, 2);
const jsonPathDemoData = JSON.stringify({"store":{"name":"图书商店","books":[{"title":"JS高级编程","price":89.9,"author":"Nicholas"},{"title":"Node.js深入浅出","price":69.9,"author":"朴灵"}],"location":{"city":"北京","address":"海淀区"}}}, null, 2);

// ============================================================
// 1. JSON TOOLS PAGE
// ============================================================
let jsonCurrentOp = 'format';
let jsonTreeCollapsed = {}, jsonTreeData = null;

function switchJsonTab(tabName) {
  document.querySelectorAll('.json-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.json-tab-content').forEach(c => c.classList.remove('active'));
  const tabBtn = document.querySelector(`.json-tab[data-tab="${tabName}"]`);
  const tabContent = document.getElementById('jsonTab' + tabName.charAt(0).toUpperCase() + tabName.slice(1));
  if (tabBtn) tabBtn.classList.add('active');
  if (tabContent) tabContent.classList.add('active');
  // Refresh editors after switching (they may have been 0-height when hidden)
  setTimeout(() => {
    if (tabName === 'diff') { editors['diffInputA']?.refresh(); editors['diffInputB']?.refresh(); }
    if (tabName === 'convert') { editors['convertInput']?.refresh(); editors['convertOutput']?.refresh(); }
    if (tabName === 'jsonpath') { editors['jsonpathInput']?.refresh(); }
    resizeAllEditors();
  }, 100);
}

function initJsonPage() {
  // Create all editors
  createCM('mainJsonInput');
  createCM('diffInputA'); createCM('diffInputB');
  createCM('convertInput'); createCM('convertOutput', true);
  createCM('jsonpathInput');

  // Tab click handlers
  document.querySelectorAll('.json-tab').forEach(tab => {
    tab.addEventListener('click', () => switchJsonTab(tab.dataset.tab));
  });

  // Basic ops button handlers
  document.querySelectorAll('#jsonOpBtns .op-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('#jsonOpBtns .op-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      jsonCurrentOp = btn.dataset.op;
      updateJsonOptions();
      runJsonOp(jsonCurrentOp);
    };
  });
  updateJsonOptions();

  // Load demo data（延迟载入：若用户在这 300ms 内已经开始输入，就不要再覆盖他）
  setTimeout(() => {
    if (getVal('mainJsonInput').trim()) return;
    setVal('mainJsonInput', demoJson); runJsonOp('format');
    setVal('diffInputA', demoJson); setVal('diffInputB', demoJson2);
    setVal('convertInput', demoJson);
    setVal('jsonpathInput', jsonPathDemoData);
    document.getElementById('jsonpathExpr').value = '$.store.books[0].title';
  }, 300);
}

function updateJsonOptions() {
  const o = document.getElementById('jsonOpOptions');
  const titles = {format:'格式化结果',compress:'压缩结果',validate:'校验结果',sort:'排序结果',escape:'转义结果',tree:'树形视图'};
  document.getElementById('jsonResultTitle').textContent = titles[jsonCurrentOp] || '结果';
  switch (jsonCurrentOp) {
    case 'format': o.innerHTML = '<span style="color:var(--text-secondary)">缩进:</span><select id="jsonIndent" onchange="runJsonOp(\'format\')"><option value="2">2空格</option><option value="4" selected>4空格</option><option value="tab">Tab</option></select>'; break;
    case 'compress': case 'validate': o.innerHTML = ''; break;
    case 'sort': o.innerHTML = '<span style="color:var(--text-secondary)">顺序:</span><select id="jsonSortOrder" onchange="runJsonOp(\'sort\')"><option value="asc">升序 A-Z</option><option value="desc">降序 Z-A</option></select>'; break;
    case 'escape': o.innerHTML = '<button class="btn btn-sm btn-primary" onclick="runJsonOp(\'escape\')">转义</button><button class="btn btn-sm btn-primary" onclick="runJsonOp(\'unescape\')">去转义</button>'; break;
    case 'tree': o.innerHTML = '<button class="btn btn-sm" onclick="jsonTreeExpandAll()">展开全部</button><button class="btn btn-sm" onclick="jsonTreeCollapseAll()">折叠全部</button>'; break;
  }
}

function runJsonOp(op) {
  const input = getVal('mainJsonInput');
  if (!input.trim()) { toast('请先输入 JSON','error'); return; }
  switch (op) {
    case 'format': {
      const r = safeParse(input);
      if (!r.success) { showJsonError(r); return; }
      const ind = document.getElementById('jsonIndent')?.value || '4';
      const istr = ind === 'tab' ? '\t' : parseInt(ind);
      const out = JSON.stringify(r.data, null, istr);
      showJsonResult(out);
      showJsonStats('📝 ' + formatBytes(new TextEncoder().encode(out).length));
      toast('格式化完成'); break;
    }
    case 'compress': {
      const r = safeParse(input);
      if (!r.success) { showJsonError(r); return; }
      const out = JSON.stringify(r.data);
      const inS = new TextEncoder().encode(input).length, outS = new TextEncoder().encode(out).length;
      showJsonResult(out);
      showJsonStats('📊 ' + formatBytes(inS) + ' → ' + formatBytes(outS) + ' · 减小 ' + (inS>0?((1-outS/inS)*100).toFixed(1):0) + '%');
      toast('压缩完成'); break;
    }
    case 'validate': {
      const r = safeParse(input);
      if (r.success) {
        const d = r.data;
        const t = Array.isArray(d) ? 'array[' + d.length + ']' : d === null ? 'null' : typeof d === 'object' ? 'object{' + Object.keys(d).length + ' keys}' : typeof d;
        document.getElementById('jsonResultContent').innerHTML = '<div class="validate-card success"><div style="font-size:16px">✅ JSON 格式正确</div><div class="struct-badges"><span class="struct-badge">📦 ' + t + '</span><span class="struct-badge">📝 ' + formatBytes(new TextEncoder().encode(input).length) + '</span></div></div>';
        hideJsonStats(); toast('✅ 校验通过');
      } else {
        document.getElementById('jsonResultContent').innerHTML = '<div class="validate-card error"><div style="font-size:16px">❌ JSON 格式错误</div><div>' + escHtml(r.error) + '</div></div>';
        hideJsonStats(); toast('校验失败','error');
      }
      break;
    }
    case 'sort': {
      const r = safeParse(input);
      if (!r.success) { showJsonError(r); return; }
      const ord = document.getElementById('jsonSortOrder')?.value || 'asc';
      const sorted = deepSortKeys(r.data, ord);
      showJsonResult(JSON.stringify(sorted, null, 2));
      showJsonStats('🔤 已按 key <b>' + (ord==='asc'?'升序':'降序') + '</b> 递归排序');
      toast('排序完成'); break;
    }
    case 'escape':
      showJsonResult(JSON.stringify(input).slice(1, -1));
      showJsonStats('🔒 已转义特殊字符');
      toast('转义完成'); break;
    case 'unescape': {
      let res = '';
      for (let i = 0; i < input.length; i++) {
        if (input[i] === '\\' && i + 1 < input.length) {
          switch (input[i + 1]) {
            case 'n': res += '\n'; i++; break; case 't': res += '\t'; i++; break;
            case 'r': res += '\r'; i++; break; case 'f': res += '\f'; i++; break;
            case 'b': res += '\b'; i++; break; case '"': res += '"'; i++; break;
            case "'": res += "'"; i++; break; case '\\': res += '\\'; i++; break;
            case '/': res += '/'; i++; break;
            case 'u':
              if (i + 5 < input.length) {
                const h = input.substring(i + 2, i + 6);
                if (/^[0-9a-fA-F]{4}$/.test(h)) { res += String.fromCharCode(parseInt(h, 16)); i += 5; break; }
              }
              res += input[i]; break;
            default: res += input[i];
          }
        } else { res += input[i]; }
      }
      showJsonResult(res); showJsonStats('🔓 已去除转义'); toast('去转义完成'); break;
    }
    case 'tree': {
      const r = safeParse(input);
      if (!r.success) { showJsonError(r); return; }
      jsonTreeData = r.data; jsonTreeCollapsed = {}; hideJsonStats();
      renderJsonTree(); toast('树形视图已生成'); break;
    }
  }
}

function showJsonResult(t) { document.getElementById('jsonResultContent').innerHTML = '<pre style="margin:0;white-space:pre-wrap;word-break:break-all">' + escHtml(t) + '</pre>'; }
function showJsonError(r) { document.getElementById('jsonResultContent').innerHTML = '<span style="color:var(--danger)">❌ ' + escHtml(r.error) + '</span>'; hideJsonStats(); toast('JSON格式错误','error'); }
function showJsonStats(h) { const e = document.getElementById('jsonInfoStats'); e.innerHTML = h; e.style.display = 'flex'; }
function hideJsonStats() { document.getElementById('jsonInfoStats').style.display = 'none'; }
function copyJsonResult() { copyTextById('jsonResultContent'); }

function deepSortKeys(obj, order) {
  if (Array.isArray(obj)) return obj.map(i => deepSortKeys(i, order));
  if (obj !== null && typeof obj === 'object') {
    const keys = Object.keys(obj).sort();
    if (order === 'desc') keys.reverse();
    const o = {};
    keys.forEach(k => o[k] = deepSortKeys(obj[k], order));
    return o;
  }
  return obj;
}

function renderJsonTree() {
  const el = document.getElementById('jsonResultContent');
  el.innerHTML = '<div class="tree-view tree-root">' + buildJsonTree(jsonTreeData, '') + '</div>';
  el.querySelectorAll('.tree-toggle').forEach(t => {
    t.onclick = function() {
      jsonTreeCollapsed[this.dataset.path] = !jsonTreeCollapsed[this.dataset.path];
      renderJsonTree();
    };
  });
}

function buildJsonTree(obj, path) {
  if (obj === null) return '<span class="tree-value-null">null</span>';
  if (Array.isArray(obj)) {
    if (!obj.length) return '<span class="tree-bracket">[]</span>';
    const c = jsonTreeCollapsed[path];
    let h = '<span class="tree-toggle" data-path="' + path + '">' + (c ? '▶' : '▼') + '</span><span class="tree-bracket">[</span>';
    if (c) { h += '<span class="tree-value-null"> … (' + obj.length + ')</span>'; }
    else {
      h += '<div class="tree-node">';
      obj.forEach((v, i) => { h += '<div><span class="tree-key">' + i + '</span>: ' + buildJsonTree(v, path + '[' + i + ']') + '</div>'; });
      h += '</div>';
    }
    h += '<span class="tree-bracket">]</span>'; return h;
  }
  if (typeof obj === 'object') {
    const keys = Object.keys(obj);
    if (!keys.length) return '<span class="tree-bracket">{}</span>';
    const c = jsonTreeCollapsed[path];
    let h = '<span class="tree-toggle" data-path="' + path + '">' + (c ? '▶' : '▼') + '</span><span class="tree-bracket">{</span>';
    if (c) { h += '<span class="tree-value-null"> … (' + keys.length + ')</span>'; }
    else {
      h += '<div class="tree-node">';
      keys.forEach(k => {
        h += '<div><span class="tree-key">"' + escHtml(k) + '"</span>: ' + buildJsonTree(obj[k], (path ? path + '.' : '') + k) + '</div>';
      });
      h += '</div>';
    }
    h += '<span class="tree-bracket">}</span>'; return h;
  }
  if (typeof obj === 'string') return '<span class="tree-value-string">"' + escHtml(obj) + '"</span>';
  if (typeof obj === 'number') return '<span class="tree-value-number">' + obj + '</span>';
  if (typeof obj === 'boolean') return '<span class="tree-value-boolean">' + obj + '</span>';
  return '<span>' + escHtml(String(obj)) + '</span>';
}

function jsonTreeExpandAll() { jsonTreeCollapsed = {}; if (jsonTreeData) renderJsonTree(); }
function jsonTreeCollapseAll() {
  if (!jsonTreeData) return;
  jsonTreeCollapsed = {};
  (function collect(o, p) {
    jsonTreeCollapsed[p] = true;
    if (Array.isArray(o)) o.forEach((v, i) => { if (v && typeof v === 'object') collect(v, p + '[' + i + ']'); });
    else if (o && typeof o === 'object') Object.entries(o).forEach(([k, v]) => { if (v && typeof v === 'object') collect(v, (p ? p + '.' : '') + k); });
  })(jsonTreeData, '');
  renderJsonTree();
}

// JSON Diff
function doJsonDiff() {
  const a = getVal('diffInputA'), b = getVal('diffInputB'), el = document.getElementById('diffResult');
  if (!a.trim() && !b.trim()) { el.innerHTML = '请输入 JSON'; return; }
  const sem = document.getElementById('semanticDiff').checked;
  let la, lb;
  if (sem) {
    const pa = safeParse(a), pb = safeParse(b);
    if (pa.success && pb.success) {
      la = JSON.stringify(deepSortKeys(pa.data, 'asc'), null, 2).split(NL);
      lb = JSON.stringify(deepSortKeys(pb.data, 'asc'), null, 2).split(NL);
    } else { la = a.split(NL); lb = b.split(NL); }
  } else { la = a.split(NL); lb = b.split(NL); }
  const diff = lcsDiff(la, lb);
  let html = '', ch = 0;
  diff.forEach(d => {
    if (d.type === 'equal') html += '<div class="diff-line diff-equal">  ' + escHtml(d.value) + '</div>';
    else if (d.type === 'remove') { html += '<div class="diff-line diff-remove">- ' + escHtml(d.value) + '</div>'; ch++; }
    else { html += '<div class="diff-line diff-add">+ ' + escHtml(d.value) + '</div>'; ch++; }
  });
  el.innerHTML = ch === 0 ? '<div style="color:var(--success)">✅ 两个 JSON 完全一致</div>' + html : '<div style="color:var(--warning);margin-bottom:6px">🔍 发现 ' + ch + ' 处差异</div>' + html;
}

function lcsDiff(la, lb) {
  const n = la.length, m = lb.length;
  const dp = Array.from({length: n + 1}, () => Array(m + 1).fill(0));
  for (let i = 1; i <= n; i++)
    for (let j = 1; j <= m; j++)
      dp[i][j] = la[i - 1] === lb[j - 1] ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1]);
  const res = []; let i = n, j = m;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && la[i - 1] === lb[j - 1]) { res.unshift({type: 'equal', value: la[i - 1]}); i--; j--; }
    else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) { res.unshift({type: 'add', value: lb[j - 1]}); j--; }
    else { res.unshift({type: 'remove', value: la[i - 1]}); i--; }
  }
  return res;
}

// JSON Convert
function doConvert() {
  const input = getVal('convertInput'), from = document.getElementById('convertFrom').value, to = document.getElementById('convertTo').value;
  if (!input.trim()) { toast('请输入内容','error'); return; }
  if (from === to) { setVal('convertOutput', input); return; }
  try {
    let r;
    switch (from + '->' + to) {
      case 'json->csv': r = jsonToCsv(input); break;
      case 'json->xml': r = jsonToXml(input); break;
      case 'json->yaml': r = jsonToYaml(input); break;
      case 'csv->json': r = csvToJson(input); break;
      case 'xml->json': r = xmlToJson(input); break;
      case 'yaml->json': r = yamlToJson(input); break;
      default: r = {success: false, error: '不支持 ' + from + ' → ' + to};
    }
    setVal('convertOutput', r.success ? r.data : '// ' + r.error);
    toast(r.success ? '转换完成' : r.error, r.success ? 'success' : 'error');
  } catch (e) { setVal('convertOutput', '// ' + e.message); }
}
function swapConvert() { const f = document.getElementById('convertFrom'), t = document.getElementById('convertTo'); [f.value, t.value] = [t.value, f.value]; }

function jsonToCsv(s) {
  const r = safeParse(s); if (!r.success) return r;
  const arr = Array.isArray(r.data) ? r.data : [r.data];
  if (!arr.length) return {success: true, data: ''};
  const keys = Object.keys(arr[0]);
  const rows = arr.map(obj => keys.map(k => {
    const v = obj[k]; if (v === null || v === undefined) return '';
    const st = String(v);
    return st.includes(',') || st.includes('"') || st.includes(NL) ? '"' + st.replace(/"/g, '""') + '"' : st;
  }).join(','));
  return {success: true, data: [keys.join(','), ...rows].join(NL)};
}

function jsonToXml(s) {
  const r = safeParse(s); if (!r.success) return r;
  function tx(n, o) {
    if (o === null) return '<' + n + '>null</' + n + '>';
    if (typeof o === 'string' || typeof o === 'number' || typeof o === 'boolean')
      return '<' + n + '>' + String(o).replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</' + n + '>';
    if (Array.isArray(o)) return o.map((v, i) => tx('item', v)).join(NL);
    let x = '<' + n + '>';
    for (const [k, v] of Object.entries(o)) x += NL + '  ' + tx(k, v).split(NL).join(NL + '  ');
    x += NL + '</' + n + '>'; return x;
  }
  return {success: true, data: tx('root', r.data)};
}

function jsonToYaml(s) {
  const r = safeParse(s); if (!r.success) return r;
  function ty(o, ind) {
    const p = '  '.repeat(ind);
    if (o === null) return 'null';
    if (typeof o === 'string') return o.includes(':') || o.includes('#') ? '"' + o.replace(/"/g, '\\"') + '"' : o;
    if (typeof o === 'number' || typeof o === 'boolean') return String(o);
    if (Array.isArray(o)) { if (!o.length) return '[]'; return o.map(v => p + '- ' + ty(v, ind + 1).trimStart()).join(NL); }
    const keys = Object.keys(o); if (!keys.length) return '{}';
    return keys.map(k => p + k + ': ' + ty(o[k], ind + 1).trimStart()).join(NL);
  }
  return {success: true, data: ty(r.data, 0)};
}

function csvToJson(s) {
  try {
    const lines = s.trim().split(NL);
    if (lines.length < 2) return {success: false, error: 'CSV至少需要标题行和一行数据'};
    const parse = l => {
      const r = []; let c = '', q = false;
      for (let i = 0; i < l.length; i++) {
        if (q) { if (l[i]==='"') { if (l[i+1]==='"') { c+='"'; i++; } else q = false; } else c += l[i]; }
        else { if (l[i]==='"') q = true; else if (l[i]===',') { r.push(c.trim()); c = ''; } else c += l[i]; }
      }
      r.push(c.trim()); return r;
    };
    const h = parse(lines[0]), d = [];
    for (let i = 1; i < lines.length; i++) {
      const v = parse(lines[i]), o = {};
      h.forEach((hk, idx) => {
        let vv = v[idx] || '';
        if (vv === 'true') vv = true; else if (vv === 'false') vv = false;
        else if (vv === 'null' || vv === '') vv = null;
        else if (!isNaN(vv) && vv !== '') vv = Number(vv);
        o[hk] = vv;
      });
      d.push(o);
    }
    return {success: true, data: JSON.stringify(d, null, 2)};
  } catch (e) { return {success: false, error: e.message}; }
}

function xmlToJson(s) {
  try {
    const p = new DOMParser(), d = p.parseFromString(s, 'text/xml'), err = d.querySelector('parsererror');
    if (err) return {success: false, error: 'XML解析失败'};
    function nt(n) {
      const o = {};
      if (n.attributes) for (const a of n.attributes) o['@' + a.name] = a.value;
      const ch = Array.from(n.childNodes).filter(cn => cn.nodeType === 1);
      if (!ch.length) {
        const t = n.textContent.trim();
        const tv = t === 'true' ? true : t === 'false' ? false : t === 'null' ? null : isNaN(Number(t)) || t === '' ? t : Number(t);
        return Object.keys(o).length ? (o['#text'] = tv, o) : tv;
      }
      const g = {};
      ch.forEach(cn => { const nm = cn.tagName; if (!g[nm]) g[nm] = []; g[nm].push(nt(cn)); });
      for (const [k, v] of Object.entries(g)) o[k] = v.length === 1 ? v[0] : v;
      return o;
    }
    return {success: true, data: JSON.stringify(nt(d.documentElement), null, 2)};
  } catch (e) { return {success: false, error: e.message}; }
}

function yamlToJson(s) {
  try {
    const lines = s.split(NL);
    function pv(idx, bi) {
      if (idx >= lines.length) return {value: null, nextIdx: idx};
      const l = lines[idx];
      if (!l || !l.trim() || l.trim().startsWith('#')) return pv(idx + 1, bi);
      const tr = l.trim(), ind = l.search(/\S/);
      if (ind < bi) return {value: null, nextIdx: idx};
      if (tr.startsWith('- ')) {
        const items = []; let i = idx;
        while (i < lines.length) {
          const cl = lines[i];
          if (!cl || !cl.trim() || cl.trim().startsWith('#')) { i++; continue; }
          if (cl.search(/\S/) < ind) break;
          if (cl.trim().startsWith('- ')) {
            const rest = cl.trim().substring(2).trim(), ci2 = cl.search('- ') + 2;
            if (rest && !rest.endsWith(':')) { items.push(ps(rest)); i++; }
            else { const sub = pv(i + 1, ci2); items.push(sub.value); i = sub.nextIdx; }
          } else break;
        }
        return {value: items, nextIdx: i};
      }
      const ci = tr.indexOf(':');
      if (ci >= 0) {
        const key = tr.substring(0, ci).trim(), rest = tr.substring(ci + 1).trim(), obj = {};
        if (rest) {
          obj[key] = ps(rest);
          let i = idx + 1;
          while (i < lines.length) {
            const cl = lines[i];
            if (!cl || !cl.trim() || cl.trim().startsWith('#')) { i++; continue; }
            if (cl.search(/\S/) !== ind) break;
            const sub = pv(i, ind);
            if (sub.value && typeof sub.value === 'object' && !Array.isArray(sub.value)) Object.assign(obj, sub.value);
            i = sub.nextIdx;
          }
          return {value: obj, nextIdx: i};
        } else {
          const nested = {}; let i = idx + 1, ci2 = ind + 2;
          while (i < lines.length) {
            const cl = lines[i];
            if (!cl || !cl.trim() || cl.trim().startsWith('#')) { i++; continue; }
            if (cl.search(/\S/) < ci2) break;
            if (cl.search(/\S/) > ci2) { i++; continue; }
            const sub = pv(i, ci2);
            if (sub.value && typeof sub.value === 'object' && !Array.isArray(sub.value)) Object.assign(nested, sub.value);
            if (sub.nextIdx === i) break;
            i = sub.nextIdx;
          }
          obj[key] = nested;
          while (i < lines.length) {
            const cl = lines[i];
            if (!cl || !cl.trim() || cl.trim().startsWith('#')) { i++; continue; }
            if (cl.search(/\S/) !== ind) break;
            const sub = pv(i, ind);
            if (sub.value && typeof sub.value === 'object' && !Array.isArray(sub.value)) Object.assign(obj, sub.value);
            if (sub.nextIdx === i) break;
            i = sub.nextIdx;
          }
          return {value: obj, nextIdx: i};
        }
      }
      return {value: ps(tr), nextIdx: idx + 1};
    }
    return {success: true, data: JSON.stringify(pv(0, 0).value, null, 2)};
  } catch (e) { return {success: false, error: e.message}; }
}

function ps(s) {
  if (!s || s === 'null' || s === '~') return null;
  if (s === 'true') return true; if (s === 'false') return false;
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) return s.slice(1, -1);
  const n = Number(s); return !isNaN(n) && s !== '' ? n : s;
}

// JSONPath
function doJsonPath() {
  const input = getVal('jsonpathInput'), expr = document.getElementById('jsonpathExpr').value.trim(), el = document.getElementById('jsonpathResult');
  if (!input.trim()) { toast('请输入JSON','error'); return; }
  if (!expr) { toast('请输入表达式','error'); return; }
  const r = safeParse(input);
  if (!r.success) { el.innerHTML = '<span style="color:var(--danger)">❌ ' + r.error + '</span>'; return; }
  try {
    const results = evalJsonPath(r.data, expr);
    if (!results.length) { el.innerHTML = '<span style="color:var(--text-secondary)">未找到匹配结果</span>'; }
    else {
      let html = '<div>找到 <b>' + results.length + '</b> 个结果:</div>';
      results.forEach((res, i) => {
        html += '<div style="margin:4px 0;padding:8px;background:var(--card-bg);border:1px solid var(--border);border-radius:4px"><div style="font-size:11px;color:var(--text-secondary)">[' + i + '] ' + escHtml(res.path) + '</div><pre style="margin:0;white-space:pre-wrap">' + escHtml(JSON.stringify(res.value, null, 2)) + '</pre></div>';
      });
      el.innerHTML = html;
    }
    toast('找到 ' + results.length + ' 个结果');
  } catch (e) { el.innerHTML = '<span style="color:var(--danger)">❌ ' + escHtml(e.message) + '</span>'; }
}

function evalJsonPath(root, expr) {
  const norm = expr.startsWith('$') ? expr.substring(1) : expr;
  const results = [];
  walkJsonPath(root, norm, root, '$', results);
  return results;
}

function walkJsonPath(cur, expr, root, cpath, results) {
  if (!expr) { results.push({path: cpath, value: cur}); return; }
  if (expr.startsWith('..')) {
    const rest = expr.substring(2);
    if (rest) walkJsonPath(cur, rest, root, cpath, results);
    else results.push({path: cpath, value: cur});
    if (Array.isArray(cur)) cur.forEach((v, i) => walkJsonPath(v, expr, root, cpath + '[' + i + ']', results));
    else if (cur && typeof cur === 'object') Object.entries(cur).forEach(([k, v]) => walkJsonPath(v, expr, root, cpath + '.' + k, results));
    return;
  }
  if (expr.startsWith('.')) {
    const m = expr.match(/^\.(\w+)(.*)/);
    if (m && cur && typeof cur === 'object' && m[1] in cur) walkJsonPath(cur[m[1]], m[2], root, cpath + '.' + m[1], results);
    return;
  }
  if (expr.startsWith('[')) {
    let d = 0, close = -1;
    for (let i = 0; i < expr.length; i++) { if (expr[i] === '[') d++; else if (expr[i] === ']') { d--; if (d === 0) { close = i; break; } } }
    const inner = expr.substring(1, close), rest = expr.substring(close + 1);
    if (inner.startsWith('?(') && inner.endsWith(')')) {
      const fexpr = inner.substring(2, inner.length - 1);
      if (Array.isArray(cur)) cur.forEach((v, i) => { if (evalJsonFilter(v, fexpr)) walkJsonPath(v, rest, root, cpath + '[' + i + ']', results); });
      return;
    }
    if (inner === '*') {
      if (Array.isArray(cur)) cur.forEach((v, i) => walkJsonPath(v, rest, root, cpath + '[' + i + ']', results));
      else if (cur && typeof cur === 'object') Object.entries(cur).forEach(([k, v]) => walkJsonPath(v, rest, root, cpath + '.' + k, results));
      return;
    }
    if (/^-?\d+$/.test(inner)) {
      const idx = parseInt(inner), actual = idx < 0 && Array.isArray(cur) ? cur.length + idx : idx;
      if (Array.isArray(cur) && actual >= 0 && actual < cur.length) walkJsonPath(cur[actual], rest, root, cpath + '[' + idx + ']', results);
      return;
    }
    if ((inner.startsWith("'") && inner.endsWith("'")) || (inner.startsWith('"') && inner.endsWith('"'))) {
      const k = inner.slice(1, -1);
      if (cur && typeof cur === 'object' && k in cur) walkJsonPath(cur[k], rest, root, cpath + '["' + k + '"]', results);
      return;
    }
    if (inner.includes(',')) {
      inner.split(',').map(s => parseInt(s.trim())).forEach(i => {
        if (Array.isArray(cur) && i >= 0 && i < cur.length) walkJsonPath(cur[i], rest, root, cpath + '[' + i + ']', results);
      });
      return;
    }
    if (inner.includes(':')) {
      const parts = inner.split(':'), start = parseInt(parts[0]) || 0, end = parts[1] ? parseInt(parts[1]) : undefined;
      if (Array.isArray(cur)) { const e = end !== undefined ? end : cur.length; for (let i = start; i < e; i++) if (i >= 0 && i < cur.length) walkJsonPath(cur[i], rest, root, cpath + '[' + i + ']', results); }
      return;
    }
  }
}

function evalJsonFilter(item, expr) {
  const m = expr.match(/@\.(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+)/);
  if (!m) return true;
  const field = m[1], op = m[2];
  let cmp = m[3].trim();
  if (cmp === 'true') cmp = true; else if (cmp === 'false') cmp = false;
  else if (cmp === 'null') cmp = null;
  else if (/^-?\d+(\.\d+)?$/.test(cmp)) cmp = Number(cmp);
  else if ((cmp.startsWith("'") && cmp.endsWith("'")) || (cmp.startsWith('"') && cmp.endsWith('"'))) cmp = cmp.slice(1, -1);
  const v = item[field];
  switch (op) { case '==': return v == cmp; case '!=': return v != cmp; case '>': return v > cmp; case '<': return v < cmp; case '>=': return v >= cmp; case '<=': return v <= cmp; }
  return false;
}

