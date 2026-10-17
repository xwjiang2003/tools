// datetime-tools.js — 时间 / 日期工具共享库
// ============================================================
// 本文件被内联进每个页面（与 timestamp.js 同机制）。
// ① 全部「纯逻辑」函数（解析 / 计算 / 格式化）集中在此，便于 Node 单测；
// ② 每个新工具页的 DOM 初始化函数 initXxxPage() 也在此定义，由 core.js 按 data-page 分派；
// ③ 注释用 // 写法，构建的 localize() 会跳过（不进英文替换），因此注释可写中文；
//    但「用户可见的字符串字面量」必须进 i18n.EN 字典，否则英文页会残留中文。
// ============================================================

// ---------- 公共：当前秒级时间戳 ----------
function dtNowSeconds() { return Math.floor(Date.now() / 1000); }

// ---------- 时间戳解析：秒/毫秒自动识别 ----------
// 返回 { ok, value(秒), error }
function dtParseTimestamp(input) {
  if (input === null || input === undefined) return { ok: false, error: 'empty' };
  var s = String(input).trim();
  if (!s) return { ok: false, error: 'empty' };
  if (!/^-?\d+$/.test(s)) return { ok: false, error: 'not_int' };
  var n = Number(s);
  if (!isFinite(n)) return { ok: false, error: 'not_int' };
  // >= 1e11 一律按毫秒（1e11 秒已是公元 5138 年，现实中不会这么输入）
  if (Math.abs(n) >= 1e11) n = Math.floor(n / 1000);
  return { ok: true, value: n };
}

// ---------- 时间戳 -> 指定时区的年月日时分秒（UTC 基准 + Intl 转时区） ----------
// tz 为 IANA 名称（'Asia/Shanghai'）或 'UTC' 或 'local'
function dtZonedParts(tsSec, tz) {
  var d = new Date(tsSec * 1000);
  if (isNaN(d.getTime())) return null;
  var resolved = (tz === 'local') ? undefined : tz; // undefined -> 运行时本地时区
  var fmt;
  try {
    fmt = new Intl.DateTimeFormat('en-US', {
      timeZone: resolved, year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit', weekday: 'short', hour12: false
    });
  } catch (e) { return null; }
  var parts = {};
  fmt.formatToParts(d).forEach(function (p) { parts[p.type] = p.value; });
  // hour12:false 在部分实现里午夜返回 '24'，规整为 '00'
  if (parts.hour === '24') parts.hour = '00';
  return parts; // {year,month,day,hour,minute,second,weekday}
}

// ---------- 日期各字段 -> 秒级时间戳（按指定时区解释） ----------
// y/m/d/h/min/sec 为数字；tz 为 IANA 或 'UTC'
function dtPartsToSeconds(y, m, d, h, min, sec, tz) {
  var ms;
  if (tz === 'UTC') {
    ms = Date.UTC(y, m - 1, d, h || 0, min || 0, sec || 0);
  } else if (!tz || tz === 'local') {
    ms = new Date(y, m - 1, d, h || 0, min || 0, sec || 0).getTime();
  } else {
    // 先按 UTC 算出该墙钟时间，再扣掉该时区相对 UTC 的偏移
    var asUtc = Date.UTC(y, m - 1, d, h || 0, min || 0, sec || 0);
    var off = dtTimezoneOffsetSeconds(tz, new Date(asUtc));
    ms = asUtc - off * 1000;
  }
  if (isNaN(ms)) return null;
  return Math.floor(ms / 1000);
}

