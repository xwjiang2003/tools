// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// cidr.js — IPv4 子网 / CIDR 计算（网络地址、广播地址、掩码、可用主机、整数与二进制表示）
// 纯函数 + 页面渲染；浏览器与 Node 单测共用。
// 全部使用 »0 无符号运算，避免 32 位符号位把 192.0.0.0/8 这类大网段算成负数。

// ---------------------------------------------------------------- 基础换算
// 点分十进制 → 无符号 32 位整数；非法返回 null（不抛异常，调用方判断即可）
function cidrIpToInt(s) {
  var m = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/.exec(String(s == null ? '' : s).trim());
  if (!m) return null;
  var n = 0;
  for (var i = 1; i <= 4; i++) {
    var o = +m[i];
    if (o > 255) return null;
    n = n * 256 + o;
  }
  return n >>> 0;
}

function cidrIntToIp(n) {
  n = n >>> 0;
  return ((n >>> 24) & 255) + '.' + ((n >>> 16) & 255) + '.' + ((n >>> 8) & 255) + '.' + (n & 255);
}

// 前缀长度 → 点分掩码
function cidrPrefixToMask(prefix) {
  if (prefix <= 0) return 0;
  if (prefix >= 32) return 0xFFFFFFFF;
  return (0xFFFFFFFF << (32 - prefix)) >>> 0;
}

// 点分掩码 → 前缀长度；不是连续 1 的掩码返回 -1
function cidrMaskToPrefix(mask) {
  mask = mask >>> 0;
  var prefix = 0;
  for (var i = 31; i >= 0; i--) {
    var bit = (mask >>> i) & 1;
    if (bit === 1) {
      if (prefix !== 31 - i) return -1;      // 出现 0 之后又有 1：非连续掩码
      prefix++;
    }
  }
  return prefix;
}

// 8 位一组的二进制串，便于核对主机位
function cidrToBinary(n) {
  n = n >>> 0;
  var out = [];
  for (var i = 3; i >= 0; i--) {
    var b = (n >>> (i * 8)) & 255;
    out.push(('0000000' + b.toString(2)).slice(-8));
  }
  return out.join('.');
}

// 地址类型判定：返回分类键，文案由页面从标签表取
function cidrIpType(n) {
  if (typeof n === 'string') n = cidrIpToInt(n);      // 允许传点分字符串，省得调用方先转
  if (n == null) return '';
  n = n >>> 0;
  var a = (n >>> 24) & 255, b = (n >>> 16) & 255;
  if (n === 4294967295) return 'broadcast';           // 255.255.255.255 是受限广播，
  if (a === 10) return 'private';                     // 必须排在 240+/reserved 之前
  if (a === 172 && b >= 16 && b <= 31) return 'private';
  if (a === 192 && b === 168) return 'private';
  if (a === 127) return 'loopback';
  if (a === 169 && b === 254) return 'linklocal';
  if (a === 100 && b >= 64 && b <= 127) return 'cgnat';
  if (a === 0) return 'thisnet';
  if (a >= 224 && a <= 239) return 'multicast';
  if (a >= 240) return 'reserved';
  if (a === 198 && (b === 18 || b === 19)) return 'benchmark';
  return 'public';
}

// 传统 A/B/C/D/E 分类（教材口径，与上面的「是否私有」互补）
function cidrIpClass(n) {
  if (typeof n === 'string') n = cidrIpToInt(n);
  if (n == null) return '';
  var a = (n >>> 24) & 255;
  if (a < 128) return 'A';
  if (a < 192) return 'B';
  if (a < 224) return 'C';
  if (a < 240) return 'D';
  return 'E';
}

// ---------------------------------------------------------------- 主计算
// 接受 "192.168.1.10/24"、"192.168.1.10/255.255.255.0"、"192.168.1.10"（按 /32）
function cidrInfo(input) {
  var s = String(input == null ? '' : input).trim();
  if (!s) return { valid: false, reason: 'empty' };
  s = s.replace(/\s+/g, '');
  var slash = s.indexOf('/');
  var ipStr = slash < 0 ? s : s.slice(0, slash);
  var ip = cidrIpToInt(ipStr);
  if (ip === null) return { valid: false, reason: 'ip' };

  var prefix = 32;
  if (slash >= 0) {
    var tail = s.slice(slash + 1);
    if (/^\d{1,2}$/.test(tail)) {
      prefix = +tail;
    } else {
      var m = cidrIpToInt(tail);
      if (m === null) return { valid: false, reason: 'prefix' };
      prefix = cidrMaskToPrefix(m);
      if (prefix < 0) return { valid: false, reason: 'mask' };
    }
  }
  if (prefix < 0 || prefix > 32) return { valid: false, reason: 'prefix' };

  var mask = cidrPrefixToMask(prefix);
  var wildcard = (~mask) >>> 0;
  var network = (ip & mask) >>> 0;
  var broadcast = (network | wildcard) >>> 0;
  var total = Math.pow(2, 32 - prefix);

  var usable, first, last;
  if (prefix === 32) { usable = 1; first = network; last = network; }
  else if (prefix === 31) { usable = 2; first = network; last = broadcast; }  // RFC 3021 点对点链路
  else { usable = total - 2; first = (network + 1) >>> 0; last = (broadcast - 1) >>> 0; }

  return {
    valid: true,
    input: s,
    ip: ip,
    ipText: cidrIntToIp(ip),
    prefix: prefix,
    mask: cidrIntToIp(mask),
    wildcard: cidrIntToIp(wildcard),
    network: cidrIntToIp(network),
    broadcast: cidrIntToIp(broadcast),
    cidr: cidrIntToIp(network) + '/' + prefix,
    first: cidrIntToIp(first),
    last: cidrIntToIp(last),
    usable: usable,
    total: total,
    type: cidrIpType(ip),
    netType: cidrIpType(ip),     // 网段类型与地址类型同源，保留字段方便日后区分
    ipClass: cidrIpClass(ip),
    ipInt: ip,
    ipHex: '0x' + ('00000000' + ip.toString(16)).slice(-8).toUpperCase(),
    ipBin: cidrToBinary(ip),
    maskBin: cidrToBinary(mask),
    // 主机位：用于解释「为什么 /24 只有 254 个可用」
    hostBits: 32 - prefix
  };
}

