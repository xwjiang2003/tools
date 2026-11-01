// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// number-to-chinese.js — 数字转中文读法 / 人民币大写
// 规则说明（中文数字的关键坑都在这里）：
//   · 连续的零只读一个「零」，且整段末尾不读零（1001 一千零一，1100 一千一百）
//   · 开头的「一十」读作「十」（12 十二，不读一十二；10 万同理读十万）
//   · 万 / 亿 / 万亿 是分段单位，逐位套单位后自然拼接，不需要额外分组逻辑
//   · 人民币大写只取到分，第三位小数起直接截断（不四舍五入），与财务系统口径一致

var NUM_CN = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
var NUM_RMB = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖'];
// 位级单位只到「千」：中文是四位一组进位（万 / 亿），
// 早期版本用一张 13 项的扁平单位表，会把 9999 亿读成「九千亿九百亿九十亿九亿」，
// 正确读法是「九千九百九十九亿」。分组处理才是对的。
var NUM_UNIT = ['', '十', '百', '千'];
var NUM_RMB_UNIT = ['', '拾', '佰', '仟'];

// 清洗输入：去空白、千分位逗号、全角数字与全角句点
function numNormalize(input) {
  return String(input == null ? '' : input).trim()
    .replace(/[\s,，_]/g, '')
    .replace(/[０-９]/g, function (c) { return String.fromCharCode(c.charCodeAt(0) - 0xFEE0); })
    .replace(/[。．]/g, '.');
}

// 四位以内（0–9999）读法
function numSec4(n, digits, u4) {
  var str = String(n), out = '', zero = false;
  for (var i = 0; i < str.length; i++) {
    var d = +str[i];
    if (d === 0) { if (out) zero = true; continue; }   // 连续零只补一个
    if (zero) { out += digits[0]; zero = false; }
    out += digits[d] + u4[str.length - 1 - i];
  }
  return out;
}

// 一亿以内：高位「万」组 + 低位组；低位不足千位时补零（100000001 一亿零一）
function numBelowYi(n, digits, u4) {
  var hi = Math.floor(n / 10000), lo = n % 10000;
  if (!hi) return numSec4(lo, digits, u4);
  var out = numSec4(hi, digits, u4) + '万';
  if (lo > 0) out += (lo < 1000 ? digits[0] : '') + numSec4(lo, digits, u4);
  return out;
}

// 整数串 → 中文读法（digits/u4 可切换成大写字符集）
function numIntToCn(str, digits, u4) {
  digits = digits || NUM_CN;
  u4 = u4 || NUM_UNIT;
  str = String(str).replace(/^0+(?=\d)/, '');
  if (str === '0') return digits[0];
  if (str.length > 13) return null;              // 万亿级上限，再大没有通用读法
  var n = Number(str);
  if (!isFinite(n)) return null;
  var out;
  if (n >= 1e8) {
    var yi = Math.floor(n / 1e8), rest = n % 1e8;
    // 亿位本身最大 99999（九万九千九百九十九亿），仍用「万」组读法
    out = numBelowYi(yi, digits, u4) + '亿';
    if (rest > 0) out += (rest < 1e7 ? digits[0] : '') + numBelowYi(rest, digits, u4);
  } else {
    out = numBelowYi(n, digits, u4);
  }
  if (out.indexOf(digits[1] + u4[1]) === 0) out = out.slice(1);   // 一十二 → 十二
  return out;
}

// 拆符号与整数/小数部分
function numSplit(input) {
  var s = numNormalize(input);
  var neg = false;
  if (s.charAt(0) === '-') { neg = true; s = s.slice(1); }
  else if (s.charAt(0) === '+') { s = s.slice(1); }
  if (!/^\d*(\.\d*)?$/.test(s) || s === '' || s === '.') return null;
  var dot = s.indexOf('.');
  var intPart = dot < 0 ? s : s.slice(0, dot);
  var decPart = dot < 0 ? '' : s.slice(dot + 1);
  intPart = intPart.replace(/^0+(?=\d)/, '');
  if (intPart === '') intPart = '0';
  return { neg: neg, int: intPart, dec: decPart };
}

