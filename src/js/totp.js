/* totp.js —— TOTP（RFC 6238）验证码生成。
 *
 * 纯前端：密钥只存在于当前输入框和一次 HMAC 计算里，不发往任何服务器，
 * 也不写 localStorage —— 刷新即清空，这也是页面上明确写出来的承诺。
 *
 * 唯一的网络动作是用户主动点「校准本机时间」时向**本站**发一次 HEAD 请求，
 * 读响应头里的 Date。它不带密钥，也不能反推密钥。
 *
 * 面向用户的文案全部走 window.__TL__（英文页零中文由 check.py 把关）。
 */
var G = (typeof window !== 'undefined') ? window : {};

// ---------------------------------------------------------------- 参数清洗

/** 位数只接受 6~8 —— RFC 4226 的动态截断最多给出 10 位十进制，密码学界通行的就是 6 与 8。 */
function totpDigits(v) {
  var n = parseInt(v, 10);
  if (!isFinite(n) || n < 6 || n > 8) return 6;
  return n;
}

/** 周期：常见 30 秒，也有 60；上限 300 防止误输入导致倒计时诡异。 */
function totpPeriod(v) {
  var n = parseInt(v, 10);
  if (!isFinite(n) || n < 1 || n > 300) return 30;
  return n;
}

/** 算法名归一：otpauth 里写 SHA1 / SHA-1 / sha256 都要认。 */
function totpAlgo(v) {
  var s = String(v == null ? '' : v).toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (s === 'SHA256') return 'SHA-256';
  if (s === 'SHA512') return 'SHA-512';
  return 'SHA-1';
}

// ---------------------------------------------------------------- Base32

/** 规范化：去掉空格、连字符、等号填充，统一大写。
 *  用户从 Google Authenticator / 1Password / 短信里复制出来的密钥几乎都带空格分组，
 *  直接按原样解码会失败，所以清洗是必须的而不是可选的。
 */
function totpBase32Clean(s) {
  return String(s == null ? '' : s).replace(/[\s\-_=]/g, '').toUpperCase();
}

/**
 * Base32 解码（RFC 4648，字母表 A-Z2-7）。
 * 返回 {ok, bytes, bad}：不用抛异常，因为输入完全来自用户粘贴，异常会把整页交互打断。
 * bad 是第一个非法字符，用来在界面上精确告诉用户「第几个字符不对」。
 */
function totpBase32Decode(s) {
  var clean = totpBase32Clean(s);
  if (!clean) return { ok: false, bytes: null, bad: '', empty: true };
  var out = [];
  var buf = 0;
  var bits = 0;
  for (var i = 0; i < clean.length; i++) {
    var ch = clean.charAt(i);
    var val;
    if (ch >= 'A' && ch <= 'Z') val = ch.charCodeAt(0) - 65;
    else if (ch >= '2' && ch <= '7') val = ch.charCodeAt(0) - 24;   // '2' → 26
    else return { ok: false, bytes: null, bad: ch, empty: false };
    buf = (buf << 5) | val;
    bits += 5;
    if (bits >= 8) {
      bits -= 8;
      out.push((buf >> bits) & 0xff);
    }
  }
  if (!out.length) return { ok: false, bytes: null, bad: '', empty: true };
  return { ok: true, bytes: new Uint8Array(out), bad: '', empty: false };
}

// ---------------------------------------------------------------- HOTP / TOTP

/** 时间步序号：Unix 秒 / 周期，向下取整。 */
function totpCounter(nowMs, period) {
  var p = totpPeriod(period);
  return Math.floor(Math.floor(nowMs / 1000) / p);
}

/** 当前时间步还剩几秒（1..period）。跨步瞬间返回整周期，不会返回 0。 */
function totpRemaining(nowMs, period) {
  var p = totpPeriod(period);
  var elapsed = Math.floor(nowMs / 1000) % p;
  if (elapsed < 0) elapsed = 0;
  return p - elapsed;
}