// 掩码速查表：/8 起每档一行（/1–/7 极少用，但保留 /1 方便教学）
function cidrMaskTable() {
  var rows = [];
  for (var p = 1; p <= 32; p++) {
    var mask = cidrPrefixToMask(p);
    var total = Math.pow(2, 32 - p);
    var usable = p >= 31 ? total : total - 2;
    rows.push({
      prefix: p,
      mask: cidrIntToIp(mask),
      wildcard: cidrIntToIp((~mask) >>> 0),
      total: total,
      usable: usable
    });
  }
  return rows;
}

// ---------------------------------------------------------------- 页面
function initCidr() {
  var input = document.getElementById('cidrInput');
  if (!input) return;
  cidrRenderMasks();          // 掩码速查与输入无关，先渲染一次
  cidrRender();
  input.addEventListener('input', cidrRender);
}

function cidrLabels() { return G.__TL__ || {}; }

function cidrRender() {
  var L = cidrLabels();
  var box = document.getElementById('cidrResult');
  var stat = document.getElementById('cidrStat');
  if (!box) return;
  var raw = document.getElementById('cidrInput').value;
  var r = cidrInfo(raw);
  if (!raw.trim()) {
    box.innerHTML = '<div class="cidr-hint">' + escHtml(L.hint || '') + '</div>';
    if (stat) stat.style.display = 'none';
    return;
  }
  if (!r.valid) {
    var msg = L['err_' + r.reason] || L.err_generic || '';
    box.innerHTML = '<div class="cidr-err">' + escHtml(msg) + '</div>';
    if (stat) stat.style.display = 'none';
    return;
  }

  var rows = [
    [L.r_cidr, r.cidr, true],
    [L.r_network, r.network, true],
    [L.r_broadcast, r.broadcast, true],
    [L.r_range, r.first + ' – ' + r.last, true],
    [L.r_usable, String(r.usable), false],
    [L.r_total, String(r.total), false],
    [L.r_mask, r.mask, true],
    [L.r_wildcard, r.wildcard, true],
    [L.r_prefix, '/' + r.prefix + ' (' + r.hostBits + ' ' + (L.r_hostbits || '') + ')', false],
    [L.r_type, L['type_' + r.type] || r.type, false],
    [L.r_class, L.r_class_val.replace('{c}', r.ipClass), false],
    [L.r_ipint, String(r.ipInt), true],
    [L.r_iphex, r.ipHex, true],
    [L.r_ipbin, r.ipBin, true],
    [L.r_maskbin, r.maskBin, true]
  ];
  var html = '<table class="dt-table"><tbody>';
  for (var i = 0; i < rows.length; i++) {
    html += '<tr><th style="width:38%">' + escHtml(rows[i][0]) + '</th><td>' +
      escHtml(rows[i][1]) + '</td></tr>';
  }
  html += '</tbody></table>';
  box.innerHTML = html;
  if (stat) {
    stat.style.display = 'flex';
    stat.textContent = (L.stat || '').replace('{n}', String(r.usable)).replace('{c}', r.cidr);
  }
  cidrRenderMasks();
}

function cidrRenderMasks() {
  var box = document.getElementById('cidrMaskTable');
  if (!box) return;
  var L = cidrLabels();
  var rows = cidrMaskTable();
  var html = '<table class="dt-table"><thead><tr><th>' + escHtml(L.m_prefix || '') +
    '</th><th>' + escHtml(L.m_mask || '') + '</th><th>' + escHtml(L.m_wildcard || '') +
    '</th><th>' + escHtml(L.m_total || '') + '</th><th>' + escHtml(L.m_usable || '') +
    '</th></tr></thead><tbody>';
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];
    html += '<tr><td>/' + r.prefix + '</td><td>' + r.mask + '</td><td>' + r.wildcard +
      '</td><td>' + r.total + '</td><td>' + r.usable + '</td></tr>';
  }
  html += '</tbody></table>';
  box.innerHTML = html;
}

G.cidrRender = cidrRender;
G.cidrClear = function () { setVal('cidrInput', ''); cidrRender(); };
G.cidrSample = function () { setVal('cidrInput', '192.168.1.130/26'); cidrRender(); };

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCidr);
  } else {
    initCidr();
  }
}

// Node 单测导出（浏览器中 module 为 undefined，自动跳过）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    cidrIpToInt: cidrIpToInt, cidrIntToIp: cidrIntToIp,
    cidrPrefixToMask: cidrPrefixToMask, cidrMaskToPrefix: cidrMaskToPrefix,
    cidrToBinary: cidrToBinary, cidrIpType: cidrIpType, cidrIpClass: cidrIpClass,
    cidrInfo: cidrInfo, cidrMaskTable: cidrMaskTable,
  };
}