// ---------- 时区相对 UTC 的偏移（秒），按 date 时刻的夏令时计算 ----------
function dtTimezoneOffsetSeconds(tz, date) {
  try {
    var dt = date || new Date();
    var dtf = new Intl.DateTimeFormat('en-US', { timeZone: tz, hour12: false,
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit' });
    var parts = {};
    dtf.formatToParts(dt).forEach(function (p) { parts[p.type] = p.value; });
    if (parts.hour === '24') parts.hour = '00';
    var asIfUtc = Date.UTC(+parts.year, +parts.month - 1, +parts.day,
      +parts.hour, +parts.minute, +parts.second);
    return Math.round((asIfUtc - dt.getTime()) / 1000);
  } catch (e) { return 0; }
}

// ---------- 时区偏移标签（如 "GMT+8"） ----------
function dtTzOffsetLabel(tz, date) {
  var dt = date || new Date();
  try {
    var dtf = new Intl.DateTimeFormat('en-US', { timeZone: tz, timeZoneName: 'shortOffset' });
    var parts = dtf.formatToParts(dt);
    for (var i = 0; i < parts.length; i++) {
      if (parts[i].type === 'timeZoneName') return parts[i].value.replace('GMT', 'UTC');
    }
  } catch (e) {}
  return '';
}

// ---------- ISO 8601 周数 + 周年（周四规则） ----------
function dtIsoWeek(date) {
  var d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  var dayNum = (d.getUTCDay() + 6) % 7;            // 周一=0
  d.setUTCDate(d.getUTCDate() - dayNum + 3);        // 最近的周四
  var firstThursday = new Date(Date.UTC(d.getUTCFullYear(), 0, 4));
  var week = 1 + Math.round(((d - firstThursday) / 86400000 - 3 +
    ((firstThursday.getUTCDay() + 6) % 7)) / 7);
  return { week: week, year: d.getUTCFullYear() };
}

// ---------- 年内第几天（1-366） ----------
function dtDayOfYear(date) {
  var start = Date.UTC(date.getUTCFullYear(), 0, 0);
  return Math.floor((date.getTime() - start) / 86400000);
}

// ---------- 闰年判断 ----------
function dtIsLeapYear(y) { return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0; }

// ---------- ISO 8601 时长 <-> 秒 ----------
// 解析 "PnYnMnDTnHnMnS" / "PnW"；年=365天、月=30天（近似，用于无参考日的时长换算）
function dtParseIsoDuration(str) {
  var s = String(str || '').trim();
  if (!s) return { ok: false, error: 'empty' };
  var m = /^P(?:(\d+(?:\.\d+)?)Y)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)W)?(?:(\d+(?:\.\d+)?)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$/.exec(s);
  if (!m) return { ok: false, error: 'bad_format' };
  var y = +m[1] || 0, mo = +m[2] || 0, w = +m[3] || 0, d = +m[4] || 0,
      h = +m[5] || 0, mi = +m[6] || 0, se = +m[7] || 0;
  var sec = se + mi * 60 + h * 3600 + d * 86400 + w * 7 * 86400 + mo * 30 * 86400 + y * 365 * 86400;
  return { ok: true, seconds: Math.round(sec) };
}
function dtSecondsToIsoDuration(totalSec) {
  var s = Math.abs(Math.round(totalSec));
  var y = Math.floor(s / (365 * 86400)); s -= y * 365 * 86400;
  var mo = Math.floor(s / (30 * 86400)); s -= mo * 30 * 86400;
  var d = Math.floor(s / 86400); s -= d * 86400;
  var h = Math.floor(s / 3600); s -= h * 3600;
  var mi = Math.floor(s / 60); s -= mi * 60;
  var str = 'P';
  if (y) str += y + 'Y';
  if (mo) str += mo + 'M';
  if (d) str += d + 'D';
  var t = (h ? h + 'H' : '') + (mi ? mi + 'M' : '') + (s ? s + 'S' : '');
  if (t) str += 'T' + t;
  if (str === 'P') str = 'PT0S';
  return (totalSec < 0 ? '-' : '') + str;
}

// ---------- 倒计时 ----------
function dtCountdown(targetSec) {
  var now = dtNowSeconds();
  var diff = targetSec - now;
  var past = diff < 0;
  diff = Math.abs(diff);
  var days = Math.floor(diff / 86400);
  var hours = Math.floor((diff % 86400) / 3600);
  var mins = Math.floor((diff % 3600) / 60);
  var secs = diff % 60;
  return { past: past, days: days, hours: hours, mins: mins, secs: secs };
}

// ---------- 日期差值（秒 -> 天/时/分/秒） ----------
function dtDiffSeconds(aSec, bSec) {
  var diff = Math.abs(aSec - bSec);
  var days = Math.floor(diff / 86400);
  var hours = Math.floor((diff % 86400) / 3600);
  var mins = Math.floor((diff % 3600) / 60);
  var secs = diff % 60;
  return { days: days, hours: hours, mins: mins, secs: secs };
}

// ---------- 日期加减（基于本地日历） ----------
// base = {y,m,d}；delta = {years,months,days}；月末钳制（如 1/31 + 1 月 = 2/28）
function dtAddDate(base, delta) {
  var y = base.y + (delta.years || 0);
  var m = base.m - 1 + (delta.months || 0);        // 0-based 月
  y += Math.floor(m / 12);
  m = ((m % 12) + 12) % 12;
  var lastDay = new Date(y, m + 1, 0).getDate();
  var day = Math.min(base.d, lastDay);
  var d = new Date(y, m, day);
  d.setDate(d.getDate() + (delta.days || 0));
  return { y: d.getFullYear(), m: d.getMonth() + 1, d: d.getDate() };
}

// ---------- 批量时间戳互转：文本块 -> 结果数组 ----------
// mode: 'ts2date' | 'date2ts'；每行一个输入
function dtBatchConvert(text, mode, tz) {
  var lines = String(text || '').split(/\r?\n/);
  var out = [];
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];
    var raw = line.trim();
    if (!raw) continue;
    if (mode === 'ts2date') {
      var r = dtParseTimestamp(raw);
      if (!r.ok) { out.push({ in: raw, ok: false, error: 'invalid' }); continue; }
      var p = dtZonedParts(r.value, tz);
      if (!p) { out.push({ in: raw, ok: false, error: 'invalid' }); continue; }
      out.push({ in: raw, ok: true, text: p.year + '-' + p.month + '-' + p.day + ' ' +
        p.hour + ':' + p.minute + ':' + p.second + ' ' + (tz === 'UTC' ? 'UTC' : tz) });
    } else {
      // date2ts：支持 "YYYY-MM-DD HH:MM:SS" 或 "YYYY-MM-DD"
      var mm = /^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?$/.exec(raw);
      if (!mm) { out.push({ in: raw, ok: false, error: 'invalid' }); continue; }
      var sec = dtPartsToSeconds(+mm[1], +mm[2], +mm[3], +mm[4] || 0, +mm[5] || 0, +mm[6] || 0, tz);
      if (sec === null) { out.push({ in: raw, ok: false, error: 'invalid' }); continue; }
      out.push({ in: raw, ok: true, text: String(sec) });
    }
  }
  return out;
}