/** 计数器转 8 字节大端。
 *  不用 BigInt：Number 精确整数上限 2^53，而计数到 2^32 需要 136 年（30 秒周期），
 *  拆成高低两半既够用又没有任何精度隐患。
 */
function totpCounterBytes(counter) {
  var n = Math.max(0, Math.floor(counter));
  var hi = Math.floor(n / 4294967296);
  var lo = n % 4294967296;
  return new Uint8Array([
    (hi >>> 24) & 0xff, (hi >>> 16) & 0xff, (hi >>> 8) & 0xff, hi & 0xff,
    (lo >>> 24) & 0xff, (lo >>> 16) & 0xff, (lo >>> 8) & 0xff, lo & 0xff
  ]);
}

/**
 * RFC 4226 §5.3 动态截断：取 HMAC 最后一字节的低 4 位作偏移，
 * 从该位置读 4 字节、抹掉最高位（避免 JS 位运算的符号位），再对 10^digits 取模。
 */
function totpHotp(hmac, digits) {
  var d = totpDigits(digits);
  var mac = hmac || [];
  if (mac.length < 20) return '';
  var offset = mac[mac.length - 1] & 0x0f;
  if (offset + 4 > mac.length) return '';
  var bin = ((mac[offset] & 0x7f) << 24) |
            ((mac[offset + 1] & 0xff) << 16) |
            ((mac[offset + 2] & 0xff) << 8) |
            (mac[offset + 3] & 0xff);
  var mod = Math.pow(10, d);
  var code = bin % mod;
  var str = String(code);
  while (str.length < d) str = '0' + str;
  return str;
}

/** 把验证码按前后两半分开展示（123 456），比连写更好读也更好抄。 */
function totpFormat(code) {
  var s = String(code == null ? '' : code);
  if (s.length < 6) return s;
  var half = Math.ceil(s.length / 2);
  return s.slice(0, half) + ' ' + s.slice(half);
}

