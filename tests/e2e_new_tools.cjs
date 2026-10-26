// E2E: drive real Chrome via CDP (Node 22 global WebSocket) against the built site.
// Covers the 5 newest tool pages end to end in the browser: wasm load, convert buttons,
// clear/reset, result rendering, i18n switch. Run: node tests/e2e_new_tools.mjs [baseUrl]
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');

const DOCS = path.join(__dirname, '..', 'docs');
const BASE = process.argv[2] || 'http://127.0.0.1:3210';
const CDP_PORT = Number(process.env.CDP_PORT || 9222);

let pass = 0, fail = 0;
const failures = [];
function ok(cond, msg, extra) {
  if (cond) { pass++; }
  else { fail++; failures.push(msg + (extra ? '\n     ' + String(extra).slice(0, 400) : '')); console.error('  x ' + msg); }
}

// ---------- static server for docs/ ----------
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.wasm': 'application/wasm', '.txt': 'text/plain; charset=utf-8',
  '.xml': 'application/xml', '.png': 'image/png', '.svg': 'image/svg+xml', '.gz': 'application/gzip' };
function startServer() {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      const p = decodeURIComponent(req.url.split('?')[0]);
      let fp = path.join(DOCS, p);
      try {
        if (fs.statSync(fp).isDirectory()) fp = path.join(fp, 'index.html');
      } catch (e) { /* fall through to 404 */ }
      fs.readFile(fp, (err, data) => {
        if (err) { res.writeHead(404); res.end('nf'); return; }
        res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
        res.end(data);
      });
    });
    srv.listen(3210, '127.0.0.1', () => resolve(srv));
  });
}

// ---------- minimal CDP client ----------
function cdpConnect(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    let id = 0;
    const pending = new Map();
    const events = [];
    ws.addEventListener('open', () => resolve({
      call(method, params) {
        return new Promise((res, rej) => {
          const msgId = ++id;
          pending.set(msgId, { res, rej });
          ws.send(JSON.stringify({ id: msgId, method, params: params || {} }));
        });
      },
      waitEvent(name, timeoutMs) {
        return new Promise((res, rej) => {
          const t0 = Date.now();
          const iv = setInterval(() => {
            const i = events.findIndex((e) => e.method === name);
            if (i >= 0) { clearInterval(iv); res(events.splice(i, 1)[0]); }
            else if (Date.now() - t0 > timeoutMs) { clearInterval(iv); rej(new Error('timeout waiting ' + name)); }
          }, 40);
        });
      },
      close() { try { ws.close(); } catch (e) {} },
    }));
    ws.addEventListener('error', (e) => reject(new Error('ws error: ' + e.message)));
    ws.addEventListener('message', (ev) => {
      let m; try { m = JSON.parse(ev.data); } catch (e) { return; }
      if (m.id !== undefined && pending.has(m.id)) {
        const { res, rej } = pending.get(m.id);
        pending.delete(m.id);
        if (m.error) rej(new Error(m.error.message)); else res(m.result);
      } else if (m.method) {
        events.push(m);
      }
    });
  });
}

async function getTargets() {
  const r = await fetch('http://127.0.0.1:' + CDP_PORT + '/json/list');
  return r.json();
}

// ---------- page driver ----------
async function openPage(cdp, url) {
  await cdp.call('Page.enable');
  await cdp.call('Runtime.enable');
  const navP = cdp.waitEvent('Page.frameNavigated', 15000);
  await cdp.call('Page.navigate', { url });
  await navP;
  // load event may already have fired; give it a bounded wait
  await Promise.race([
    cdp.waitEvent('Page.loadEventFired', 8000),
    new Promise((r) => setTimeout(r, 6000)),
  ]);
}