// 世界时钟 / 时区页的时区数据集由构建期注入到 window.__WC_ZONES__（按当前语言本地化，中英文各自正确），
// 不再在此硬编码，避免中文数据泄漏到英文页。下方各 init 函数统一读取该全局变量。
// 数据结构：[{ tz, off, label, cities }]，顺序即标准 UTC 偏移从早到晚（UTC−12 → UTC+14）。

// 通用消息字典：进 i18n.EN 用于英文页；中文为默认。
var DT_MSG = {
  '请输入时间戳': 'Enter a timestamp',
  '无效的时间戳': 'Invalid timestamp',
  '请选择日期时间': 'Pick a date and time',
  '请输入日期': 'Enter a date',
  '请输入时长': 'Enter a duration',
  '时长格式无效': 'Invalid duration format',
  '开始日期不能晚于结束日期': 'Start date must not be after end date',
  '已转换 ': 'Converted ',
  ' 行': ' rows',
  '行（含 ': ' rows (',
  ' 行无效）': ' invalid)',
  '剩余': 'Remaining',
  '已过': 'Elapsed',
  '当前 ISO 周数': 'Current ISO week',
  '当前年内第几天': 'Current day of year',
  '闰年': 'Leap year',
  '平年': 'Common year',
  '当前': 'Now',
  '1 分钟后': 'In 1 minute',
  '1 小时后': 'In 1 hour',
  '今天 00:00': 'Today 00:00',
  '明天 00:00': 'Tomorrow 00:00',
  '本周一 00:00': 'This Monday 00:00',
  '本月 1 日 00:00': '1st of month 00:00',
  '本年 1 月 1 日 00:00': 'Jan 1 of year 00:00',
  '1 天后': 'In 1 day',
  '7 天后': 'In 7 days',
  '30 天后': 'In 30 days',
  '1 年后': 'In 1 year',
  '2038-01-19 (2038 问题临界)': '2038-01-19 (2038 limit)',
  'Unix 纪元起点': 'Unix epoch',
  '天': 'days',
  '时': 'h',
  '分': 'm',
  '秒': 's',
  ' 天 ': ' days ',
  ' 时 ': ' h ',
  ' 分 ': ' m ',
  ' 秒': ' s',
  ' 天': ' days',
  ' 周起': ' wk start',
  '第 ': 'Week ',
  '时间戳 ': 'Timestamp '
};

function dtMsg(zh) {
  var code = (document.documentElement.lang || 'zh-CN').slice(0, 2);
  if (code === 'en' && typeof DT_MSG !== 'undefined' && DT_MSG[zh]) return DT_MSG[zh];
  return zh;
}

// ============================================================
// 各工具页初始化（由 core.js 按 data-page 分派）
// 每个 initXxxPage 在元素缺失时直接返回，因此本文件被内联进所有页面也不会报错。
// ============================================================

function initBatchPage() {
  var root = document.getElementById('batchTool');
  if (!root) return;
  var input = document.getElementById('batchInput');
  var tzSel = document.getElementById('batchTz');
  var modeBtns = document.querySelectorAll('#batchMode .op-btn');
  var result = document.getElementById('batchResult');
  var info = document.getElementById('batchInfo');
  var mode = 'ts2date';
  modeBtns.forEach(function (b) {
    b.onclick = function () {
      modeBtns.forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      mode = b.dataset.op;
      runBatch();
    };
  });
  tzSel.onchange = runBatch;
  input.oninput = function () { debounce(runBatch, 200)(); };
  function runBatch() {
    var tz = tzSel.value;
    var rows = dtBatchConvert(input.value, mode, tz);
    if (!rows.length) { result.innerHTML = ''; info.textContent = ''; return; }
    var ok = rows.filter(function (r) { return r.ok; }).length;
    var bad = rows.length - ok;
    info.textContent = dtMsg('已转换 ') + ok + dtMsg(' 行') +
      (bad ? dtMsg('（含 ') + bad + dtMsg(' 行无效）') : '');
    var html = '<table class="dt-batch-table"><thead><tr><th>' +
      (mode === 'ts2date' ? '时间戳' : '日期') + '</th><th>' +
      (mode === 'ts2date' ? '日期' : '时间戳') + '</th></tr></thead><tbody>';
    rows.forEach(function (r) {
      if (r.ok) html += '<tr><td>' + escapeHtml(r.in) + '</td><td>' + escapeHtml(r.text) + '</td></tr>';
      else html += '<tr class="dt-bad"><td>' + escapeHtml(r.in) + '</td><td>✗ ' + dtMsg('无效的时间戳') + '</td></tr>';
    });
    html += '</tbody></table>';
    result.innerHTML = html;
  }
  runBatch();
}

