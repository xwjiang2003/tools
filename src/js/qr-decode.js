/* qr-decode.js —— 二维码图片解码。
 *
 * 纯前端：图片只在本标签页内存里过一遍 canvas，jsQR 读像素，没有任何上传路径。
 * 所有面向用户的文本走 window.__TL__（英文页零中文由 check.py 把关）。
 */
var G = (typeof window !== 'undefined') ? window : {};

// 短链服务：命中就在结果里提示一句，因为跳转前看不到真实去向。
var QR_SHORTENERS = [
  'bit.ly', 't.co', 'tinyurl.com', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly',
  'rebrand.ly', 's.id', 'url.cn', 'dwz.cn', 't.cn', 'suo.im', 'shorturl.at',
  'cutt.ly', 'rb.gy', 'v.gd'
];

// ---------------------------------------------------------------- 纯函数

/** decodeURIComponent 遇到畸形的 % 序列会抛 URIError，而二维码内容是任意的 —— 不能让它炸掉整条解码链。 */
function qrSafeDecode(s) {
  var v = String(s == null ? '' : s).replace(/\+/g, ' ');
  try { return decodeURIComponent(v); } catch (e) { return v; }
}

/** WIFI:T:WPA;S:ssid;P:pass;H:true;; —— 值里允许 \; \, \: \\ 转义。 */
function qrParseWifi(s) {
  var body = String(s || '').replace(/^WIFI:/i, '');
  var out = { ssid: '', pass: '', enc: '', hidden: false };
  var parts = [];
  var cur = '';
  for (var i = 0; i < body.length; i++) {
    var ch = body.charAt(i);
    if (ch === '\\' && i + 1 < body.length) { cur += body.charAt(i + 1); i++; continue; }
    if (ch === ';') { parts.push(cur); cur = ''; continue; }
    cur += ch;
  }
  if (cur) parts.push(cur);

  for (var k = 0; k < parts.length; k++) {
    var p = parts[k];
    if (p.length < 2 || p.charAt(1) !== ':') continue;
    var tag = p.charAt(0).toUpperCase();
    var val = p.slice(2);
    if (tag === 'S') out.ssid = val;
    else if (tag === 'P') out.pass = val;
    else if (tag === 'T') out.enc = val;
    else if (tag === 'H') out.hidden = /^(true|1|yes)$/i.test(val.trim());
  }
  return out;
}

/** vCard 3.0/4.0：按行取 FN / TEL / EMAIL / ORG / TITLE / URL，处理折行续行。 */
function qrParseVcard(s) {
  var out = { name: '', tel: '', email: '', org: '', title: '', site: '' };
  var text = String(s || '').replace(/\r\n/g, '\n').replace(/\n[ \t]/g, '');
  var lines = text.split('\n');
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];
    var idx = line.indexOf(':');
    if (idx < 1) continue;
    var prop = line.slice(0, idx).split(';')[0].toUpperCase();
    var val = line.slice(idx + 1).trim();
    if (!val) continue;
    if (prop === 'FN' && !out.name) out.name = val;
    else if (prop === 'TEL' && !out.tel) out.tel = val;
    else if (prop === 'EMAIL' && !out.email) out.email = val;
    else if (prop === 'ORG' && !out.org) out.org = val;
    else if (prop === 'TITLE' && !out.title) out.title = val;
    else if (prop === 'URL' && !out.site) out.site = val;
  }
  return out;
}

/** MECARD:N:张三;TEL:123;EMAIL:a@b.com;; */
function qrParseMecard(s) {
  var out = { name: '', tel: '', email: '', org: '', title: '', site: '' };
  var body = String(s || '').replace(/^MECARD:/i, '');
  var parts = body.split(';');
  for (var i = 0; i < parts.length; i++) {
    var p = parts[i];
    var idx = p.indexOf(':');
    if (idx < 1) continue;
    var tag = p.slice(0, idx).toUpperCase();
    var val = p.slice(idx + 1).replace(/\\([\\;,])/g, '$1').trim();
    if (!val) continue;
    if (tag === 'N' && !out.name) out.name = val;
    else if (tag === 'TEL' && !out.tel) out.tel = val;
    else if (tag === 'EMAIL' && !out.email) out.email = val;
    else if (tag === 'ORG' && !out.org) out.org = val;
    else if (tag === 'TITLE' && !out.title) out.title = val;
    else if (tag === 'URL' && !out.site) out.site = val;
  }
  return out;
}

