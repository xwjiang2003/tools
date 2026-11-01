// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// url-parser.js — 拆解 URL，并把查询参数做成一改就重新拼装的可编辑表格
// 依赖浏览器内置 URL / URLSearchParams（Node 10+ 也有，单测直接跑）。

function urlParseInfo(raw) {
  var s = String(raw == null ? '' : raw).trim();
  if (!s) return { valid: false, reason: 'empty' };
  var hasScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(s);
  var u;
  try {
    // 缺协议时按 https 补全（现在默认就是 https，用 http 反而要用户再改一次）
    u = new URL(hasScheme ? s : 'https://' + s);
  } catch (e) {
    return { valid: false, reason: 'url' };
  }
  var params = [];
  u.searchParams.forEach(function (v, k) { params.push({ k: k, v: v }); });
  return {
    valid: true,
    scheme: u.protocol.replace(':', ''),
    user: u.username,
    pass: u.password,
    host: u.hostname,
    port: u.port,
    path: u.pathname,
    search: u.search,
    hash: u.hash,
    origin: u.origin,
    params: params,
    addedScheme: !hasScheme
  };
}

// 从结构化字段重新拼 URL。参数值统一按 encodeURIComponent 还原，
// 不用 URLSearchParams.toString()：它把空格编成 '+'，在路径与参数混排时容易引起误解。
function urlRebuild(o) {
  var s = (o.scheme || 'http') + '://';
  if (o.user) s += encodeURIComponent(o.user) + (o.pass ? ':' + encodeURIComponent(o.pass) : '') + '@';
  s += o.host || '';
  if (o.port) s += ':' + o.port;
  var path = o.path || '/';
  if (path.charAt(0) !== '/') path = '/' + path;
  s += path;
  var qs = [];
  (o.params || []).forEach(function (p) {
    if (!p || p.k === '' || p.k == null) return;          // 名字为空的行直接跳过
    qs.push(encodeURIComponent(p.k) + '=' + encodeURIComponent(p.v == null ? '' : p.v));
  });
  if (qs.length) s += '?' + qs.join('&');
  if (o.hash) s += o.hash;
  return s;
}

// 参数值里出现 %xx 序列时给出解码后的可读形式，纯中文/空格保持原样
function urlReadable(v) {
  var s = String(v == null ? '' : v);
  if (/%[0-9a-f]{2}/i.test(s)) {
    try { return decodeURIComponent(s.replace(/\+/g, ' ')); } catch (e) { return s; }
  }
  return s;
}

// ---------------------------------------------------------------- 页面
function urlTL() { return G.__TL__ || {}; }
var urlState = null;      // 当前解析结果，供参数编辑回写

function urlRender() {
  var L = urlTL();
  var box = document.getElementById('urlFields');
  var pbox = document.getElementById('urlParams');
  var obox = document.getElementById('urlOut');
  if (!box || !pbox || !obox) return;
  var raw = getVal('urlInput');
  if (!raw.trim()) {
    urlState = null;
    box.innerHTML = '<tr><td colspan="2" class="tl-hint">' + escHtml(L.hint || '') + '</td></tr>';
    pbox.innerHTML = '';
    obox.textContent = '';
    return;
  }
  var r = urlParseInfo(raw);
  if (!r.valid) {
    urlState = null;
    box.innerHTML = '<tr><td colspan="2" class="tl-err">' + escHtml(L.err_url || '') + '</td></tr>';
    pbox.innerHTML = '';
    obox.textContent = '';
    return;
  }
  urlState = r;

  var rows = [
    [L.f_scheme, r.scheme],
    [L.f_host, r.host],
    [L.f_port, r.port || L.f_port_default],
    [L.f_path, r.path],
    [L.f_hash, r.hash || '—']
  ];
  if (r.user) rows.splice(1, 0, [L.f_user, r.user + (r.pass ? ' / ' + r.pass : '')]);
  var html = '';
  for (var i = 0; i < rows.length; i++) {
    html += '<tr><th style="width:30%">' + escHtml(rows[i][0]) + '</th><td><code>' +
      escHtml(rows[i][1]) + '</code></td></tr>';
  }
  box.innerHTML = html;

  urlRenderParams();
  urlSyncOut();
}

function urlRenderParams() {
  var L = urlTL();
  var box = document.getElementById('urlParams');
  if (!box || !urlState) return;
  if (!urlState.params.length) {
    box.innerHTML = '<div class="tl-hint" style="padding:8px 0">' + escHtml(L.no_params || '') + '</div>';
    return;
  }
  var html = '<table class="dt-table"><thead><tr><th>' + escHtml(L.p_name) + '</th><th>' +
    escHtml(L.p_value) + '</th><th>' + escHtml(L.p_readable) + '</th><th></th></tr></thead><tbody>';
  for (var i = 0; i < urlState.params.length; i++) {
    var p = urlState.params[i];
    html += '<tr><td><input class="tl-input" data-pk="' + i + '" value="' + escAttr(p.k) +
      '"></td><td><input class="tl-input" data-pv="' + i + '" value="' + escAttr(p.v) +
      '"></td><td class="tl-wrap">' + escHtml(urlReadable(p.v)) +
      '</td><td><button class="btn btn-sm" type="button" data-pdel="' + i + '">✕</button></td></tr>';
  }
  html += '</tbody></table>' +
    '<div class="row" style="gap:8px;margin-top:8px"><button class="btn btn-sm" type="button" id="urlAddParam">' +
    escHtml(L.p_add) + '</button></div>';
  box.innerHTML = html;
}

function urlSyncOut() {
  var box = document.getElementById('urlOut');
  if (!box || !urlState) return;
  box.textContent = urlRebuild(urlState);
}

G.urlRender = urlRender;
G.urlClear = function () { setVal('urlInput', ''); urlRender(); };
G.urlSample = function () {
  setVal('urlInput', 'https://devtools.help/regex/?pattern=%5Cd%2B&flags=g&lang=zh#result');
  urlRender();
};

function initUrl() {
  var input = document.getElementById('urlInput');
  if (!input) return;
  if (!input.value) {
    input.value = 'https://devtools.help/regex/?pattern=%5Cd%2B&flags=g&lang=zh#result';
  }
  urlRender();
  input.addEventListener('input', urlRender);

  // 参数区是动态替换的，事件挂在外层容器上（委托），避免每渲染一次重绑一遍
  var pbox = document.getElementById('urlParams');
  if (pbox) {
    pbox.addEventListener('input', function (e) {
      var t = e.target;
      if (!urlState) return;
      var ik = t.getAttribute && t.getAttribute('data-pk');
      var iv = t.getAttribute && t.getAttribute('data-pv');
      if (ik != null) urlState.params[+ik].k = t.value;
      else if (iv != null) urlState.params[+iv].v = t.value;
      else return;
      urlSyncOut();
    });
    pbox.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-pdel],#urlAddParam') : null;
      if (!b || !urlState) return;
      if (b.id === 'urlAddParam') {
        urlState.params.push({ k: '', v: '' });
      } else {
        urlState.params.splice(+b.getAttribute('data-pdel'), 1);
      }
      urlRenderParams();
      urlSyncOut();
    });
  }
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUrl);
  } else {
    initUrl();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { urlParseInfo: urlParseInfo, urlRebuild: urlRebuild, urlReadable: urlReadable };
}