function initTimestampListPage() {
  var root = document.getElementById('tsListTool');
  if (!root) return;
  var tzSel = document.getElementById('tsListTz');
  var body = document.getElementById('tsListBody');
  function render() {
    var tz = tzSel.value;
    var now = dtNowSeconds();
    var html = '';
    var marks = [
      { label: dtMsg('当前'), sec: now },
      { label: dtMsg('1 分钟后'), sec: now + 60 },
      { label: dtMsg('1 小时后'), sec: now + 3600 },
      { label: dtMsg('今天 00:00'), sec: startOfDay(now, tz) },
      { label: dtMsg('明天 00:00'), sec: startOfDay(now, tz) + 86400 },
      { label: dtMsg('本周一 00:00'), sec: startOfWeek(now, tz) },
      { label: dtMsg('本月 1 日 00:00'), sec: startOfMonth(now, tz) },
      { label: dtMsg('本年 1 月 1 日 00:00'), sec: startOfYear(now, tz) },
      { label: dtMsg('1 天后'), sec: now + 86400 },
      { label: dtMsg('7 天后'), sec: now + 7 * 86400 },
      { label: dtMsg('30 天后'), sec: now + 30 * 86400 },
      { label: dtMsg('1 年后'), sec: now + 365 * 86400 },
      { label: dtMsg('2038-01-19 (2038 问题临界)'), sec: 2147483647 },
      { label: dtMsg('Unix 纪元起点'), sec: 0 }
    ];
    marks.forEach(function (m) {
      var p = dtZonedParts(m.sec, tz);
      html += '<tr><td>' + escapeHtml(m.label) + '</td><td>' + m.sec + '</td><td>' +
        m.sec * 1000 + '</td><td>' + (p ? p.year + '-' + p.month + '-' + p.day + ' ' +
        p.hour + ':' + p.minute + ':' + p.second : '-') + '</td></tr>';
    });
    body.innerHTML = html;
  }
  tzSel.onchange = render;
  render();
}

// 以下三个辅助：按指定时区取「某时刻」所在日/周/月/年的 00:00 秒值
function startOfDay(sec, tz) {
  var p = dtZonedParts(sec, tz); if (!p) return sec;
  return dtPartsToSeconds(+p.year, +p.month, +p.day, 0, 0, 0, tz);
}
function startOfWeek(sec, tz) {
  var p = dtZonedParts(sec, tz); if (!p) return sec;
  var d = new Date(dtPartsToSeconds(+p.year, +p.month, +p.day, 0, 0, 0, tz) * 1000);
  var dow = (d.getUTCDay() + 6) % 7; // 周一=0
  return dtPartsToSeconds(+p.year, +p.month, +p.day, 0, 0, 0, tz) - dow * 86400;
}
function startOfMonth(sec, tz) {
  var p = dtZonedParts(sec, tz); if (!p) return sec;
  return dtPartsToSeconds(+p.year, +p.month, 1, 0, 0, 0, tz);
}
function startOfYear(sec, tz) {
  var p = dtZonedParts(sec, tz); if (!p) return sec;
  return dtPartsToSeconds(+p.year, 1, 1, 0, 0, 0, tz);
}

function initWeeknumbersPage() {
  var root = document.getElementById('weekTool');
  if (!root) return;
  var out = document.getElementById('weekOut');
  function update() {
    var w = dtIsoWeek(new Date());
    out.innerHTML = '<div class="dt-big">' + w.week + '</div>' +
      '<div class="dt-sub">ISO ' + w.year + ' · ' + dtMsg('当前 ISO 周数') + '</div>';
  }
  update();
  setInterval(update, 1000 * 60); // 每分钟刷新（跨周边界）
}

function initDaynumbersPage() {
  var root = document.getElementById('dayTool');
  if (!root) return;
  var out = document.getElementById('dayOut');
  function update() {
    var doy = dtDayOfYear(new Date());
    var total = dtIsLeapYear(new Date().getUTCFullYear()) ? 366 : 365;
    out.innerHTML = '<div class="dt-big">' + doy + '</div>' +
      '<div class="dt-sub">' + dtMsg('当前年内第几天') + ' · ' + total + ' ' + dtMsg('天') + '</div>';
  }
  update();
  setInterval(update, 1000 * 60);
}

function initYearsPage() {
  var root = document.getElementById('yearsTool');
  if (!root) return;
  var body = document.getElementById('yearsBody');
  var yearOut = document.getElementById('yearsNow');
  var nowY = new Date().getUTCFullYear();
  yearOut.textContent = nowY;
  var html = '';
  for (var y = 1800; y <= 2100; y++) {
    var leap = dtIsLeapYear(y);
    var days = leap ? 366 : 365;
    var isoFirst = dtIsoWeek(new Date(Date.UTC(y, 0, 1))).week;
    var cls = (y === nowY) ? ' class="dt-now"' : '';
    html += '<tr' + cls + '><td>' + y + '</td><td>' + days + '</td><td>' +
      (leap ? dtMsg('闰年') : dtMsg('平年')) + '</td>' + dtMsg('第 ') + isoFirst + dtMsg(' 周起') + '</td></tr>';
  }
  body.innerHTML = html;
}

// ---------- 表盘指针角度（世界时钟模拟视图） ----------
// 由某时区的墙钟分解（dtZonedParts 结果）算出时针/分针/秒针角度（度）。
// 时针连续走动（含分/秒的小数贡献），秒针按秒跳动。
function wcHandAngles(p) {
  var h = (+p.hour) % 12, m = +p.minute, s = +p.second;
  return {
    hour: (h + m / 60 + s / 3600) * 30,
    minute: (m + s / 60) * 6,
    second: s * 6
  };
}