// 中文读法：整数部分按位读，小数部分逐位读（3.14 → 三点一四）
function numToCn(input) {
  var p = numSplit(input);
  if (!p) return { valid: false, reason: 'number' };
  var head = numIntToCn(p.int);
  if (head === null) return { valid: false, reason: 'range' };
  var out = (p.neg ? '负' : '') + head;
  if (p.dec) {
    var ds = '';
    for (var i = 0; i < p.dec.length; i++) ds += NUM_CN[+p.dec[i]];
    out += '点' + ds;
  }
  return { valid: true, text: out };
}

// 人民币大写：只到分，第三位小数起截断
function numToRmb(input) {
  var p = numSplit(input);
  if (!p) return { valid: false, reason: 'number' };
  if (p.int.replace(/^0+/, '').length > 13) return { valid: false, reason: 'range' };

  var dec = (p.dec + '00').slice(0, 2);
  var jiao = +dec[0], fen = +dec[1];
  var isZeroInt = /^0+$/.test(p.int);

  var out = '';
  if (!isZeroInt) {
    var head = numIntToCn(p.int, NUM_RMB, NUM_RMB_UNIT);
    if (head === null) return { valid: false, reason: 'range' };
    out = head + '元';
  }

  // 整数部分为 0 时也写「零元」：财务凭据上 0.05 必须写成 零元零伍分，
  // 只写「伍分」在正式场景会被退单。
  if (isZeroInt) out = '零元';

  if (jiao === 0 && fen === 0) {
    out += '整';
  } else if (jiao === 0) {
    out += '零' + NUM_RMB[fen] + '分';
  } else {
    out += NUM_RMB[jiao] + '角';
    out += fen === 0 ? '整' : NUM_RMB[fen] + '分';
  }
  return { valid: true, text: (p.neg ? '负' : '') + out };
}

// 千分位分组，便于人工核对位数
function numGroup(input) {
  var p = numSplit(input);
  if (!p) return null;
  var intPart = p.int.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return (p.neg ? '-' : '') + intPart + (p.dec ? '.' + p.dec : '');
}

// ---------------------------------------------------------------- 页面
function numTL() { return G.__TL__ || {}; }

function numRender() {
  var L = numTL();
  var box = document.getElementById('numResult');
  if (!box) return;
  var raw = getVal('numInput');
  var lines = String(raw).split('\n');
  var rows = [], bad = 0;
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (!line) continue;
    var rmb = numToRmb(line), cn = numToCn(line), grp = numGroup(line);
    if (!rmb.valid) {
      bad++;
      var msg = L['err_' + rmb.reason] || L.err_generic || '';
      rows.push([escHtml(line), '<span style="color:var(--danger)">' + escHtml(msg) + '</span>', '']);
    } else {
      rows.push([escHtml(grp || line), escHtml(rmb.text), escHtml(cn.valid ? cn.text : '')]);
    }
  }
  if (!rows.length) {
    box.innerHTML = '<div class="tl-hint">' + escHtml(L.hint || '') + '</div>';
    return;
  }
  var html = '<table class="dt-table"><thead><tr><th>' + escHtml(L.c_num) + '</th><th>' +
    escHtml(L.c_rmb) + '</th><th>' + escHtml(L.c_cn) + '</th></tr></thead><tbody>';
  for (var j = 0; j < rows.length; j++) {
    html += '<tr><td>' + rows[j][0] + '</td><td class="tl-wrap"><b>' + rows[j][1] +
      '</b></td><td class="tl-wrap">' + rows[j][2] + '</td></tr>';
  }
  html += '</tbody></table>';
  box.innerHTML = html;

  var stat = document.getElementById('numStat');
  if (stat) {
    stat.style.display = 'flex';
    stat.textContent = (L.stat || '').replace('{n}', String(rows.length))
      .replace('{e}', String(bad));
  }
}

G.numRender = numRender;
G.numClear = function () { setVal('numInput', ''); numRender(); };
G.numSample = function () {
  setVal('numInput', '1234.56\n10086\n100000000\n0.05\n-210.5\n10001');
  numRender();
};

function initNum() {
  var input = document.getElementById('numInput');
  if (!input) return;
  if (!input.value) input.value = '1234.56\n10086\n100000000\n0.05\n-210.5';
  numRender();
  input.addEventListener('input', numRender);
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNum);
  } else {
    initNum();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { numNormalize: numNormalize, numIntToCn: numIntToCn, numSplit: numSplit,
                     numToCn: numToCn, numToRmb: numToRmb, numGroup: numGroup };
}
