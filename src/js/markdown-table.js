// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// markdown-table.js — 表格文本 ↔ Markdown 表格
// 关键点：对齐填充必须按「显示宽度」算，中文/全角字符占两列，用 str.length 拼出来的表格在等宽字体下会错位。

// 单字符显示宽度：CJK、全角标点、假名、谚文算 2
function mdCharWidth(ch) {
  var c = ch.codePointAt(0);
  if (c < 32) return 0;
  if ((c >= 0x1100 && c <= 0x115F) || (c >= 0x2E80 && c <= 0x303E) ||
      (c >= 0x3041 && c <= 0x33FF) || (c >= 0x3400 && c <= 0x4DBF) ||
      (c >= 0x4E00 && c <= 0x9FFF) || (c >= 0xA000 && c <= 0xA4CF) ||
      (c >= 0xAC00 && c <= 0xD7A3) || (c >= 0xF900 && c <= 0xFAFF) ||
      (c >= 0xFE30 && c <= 0xFE6F) || (c >= 0xFF00 && c <= 0xFF60) ||
      (c >= 0xFFE0 && c <= 0xFFE6) || (c >= 0x1F300 && c <= 0x1F64F) ||
      (c >= 0x1F900 && c <= 0x1F9FF) || (c >= 0x20000 && c <= 0x3FFFD)) {
    return 2;
  }
  return 1;
}

function mdTextWidth(s) {
  var w = 0;
  var arr = Array.from(String(s == null ? '' : s));
  for (var i = 0; i < arr.length; i++) w += mdCharWidth(arr[i]);
  return w;
}

// 自动判断分隔符：制表符优先（从 Excel/Sheets 复制过来的就是它），其次逗号、分号、竖线
function mdDetectDelimiter(text) {
  var sample = String(text || '').split('\n').slice(0, 5).join('\n');
  if (sample.indexOf('\t') >= 0) return '\t';
  if (sample.split(',').length > sample.split('\n').length) return ',';
  if (sample.split(';').length > sample.split('\n').length) return ';';
  if (sample.split('|').length > sample.split('\n').length) return '|';
  return '\t';
}

// 解析分隔文本。带引号的字段可以包含分隔符，"" 表示一个双引号（CSV 惯例）。
function mdParseDelimited(text, delim) {
  delim = delim || '\t';
  var rows = [], row = [], cell = '', i = 0;
  var s = String(text == null ? '' : text);
  var inQuote = false;
  while (i < s.length) {
    var ch = s.charAt(i);
    if (inQuote) {
      if (ch === '"') {
        if (s.charAt(i + 1) === '"') { cell += '"'; i += 2; continue; }
        inQuote = false; i++; continue;
      }
      cell += ch; i++; continue;
    }
    if (ch === '"' && cell === '') { inQuote = true; i++; continue; }
    if (ch === delim) { row.push(cell); cell = ''; i++; continue; }
    if (ch === '\r') { i++; continue; }
    if (ch === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; i++; continue; }
    cell += ch; i++;
  }
  if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
  // 丢掉完全空白的尾部行与尾部空列，避免从 Excel 复制时多带的制表符
  while (rows.length && rows[rows.length - 1].every(function (c) { return String(c).trim() === ''; })) rows.pop();
  return rows;
}

// 判断一列是否「全数字」——用于自动右对齐
function mdColumnIsNumeric(rows, col) {
  var seen = 0;
  for (var i = 1; i < rows.length; i++) {      // 跳过表头
    var v = String(rows[i][col] == null ? '' : rows[i][col]).trim();
    if (v === '') continue;
    seen++;
    if (!/^[-+]?[\d,]*\.?\d+(%|‰)?$/.test(v)) return false;
  }
  return seen > 0;
}