// ---------- 是否处于夏令时（启发式：当前偏移 != 冬夏两个探点中较小的标准偏移） ----------
// 无夏令时的时区全年偏移恒定（jan === jul）返回 false；南半球（7 月为冬）同样适用。
function wcIsDst(tz, now) {
  var y = (now || new Date()).getUTCFullYear();
  var jan = dtTimezoneOffsetSeconds(tz, new Date(y, 0, 1));
  var jul = dtTimezoneOffsetSeconds(tz, new Date(y, 6, 1));
  if (jan === jul) return false;
  return dtTimezoneOffsetSeconds(tz, now || new Date()) !== Math.min(jan, jul);
}

function initWorldClockPage() {
  var root = document.getElementById('worldTool');
  if (!root) return;
  var body = document.getElementById('worldBody');
  var grid = document.getElementById('worldDials');
  var refBody = document.getElementById('worldRefBody');
  var refWrap = document.getElementById('worldRefWrap');
  var searchInput = document.getElementById('worldSearch');
  var searchResults = document.getElementById('worldSearchResults');
  var Z = window.__WC_ZONES__ || [];
  var isEn = (document.documentElement.lang || 'zh-CN').slice(0, 2) === 'en';
  var citySep = isEn ? ', ' : '、';
  var dstLabel = dtMsg('夏令时');
  // 列表视图：沿用原表格
  body.innerHTML = Z.map(function (x) {
    return '<tr><td>' + escapeHtml(x.label) + '</td>' +
      '<td><span class="dt-clock" data-tz="' + escapeHtml(x.tz) + '">--:--:--</span></td>' +
      '<td><span class="dt-off" data-off="' + escapeHtml(x.tz) + '"></span></td></tr>';
  }).join('');
  // 一张圆形模拟表盘（表盘视图 + 搜索结果共用）
  function dialSvg(tz) {
    var label = escapeHtml(tz);
    return '<svg class="wc-dial" viewBox="0 0 100 100" role="img" aria-label="' + label + '">' +
      '<circle class="wc-face" cx="50" cy="50" r="47"/>' + wcTicks() +
      '<line class="wc-hand wc-hour" data-hh="' + label + '" x1="50" y1="55" x2="50" y2="27"/>' +
      '<line class="wc-hand wc-min" data-hm="' + label + '" x1="50" y1="57" x2="50" y2="17"/>' +
      '<line class="wc-hand wc-sec" data-hs="' + label + '" x1="50" y1="60" x2="50" y2="13"/>' +
      '<circle class="wc-pin" cx="50" cy="50" r="3.4"/></svg>';
  }
  // 表盘视图：每个时区一张卡，卡上标注时区 + 全部同区城市 + 统一时间（合并同城多城市）
  var dateFmt = {};
  if (grid) {
    grid.innerHTML = Z.map(function (x) {
      return '<div class="wc-card" data-tz="' + escapeHtml(x.tz) + '">' +
        '<div class="wc-city">' + escapeHtml(x.label) + '</div>' +
        '<div class="wc-tz">' + escapeHtml(x.tz) + '</div>' +
        '<div class="wc-cities">' + escapeHtml(x.cities.join(citySep)) + '</div>' +
        dialSvg(x.tz) +
        '<div class="wc-date" data-wd="' + escapeHtml(x.tz) + '"></div>' +
        '<div class="wc-time dt-clock" data-tz="' + escapeHtml(x.tz) + '">--:--:--</div>' +
        '<div class="wc-meta"><span class="dt-off" data-off="' + escapeHtml(x.tz) + '"></span>' +
          '<span class="wc-dst" data-dst="' + escapeHtml(x.tz) + '" hidden>' + dstLabel + '</span></div>' +
        '</div>';
    }).join('');
    // 日期文案按页面语言由 Intl 生成（无源码字面量，各语言页各自正确）。
    // locale 取自 <html lang>（构建期写入的 BCP47 标签：zh-CN/en/ja/ko/es/pt-BR/fr/de/ru/id），
    // 裸 'en' 映射为 'en-US' 以保持英文页格式稳定。
    var loc = document.documentElement.lang || 'zh-CN';
    if (loc.slice(0, 2) === 'en') loc = 'en-US';
    Z.forEach(function (x) {
      try {
        dateFmt[x.tz] = new Intl.DateTimeFormat(loc, {
          timeZone: x.tz, year: 'numeric',
          month: isEn ? 'short' : 'long', day: 'numeric',
          weekday: isEn ? 'short' : 'long'
        });
      } catch (e) { dateFmt[x.tz] = null; }
    });
  }
  // 时区一览：静态表（按 UTC 顺序，标准偏移 + 主要城市），不随秒刷新。
  if (refBody) {
    refBody.innerHTML = Z.map(function (x) {
      return '<tr>' +
        '<td><span class="wc-rep">' + escapeHtml(x.label) + '</span>' +
        '<span class="wc-iana">' + escapeHtml(x.tz) + '</span></td>' +
        '<td class="wc-off-std">' + escapeHtml(x.off || '') + '</td>' +
        '<td class="wc-cities">' + escapeHtml(x.cities.join(citySep)) + '</td>' +
        '</tr>';
    }).join('');
    var refNote = document.getElementById('worldRefNote');
    if (refNote) refNote.textContent = dtMsg('按标准 UTC 偏移从早到晚排列（UTC−12 → UTC+14）；实行夏令时的地区当前偏移会在标准值基础上增减 1 小时。');
  }
  // 城市搜索索引：每条 = 一个城市 -> 所在时区；同时索引时区名与偏移
  var searchIndex = [];
  Z.forEach(function (x) {
    x.cities.forEach(function (c) {
      searchIndex.push({ city: c, tz: x.tz, off: x.off, label: x.label, all: x.cities });
    });
  });
  // 收集需要指针 / 日期 / DST 刷新的表盘卡片（表盘视图 + 搜索结果共用）
  var refs = [];
  function rebuildRefs() {
    var cards = document.querySelectorAll('#worldDials .wc-card, #worldSearchResults .wc-card');
    var arr = [];
    cards.forEach(function (card) {
      var tz = card.getAttribute('data-tz');
      var hh = card.querySelector('[data-hh]');
      if (!tz || !hh) return;
      arr.push({
        tz: tz,
        hh: hh,
        hm: card.querySelector('[data-hm]'),
        hs: card.querySelector('[data-hs]'),
        wd: card.querySelector('[data-wd]'),
        dst: card.querySelector('[data-dst]'),
        dstOn: null
      });
    });
    refs = arr;
  }
  rebuildRefs();
  function renderSearch(q) {
    if (!searchResults) return;
    var t = q.trim().toLowerCase();
    if (!t) { searchResults.hidden = true; searchResults.innerHTML = ''; return; }
    var seen = {}, matches = [];
    searchIndex.forEach(function (e) {
      var hay = (e.city + ' ' + e.tz + ' ' + e.off + ' ' + e.label).toLowerCase();
      if (hay.indexOf(t) === -1) return;
      var key = e.city + '|' + e.tz;
      if (seen[key]) return; seen[key] = 1;
      matches.push(e);
    });
    if (!matches.length) {
      searchResults.hidden = false;
      searchResults.innerHTML = '<p class="wc-search-empty">' +
        escapeHtml(dtMsg('无匹配城市，换个关键词试试')) + '</p>';
      rebuildRefs();
      return;
    }
    searchResults.hidden = false;
    searchResults.innerHTML = matches.map(function (e) {
      var others = e.all.filter(function (c) { return c !== e.city; });
      var otherLine = others.length
        ? '<div class="wc-zone-cities">' + escapeHtml(others.join(citySep)) + '</div>' : '';
      return '<div class="wc-card wc-card-mini" data-tz="' + escapeHtml(e.tz) + '">' +
        '<div class="wc-city">' + escapeHtml(e.city) + '</div>' +
        '<div class="wc-tz">' + escapeHtml(e.tz) + '</div>' +
        dialSvg(e.tz) +
        '<div class="wc-date" data-wd="' + escapeHtml(e.tz) + '"></div>' +
        '<div class="wc-time dt-clock" data-tz="' + escapeHtml(e.tz) + '">--:--:--</div>' +
        '<div class="wc-meta"><span class="dt-off" data-off="' + escapeHtml(e.tz) + '"></span>' +
          '<span class="wc-dst" data-dst="' + escapeHtml(e.tz) + '" hidden>' + dstLabel + '</span></div>' +
        otherLine + '</div>';
    }).join('');
    rebuildRefs();
  }
  var dstClock = null; // 夏令时状态缓存（每分钟校对一次足够）
  function refreshDst(now) {
    dstClock = { at: now.getTime(), state: {} };
    refs.forEach(function (r) {
      var on = false;
      try { on = wcIsDst(r.tz, now); } catch (e) {}
      r.dstOn = on;
    });
  }
  function tick() {
    var now = new Date();
    var ts = Math.floor(now.getTime() / 1000);
    document.querySelectorAll('.dt-clock').forEach(function (el) {
      var p = dtZonedParts(ts, el.getAttribute('data-tz'));
      el.textContent = p ? (p.hour + ':' + p.minute + ':' + p.second) : '--';
    });
    document.querySelectorAll('.dt-off').forEach(function (el) {
      el.textContent = dtTzOffsetLabel(el.getAttribute('data-off'), now);
    });
    if (!refs.length) return;
    if (!dstClock || now.getTime() - dstClock.at > 60000) refreshDst(now);
    refs.forEach(function (r) {
      var p = dtZonedParts(ts, r.tz);
      if (!p) return;
      var a = wcHandAngles(p);
      r.hh.setAttribute('transform', 'rotate(' + a.hour + ' 50 50)');
      r.hm.setAttribute('transform', 'rotate(' + a.minute + ' 50 50)');
      r.hs.setAttribute('transform', 'rotate(' + a.second + ' 50 50)');
      if (r.wd && dateFmt[r.tz]) r.wd.textContent = dateFmt[r.tz].format(now);
      if (r.dst) r.dst.hidden = !r.dstOn;
    });
  }
  // 视图切换：表盘 / 列表 / 时区一览，选择写入 localStorage（跨刷新记忆）
  var btnDial = document.getElementById('wcViewDial');
  var btnList = document.getElementById('wcViewList');
  var btnRef = document.getElementById('wcViewRef');
  var listWrap = document.getElementById('worldListWrap');
  var searching = false;
  function showViews(on) {
    if (grid) grid.style.display = on ? '' : 'none';
    if (listWrap) listWrap.style.display = on ? '' : 'none';
    if (refWrap) refWrap.style.display = on ? '' : 'none';
  }
  function setView(v) {
    var dial = v === 'dial', list = v === 'list', ref = v === 'ref';
    // 只显示当前视图，其余隐藏（避免三视图互相叠加）
    if (grid) grid.style.display = dial ? '' : 'none';
    if (listWrap) listWrap.style.display = list ? '' : 'none';
    if (refWrap) refWrap.style.display = ref ? '' : 'none';
    if (searchResults) searchResults.hidden = true;
    [['wcViewDial', dial], ['wcViewList', list], ['wcViewRef', ref]].forEach(function (p) {
      var b = document.getElementById(p[0]);
      if (!b) return;
      b.classList.toggle('active', p[1]);
      b.setAttribute('aria-pressed', String(p[1]));
    });
    try { localStorage.setItem('devtools-wcview', v); } catch (e) {}
  }
  if (btnDial && btnList && btnRef) {
    btnDial.onclick = function () { if (!searching) setView('dial'); };
    btnList.onclick = function () { if (!searching) setView('list'); };
    btnRef.onclick = function () { if (!searching) setView('ref'); };
    var saved = '';
    try { saved = localStorage.getItem('devtools-wcview') || ''; } catch (e) {}
    setView(saved === 'list' ? 'list' : (saved === 'ref' ? 'ref' : 'dial'));
  }
  // 搜索框：输入即筛选城市，展示匹配城市的时区与实时表盘时间
  if (searchInput) {
    searchInput.placeholder = dtMsg('搜索城市、时区或偏移');
    searchInput.oninput = function () {
      var q = searchInput.value;
      searching = q.trim().length > 0;
      if (searching) {
        showViews(false);
        renderSearch(q);
      } else {
        var sv = '';
        try { sv = localStorage.getItem('devtools-wcview') || 'dial'; } catch (e) {}
        setView(sv === 'list' ? 'list' : (sv === 'ref' ? 'ref' : 'dial'));
        rebuildRefs();
      }
    };
  }
  tick();
  setInterval(tick, 1000);
}