async function evalPage(cdp, expr) {
  const r = await cdp.call('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error('page eval threw: ' + JSON.stringify(r.exceptionDetails.exception || r.exceptionDetails.text));
  return r.result.value;
}

// wait until expr returns truthy (poll, never fixed sleep)
async function waitFor(cdp, expr, timeoutMs, label) {
  const t0 = Date.now();
  for (;;) {
    try { if (await evalPage(cdp, expr)) return; } catch (e) { /* keep polling */ }
    if (Date.now() - t0 > timeoutMs) throw new Error('timeout waiting for: ' + label);
    await new Promise((r) => setTimeout(r, 120));
  }
}

// page-side assertion bundle: returns [{name, cond, extra}]
async function runChecks(cdp, page, checks) {
  for (const c of checks) {
    let res;
    try {
      res = await evalPage(cdp, '(function(){' + c.expr + '})()');
    } catch (e) {
      ok(false, page + ' :: ' + c.name + ' (eval error)', e.message);
      continue;
    }
    ok(!!res.cond, page + ' :: ' + c.name, res.extra);
  }
}

// helpers injected into every check expression
const HELPERS = `
  function setVal(id, v){ var el = document.getElementById(id); if(!el) throw new Error('no el '+id);
    el.value = v; el.dispatchEvent(new Event('input', {bubbles:true})); return el.value; }
  function clickId(id){ var el = document.getElementById(id); if(!el) throw new Error('no btn '+id); el.click(); }
  function resultText(id){ return document.getElementById(id).innerText || ''; }
`;

const PAGES = [
  {
    name: 'gofmt-online',
    path: '/gofmt-online/',
    ready: "document.getElementById('gofmtInput') && document.getElementById('gofmtResult')",
    checks: [
      { name: 'wasm loads + formats sloppy Go', expr: HELPERS + `
        setVal('gofmtInput', 'package main\\nimport "fmt"\\nfunc main(){\\nfmt.Println( "hi" )\\n}');
        window.gofmtRun();
        return new Promise(function(resolve){
          var t0 = Date.now();
          (function poll(){
            var t = resultText('gofmtResult');
            if (t.indexOf('hi') >= 0 || t.indexOf('错误') >= 0) {
              resolve({cond: t.indexOf('hi') >= 0 && t.indexOf('fmt.Println("hi")') >= 0, extra: t.slice(0,300)});
            } else if (Date.now() - t0 > 8000) {
              resolve({cond:false, extra:'timeout, result so far: ' + t.slice(0,200)});
            } else setTimeout(poll, 100);
          })();
        });` },
      { name: 'gofmt output uses tab indent', expr: HELPERS + `
        var t = resultText('gofmtResult');
        return {cond: /\\t/.test(t), extra: JSON.stringify(t.slice(0,120))};` },
      { name: 'clear resets panel', expr: HELPERS + `
        window.gofmtClear();
        var t = resultText('gofmtResult');
        var reset = t.indexOf('选择操作开始') >= 0 || t.indexOf('Choose an operation') >= 0;
        return {cond: reset && document.getElementById('gofmtInput').value === '', extra: t.slice(0,80)};` },
      { name: 'syntax error surfaces an error', expr: HELPERS + `
        setVal('gofmtInput', 'package main\\nfunc broken( {');
        window.gofmtRun();
        return new Promise(function(resolve){
          var t0 = Date.now();
          (function poll(){
            var t = resultText('gofmtResult');
            var isErr = t.indexOf('错误') >= 0 || t.indexOf('Error') >= 0;
            if (isErr) resolve({cond:true});
            else if (Date.now() - t0 > 8000) resolve({cond:false, extra:'no error shown: ' + t.slice(0,200)});
            else setTimeout(poll, 100);
          })();
        });` },
    ],
  },
  {
    name: 'cron-generator',
    path: '/cron-generator/',
    ready: "document.getElementById('cronMinute') && document.getElementById('cronMinute').options.length > 1",
    checks: [
      { name: 'fields populated + default expression', expr: HELPERS + `
        window.cronBuild();
        var t = resultText('cronResult');
        return {cond: /^[\\d*/,\\-]+ [\\d*/,\\-]+ [\\d*/,\\-]+ [\\d*/,\\-]+ [\\d*/,\\-]+$/.test(t.trim().split('\\n')[0]), extra: t.slice(0,200)};` },
      { name: 'changing a field rebuilds the expression', expr: HELPERS + `
        var sel = document.getElementById('cronMinute');
        var opts = Array.prototype.map.call(sel.options, function(o){return o.value;});
        var pick = opts.filter(function(v){return /^\\d+$/.test(v);})[0] || opts[1];
        sel.value = pick;
        sel.dispatchEvent(new Event('change', {bubbles:true}));
        var t = resultText('cronResult');
        return {cond: t.trim().indexOf(pick + ' ') === 0 || t.indexOf('\\n' + pick + ' ') >= 0 || t.indexOf(pick) >= 0, extra: 'picked ' + pick + ' -> ' + t.slice(0,120)};` },
      { name: 'reset restores defaults', expr: HELPERS + `
        window.cronReset();
        var sel = document.getElementById('cronMinute');
        var t = resultText('cronResult');
        return {cond: sel.selectedIndex === 0 || /\\* \\* \\* \\* \\*/.test(t), extra: 'sel=' + sel.selectedIndex + ' result=' + t.slice(0,80)};` },
    ],
  },
  {
    name: 'csv-to-sql-insert',
    path: '/csv-to-sql-insert/',
    ready: "document.getElementById('c2sInput') && document.getElementById('c2sTable')",
    checks: [
      { name: 'generates INSERT statements', expr: HELPERS + `
        setVal('c2sInput', 'id,name\\n1,Alice\\n2,O\\'Neil');
        window.c2sRun();
        var t = resultText('c2sResult');
        var good = t.indexOf('INSERT INTO') >= 0 && t.indexOf('Alice') >= 0;
        var esc = t.indexOf("O''Neil") >= 0;
        return {cond: good && esc, extra: t.slice(0,300)};` },
      { name: 'empty cell becomes NULL', expr: HELPERS + `
        setVal('c2sInput', 'id,name\\n1,\\n2,Bob');
        window.c2sRun();
        var t = resultText('c2sResult');
        return {cond: t.indexOf('NULL') >= 0, extra: t.slice(0,300)};` },
      { name: 'table name field is honoured', expr: HELPERS + `
        setVal('c2sTable', 'people');
        setVal('c2sInput', 'id\\n1');
        window.c2sRun();
        var t = resultText('c2sResult');
        return {cond: t.indexOf('people') >= 0, extra: t.slice(0,200)};` },
    ],
  },
  {
    name: 'sql-formatter',
    path: '/sql-formatter/',
    ready: "document.getElementById('sqlfmtInput') && document.getElementById('sqlfmtUpper')",
    checks: [
      { name: 'formats SELECT with keyword casing', expr: HELPERS + `
        setVal('sqlfmtInput', "select id,name from users where status='active' order by id desc limit 5;");
        window.sqlfmtRun();
        var t = resultText('sqlfmtResult');
        return {cond: t.indexOf('SELECT') >= 0 && t.indexOf('FROM') >= 0 && t.indexOf('WHERE') >= 0 && t.indexOf('ORDER BY') >= 0, extra: t.slice(0,400)};` },
      { name: 'idempotent second pass', expr: HELPERS + `
        window.sqlfmtRun();
        var a = resultText('sqlfmtResult');
        setVal('sqlfmtInput', a);
        window.sqlfmtRun();
        var b = resultText('sqlfmtResult');
        return {cond: a === b, extra: 'first: ' + a.slice(0,200) + ' || second: ' + b.slice(0,200)};` },
      { name: 'lowercase mode keeps input case', expr: HELPERS + `
        document.getElementById('sqlfmtUpper').checked = false;
        setVal('sqlfmtInput', "select id from t;");
        window.sqlfmtRun();
        var t = resultText('sqlfmtResult');
        return {cond: t.indexOf('select') >= 0 && t.indexOf('SELECT') < 0, extra: t.slice(0,120)};
        ` },
    ],
  },
  {
    name: 'markdown-to-html',
    path: '/markdown-to-html/',
    ready: "document.getElementById('md2hInput') && document.getElementById('md2hResult')",
    checks: [
      { name: 'renders headings, bold, code, table', expr: HELPERS + `
        setVal('md2hInput', '# Title\\n\\nSome **bold** and \`code\`.\\n\\n| a | b |\\n| - | - |\\n| 1 | 2 |');
        window.md2hRun();
        var box = document.getElementById('md2hResult');
        var h1 = box.querySelector('h1');
        var strong = box.querySelector('strong');
        var code = box.querySelector('code');
        var table = box.querySelector('table');
        var td = box.querySelector('td');
        var okAll = !!h1 && h1.textContent.indexOf('Title') >= 0
          && !!strong && strong.textContent === 'bold'
          && !!code && code.textContent === 'code'
          && !!table && !!td && td.textContent === '1';
        return {cond: okAll, extra: box.innerHTML.slice(0,400)};` },
      { name: 'output is escaped (no raw script)', expr: HELPERS + `
        setVal('md2hInput', '<script>alert(1)</script>\\n\\n**x**');
        window.md2hRun();
        var box = document.getElementById('md2hResult');
        var realScript = box.querySelector('script');
        var rawHtml = box.innerHTML;
        return {cond: !realScript && rawHtml.indexOf('<script>alert') < 0 && rawHtml.indexOf('&lt;script&gt;') >= 0, extra: rawHtml.slice(0,200)};` },
      { name: 'preview mode renders live DOM', expr: HELPERS + `
        var box = document.getElementById('md2hResult');
        var before = box.querySelectorAll('h1,table,strong,code').length;
        return {cond: before > 0, extra: 'rendered nodes: ' + before};` },
    ],
  },
];

async function main() {
  const srv = await startServer();
  // prefer a fresh target; fall back to any existing blank page
  let blank = null;
  try {
    const r = await fetch('http://127.0.0.1:' + CDP_PORT + '/json/new?about:blank', { method: 'PUT' });
    if (r.ok) blank = await r.json();
  } catch (e) { /* older Chrome rejects /json/new without PUT or blocks it; fall through */ }
  if (!blank) {
    const targets = await getTargets();
    blank = targets.find((t) => t.type === 'page' && t.url === 'about:blank');
  }
  if (!blank) throw new Error('no usable page target; is Chrome running with --remote-debugging-port?');
  const cdp = await cdpConnect(blank.webSocketDebuggerUrl);
  console.log('CDP connected. base=' + BASE);

  for (const page of PAGES) {
    console.log('--- ' + page.name + ' ---');
    await openPage(cdp, BASE + page.path);
    await waitFor(cdp, '!!(' + page.ready + ')', 10000, page.name + ' ready');
    await runChecks(cdp, page.name, page.checks);
  }

  // one non-zh language spot check on a new page (cron field labels stay canonical English)
  console.log('--- en/sql-formatter (language switch) ---');
  await openPage(cdp, BASE + '/en/sql-formatter/');
  await waitFor(cdp, "!!(document.getElementById('sqlfmtInput'))", 10000, 'en page');
  await runChecks(cdp, 'en/sql-formatter', [
    { name: 'english chrome renders', expr: HELPERS + `
      var t = document.body.innerText;
      return {cond: t.indexOf('SQL Formatter') >= 0 || t.indexOf('Format') >= 0, extra: t.slice(0,120)};` },
  ]);

  cdp.close();
  srv.close();
  console.log('\\n==== E2E: ' + pass + ' passed, ' + fail + ' failed ====');
  if (failures.length) { console.log(failures.join('\\n')); process.exit(1); }
}

main().catch((e) => { console.error('E2E driver error:', e); process.exit(2); });