// 生成 Markdown 表格。opts: {aligns: ['l'|'c'|'r'|''], autoNumeric: bool}
function mdBuildTable(rows, opts) {
  opts = opts || {};
  if (!rows || !rows.length) return '';
  var ncol = 0;
  for (var i = 0; i < rows.length; i++) ncol = Math.max(ncol, rows[i].length);
  if (!ncol) return '';

  // 补齐成矩形，顺便把单元格里的换行/竖线转义掉（否则会破坏表格结构）
  var grid = rows.map(function (r) {
    var out = [];
    for (var c = 0; c < ncol; c++) {
      out.push(String(r[c] == null ? '' : r[c]).replace(/\r?\n/g, ' ').replace(/\|/g, '\\|').trim());
    }
    return out;
  });

  var aligns = [];
  for (var c2 = 0; c2 < ncol; c2++) {
    var a = (opts.aligns && opts.aligns[c2]) || '';
    if (!a && opts.autoNumeric && mdColumnIsNumeric(grid, c2)) a = 'r';
    aligns.push(a);
  }

  var widths = [];
  for (var c3 = 0; c3 < ncol; c3++) {
    var w = 3;                                  // 分隔行至少 ---
    for (var r2 = 0; r2 < grid.length; r2++) w = Math.max(w, mdTextWidth(grid[r2][c3]));
    widths.push(w);
  }

  function pad(str, w, align) {
    var fill = w - mdTextWidth(str);
    if (fill <= 0) return str;
    if (align === 'r') return new Array(fill + 1).join(' ') + str;
    if (align === 'c') {
      var l = Math.floor(fill / 2);
      return new Array(l + 1).join(' ') + str + new Array(fill - l + 1).join(' ');
    }
    return str + new Array(fill + 1).join(' ');
  }

  var lines = [];
  lines.push('| ' + grid[0].map(function (c, idx) { return pad(c, widths[idx], aligns[idx]); }).join(' | ') + ' |');
  lines.push('| ' + widths.map(function (w2, idx) {
    var a = aligns[idx];
    if (a === 'r') return new Array(w2 - 1).join('-') + ':';
    if (a === 'c') return ':' + new Array(w2 - 2).join('-') + ':';
    if (a === 'l') return ':' + new Array(w2).join('-');
    return new Array(w2 + 1).join('-');
  }).join(' | ') + ' |');
  for (var r3 = 1; r3 < grid.length; r3++) {
    lines.push('| ' + grid[r3].map(function (c, idx) { return pad(c, widths[idx], aligns[idx]); }).join(' | ') + ' |');
  }
  return lines.join('\n');
}

// 解析已有的 Markdown 表格（用于反向导出 CSV）
function mdParseTable(md) {
  var lines = String(md || '').split('\n');
  var rows = [];
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (!line || line.indexOf('|') < 0) continue;
    if (/^\|?[\s:|-]+\|?$/.test(line)) continue;       // 分隔行
    // 手写扫描而不是 split(/(?<!\\|)/)：后行断言在 Safari 16.4 之前会直接抛语法错误
    var body = line.replace(/^\s*\|/, '').replace(/\|\s*$/, '');
    var cells = [], cur = '', esc = false;
    for (var k = 0; k < body.length; k++) {
      var ch = body.charAt(k);
      if (esc) { cur += ch; esc = false; continue; }
      if (ch === '\\') { esc = true; cur += ch; continue; }
      if (ch === '|') { cells.push(cur); cur = ''; continue; }
      cur += ch;
    }
    cells.push(cur);
    cells = cells.map(function (c) { return c.trim().replace(/\\\|/g, '|'); });
    rows.push(cells);
  }
  return rows;
}

