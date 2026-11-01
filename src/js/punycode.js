// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// punycode.js — 国际化域名（IDN）与 Punycode 互转
// 编码方向直接用浏览器内置的 URL 解析器（它按 UTS#46 做规范化，比手写实现更接近真实注册规则），
// 解码方向没有内置 API，用 RFC 3492 的标准算法自己解。

var PUNY_BASE = 36, PUNY_TMIN = 1, PUNY_TMAX = 26, PUNY_SKEW = 38,
    PUNY_DAMP = 700, PUNY_INITIAL_BIAS = 72, PUNY_INITIAL_N = 128;

// RFC 3492 解码：把 "fsqu00a" 还原成 "例子"
function punyDecodeLabel(input) {
  var output = [], n = PUNY_INITIAL_N, bias = PUNY_INITIAL_BIAS, i = 0;
  var basic = input.lastIndexOf('-');
  if (basic > 0) {
    for (var j = 0; j < basic; j++) output.push(input.charCodeAt(j));
  }
  var idx = basic > 0 ? basic + 1 : 0;

  while (idx < input.length) {
    var oldi = i, w = 1;
    for (var k = PUNY_BASE; ; k += PUNY_BASE) {
      if (idx >= input.length) throw new Error('truncated');
      var c = input.charCodeAt(idx++), digit;
      if (c >= 48 && c <= 57) digit = c - 22;          // 0-9 → 26-35
      else if (c >= 65 && c <= 90) digit = c - 65;     // A-Z → 0-25
      else if (c >= 97 && c <= 122) digit = c - 97;    // a-z → 0-25
      else throw new Error('bad digit');
      i += digit * w;
      var t = k <= bias ? PUNY_TMIN : (k >= bias + PUNY_TMAX ? PUNY_TMAX : k - bias);
      if (digit < t) break;
      w *= PUNY_BASE - t;
    }
    var out = output.length + 1;
    var delta = oldi === 0 ? Math.floor((i - oldi) / PUNY_DAMP) : Math.floor((i - oldi) / 2);
    delta += Math.floor(delta / out);
    var kk = 0;
    while (delta > ((PUNY_BASE - PUNY_TMIN) * PUNY_TMAX) >> 1) {
      delta = Math.floor(delta / (PUNY_BASE - PUNY_TMIN));
      kk += PUNY_BASE;
    }
    bias = Math.floor(kk + (PUNY_BASE - PUNY_TMIN + 1) * delta / (delta + PUNY_SKEW));
    n += Math.floor(i / out);
    i = i % out;
    output.splice(i, 0, n);
    i++;
  }
  return String.fromCodePoint.apply(null, output);
}

// 整个域名（各标签）解码；纯 ASCII 无 xn-- 前缀的标签原样返回
function punyDecodeDomain(host) {
  return String(host).split('.').map(function (label) {
    if (/^xn--/i.test(label)) {
      try { return punyDecodeLabel(label.slice(4).toLowerCase()); }
      catch (e) { return label; }
    }
    return label;
  }).join('.');
}

// 拆出主机名：接受裸域名、带协议、带路径的完整 URL
function punyHostOf(str) {
  var s = String(str == null ? '' : str).trim();
  if (!s) return null;
  var hasScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(s);
  try {
    var u = new URL(hasScheme ? s : 'http://' + s);
    return {
      ascii: u.hostname,
      unicode: punyDecodeDomain(u.hostname),
      rest: (u.pathname === '/' ? '' : u.pathname) + u.search + u.hash,
      hasScheme: hasScheme,
      scheme: hasScheme ? u.protocol.replace(':', '') : ''
    };
  } catch (e) {
    return null;
  }
}

// 码点长度（不是 UTF-16 长度）："例子" 是 2 个字符而不是 2 个代理对
function punyCharLen(s) {
  return Array.from(String(s)).length;
}

