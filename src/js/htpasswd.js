// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// htpasswd.js — 生成 Nginx / Apache 的 Basic 认证文件行（apr1 / SHA1 / 明文）
// 为什么不用现成的 md5()：apr1 需要「对任意字节串做 MD5」，中间会喂进 16 字节二进制摘要，
// 而 hash.js 的 md5() 走 TextEncoder，非 ASCII 字节会被 UTF-8 二次编码，结果必然错。
// 所以这里带一份字节级的 MD5 实现（输入 Uint8Array / 普通数组，输出 16 字节）。

var HT_MD5_K = [
  0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
  0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
  0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
  0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
  0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
  0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
  0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
  0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
];
var HT_MD5_S = [
  7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
  5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
];

function htRotl(x, n) { return ((x << n) | (x >>> (32 - n))) >>> 0; }

// 字节级 MD5：返回 16 字节数组
function htMd5Bytes(input) {
  // 传字符串时按 UTF-8 取字节：Uint8Array 构造器对字符串会静默产出空数组，
  // 那样 MD5('abc') 会算成 MD5('')，错得毫无征兆。
  var msg = typeof input === 'string' ? htUtf8(input)
    : (input instanceof Uint8Array ? input : new Uint8Array(input));
  var len = msg.length;
  var withOne = len + 1;
  var padLen = ((withOne + 8 + 63) >> 6) << 6;
  var buf = new Uint8Array(padLen);
  buf.set(msg);
  buf[len] = 0x80;
  var bitLenLo = (len * 8) >>> 0;
  var bitLenHi = Math.floor(len * 8 / 4294967296) >>> 0;
  var dv = new DataView(buf.buffer);
  dv.setUint32(padLen - 8, bitLenLo, true);
  dv.setUint32(padLen - 4, bitLenHi, true);

  var h0 = 0x67452301, h1 = 0xefcdab89, h2 = 0x98badcfe, h3 = 0x10325476;
  var w = new Uint32Array(16);
  for (var off = 0; off < padLen; off += 64) {
    for (var j = 0; j < 16; j++) w[j] = dv.getUint32(off + j * 4, true);
    var a = h0, b = h1, c = h2, d = h3;
    for (var i = 0; i < 64; i++) {
      var f, g;
      if (i < 16) { f = (b & c) | (~b & d); g = i; }
      else if (i < 32) { f = (d & b) | (~d & c); g = (5 * i + 1) & 15; }
      else if (i < 48) { f = b ^ c ^ d; g = (3 * i + 5) & 15; }
      else { f = c ^ (b | ~d); g = (7 * i) & 15; }
      var tmp = d;
      d = c; c = b;
      b = (b + htRotl((a + f + HT_MD5_K[i] + w[g]) >>> 0, HT_MD5_S[i])) >>> 0;
      a = tmp;
    }
    h0 = (h0 + a) >>> 0; h1 = (h1 + b) >>> 0;
    h2 = (h2 + c) >>> 0; h3 = (h3 + d) >>> 0;
  }
  var out = new Uint8Array(16);
  var ov = new DataView(out.buffer);
  ov.setUint32(0, h0, true); ov.setUint32(4, h1, true);
  ov.setUint32(8, h2, true); ov.setUint32(12, h3, true);
  return out;
}

function htUtf8(str) {
  if (typeof TextEncoder !== 'undefined') return new TextEncoder().encode(str);
  var out = [], s = String(str);
  for (var i = 0; i < s.length; i++) {
    var c = s.charCodeAt(i);
    if (c < 0x80) out.push(c);
    else if (c < 0x800) out.push(0xc0 | (c >> 6), 0x80 | (c & 63));
    else out.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
  }
  return new Uint8Array(out);
}

function htConcat(parts) {
  var total = 0, i;
  for (i = 0; i < parts.length; i++) total += parts[i].length;
  var out = new Uint8Array(total), pos = 0;
  for (i = 0; i < parts.length; i++) { out.set(parts[i], pos); pos += parts[i].length; }
  return out;
}

// Apache 的 to64 编码表（apr1 专用，不是标准 Base64）
var HT_ITOA64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

// apr1 的打包顺序是定死的：按每 3 字节一组，从低位开始每 6 位取一个字符。
// 这里必须逐字照抄 Apache 的 b64_from_24bit 调用顺序，按顺序字节流编码会得到完全不同的串。
function htB64From24(b2, b1, b0, n) {
  var w = ((b2 & 0xff) << 16) | ((b1 & 0xff) << 8) | (b0 & 0xff);
  var out = '';
  for (var i = 0; i < n; i++) {
    out += HT_ITOA64.charAt(w & 0x3f);
    w >>= 6;
  }
  return out;
}

// 兼容入口：对 16 字节摘要按 apr1 规则生成 22 字符
function htTo64(bytes) {
  var f = bytes;
  return htB64From24(f[0], f[6], f[12], 4) +
         htB64From24(f[1], f[7], f[13], 4) +
         htB64From24(f[2], f[8], f[14], 4) +
         htB64From24(f[3], f[9], f[15], 4) +
         htB64From24(f[4], f[10], f[5], 4) +
         htB64From24(0, 0, f[11], 2);
}