// 表盘刻度：12 个整点粗刻度
function wcTicks() {
  var s = '';
  for (var i = 0; i < 12; i++) {
    s += '<line class="wc-tick" x1="50" y1="7" x2="50" y2="13" transform="rotate(' + (i * 30) + ' 50 50)"/>';
  }
  return s;
}

function initCountdownPage() {
  var root = document.getElementById('cdTool');
  if (!root) return;
  var input = document.getElementById('cdInput');
  var result = document.getElementById('cdResult');
  var share = document.getElementById('cdShare');
  function render() {
    var r = dtParseTimestamp(input.value);
    if (!r.ok) { result.innerHTML = ''; if (share) share.style.display = 'none'; return; }
    tick(r.value);
    if (share) share.style.display = '';
  }
  function tick(target) {
    var c = dtCountdown(target);
    var label = c.past ? dtMsg('已过') : dtMsg('剩余');
    result.innerHTML = '<div class="dt-sub">' + label + '</div>' +
      '<div class="dt-big">' + c.days + ':' + pad(c.hours) + ':' + pad(c.mins) + ':' + pad(c.secs) +
      '</div><div class="dt-sub">' + c.days + dtMsg(' 天 ') + c.hours + dtMsg(' 时 ') + c.mins +
      dtMsg(' 分 ') + c.secs + dtMsg(' 秒') + '</div>';
  }
  input.oninput = render;
  // deep-link 回放：?target= 自动填入并倒计时
  try {
    var p = new URLSearchParams(location.search).get('target');
    if (p) input.value = p;
  } catch (e) {}
  if (input.value) render();
}