// 导出为分隔文本，含分隔符/引号/换行的字段加引号
function mdToDelimited(rows, delim) {
  delim = delim || '\t';
  return rows.map(function (r) {
    return r.map(function (c) {
      var v = String(c == null ? '' : c);
      if (v.indexOf(delim) >= 0 || v.indexOf('"') >= 0 || v.indexOf('\n') >= 0) {
        return '"' + v.replace(/"/g, '""') + '"';
      }
      return v;
    }).join(delim);
  }).join('\n');
}

// ---------------------------------------------------------------- 页面
function mdTL() { return G.__TL__ || {}; }
// 演示表格随页面语言切换（中文表头只出现在中文页），避免中文字面量进英文页。
function mdSampleText() {
  var tl = mdTL();
  return tl.sample_text || 'tool\trole\tstatus\nregex\tregex tester\tonline';
}
var mdMode = 'toMd';        // toMd | toText
var mdAlign = '';
var mdDelim = '';           // 空 = 自动

function mdRender() {
  var L = mdTL();
  var out = document.getElementById('mdOut');
  if (!out) return;
  var raw = getVal('mdInput');
  if (!raw.trim()) {
    out.value = '';
    mdStat(L.hint || '');
    return;
  }
  if (mdMode === 'toMd') {
    var d = mdDelim || mdDetectDelimiter(raw);
    var rows = mdParseDelimited(raw, d);
    out.value = mdBuildTable(rows, { aligns: mdAlign ? fillAlign(rows, mdAlign) : null, autoNumeric: !mdAlign });
    mdStat((L.stat_rows || '').replace('{r}', String(rows.length))
      .replace('{c}', String(rows.length ? rows[0].length : 0))
      .replace('{d}', d === '\t' ? 'TAB' : d));
  } else {
    var t = mdParseTable(raw);
    out.value = mdToDelimited(t, '\t');
    mdStat((L.stat_rows || '').replace('{r}', String(t.length))
      .replace('{c}', String(t.length ? t[0].length : 0))
      .replace('{d}', 'TAB'));
  }
}

function fillAlign(rows, a) {
  var n = 0;
  for (var i = 0; i < rows.length; i++) n = Math.max(n, rows[i].length);
  var arr = [];
  for (var j = 0; j < n; j++) arr.push(a);
  return arr;
}

function mdStat(text) {
  var el = document.getElementById('mdStat');
  if (!el) return;
  el.style.display = 'flex';
  el.textContent = text;
}

G.mdRender = mdRender;
G.mdClear = function () { setVal('mdInput', ''); mdRender(); };
G.mdSample = function () {
  mdMode = 'toMd';
  setVal('mdInput', mdSampleText());
  mdRender();
};
G.mdCopyOut = function () {
  var out = document.getElementById('mdOut');
  if (!out || !out.value) return;
  if (navigator.clipboard) navigator.clipboard.writeText(out.value).then(function () {
    toast((mdTL().copied || 'OK'));
  }, function () {
    toast((mdTL().copy_fail || 'Copy failed'), 'error');
  });
};

function initMd() {
  var input = document.getElementById('mdInput');
  if (!input) return;
  if (!input.value) {
    input.value = mdSampleText();
  }
  mdRender();
  input.addEventListener('input', mdRender);

  var modeBox = document.getElementById('mdMode');
  if (modeBox) {
    modeBox.addEventListener('click', function (e) {
      var b = e.target.closest('[data-mode]');
      if (!b) return;
      mdMode = b.getAttribute('data-mode');
      Array.prototype.forEach.call(modeBox.querySelectorAll('[data-mode]'), function (x) {
        x.classList.toggle('active', x === b);
      });
      mdRender();
    });
  }
  var alBox = document.getElementById('mdAlign');
  if (alBox) {
    alBox.addEventListener('click', function (e) {
      var b = e.target.closest('[data-align]');
      if (!b) return;
      mdAlign = b.getAttribute('data-align');
      Array.prototype.forEach.call(alBox.querySelectorAll('[data-align]'), function (x) {
        x.classList.toggle('active', x === b);
      });
      mdRender();
    });
  }
  var dBox = document.getElementById('mdDelim');
  if (dBox) {
    dBox.addEventListener('click', function (e) {
      var b = e.target.closest('[data-delim]');
      if (!b) return;
      mdDelim = b.getAttribute('data-delim');
      Array.prototype.forEach.call(dBox.querySelectorAll('[data-delim]'), function (x) {
        x.classList.toggle('active', x === b);
      });
      mdRender();
    });
  }
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMd);
  } else {
    initMd();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { mdCharWidth: mdCharWidth, mdTextWidth: mdTextWidth,
                     mdDetectDelimiter: mdDetectDelimiter, mdParseDelimited: mdParseDelimited,
                     mdBuildTable: mdBuildTable, mdParseTable: mdParseTable,
                     mdToDelimited: mdToDelimited, mdColumnIsNumeric: mdColumnIsNumeric };
}