/** 链接里的可疑信号。只给信号，不给"安全/不安全"的结论。 */
function qrUrlRisks(url) {
  var out = [];
  var u = String(url || '').trim();
  var m = /^([a-z][a-z0-9+.-]*):\/\/([^/?#]*)/i.exec(u);
  if (!m) return out;
  var scheme = m[1].toLowerCase();
  if (scheme === 'http') out.push('http');
  var auth = m[2];
  if (auth.indexOf('@') >= 0) out.push('userinfo');
  var host = auth.split('@').pop().replace(/:\d+$/, '').replace(/^\[|\]$/g, '');
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host) || host.indexOf(':') >= 0) out.push('ip');
  var bare = host.toLowerCase().replace(/^www\./, '');
  if (QR_SHORTENERS.indexOf(bare) >= 0) out.push('short');
  return out;
}

/**
 * 解码尺度计划。为什么要多档：jsQR 在 300~1200 px 之间最稳，
 * 原图太大（手机照片）会被内部降采样到糊，太小（贴图缩略图）则根本不够像素。
 * pad=true 的那一档会在四周补白边——二维码的静区被裁掉是最常见的失败原因。
 */
function qrScales(w, h) {
  var W = Math.max(1, Math.round(Number(w) || 0));
  var H = Math.max(1, Math.round(Number(h) || 0));
  var longest = Math.max(W, H);
  var targets = [];
  if (longest <= 2000) targets.push(longest);   // 原尺寸优先：清晰大图命中率最高
  targets.push(1600, 1000, 700);
  if (longest < 500) targets.push(900);         // 小图放大才够像素
  var seen = {};
  var out = [];
  for (var i = 0; i < targets.length; i++) {
    var t = Math.round(targets[i]);
    if (t < 40 || seen[t]) continue;
    seen[t] = 1;
    out.push({ maxSide: t, pad: false });
    out.push({ maxSide: t, pad: true });
  }
  return out;
}

/**
 * 把一段文本判成"要展示成什么"。
 * 返回 {kind, labelKey, raw, fields, link, risks, text, secretHidden}
 * fields 项：{key, value, tl} —— tl 非空时 value 是个 TL 键（如 v_yes）。
 * 纯函数，不碰 DOM 与 i18n，方便 Node 单测。
 */