// 倒计时「复制分享链接」
function shareCountdownLink() {
  var v = document.getElementById('cdInput').value.trim();
  if (!v) { toast('请先输入时间戳', 'error'); return; }
  var url = location.origin + location.pathname + '?target=' + encodeURIComponent(v);
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(function () { toast('已复制分享链接'); },
      function () { toast('复制失败', 'error'); });
  } else { toast('复制失败', 'error'); }
}

function initDateDifferencePage() {
  var root = document.getElementById('diffTool');
  if (!root) return;
  var a = document.getElementById('diffA');
  var b = document.getElementById('diffB');
  var result = document.getElementById('diffResult');
  var tzSel = document.getElementById('diffTz');
  function render() {
    var ra = dtParseDateInput(a.value, tzSel ? tzSel.value : 'local');
    var rb = dtParseDateInput(b.value, tzSel ? tzSel.value : 'local');
    if (!ra || !rb) { result.innerHTML = ''; return; }
    if (ra > rb) { var t = ra; ra = rb; rb = t; }
    var d = dtDiffSeconds(ra, rb);
    result.innerHTML = '<div class="dt-big">' + d.days + dtMsg(' 天') + '</div>' +
      '<div class="dt-sub">' + d.hours + dtMsg(' 时 ') + d.mins + dtMsg(' 分 ') + d.secs +
      dtMsg(' 秒') + ' · ' + (rb - ra) + dtMsg(' 秒') + '</div>';
  }
  a.onchange = render; b.onchange = render;
  if (tzSel) tzSel.onchange = render;
  if (a.value && b.value) render();
}