function punyInfo(input) {
  var h = punyHostOf(input);
  if (!h) return { valid: false, reason: 'host' };
  var asciiLabels = h.ascii.split('.');
  var uniLabels = h.unicode.split('.');
  var labels = [];
  for (var i = 0; i < asciiLabels.length; i++) {
    var a = asciiLabels[i], u = uniLabels[i] || a;
    labels.push({
      ascii: a,
      unicode: u,
      // 前缀长度限制按「ASCII 形式」算：注册局校验的就是这个串
      len: a.length,
      tooLong: a.length > 63,
      isPuny: /^xn--/i.test(a)
    });
  }
  return {
    valid: true,
    input: String(input),
    ascii: h.ascii,
    unicode: h.unicode,
    rest: h.rest,
    labels: labels,
    totalLen: h.ascii.length,
    tooLong: h.ascii.length > 253,
    changed: h.ascii !== h.unicode,
    isIdn: h.ascii !== h.unicode
  };
}

// ---------------------------------------------------------------- 页面
function punyTL() { return G.__TL__ || {}; }

function punyRender() {
  var L = punyTL();
  var box = document.getElementById('punyResult');
  if (!box) return;
  var raw = getVal('punyInput');
  if (!raw.trim()) {
    box.innerHTML = '<div class="tl-hint">' + escHtml(L.hint || '') + '</div>';
    return;
  }
  var r = punyInfo(raw);
  if (!r.valid) {
    box.innerHTML = '<div class="tl-err">' + escHtml(L.err_host || '') + '</div>';
    return;
  }

  var html = '<table class="dt-table"><tbody>';
  html += '<tr><th style="width:34%">' + escHtml(L.r_ascii) + '</th><td><code>' +
    escHtml(r.ascii) + '</code></td></tr>';
  html += '<tr><th>' + escHtml(L.r_unicode) + '</th><td><code>' + escHtml(r.unicode) + '</code></td></tr>';
  html += '<tr><th>' + escHtml(L.r_len) + '</th><td>' + r.totalLen +
    (r.tooLong ? ' <span style="color:var(--danger)">' + escHtml(L.too_long_domain) + '</span>' : '') +
    '</td></tr>';
  html += '<tr><th>' + escHtml(L.r_status) + '</th><td>' +
    escHtml(r.isIdn ? L.status_idn : L.status_ascii) + '</td></tr>';
  if (r.rest) {
    html += '<tr><th>' + escHtml(L.r_rest) + '</th><td><code>' + escHtml(r.rest) + '</code></td></tr>';
  }
  html += '</tbody></table>';

  // 标签明细：逐段显示，方便判断是哪一段超了 63 字节
  html += '<table class="dt-table" style="margin-top:12px"><thead><tr><th>#</th><th>' +
    escHtml(L.c_unicode) + '</th><th>' + escHtml(L.c_ascii) + '</th><th>' +
    escHtml(L.c_len) + '</th></tr></thead><tbody>';
  for (var i = 0; i < r.labels.length; i++) {
    var lb = r.labels[i];
    html += '<tr' + (lb.tooLong ? ' class="dt-bad"' : '') + '><td>' + (i + 1) + '</td><td>' +
      escHtml(lb.unicode) + '</td><td><code>' + escHtml(lb.ascii) + '</code></td><td>' +
      lb.len + (lb.tooLong ? ' ⚠' : '') + '</td></tr>';
  }
  html += '</tbody></table>';
  box.innerHTML = html;
}

G.punyRender = punyRender;
G.punyClear = function () { setVal('punyInput', ''); punyRender(); };
// 演示域名随页面语言切换：中文页用中文域名，英文页用带变音符的拉丁/西里尔域名，
// 否则中文字面量会被内联进英文页（check.py 的非 CJK 页零中文门禁会挂）。
function punySampleText() {
  var tl = (typeof window !== 'undefined' && window.__TL__) || {};
  return tl.sample_text || 'xn--mnchen-3ya.de';
}
G.punySample = function () { setVal('punyInput', punySampleText()); punyRender(); };

function initPuny() {
  var input = document.getElementById('punyInput');
  if (!input) return;
  if (!input.value) input.value = punySampleText();
  punyRender();
  input.addEventListener('input', punyRender);
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPuny);
  } else {
    initPuny();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { punyDecodeLabel: punyDecodeLabel, punyDecodeDomain: punyDecodeDomain,
                     punyHostOf: punyHostOf, punyInfo: punyInfo, punyCharLen: punyCharLen };
}