function qrClassify(text) {
  var raw = (text == null) ? '' : String(text);
  var s = raw.replace(/^\uFEFF/, '').trim();
  if (!s) return { kind: 'empty', labelKey: 'kind_text', raw: raw, fields: [], link: null, risks: [], text: '' };

  var upper = s.toUpperCase();

  if (upper.indexOf('WIFI:') === 0) {
    var w = qrParseWifi(s);
    var wf = [];
    if (w.ssid) wf.push({ key: 'f_ssid', value: w.ssid });
    if (w.pass) wf.push({ key: 'f_pass', value: w.pass, secret: true });
    if (w.enc) wf.push({ key: 'f_enc', value: w.enc });
    if (w.hidden) wf.push({ key: 'f_hidden', value: 'v_yes', tl: 'v_yes' });
    return { kind: 'wifi', labelKey: 'kind_wifi', raw: raw, fields: wf, link: null, risks: [], text: s };
  }

  if (upper.indexOf('BEGIN:VCARD') === 0 || upper.indexOf('MECARD:') === 0) {
    var v = upper.indexOf('MECARD:') === 0 ? qrParseMecard(s) : qrParseVcard(s);
    var cf = [];
    if (v.name) cf.push({ key: 'f_name', value: v.name });
    if (v.tel) cf.push({ key: 'f_tel', value: v.tel });
    if (v.email) cf.push({ key: 'f_email', value: v.email });
    if (v.org) cf.push({ key: 'f_org', value: v.org });
    if (v.title) cf.push({ key: 'f_title', value: v.title });
    if (v.site) cf.push({ key: 'f_site', value: v.site });
    return { kind: 'vcard', labelKey: 'kind_vcard', raw: raw, fields: cf, link: null, risks: [], text: s };
  }

  if (upper.indexOf('MAILTO:') === 0) {
    var rest = s.slice(7);
    var q = rest.indexOf('?');
    var addr = q >= 0 ? rest.slice(0, q) : rest;
    var mf = [];
    if (addr) mf.push({ key: 'f_email', value: qrSafeDecode(addr) });
    if (q >= 0) {
      var params = rest.slice(q + 1).split('&');
      for (var pi = 0; pi < params.length; pi++) {
        var kv = params[pi].split('=');
        var name = (kv[0] || '').toLowerCase();
        var pv = qrSafeDecode(kv[1] || '');
        if (name === 'subject' && pv) mf.push({ key: 'f_subject', value: pv });
        else if (name === 'body' && pv) mf.push({ key: 'f_body', value: pv });
      }
    }
    return { kind: 'mailto', labelKey: 'kind_mailto', raw: raw, fields: mf, link: null, risks: [], text: s };
  }

  if (upper.indexOf('TEL:') === 0) {
    var tel = s.slice(4).trim();
    return {
      kind: 'tel', labelKey: 'kind_tel', raw: raw,
      fields: tel ? [{ key: 'f_tel', value: tel }] : [], link: null, risks: [], text: s
    };
  }

  if (upper.indexOf('SMSTO:') === 0 || upper.indexOf('SMS:') === 0) {
    var sbody = upper.indexOf('SMSTO:') === 0 ? s.slice(6) : s.slice(4);
    var ci = sbody.indexOf(':');
    var num = ci >= 0 ? sbody.slice(0, ci) : sbody;
    var body2 = ci >= 0 ? sbody.slice(ci + 1) : '';
    var sf = [];
    if (num) sf.push({ key: 'f_tel', value: num });
    if (body2) sf.push({ key: 'f_body', value: body2 });
    return { kind: 'sms', labelKey: 'kind_sms', raw: raw, fields: sf, link: null, risks: [], text: s };
  }

  if (upper.indexOf('GEO:') === 0) {
    var coords = s.slice(4).split(',');
    var gf = [];
    if (coords[0]) gf.push({ key: 'f_lat', value: coords[0].trim() });
    if (coords[1]) gf.push({ key: 'f_lon', value: coords[1].trim() });
    return { kind: 'geo', labelKey: 'kind_geo', raw: raw, fields: gf, link: null, risks: [], text: s };
  }

  if (upper.indexOf('OTPAUTH:') === 0) {
    // 只显示签发方与账号；密钥本身不展示，避免截图二次泄露。
    var of = [];
    var im = /[?&]issuer=([^&]*)/i.exec(s);
    var otpLabel = s.replace(/^otpauth:\/\/[^/]+\//i, '').split('?')[0];
    var decLabel = qrSafeDecode(otpLabel);
    var issuer = im ? qrSafeDecode(im[1]) : '';
    if (issuer) of.push({ key: 'f_issuer', value: issuer });
    if (decLabel) of.push({ key: 'f_account', value: decLabel });
    return {
      kind: 'otpauth', labelKey: 'kind_otpauth', raw: raw, fields: of,
      link: null, risks: [], text: s, secretHidden: /[?&]secret=/i.test(s)
    };
  }

  if (/^https?:\/\//i.test(s)) {
    return {
      kind: 'url', labelKey: 'kind_url', raw: raw, fields: [],
      link: s, risks: qrUrlRisks(s), text: s
    };
  }

  if (/^www\.[^\s]+$/i.test(s)) {
    var full = 'https://' + s;
    return {
      kind: 'url', labelKey: 'kind_url', raw: raw, fields: [],
      link: full, risks: qrUrlRisks(full), text: full
    };
  }

  return { kind: 'text', labelKey: 'kind_text', raw: raw, fields: [], link: null, risks: [], text: s };
}

// ---------------------------------------------------------------- 页面

function initQrDecode() {
  var drop = document.getElementById('qrDrop');
  if (!drop) return;

  var L = G.__TL__ || {};
  function T(k, fb) { var v = L[k]; return (v == null) ? (fb == null ? k : fb) : v; }
  function $(id) { return document.getElementById(id); }

  var fileInput = $('qrFile');
  var results = $('qrResults');
  var bar = $('qrBar');
  var statusEl = $('qrStatus');

  var state = { urls: [], queue: [], busy: false, total: 0, done: 0 };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function updateStatus() {
    if (!bar) return;
    if (!state.total) { bar.hidden = true; return; }
    bar.hidden = false;
    if (statusEl) statusEl.textContent = state.busy ? T('st_working') : T('st_done');
  }

  function addCard(file, skipThumb) {
    var wrap = document.createElement('article');
    wrap.className = 'qr-card';

    var media = document.createElement('div');
    media.className = 'qr-card-media';
    if (skipThumb) {
      media.hidden = true;          // 非图片文件不建缩略图，别留一个破图占位
      wrap.classList.add('is-nothumb');
    } else {
      var img = document.createElement('img');
      img.alt = '';
      try {
        var url = URL.createObjectURL(file);
        state.urls.push(url);
        img.src = url;
      } catch (e) { /* 极端环境下 createObjectURL 不可用，缩略图留空即可 */ }
      media.appendChild(img);
    }

    var body = document.createElement('div');
    body.className = 'qr-card-body';
    body.innerHTML = '<div class="qr-card-head"><span class="qr-kind is-wait">' +
      esc(T('st_working')) + '</span></div>';

    wrap.appendChild(media);
    wrap.appendChild(body);
    if (results) results.appendChild(wrap);
    return body;
  }

  function headHtml(labelKey, badgeClass) {
    return '<div class="qr-card-head"><span class="qr-kind ' + badgeClass + '">' +
      esc(T(labelKey)) + '</span></div>';
  }

  function fieldsHtml(fields) {
    if (!fields || !fields.length) return '';
    var rows = '';
    for (var i = 0; i < fields.length; i++) {
      var f = fields[i];
      var val = f.tl ? T(f.tl) : f.value;
      rows += '<div class="qr-field' + (f.secret ? ' is-secret' : '') + '">' +
        '<span class="qr-field-k">' + esc(T(f.key)) + '</span>' +
        '<span class="qr-field-v">' + esc(val) + '</span></div>';
    }
    return '<div class="qr-fields">' + rows + '</div>';
  }

  function warnHtml(risks) {
    var msgs = [];
    if (risks && risks.length) {
      if (risks.indexOf('http') >= 0) msgs.push(T('warn_http'));
      if (risks.indexOf('ip') >= 0) msgs.push(T('warn_ip'));
      if (risks.indexOf('userinfo') >= 0) msgs.push(T('warn_userinfo'));
      if (risks.indexOf('short') >= 0) msgs.push(T('warn_short'));
    }
    var out = '';
    if (msgs.length) {
      out += '<ul class="qr-warn">';
      for (var i = 0; i < msgs.length; i++) out += '<li>' + esc(msgs[i]) + '</li>';
      out += '</ul>';
    }
    // 链接类统一给一句"来源要自己确认"，与上面的具体信号分开，避免读成同一个警告
    if (msgs.length) out += '<p class="qr-warn-note">' + esc(T('warn_link')) + '</p>';
    return out;
  }

  function actionsHtml(res) {
    var out = '<div class="qr-card-actions">' +
      '<button type="button" class="btn btn-sm qr-copy">' + esc(T('act_copy')) + '</button>';
    if (res.link) {
      out += '<a class="btn btn-sm qr-open" target="_blank" rel="noopener noreferrer" href="' +
        esc(res.link) + '">' + esc(T('act_open')) + '</a>';
    }
    out += '</div>';
    return out;
  }

  function setOk(body, res) {
    var textHtml = res.kind === 'url' || res.kind === 'text'
      ? '<p class="qr-text">' + esc(res.text) + '</p>'
      : '';
    body.innerHTML = headHtml(res.labelKey, 'is-' + res.kind) +
      fieldsHtml(res.fields) + textHtml + warnHtml(res.risks) + actionsHtml(res);
    body.dataset.raw = res.raw;

    var copyBtn = body.querySelector('.qr-copy');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        var done = function () { copyBtn.textContent = T('copied'); };
        var fail = function () { copyBtn.textContent = T('copy_fail'); };
        var text = body.dataset.raw || '';
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () { legacyCopy(text) ? done() : fail(); });
        } else {
          legacyCopy(text) ? done() : fail();
        }
      });
    }
  }

  function legacyCopy(text) {
    try {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      var ok = document.execCommand('copy');
      document.body.removeChild(ta);
      return ok;
    } catch (e) { return false; }
  }

  function setFail(body, key) {
    body.innerHTML = headHtml('st_none', 'is-fail') +
      '<p class="qr-empty">' + esc(T(key)) + '</p>' +
      '<p class="qr-empty-why">' + esc(T('res_why')) + '</p>';
  }

  /** 逐档试解码，返回 jsQR 结果或 null。会阻塞主线程，调用前先让 UI 画一帧。 */
  function scanBitmap(bmp) {
    var attempts = qrScales(bmp.width, bmp.height);
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return null;
    var longest = Math.max(bmp.width, bmp.height);
    var seen = {};

    for (var i = 0; i < attempts.length; i++) {
      var a = attempts[i];
      var scale = a.maxSide / longest;
      if (scale > 3) scale = 3;           // 放大封顶 3 倍，再大只是浪费像素
      var w = Math.max(1, Math.round(bmp.width * scale));
      var h = Math.max(1, Math.round(bmp.height * scale));
      var pad = a.pad ? Math.max(8, Math.round(Math.max(w, h) * 0.08)) : 0;

      // 不同 maxSide 缩到同一尺寸时不必重复解码（小图放大后很常见）
      var sig = w + 'x' + h + (pad ? 'p' : '');
      if (seen[sig]) continue;
      seen[sig] = 1;

      canvas.width = w + pad * 2;
      canvas.height = h + pad * 2;
      // 补白边那档必须先铺白底，透明区域会被读成黑色，反而更难解
      if (pad) {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
      ctx.drawImage(bmp, pad, pad, w, h);

      var data;
      try { data = ctx.getImageData(0, 0, canvas.width, canvas.height); }
      catch (e) { return null; }

      var hit = null;
      if (typeof G.jsQR === 'function') {
        hit = G.jsQR(data.data, canvas.width, canvas.height, { inversionAttempts: 'attemptBoth' });
      }
      if (hit && hit.data) return hit;
    }
    return null;
  }

  async function decodeFile(file) {
    var isImg = !!file.type && file.type.indexOf('image/') === 0;
    var body = addCard(file, !isImg);
    // 非图片文件也进队列排队，卡片才会严格按选择顺序出现。
    // 若在 handleFiles 里立刻出卡片，坏文件会抢在所有图片前面，顺序和用户选的对不上。
    if (!isImg) { setFail(body, 'msg_badfile'); return; }
    if (typeof G.jsQR !== 'function') { setFail(body, 'lib_fail'); return; }

    var bmp = null;
    try {
      bmp = await createImageBitmap(file, { imageOrientation: 'from-image' });
    } catch (e) {
      try { bmp = await createImageBitmap(file); } catch (e2) { bmp = null; }
    }
    if (!bmp) { setFail(body, 'msg_readfail'); return; }

    // 先让"正在识别"这一帧真正画出来（rAF 等绘制，再让出主线程），
    // 否则大图一进来就进同步解码，用户看到的是空白卡片卡住不动。
    await new Promise(function (r) {
      if (typeof G.requestAnimationFrame === 'function') {
        G.requestAnimationFrame(function () { setTimeout(r, 0); });
      } else {
        setTimeout(r, 0);
      }
    });

    var hit = null;
    try { hit = scanBitmap(bmp); } catch (e) { hit = null; }
    if (bmp.close) bmp.close();

    if (hit && hit.data) setOk(body, qrClassify(hit.data));
    else setFail(body, 'res_none');
  }

  function pump() {
    if (state.busy) return;
    var file = state.queue.shift();
    if (!file) { updateStatus(); return; }
    state.busy = true;
    state.total++;
    updateStatus();
    decodeFile(file).then(function () {
      state.busy = false;
      state.done++;
      updateStatus();
      pump();
    }, function () {
      state.busy = false;
      state.done++;
      updateStatus();
      pump();
    });
  }

  function handleFiles(files) {
    if (!files || !files.length) return;
    for (var i = 0; i < files.length; i++) state.queue.push(files[i]);
    updateStatus();
    pump();
  }

  // ---- 交互：点击 / 拖拽 / 粘贴 / 键盘
  if (fileInput) {
    fileInput.addEventListener('change', function () {
      handleFiles(fileInput.files);
      fileInput.value = '';   // 允许重复选同一张
    });
  }

  var pickBtn = $('qrPick');
  if (pickBtn) {
    pickBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (fileInput) fileInput.click();
    });
  }

  drop.addEventListener('click', function () { if (fileInput) fileInput.click(); });
  drop.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
      e.preventDefault();
      if (fileInput) fileInput.click();
    }
  });

  ['dragenter', 'dragover'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) {
      e.preventDefault();
      drop.classList.add('is-over');
    });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) {
      e.preventDefault();
      drop.classList.remove('is-over');
    });
  });
  drop.addEventListener('drop', function (e) {
    var dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length) handleFiles(dt.files);
  });

  G.addEventListener('paste', function (e) {
    var items = (e.clipboardData && e.clipboardData.items) || [];
    var files = [];
    for (var i = 0; i < items.length; i++) {
      if (items[i].kind === 'file' && (items[i].type || '').indexOf('image/') === 0) {
        var f = items[i].getAsFile();
        if (f) files.push(f);
      }
    }
    if (files.length) {
      e.preventDefault();
      handleFiles(files);
    }
  });

  var clearBtn = $('qrClear');
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      for (var i = 0; i < state.urls.length; i++) {
        try { URL.revokeObjectURL(state.urls[i]); } catch (e) { /* 已释放 */ }
      }
      state.urls = [];
      state.queue = [];
      state.total = 0;
      state.done = 0;
      if (results) results.innerHTML = '';
      updateStatus();
    });
  }
}

// ---------------------------------------------------------------- 导出

G.qrParseWifi = qrParseWifi;
G.qrParseVcard = qrParseVcard;
G.qrParseMecard = qrParseMecard;
G.qrUrlRisks = qrUrlRisks;
G.qrScales = qrScales;
G.qrClassify = qrClassify;
G.initQrDecode = initQrDecode;

if (typeof G.addEventListener === 'function' && typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    G.addEventListener('DOMContentLoaded', initQrDecode);
  } else {
    initQrDecode();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    qrParseWifi: qrParseWifi,
    qrParseVcard: qrParseVcard,
    qrParseMecard: qrParseMecard,
    qrUrlRisks: qrUrlRisks,
    qrScales: qrScales,
    qrClassify: qrClassify
  };
}