/** otpauth://totp/Issuer:account?secret=...&issuer=...&digits=6&period=30&algorithm=SHA1 */
function totpParseUri(uri) {
  var raw = String(uri == null ? '' : uri).replace(/^\s+|\s+$/g, '');
  if (!/^otpauth:\/\//i.test(raw)) return null;
  var rest = raw.replace(/^otpauth:\/\//i, '');
  var qIdx = rest.indexOf('?');
  var head = qIdx >= 0 ? rest.slice(0, qIdx) : rest;
  var query = qIdx >= 0 ? rest.slice(qIdx + 1) : '';

  var slash = head.indexOf('/');
  var type = (slash >= 0 ? head.slice(0, slash) : head).toLowerCase();
  if (type !== 'totp') return { ok: false, reason: 'type', type: type };

  var label = slash >= 0 ? head.slice(slash + 1) : '';
  try { label = decodeURIComponent(label); } catch (e) { /* 畸形编码就按原样用 */ }

  var params = {};
  var pairs = query.split('&');
  for (var i = 0; i < pairs.length; i++) {
    if (!pairs[i]) continue;
    var eq = pairs[i].indexOf('=');
    var k = eq >= 0 ? pairs[i].slice(0, eq) : pairs[i];
    var v = eq >= 0 ? pairs[i].slice(eq + 1) : '';
    try { v = decodeURIComponent(v.replace(/\+/g, ' ')); } catch (e) { /* 同上 */ }
    params[k.toLowerCase()] = v;
  }

  var issuer = params.issuer || '';
  var account = label;
  var colon = label.indexOf(':');
  if (colon >= 0) {
    if (!issuer) issuer = label.slice(0, colon).replace(/^\s+|\s+$/g, '');
    account = label.slice(colon + 1).replace(/^\s+|\s+$/g, '');
  }

  return {
    ok: true,
    secret: totpBase32Clean(params.secret || ''),
    issuer: issuer,
    account: account,
    digits: totpDigits(params.digits || 6),
    period: totpPeriod(params.period || 30),
    algorithm: totpAlgo(params.algorithm || 'SHA1')
  };
}

/** 生成规范 otpauth 链接，方便用户自己存起来（本页不落盘）。 */
function totpBuildUri(opts) {
  opts = opts || {};
  var issuer = String(opts.issuer || '').replace(/^\s+|\s+$/g, '');
  var account = String(opts.account || '').replace(/^\s+|\s+$/g, '') || 'account';
  var label = issuer ? issuer + ':' + account : account;
  var q = ['secret=' + encodeURIComponent(totpBase32Clean(opts.secret || ''))];
  if (issuer) q.push('issuer=' + encodeURIComponent(issuer));
  q.push('algorithm=' + totpAlgo(opts.algorithm).replace(/-/g, ''));
  q.push('digits=' + totpDigits(opts.digits));
  q.push('period=' + totpPeriod(opts.period));
  return 'otpauth://totp/' + encodeURIComponent(label).replace(/%3A/g, ':') + '?' + q.join('&');
}

// ---------------------------------------------------------------- HMAC（异步）

/** 用 Web Crypto 算 HMAC。返回 Promise<Uint8Array>。
 *  这里只用 crypto.subtle —— 它是浏览器内唯一的原生 HMAC，自己用 JS 实现 SHA-1
 *  既慢又容易写错；代价是需要安全上下文（https 或 localhost）。 */
function totpHmac(secretBytes, counter, algorithm) {
  var subtle = (G.crypto && G.crypto.subtle) || null;
  if (!subtle) return Promise.reject(new Error('nocrypto'));
  var algo = totpAlgo(algorithm);
  return subtle.importKey('raw', secretBytes, { name: 'HMAC', hash: { name: algo } }, false, ['sign'])
    .then(function (key) {
      return subtle.sign('HMAC', key, totpCounterBytes(counter));
    })
    .then(function (sig) {
      return new Uint8Array(sig);
    });
}

// ---------------------------------------------------------------- 页面

function initTotp() {
  var input = document.getElementById('ttSecret');
  if (!input) return;
  var L = G.__TL__ || {};

  var codeBtn = document.getElementById('ttCode');
  var barFill = document.getElementById('ttBarFill');
  var remainEl = document.getElementById('ttRemain');
  var errEl = document.getElementById('ttErr');
  var skewEl = document.getElementById('ttSkew');
  var toast = document.getElementById('ttToast');
  var algoSel = document.getElementById('ttAlgo');
  var digitsSel = document.getElementById('ttDigits');
  var periodSel = document.getElementById('ttPeriod');
  var uriEl = document.getElementById('ttUri');
  var idleEl = document.getElementById('ttIdle');

  var skewMs = 0;
  var lastCounter = -1;
  var lastCode = '';
  var busy = false;
  var timer = null;

  function t(key, fallback) {
    var v = L[key];
    return (v == null || v === '') ? (fallback == null ? '' : fallback) : v;
  }

  function flash(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.hidden = false;
    clearTimeout(flash._t);
    flash._t = setTimeout(function () { toast.hidden = true; }, 1800);
  }

  function showErr(msg) {
    if (!errEl) return;
    if (!msg) { errEl.hidden = true; errEl.textContent = ''; return; }
    errEl.hidden = false;
    errEl.textContent = msg;
  }

  function params() {
    return {
      algorithm: totpAlgo(algoSel && algoSel.value),
      digits: totpDigits(digitsSel && digitsSel.value),
      period: totpPeriod(periodSel && periodSel.value)
    };
  }

  /** 当前输入对应的密钥；非法时顺手把错误写在输入框下面。 */
  function secretBytes() {
    var d = totpBase32Decode(input.value);
    if (!d.ok) {
      if (d.empty) showErr('');
      else if (d.bad) showErr(t('err_char').replace('{c}', d.bad));
      else showErr(t('err_short'));
      return null;
    }
    showErr('');
    return d.bytes;
  }

  function idle() {
    if (codeBtn) {
      codeBtn.textContent = t('code_idle', '\u2014 \u2014 \u2014');
      codeBtn.classList.add('is-idle');
    }
    if (remainEl) remainEl.textContent = '';
    if (barFill) barFill.style.width = '0%';
    if (idleEl) idleEl.textContent = t('idle_hint');
  }

  function renderRemain(nowMs, period) {
    var remain = totpRemaining(nowMs, period);
    var pct = ((period - remain) / period) * 100;
    if (remainEl) remainEl.textContent = remain + 's';
    if (barFill) {
      barFill.style.width = pct.toFixed(2) + '%';
      // 最后 5 秒变色，提醒「这个码马上作废」
      barFill.className = 'tt-bar-fill' + (remain <= 5 ? ' is-warn' : '');
    }
  }

  function compute(force) {
    var bytes = secretBytes();
    if (!bytes) { idle(); lastCode = ''; lastCounter = -1; return; }
    if (idleEl) idleEl.textContent = '';

    var now = Date.now() + skewMs;
    var p = params();
    var counter = totpCounter(now, p.period);
    renderRemain(now, p.period);
    if (!force && counter === lastCounter && lastCode) return;
    if (busy) return;

    lastCounter = counter;
    busy = true;
    totpHmac(bytes, counter, p.algorithm).then(function (mac) {
      var code = totpHotp(mac, p.digits);
      if (!code) { idle(); return; }
      lastCode = code;
      if (codeBtn) {
        codeBtn.textContent = totpFormat(code);
        codeBtn.classList.remove('is-idle');
        codeBtn.setAttribute('data-code', code);
      }
    }, function (e) {
      lastCounter = -1;
      showErr(t('err_nocrypto'));
    }).then(function () { busy = false; });
  }

  function tick() {
    if (!input.value.replace(/\s/g, '')) { idle(); return; }
    compute(false);
  }

  function start() {
    if (timer) clearInterval(timer);
    // 200ms 而不是 1000ms：进度条要平滑，而 HMAC 只在时间步变化时才真的重算
    timer = setInterval(tick, 200);
  }

  // ---- 输入 —— 粘贴 otpauth 链接时自动拆参数
  input.addEventListener('input', function () {
    var v = input.value.replace(/^\s+|\s+$/g, '');
    var u = totpParseUri(v);
    if (u && u.ok) {
      input.value = u.secret;
      if (algoSel) algoSel.value = u.algorithm;
      if (digitsSel) digitsSel.value = String(u.digits);
      if (periodSel) periodSel.value = String(u.period);
      renderUriInfo(u);
    } else if (u && !u.ok) {
      showErr(t('err_hotp'));
    }
    lastCounter = -1;
    lastCode = '';
    compute(true);
  });

  function renderUriInfo(u) {
    if (!uriEl) return;
    if (u && u.ok && (u.issuer || u.account)) {
      var bits = [];
      if (u.issuer) bits.push(u.issuer);
      if (u.account) bits.push(u.account);
      uriEl.textContent = bits.join(' · ');
      uriEl.hidden = false;
    } else {
      uriEl.hidden = true;
      uriEl.textContent = '';
    }
  }

  if (algoSel) algoSel.addEventListener('change', function () { lastCounter = -1; lastCode = ''; compute(true); });
  if (digitsSel) digitsSel.addEventListener('change', function () { lastCounter = -1; lastCode = ''; compute(true); });
  if (periodSel) periodSel.addEventListener('change', function () { lastCounter = -1; lastCode = ''; compute(true); });

  // ---- 点击验证码即复制
  if (codeBtn) {
    codeBtn.addEventListener('click', function () {
      if (!lastCode) return;
      var done = function () { flash(t('copied')); };
      var fail = function () { flash(t('copy_fail')); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(lastCode).then(done, fail);
      } else {
        try {
          var ta = document.createElement('textarea');
          ta.value = lastCode;
          ta.style.position = 'fixed';
          ta.style.left = '-9999px';
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          done();
        } catch (e) { fail(); }
      }
    });
  }

  var copyBtn = document.getElementById('ttCopy');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      if (!lastCode) { flash(t('copy_empty')); return; }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(lastCode).then(function () { flash(t('copied')); },
          function () { flash(t('copy_fail')); });
      } else {
        codeBtn && codeBtn.click();
      }
    });
  }

  var clearBtn = document.getElementById('ttClear');
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      input.value = '';
      lastCode = '';
      lastCounter = -1;
      showErr('');
      renderUriInfo(null);
      idle();
    });
  }

  var eyeBtn = document.getElementById('ttEye');
  if (eyeBtn) {
    eyeBtn.addEventListener('click', function () {
      // 初始是明文（粘完能核对），点一下才遮起来
      var toHidden = input.type !== 'password';
      input.type = toHidden ? 'password' : 'text';
      eyeBtn.textContent = toHidden ? t('btn_show') : t('btn_hide');
    });
  }

  // ---- 时钟校准：TOTP 失败最常见的原因就是本机时间偏了
  var syncBtn = document.getElementById('ttSync');
  if (syncBtn) {
    syncBtn.addEventListener('click', function () {
      syncBtn.disabled = true;
      var t0 = Date.now();
      fetch(location.href.split('#')[0], { method: 'HEAD', cache: 'no-store' })
        .then(function (r) {
          var d = r.headers.get('date');
          if (!d) throw new Error('nodate');
          var serverMs = new Date(d).getTime();
          if (!isFinite(serverMs)) throw new Error('baddate');
          var rtt = Date.now() - t0;
          // 响应头的时间精确到秒，再叠上往返延迟，所以估算误差就是 ±(rtt/2 + 1s)
          skewMs = serverMs + Math.floor(rtt / 2) - Date.now();
          var secs = Math.round(skewMs / 1000);
          if (skewEl) {
            skewEl.hidden = false;
            skewEl.textContent = t('skew_ok')
              .replace('{n}', (secs > 0 ? '+' : '') + secs)
              .replace('{e}', String(Math.round(rtt / 2 / 1000 + 1)));
          }
          lastCounter = -1;
          lastCode = '';
          compute(true);
        })
        .catch(function () {
          if (skewEl) {
            skewEl.hidden = false;
            skewEl.textContent = t('skew_fail');
          }
        })
        .then(function () { syncBtn.disabled = false; });
    });
  }

  // 页面在后台时不必重算；切回来立刻追一次（时间步可能已经跳了好几个）
  if (typeof document.addEventListener === 'function') {
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) { lastCounter = -1; compute(true); }
    });
  }

  start();
  if (input.value) compute(true);
  else idle();
}