// apr1（$apr1$salt$hash）：Apache htpasswd -m / nginx 常用的那种
function htApr1(password, salt) {
  var pw = htUtf8(String(password));
  var saltStr = String(salt || '').slice(0, 8);
  if (!saltStr) saltStr = htRandomSalt(8);
  var magic = htUtf8('$apr1$');
  var saltB = htUtf8(saltStr);

  var ctx = htConcat([pw, magic, saltB]);
  var final = htMd5Bytes(htConcat([pw, saltB, pw]));

  // 把 16 字节摘要按密码长度循环拼进去
  for (var pl = pw.length; pl > 0; pl -= 16) {
    ctx = htConcat([ctx, final.subarray(0, Math.min(pl, 16))]);
  }

  // 按密码长度二进制位的 0/1 追加 \0 或密码首字节
  for (var i = pw.length; i; i >>= 1) {
    ctx = htConcat([ctx, (i & 1) ? new Uint8Array([0]) : pw.subarray(0, 1)]);
  }

  final = htMd5Bytes(ctx);

  // 1000 轮搅拌
  for (var r = 0; r < 1000; r++) {
    var parts = [];
    parts.push((r & 1) ? pw : final);
    if (r % 3) parts.push(saltB);
    if (r % 7) parts.push(pw);
    parts.push((r & 1) ? final : pw);
    final = htMd5Bytes(htConcat(parts));
  }

  // 按 apr1 规定的字节序打包
  return '$apr1$' + saltStr + '$' + htTo64(final);
}

function htRandomSalt(n) {
  var chars = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  var out = '';
  var buf = new Uint8Array(n);
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) crypto.getRandomValues(buf);
  else for (var i = 0; i < n; i++) buf[i] = Math.floor(Math.random() * 256);
  for (var j = 0; j < n; j++) out += chars.charAt(buf[j] % 64);
  return out;
}

// SHA-1 的 {SHA} 形式（Apache -s），需要 Web Crypto，返回 Promise
function htSha1(password) {
  var buf = htUtf8(String(password));
  return crypto.subtle.digest('SHA-1', buf).then(function (d) {
    var bytes = new Uint8Array(d), bin = '';
    for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return '{SHA}' + btoa(bin);
  });
}

// ---------------------------------------------------------------- 页面
function htTL() { return G.__TL__ || {}; }
var htAlgo = 'apr1';

function htBuildLine(user, pw, algo) {
  if (algo === 'plain') return user + ':' + pw;
  if (algo === 'sha') return null;                  // 异步，单独处理
  return user + ':' + htApr1(pw, htSalt);
}
var htSalt = '';

function htRender() {
  var L = htTL();
  var box = document.getElementById('htOut');
  if (!box) return;
  // 把当前盐值显示出来：同样的密码换个盐就是另一个串，这是很多人踩过的坑
  var saltBox = document.getElementById('htSaltShow');
  if (saltBox) saltBox.value = htSalt;
  var user = getVal('htUser').trim();
  var pw = getVal('htPass');
  if (!user || !pw) {
    box.innerHTML = '<div class="tl-hint">' + escHtml(L.hint || '') + '</div>';
    return;
  }
  if (!/^[A-Za-z0-9._@-]{1,64}$/.test(user)) {
    box.innerHTML = '<div class="tl-err">' + escHtml(L.err_user || '') + '</div>';
    return;
  }
  if (htAlgo === 'sha') {
    htSha1(pw).then(function (line) {
      htShow(user + ':' + line, L);
    }, function () {
      box.innerHTML = '<div class="tl-err">' + escHtml(L.err_crypto || '') + '</div>';
    });
    return;
  }
  htShow(htBuildLine(user, pw, htAlgo), L);
}

function htShow(line, L) {
  var box = document.getElementById('htOut');
  var html = '<div class="tl-copyline"><code id="htLine">' + escHtml(line) +
    '</code><button class="btn btn-sm" type="button" onclick="htCopy()">' +
    escHtml(L.copy || '') + '</button></div>';
  html += '<div class="tl-note" style="margin-top:10px">' + escHtml(L.usage || '') + '</div>';
  var cfg = 'auth_basic "Restricted";\n' +
    'auth_basic_user_file /etc/nginx/.htpasswd;';
  var apache = htAlgo === 'plain' ? '' : '# ' + (L.gen_comment || 'Apache httpd-tools') + '\n' +
    'htpasswd -c /etc/nginx/.htpasswd ' + (getVal('htUser').trim());
  html += '<div class="tl-copyline"><span style="min-width:70px;font-size:12.5px;color:var(--text-secondary)">nginx</span><code>' +
    escHtml(cfg) + '</code></div>';
  if (apache) {
    html += '<div class="tl-copyline"><span style="min-width:70px;font-size:12.5px;color:var(--text-secondary)">apache</span><code>' +
      escHtml(apache) + '</code></div>';
  }
  box.innerHTML = html;
}

G.htRender = htRender;
G.htCopy = function () {
  var el = document.getElementById('htLine');
  if (el && navigator.clipboard) {
    navigator.clipboard.writeText(el.textContent).then(function () {
      toast((htTL().copied || 'OK'));
    }, function () {
      toast((htTL().copy_fail || 'Copy failed'), 'error');
    });
  }
};
G.htNewSalt = function () { htSalt = htRandomSalt(8); htRender(); };

function initHt() {
  var u = document.getElementById('htUser');
  if (!u) return;
  htSalt = htRandomSalt(8);
  if (!u.value) u.value = 'admin';
  htRender();
  u.addEventListener('input', htRender);
  document.getElementById('htPass').addEventListener('input', htRender);

  var al = document.getElementById('htAlgo');
  if (al) {
    al.addEventListener('click', function (e) {
      var b = e.target.closest('[data-algo]');
      if (!b) return;
      htAlgo = b.getAttribute('data-algo');
      Array.prototype.forEach.call(al.querySelectorAll('[data-algo]'), function (x) {
        x.classList.toggle('active', x === b);
      });
      htRender();
    });
  }
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHt);
  } else {
    initHt();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { htMd5Bytes: htMd5Bytes, htApr1: htApr1, htTo64: htTo64,
                     htRandomSalt: htRandomSalt, htUtf8: htUtf8 };
}