function initDateCalculatorPage() {
  var root = document.getElementById('calcTool');
  if (!root) return;
  var base = document.getElementById('calcBase');
  var dy = document.getElementById('calcYears');
  var dm = document.getElementById('calcMonths');
  var dd = document.getElementById('calcDays');
  var result = document.getElementById('calcResult');
  function render() {
    var bm = /^(\d{4})-(\d{1,2})-(\d{1,2})/.exec(base.value);
    if (!bm) { result.innerHTML = ''; return; }
    var res = dtAddDate({ y: +bm[1], m: +bm[2], d: +bm[3] },
      { years: +dy.value || 0, months: +dm.value || 0, days: +dd.value || 0 });
    var sec = dtPartsToSeconds(res.y, res.m, res.d, 0, 0, 0, 'local');
    result.innerHTML = '<div class="dt-big">' + res.y + '-' + pad(res.m) + '-' + pad(res.d) +
      '</div><div class="dt-sub">' + dtMsg('时间戳 ') + sec + '</div>';
  }
  [base, dy, dm, dd].forEach(function (el) { el.oninput = render; el.onchange = render; });
  if (base.value) render();
}

function initDurationPage() {
  var root = document.getElementById('durTool');
  if (!root) return;
  var toSec = document.getElementById('durToSec');
  var toIso = document.getElementById('durToIso');
  var secOut = document.getElementById('durSecOut');
  var isoOut = document.getElementById('durIsoOut');
  toSec.oninput = function () {
    var r = dtParseIsoDuration(toSec.value);
    secOut.textContent = r.ok ? String(r.seconds) : (r.error ? dtMsg('时长格式无效') : '');
  };
  toIso.oninput = function () {
    var n = parseInt(toIso.value, 10);
    isoOut.textContent = isNaN(n) ? '' : dtSecondsToIsoDuration(n);
  };
  if (toSec.value) toSec.oninput();
  if (toIso.value) toIso.oninput();
}

function initTimezonesPage() {
  var root = document.getElementById('tzTool');
  if (!root) return;
  var body = document.getElementById('tzBody');
  var Z = window.__WC_ZONES__ || [];
  var zones = Z.map(function (x) { return x.tz; });
  var now = new Date();
  var html = '';
  Z.forEach(function (x) {
    var p = dtZonedParts(Math.floor(now.getTime() / 1000), x.tz);
    html += '<tr><td>' + escapeHtml(x.label) + '</td>' +
      '<td>' + escapeHtml(x.tz) + '</td>' +
      '<td>' + escapeHtml(dtTzOffsetLabel(x.tz, now)) + '</td>' +
      '<td>' + (p ? p.hour + ':' + p.minute + ':' + p.second : '--') + '</td></tr>';
  });
  body.innerHTML = html;
  setInterval(function () {
    var nn = new Date();
    document.querySelectorAll('#tzBody tr').forEach(function (tr, i) {
      var p = dtZonedParts(Math.floor(nn.getTime() / 1000), zones[i]);
      var cells = tr.querySelectorAll('td');
      if (cells[3]) cells[3].textContent = p ? (p.hour + ':' + p.minute + ':' + p.second) : '--';
    });
  }, 1000);
}

// ---------- 小工具 ----------
function pad(n) { n = String(n); return n.length < 2 ? '0' + n : n; }
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}
function debounce(fn, ms) {
  var t; return function () {
    var args = arguments, ctx = this;
    clearTimeout(t); t = setTimeout(function () { fn.apply(ctx, args); }, ms);
  };
}
// 解析 datetime-local 输入为秒（本地时区）
function dtParseDateInput(val, tz) {
  if (!val) return null;
  var d = new Date(val);
  if (isNaN(d.getTime())) return null;
  return Math.floor(d.getTime() / 1000);
}

// Node 单测导出（浏览器中 module 为 undefined，自动跳过）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    dtParseTimestamp: dtParseTimestamp, dtNowSeconds: dtNowSeconds,
    dtZonedParts: dtZonedParts,
    dtPartsToSeconds: dtPartsToSeconds, dtTimezoneOffsetSeconds: dtTimezoneOffsetSeconds,
    dtTzOffsetLabel: dtTzOffsetLabel, dtIsoWeek: dtIsoWeek, dtDayOfYear: dtDayOfYear,
    dtIsLeapYear: dtIsLeapYear, dtParseIsoDuration: dtParseIsoDuration,
    dtSecondsToIsoDuration: dtSecondsToIsoDuration, dtCountdown: dtCountdown,
    dtDiffSeconds: dtDiffSeconds, dtAddDate: dtAddDate, dtBatchConvert: dtBatchConvert,
    wcHandAngles: wcHandAngles, wcIsDst: wcIsDst
  };
}