// ---------------------------------------------------------------- 导出

G.totpDigits = totpDigits;
G.totpPeriod = totpPeriod;
G.totpAlgo = totpAlgo;
G.totpBase32Clean = totpBase32Clean;
G.totpBase32Decode = totpBase32Decode;
G.totpCounter = totpCounter;
G.totpRemaining = totpRemaining;
G.totpCounterBytes = totpCounterBytes;
G.totpHotp = totpHotp;
G.totpFormat = totpFormat;
G.totpParseUri = totpParseUri;
G.totpBuildUri = totpBuildUri;
G.totpHmac = totpHmac;
G.initTotp = initTotp;

if (typeof G.addEventListener === 'function' && typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    G.addEventListener('DOMContentLoaded', initTotp);
  } else {
    initTotp();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    totpDigits: totpDigits,
    totpPeriod: totpPeriod,
    totpAlgo: totpAlgo,
    totpBase32Clean: totpBase32Clean,
    totpBase32Decode: totpBase32Decode,
    totpCounter: totpCounter,
    totpRemaining: totpRemaining,
    totpCounterBytes: totpCounterBytes,
    totpHotp: totpHotp,
    totpFormat: totpFormat,
    totpParseUri: totpParseUri,
    totpBuildUri: totpBuildUri
  };
}
