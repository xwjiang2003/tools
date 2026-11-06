// altimeter.js — 网页版海拔计：GNSS 椭球高 + 精度诚实显示 + 气压计探测 + 轨迹导出
//
// 立场（写在代码里，避免以后有人把它"优化"成看起来更准）：
//   1. 网页只能拿到 GNSS 单点解算的 WGS-84 椭球高，垂直误差 10~30 m，不是正高；
//   2. 拿不到垂直精度时必须显示"未知"，绝不能编一个 ±1 m；
//   3. 第一帧定位到达前显示占位符，不显示 0 m（那会让人以为自己在海平面）；
//   4. 气压计在浏览器里基本读不到（Chromium 需 flag、iOS Safari 不开放），
//      所以它是一块"探测 + 说明"的模块，而不是主数据源。
// 所有界面文案来自 window.__TL__（构建期按语言注入），本文件不得出现任何中文字面量：
// 它会内联进英文页，check.py 的非中文页零 CJK 断言会直接判定泄漏。

var G = (typeof window !== 'undefined') ? window : {};

// 国际标准大气：h = 44330 × (1 − (P/P0)^(1/5.255))
var ALT_H0 = 44330;
var ALT_LAPSE = 1 / 5.255;      // ≈ 0.190263
var ALT_FT = 0.3048;            // 1 英尺 = 0.3048 米
var ALT_MAX_POINTS = 3600;      // 轨迹上限（1 Hz 约一小时），超出丢最早的点
var ALT_STALE_MS = 15000;       // 多久没有新解算就提示"信号中断"（偶发错误不顶掉测量状态）

// ---------------------------------------------------------------- 纯函数

/**
 * 统一的数值入口：null / '' / 布尔值一律视为"没有值"返回 NaN。
 * 直接用 Number(v) 会把 null 变成 0，而 0 在这里是有意义的值（海平面、零度），
 * 一旦混淆就会出现"没数据却显示 0 米"这种最伤信任的 bug。
 */
function altNum(v) {
  if (v == null || v === '' || typeof v === 'boolean') return NaN;
  var n = Number(v);
  return isFinite(n) ? n : NaN;
}

/** 气压（hPa）→ 海拔（米）。p0 为海平面基准气压。无效输入返回 null。 */
function altPressureToHeight(p, p0) {
  p = altNum(p); p0 = altNum(p0);
  if (!isFinite(p) || !isFinite(p0) || p <= 0 || p0 <= 0) return null;
  return ALT_H0 * (1 - Math.pow(p / p0, ALT_LAPSE));
}

/** 已知海拔反推海平面基准气压（hPa）。h 超过 44330 m 或输入无效时返回 null。 */
function altRefPressure(p, h) {
  p = altNum(p); h = altNum(h);
  if (!isFinite(p) || !isFinite(h) || p <= 0) return null;
  var base = 1 - h / ALT_H0;
  if (base <= 0) return null;
  return p / Math.pow(base, 5.255);
}

/** 海平面附近 1 hPa 对应多少米（用作说明里的量级参考）。 */
function altMetresPerHpa(p, p0) {
  var a = altPressureToHeight(p, p0);
  var b = altPressureToHeight(altNum(p) - 1, p0);
  if (a == null || b == null) return null;
  return b - a;          // 气压降 1 hPa，高度上升多少米（正值）
}

/** AmbientPressureSensor 的原始单位是 kPa，日历式气压习惯用 hPa。 */
function altKpaToHpa(kpa) {
  var v = altNum(kpa);
  return isFinite(v) ? v * 10 : null;
}

function altToFeet(m) {
  var v = altNum(m);
  return isFinite(v) ? v / ALT_FT : null;
}

function altToMetres(ft) {
  var v = altNum(ft);
  return isFinite(v) ? v * ALT_FT : null;
}

/**
 * 按精度决定显示几位小数：不知道精度就只给整数。
 * 这是"不假装精确"的最后一环——±30 m 的高度写成 1286.4 会误导人。
 */
function altDecimals(vacc) {
  var v = altNum(vacc);
  if (!isFinite(v) || v >= 1) return 0;
  return 1;
}

/** 四舍五入到 d 位；无效值返回 null 由调用方渲染占位符。-0 归一成 0。 */
function altRound(v, d) {
  var n = altNum(v);
  if (!isFinite(n)) return null;
  var f = Math.pow(10, d == null ? 0 : d);
  var r = Math.round(n * f) / f;
  return r === 0 ? 0 : r;
}

/**
 * 轨迹统计。
 * points: [{t: 毫秒时间戳, ele: 米或 null}]，按时间升序。
 * opts.threshold: 计入爬升/下降的最小高差（默认 2 m，滤掉 GNSS 垂直抖动）。
 * opts.window: 计算垂直速度的时间窗口（默认 60 秒）。
 * 返回 {asc, desc, vSpeed(m/min), n}，n 为有效采样点数。
 */
function altTrackStats(points, opts) {
  opts = opts || {};
  var thr = opts.threshold == null ? 2 : Number(opts.threshold);
  var win = opts.window == null ? 60000 : Number(opts.window);
  var asc = 0, desc = 0, n = 0, ref = null;
  var last = null, first = null;
  var arr = points || [];
  for (var i = 0; i < arr.length; i++) {
    var p = arr[i];
    if (!p || p.ele == null) continue;
    var e = Number(p.ele);
    if (!isFinite(e)) continue;
    n++;
    if (ref === null) { ref = e; continue; }
    var d = e - ref;
    if (d >= thr) { asc += d; ref = e; }
    else if (d <= -thr) { desc += -d; ref = e; }
  }
  // 垂直速度只看最近一个窗口：从末尾往前找仍在窗口内的最早点。
  for (var j = arr.length - 1; j >= 0; j--) {
    var q = arr[j];
    if (!q || q.ele == null || !isFinite(Number(q.ele)) || !isFinite(Number(q.t))) continue;
    if (last === null) last = q;
    if (last.t - q.t <= win) first = q;
    else break;
  }
  var vSpeed = 0;
  if (last && first && last !== first) {
    var dtMin = (last.t - first.t) / 60000;
    // 少于 0.6 秒的两点算不出有意义的速率，直接给 0 而不是放大噪声
    if (dtMin > 0.01) vSpeed = (Number(last.ele) - Number(first.ele)) / dtMin;
  }
  return { asc: asc, desc: desc, vSpeed: vSpeed, n: n };
}

function altXmlEsc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}

function altIso(t) {
  var d = new Date(Number(t) || Date.now());
  return isFinite(d.getTime()) ? d.toISOString() : new Date().toISOString();
}

/**
 * GPX 1.1：带 ele 与 time，Strava / Komoot / 两步路 / Garmin Connect 都能直接导入。
 * 没有 ele 的点也保留（位置本身有价值），只是不带 <ele>。
 */
function altBuildGpx(points, name) {
  var label = altXmlEsc(name || 'Track');
  var arr = points || [];
  var start = arr.length ? arr[0].t : Date.now();
  var out = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<gpx version="1.1" creator="devtools.help altimeter" xmlns="http://www.topografix.com/GPX/1/1">',
    '  <metadata><name>' + label + '</name><time>' + altIso(start) + '</time></metadata>',
    '  <trk><name>' + label + '</name><trkseg>'
  ];
  for (var i = 0; i < arr.length; i++) {
    var p = arr[i];
    if (!p || !isFinite(Number(p.lat)) || !isFinite(Number(p.lon))) continue;
    var line = '    <trkpt lat="' + Number(p.lat).toFixed(6) + '" lon="' + Number(p.lon).toFixed(6) + '">';
    if (p.ele != null && isFinite(Number(p.ele))) line += '<ele>' + Number(p.ele).toFixed(1) + '</ele>';
    if (p.t != null) line += '<time>' + altIso(p.t) + '</time>';
    line += '</trkpt>';
    out.push(line);
  }
  out.push('  </trkseg></trk>', '</gpx>');
  return out.join('\n') + '\n';
}

/** CSV：列名用英文，避免导出文件随界面语言漂移。 */
function altBuildCsv(points) {
  var head = 'time_iso,lat,lon,ele_m,ele_acc_m,horiz_acc_m';
  var rows = [head];
  var arr = points || [];
  for (var i = 0; i < arr.length; i++) {
    var p = arr[i];
    if (!p) continue;
    rows.push([
      altIso(p.t),
      isFinite(Number(p.lat)) ? Number(p.lat).toFixed(6) : '',
      isFinite(Number(p.lon)) ? Number(p.lon).toFixed(6) : '',
      p.ele != null && isFinite(Number(p.ele)) ? Number(p.ele).toFixed(1) : '',
      p.vacc != null && isFinite(Number(p.vacc)) ? Number(p.vacc).toFixed(1) : '',
      p.hacc != null && isFinite(Number(p.hacc)) ? Number(p.hacc).toFixed(1) : ''
    ].join(','));
  }
  return rows.join('\n') + '\n';
}

/** 导出文件名：ISO 时间去冒号，Windows 也能存。 */
function altFileName(prefix, t, ext) {
  var iso = altIso(t).replace(/[:.]/g, '-').replace('T', '_').slice(0, 19);
  return prefix + '-' + iso + '.' + ext;
}

// ---------------------------------------------------------------- 页面

function initAltimeter() {
  var root = document.getElementById('altValue');
  if (!root) return;

  var L = G.__TL__ || {};
  function T(k, fb) { var v = L[k]; return (v == null) ? fb : v; }
  function TF(k, val, fb) { return String(T(k, fb)).replace('{v}', val); }
  function $(id) { return document.getElementById(id); }

  var state = {
    unit: 'm', running: false, watchId: null,
    last: null, track: [], firstFixAt: 0, liveAt: 0, wake: null,
    baro: { ok: false, p: null, p0: null, auto: false, sensor: null },
    timer: null, beat: null
  };

  try {
    if (localStorage.getItem('altimeter:unit') === 'ft') state.unit = 'ft';
  } catch (e) { /* 隐私模式下不可用，忽略 */ }

  function docLang() {
    var l = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
    return l || 'en';
  }

  function num(v, d) {
    var n = altRound(v, d);
    return n == null ? '—' : String(n);
  }

  // 米 → 当前单位
  function len(m, d) {
    if (m == null || !isFinite(Number(m))) return '—';
    return num(state.unit === 'ft' ? altToFeet(m) : Number(m), d);
  }

  // 单位符号统一用 m / ft（不写"米/英尺"）：主数字旁边就是这个符号，
  // 界面上两处用不同写法会让人怀疑是不是两个量。
  function unitLabel() {
    return state.unit === 'ft' ? 'ft' : 'm';
  }

  function speedLabel() {
    return state.unit === 'ft' ? 'ft/min' : 'm/min';
  }

  function accText(m) {
    if (m == null || !isFinite(Number(m))) return T('acc_unknown', 'accuracy unknown');
    var d = altDecimals(m);
    return TF('acc_fmt', len(m, d) + ' ' + unitLabel(), '±{v}');
  }

  function setStatus(key, fallback) {
    var el = $('altStatus');
    if (el) el.textContent = T(key, fallback || key);
  }

  function setHint(key, fallback) {
    var el = $('altHint');
    if (el) el.textContent = T(key, fallback || '');
  }

  function toast(msg) {
    var el = $('altToast');
    if (!el) return;
    el.textContent = msg;
    el.hidden = false;
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { el.hidden = true; }, 2400);
  }

  function geoN() {
    var el = $('geoN');
    var v = el ? parseFloat(el.value) : 0;
    return isFinite(v) ? v : 0;
  }

  // ------------------------------------------------------------ 渲染

  // 占位符 "—" 在 76px 粗体下会画成一根黑条，看起来像加载动画或遮挡块。
  // 加 .is-empty 让它变成细的浅灰短横，一眼看出"这里还没数"。
  function setValue(el, text, isEmpty) {
    if (!el) return;
    el.textContent = text;
    if (isEmpty) el.classList.add('is-empty');
    else el.classList.remove('is-empty');
  }

  function render() {
    var last = state.last;
    var n = geoN();
    var valueEl = $('altValue');
    var markEl = $('altMark');
    var accEl = $('altAcc');

    if (markEl) markEl.textContent = unitLabel();

    if (!last) {
      setValue(valueEl, '—', true);
      if (accEl) accEl.textContent = '—';
    } else if (last.ele == null) {
      // 徽章只放"精度"，长句解释放 hint 行；原来是整句塞进胶囊，撑成一条蓝带很怪。
      setValue(valueEl, '—', true);
      if (accEl) accEl.textContent = accText(last.vacc);
    } else {
      var shown = last.ele - n;
      var d = altDecimals(last.vacc);
      setValue(valueEl, len(shown, d), false);
      if (accEl) accEl.textContent = accText(last.vacc);
    }

    // 提示行跟着定位质量走，测量中才接管（权限被拒时 stop 之后不能再覆盖掉拒绝提示）
    if (state.running) {
      if (last && last.ele == null) setHint('hint_noele', '');
      else setHint('hint_privacy', '');
    }

    if ($('mHacc')) $('mHacc').textContent = last ? accText(last.hacc) : '—';
    if ($('mVacc')) $('mVacc').textContent = last ? accText(last.vacc) : '—';
    if ($('mTime')) {
      $('mTime').textContent = last
        ? new Date(last.t).toLocaleTimeString(docLang(), { hour12: false })
        : '—';
    }

    var stats = altTrackStats(state.track, { threshold: state.unit === 'ft' ? 6.5 : 2 });
    // 少于两个带海拔的样点，速度和累计爬升都无从算起——写 0 会被当成"确实没动"。
    var enough = stats.n >= 2;
    if ($('mVspeed')) {
      if (last && enough) {
        var vs = state.unit === 'ft' ? altToFeet(stats.vSpeed) : stats.vSpeed;
        $('mVspeed').textContent = num(vs, 1) + ' ' + speedLabel();
      } else {
        $('mVspeed').textContent = '—';
      }
    }
    // 累计爬升/下降跟主单位一起变，模板里不写死单位，否则切到 ft 会显示"181 m"
    if ($('cAsc')) $('cAsc').textContent = enough ? len(stats.asc, 0) + ' ' + unitLabel() : '—';
    if ($('cDesc')) $('cDesc').textContent = enough ? len(stats.desc, 0) + ' ' + unitLabel() : '—';
    if ($('cPts')) $('cPts').textContent = String(stats.n);

    // 定位详情
    if ($('rEll')) $('rEll').textContent = last && last.ele != null
      ? len(last.ele, altDecimals(last.vacc)) + ' ' + unitLabel() : '—';
    if ($('rOrtho')) $('rOrtho').textContent = last && last.ele != null
      ? len(last.ele - n, altDecimals(last.vacc)) + ' ' + unitLabel() : '—';
    if ($('rLat')) $('rLat').textContent = last ? last.lat.toFixed(6) : '—';
    if ($('rLon')) $('rLon').textContent = last ? last.lon.toFixed(6) : '—';
    if ($('rHacc')) $('rHacc').textContent = last ? accText(last.hacc) : '—';
    if ($('rVacc')) $('rVacc').textContent = last ? accText(last.vacc) : '—';
    // 这一行数的是"收到几次定位"，与剖面里"海拔采样点"口径不同，别再混用同一个数字
    if ($('rPts')) $('rPts').textContent = String(state.track.length);
    if ($('rSrc')) {
      if (!last) $('rSrc').textContent = T('v_none', 'none yet');
      else if (last.ele == null) $('rSrc').textContent = T('v_horiz', 'horizontal only');
      else $('rSrc').textContent = T('v_gps', 'GNSS fix');
    }

    renderBaro();
    drawChart();
  }

  function renderBaro() {
    var b = state.baro;
    if (!b.ok) return;
    if ($('baroP')) $('baroP').textContent = b.p == null ? T('baro_wait', 'waiting') :
      b.p.toFixed(2) + ' hPa';
    if ($('baroP0')) $('baroP0').textContent = b.p0 == null ? '—' : b.p0.toFixed(2) + ' hPa';
    var h = (b.p != null && b.p0 != null) ? altPressureToHeight(b.p, b.p0) : null;
    if ($('baroH')) $('baroH').textContent = h == null ? '—' : len(h, 1) + ' ' + unitLabel();
  }

  // ------------------------------------------------------------ 图表

  function cssVar(name, fallback) {
    try {
      var v = getComputedStyle(document.documentElement).getPropertyValue(name);
      return v && v.trim() ? v.trim() : fallback;
    } catch (e) { return fallback; }
  }

  function drawChart() {
    var cv = $('altChart');
    if (!cv) return;
    var pts = [];
    for (var i = 0; i < state.track.length; i++) {
      var p = state.track[i];
      if (p && p.ele != null && isFinite(Number(p.ele))) pts.push(p);
    }
    var empty = $('chartEmpty');
    if (pts.length < 2) {
      // 空态要分清两种：还没开始，和在测但设备不给海拔。
      // 后者说"开始测量后会出现曲线"是错的——用户明明已经开始了。
      if (empty) {
        empty.textContent = state.track.length
          ? T('chart_noele', 'Fixes are arriving, but none carries an altitude')
          : T('chart_empty', 'Start measuring and the curve shows up here');
        empty.hidden = false;
      }
      cv.hidden = true;
      return;
    }
    if (empty) empty.hidden = true;
    cv.hidden = false;

    var W = Math.max(280, cv.clientWidth || 640);
    var H = 170;
    var dpr = G.devicePixelRatio || 1;
    if (cv.width !== Math.round(W * dpr)) cv.width = Math.round(W * dpr);
    if (cv.height !== Math.round(H * dpr)) cv.height = Math.round(H * dpr);
    var ctx = cv.getContext('2d');
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    var L0 = 46, R0 = 12, T0 = 12, B0 = 22;
    var vals = pts.map(function (q) {
      return state.unit === 'ft' ? altToFeet(q.ele) : Number(q.ele);
    });
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    if (hi - lo < 5) { var mid = (hi + lo) / 2; lo = mid - 2.5; hi = mid + 2.5; }
    var pad = (hi - lo) * 0.12;
    lo -= pad; hi += pad;

    var t0 = pts[0].t, t1 = pts[pts.length - 1].t;
    var span = Math.max(1, t1 - t0);
    var plotW = W - L0 - R0, plotH = H - T0 - B0;
    function X(t) { return L0 + (t - t0) / span * plotW; }
    function Y(v) { return T0 + (hi - v) / (hi - lo) * plotH; }

    var grid = cssVar('--border', '#e1e5eb');
    var muted = cssVar('--text-muted', '#adb5bd');
    var primary = cssVar('--primary', '#4a90d9');
    var textCol = cssVar('--text-secondary', '#6c757d');

    ctx.font = '11px "JetBrains Mono", Consolas, monospace';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    var steps = 4;
    for (var g = 0; g <= steps; g++) {
      var v = lo + (hi - lo) * g / steps;
      var y = Y(v);
      ctx.strokeStyle = grid;
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(L0, y + 0.5); ctx.lineTo(W - R0, y + 0.5); ctx.stroke();
      ctx.fillStyle = muted;
      ctx.fillText(String(Math.round(v)), L0 - 6, y);
    }

    // 面积渐变
    var grad = ctx.createLinearGradient(0, T0, 0, T0 + plotH);
    grad.addColorStop(0, 'rgba(74,144,217,0.22)');
    grad.addColorStop(1, 'rgba(74,144,217,0.02)');
    ctx.beginPath();
    ctx.moveTo(X(pts[0].t), Y(vals[0]));
    for (var k = 1; k < pts.length; k++) ctx.lineTo(X(pts[k].t), Y(vals[k]));
    ctx.lineTo(X(t1), T0 + plotH);
    ctx.lineTo(X(t0), T0 + plotH);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // 折线
    ctx.beginPath();
    ctx.moveTo(X(pts[0].t), Y(vals[0]));
    for (var m = 1; m < pts.length; m++) ctx.lineTo(X(pts[m].t), Y(vals[m]));
    ctx.strokeStyle = primary;
    ctx.lineWidth = 1.8;
    ctx.lineJoin = 'round';
    ctx.stroke();

    // 末点
    ctx.beginPath();
    ctx.arc(X(t1), Y(vals[vals.length - 1]), 3, 0, Math.PI * 2);
    ctx.fillStyle = primary;
    ctx.fill();

    // 时间轴：首尾两个刻度
    ctx.fillStyle = textCol;
    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';
    ctx.fillText(new Date(t0).toLocaleTimeString(docLang(), { hour12: false }), L0, T0 + plotH + 6);
    ctx.textAlign = 'right';
    ctx.fillText(new Date(t1).toLocaleTimeString(docLang(), { hour12: false }), W - R0, T0 + plotH + 6);
  }

  // ------------------------------------------------------------ 轨迹

  function pushPoint(fix) {
    var arr = state.track;
    var prev = arr[arr.length - 1];
    // 同一位置且间隔过短不重复记（部分设备 watchPosition 会成串抖动）
    if (prev && fix.t - prev.t < 900 &&
        prev.lat === fix.lat && prev.lon === fix.lon) return;
    arr.push(fix);
    if (arr.length > ALT_MAX_POINTS) arr.splice(0, arr.length - ALT_MAX_POINTS);
  }

  // ------------------------------------------------------------ 定位

  function insecure() {
    return G.isSecureContext === false;
  }

  function onPos(pos) {
    var c = pos.coords;
    var fix = {
      t: pos.timestamp || Date.now(),
      lat: c.latitude,
      lon: c.longitude,
      ele: (c.altitude == null || !isFinite(c.altitude)) ? null : c.altitude,
      vacc: (c.altitudeAccuracy == null || !isFinite(c.altitudeAccuracy)) ? null : c.altitudeAccuracy,
      hacc: (c.accuracy == null || !isFinite(c.accuracy)) ? null : c.accuracy
    };
    state.last = fix;
    if (!state.firstFixAt) state.firstFixAt = fix.t;
    state.liveAt = Date.now();
    setStatus('st_live', 'Measuring');
    pushPoint(fix);
    // 气压计可用但还没基准：用当前 GPS 高度自动校准一次，之后气压高度只做相对变化
    if (state.baro.ok && state.baro.p != null && state.baro.p0 == null && fix.ele != null) {
      var p0 = altRefPressure(state.baro.p, fix.ele);
      if (p0 != null) { state.baro.p0 = p0; state.baro.auto = true; }
    }
    render();
  }

  function onErr(err) {
    var code = err && err.code;
    if (code === 1) {
      setStatus('st_denied', 'Location permission denied');
      setHint('hint_denied', '');
      stop(true);
      return;
    }
    // 已经拿到过有效定位时报错，多半是进隧道、上楼、树荫遮挡——watchPosition 会自己重试。
    // 这种偶发错误不该把"测量中"顶掉，否则状态会在两句话之间来回闪；
    // 只有真正过期（超过 STALE_MS 没有新解）才提示中断，见下面的心跳。
    if (state.firstFixAt) return;
    setStatus(code === 3 ? 'st_timeout' : 'st_unavailable',
      code === 3 ? 'Location timed out' : 'Position unavailable');
  }

  function reqWake() {
    if (!navigator.wakeLock || state.wake) return;
    try {
      navigator.wakeLock.request('screen').then(function (s) {
        state.wake = s;
        s.addEventListener('release', function () { state.wake = null; });
      }, function () { /* 不支持或被拒绝：不影响测量 */ });
    } catch (e) { /* 老浏览器没有 wakeLock */ }
  }

  function relWake() {
    if (!state.wake) return;
    try { state.wake.release(); } catch (e) { /* ignore */ }
    state.wake = null;
  }

  function setBtn(running) {
    var b = $('altBtn');
    if (!b) return;
    b.textContent = running ? T('btn_stop', 'Stop') : T('btn_start', 'Start measuring');
    b.classList.toggle('alt-btn-stop', running);
  }

  function start() {
    if (!('geolocation' in navigator)) {
      setStatus('st_unavailable', 'This device has no location support');
      return;
    }
    if (insecure()) {
      setStatus('st_insecure', 'HTTPS is required for geolocation');
      return;
    }
    state.running = true;
    state.firstFixAt = 0;
    setBtn(true);
    setHint('hint_privacy', '');
    setStatus('st_asking', 'Asking for location permission...');

    // 授权对话框关闭后迟迟没有第一帧 → 说明在搜星，不是卡死
    clearTimeout(state.timer);
    state.timer = setTimeout(function () {
      if (state.running && !state.firstFixAt) setStatus('st_searching', 'Searching for satellites...');
    }, 6000);

    try {
      state.watchId = navigator.geolocation.watchPosition(onPos, onErr, {
        enableHighAccuracy: true, maximumAge: 0, timeout: 30000
      });
    } catch (e) {
      setStatus('st_unavailable', 'This device has no location support');
      state.running = false;
      setBtn(false);
      return;
    }
    // 心跳：定位回调沉默时（走进室内、隧道）界面必须主动说"信号中断"，
    // 否则用户看到的是一个冻住的数字，还以为海拔真的没变。
    clearInterval(state.beat);
    state.beat = setInterval(function () {
      if (!state.running || !state.firstFixAt) return;
      if (Date.now() - state.liveAt > ALT_STALE_MS) {
        setStatus('st_lost', 'Satellite signal lost, retrying');
      }
    }, 5000);
    reqWake();
  }

  function stop(silent) {
    state.running = false;
    clearTimeout(state.timer);
    clearInterval(state.beat);
    state.beat = null;
    if (state.watchId != null) {
      try { navigator.geolocation.clearWatch(state.watchId); } catch (e) { /* ignore */ }
      state.watchId = null;
    }
    relWake();
    setBtn(false);
    if (!silent) setStatus('st_stopped', 'Stopped');
  }

  // ------------------------------------------------------------ 气压计

  function initBaro() {
    var badge = $('baroBadge');
    var body = $('baroBody');
    var cal = $('baroCal');
    var note = $('baroNote');
    var why = $('baroWhy');

    function unavailable() {
      if (badge) badge.textContent = T('baro_off', 'unavailable');
      if (why) { why.hidden = false; why.textContent = T('baro_off_why', ''); }
      if (body) body.hidden = true;
      if (cal) cal.hidden = true;
      if (note) note.hidden = true;
    }

    var Ctor = G.AmbientPressureSensor;
    if (typeof Ctor !== 'function') { unavailable(); return; }

    var sensor;
    try {
      sensor = new Ctor({ frequency: 2 });
    } catch (e) { unavailable(); return; }

    sensor.addEventListener('reading', function () {
      var hpa = altKpaToHpa(sensor.pressure);
      if (hpa == null) return;
      state.baro.p = hpa;
      if (state.baro.p0 == null && state.last && state.last.ele != null) {
        var p0 = altRefPressure(hpa, state.last.ele);
        if (p0 != null) { state.baro.p0 = p0; state.baro.auto = true; }
      }
      renderBaro();
    });
    sensor.addEventListener('error', function () { unavailable(); });

    try { sensor.start(); } catch (e) { unavailable(); return; }

    state.baro.ok = true;
    state.baro.sensor = sensor;
    if (badge) badge.textContent = T('baro_on', 'connected');
    if (why) why.hidden = true;
    if (body) body.hidden = false;
    if (cal) cal.hidden = false;
    if (note) note.hidden = false;
    renderBaro();
  }

  function calibrate() {
    var input = $('calH');
    var msg = $('calMsg');
    var h = input ? parseFloat(input.value) : NaN;
    var p = state.baro.p;
    if (!isFinite(h) || p == null) {
      if (msg) { msg.hidden = false; msg.textContent = T('baro_cal_err', 'Enter a valid altitude'); }
      return;
    }
    var p0 = altRefPressure(p, state.unit === 'ft' ? altToMetres(h) : h);
    if (p0 == null) {
      if (msg) { msg.hidden = false; msg.textContent = T('baro_cal_err', 'Enter a valid altitude'); }
      return;
    }
    state.baro.p0 = p0;
    state.baro.auto = false;
    if (msg) { msg.hidden = false; msg.textContent = T('baro_cal_ok', 'Calibrated'); }
    renderBaro();
  }

  // ------------------------------------------------------------ 导出

  function download(name, text, mime) {
    try {
      var blob = new Blob([text], { type: mime });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = name;
      a.rel = 'noopener';
      document.body.appendChild(a);
      a.click();
      setTimeout(function () {
        try { URL.revokeObjectURL(url); } catch (e) { /* ignore */ }
        if (a.parentNode) a.parentNode.removeChild(a);
      }, 0);
      return true;
    } catch (e) { return false; }
  }

  // ------------------------------------------------------------ 事件绑定

  var btn = $('altBtn');
  if (btn) btn.addEventListener('click', function () {
    if (state.running) stop(false);
    else start();
  });

  var unitBox = document.querySelector('.alt-units');
  if (unitBox) unitBox.addEventListener('click', function (e) {
    var b = e.target.closest('[data-unit]');
    if (!b) return;
    state.unit = b.getAttribute('data-unit') === 'ft' ? 'ft' : 'm';
    var all = unitBox.querySelectorAll('[data-unit]');
    for (var i = 0; i < all.length; i++) {
      all[i].classList.toggle('active', all[i] === b);
    }
    try { localStorage.setItem('altimeter:unit', state.unit); } catch (e2) { /* ignore */ }
    render();
  });
  if (state.unit === 'ft' && unitBox) {
    var allU = unitBox.querySelectorAll('[data-unit]');
    for (var ui = 0; ui < allU.length; ui++) {
      allU[ui].classList.toggle('active', allU[ui].getAttribute('data-unit') === 'ft');
    }
  }

  var geoInput = $('geoN');
  if (geoInput) geoInput.addEventListener('input', render);

  var calBtn = $('calBtn');
  if (calBtn) calBtn.addEventListener('click', calibrate);

  var gpxBtn = $('expGpx');
  if (gpxBtn) gpxBtn.addEventListener('click', function () {
    if (!state.track.length) { toast(T('msg_empty', 'No track data yet')); return; }
    var ok = download(altFileName('altitude', state.track[0].t, 'gpx'),
      altBuildGpx(state.track, 'Altitude track'), 'application/gpx+xml');
    if (ok) toast(T('msg_gpx', 'GPX exported'));
  });

  var csvBtn = $('expCsv');
  if (csvBtn) csvBtn.addEventListener('click', function () {
    if (!state.track.length) { toast(T('msg_empty', 'No track data yet')); return; }
    var ok = download(altFileName('altitude', state.track[0].t, 'csv'),
      altBuildCsv(state.track), 'text/csv;charset=utf-8');
    if (ok) toast(T('msg_csv', 'CSV exported'));
  });

  var clearBtn = $('expClear');
  if (clearBtn) clearBtn.addEventListener('click', function () {
    state.track = [];
    render();
    toast(T('msg_cleared', 'Cleared'));
  });

  // 主题切换后 canvas 上的颜色要跟着变（颜色是读取 CSS 变量画上去的）
  if (G.MutationObserver) {
    try {
      new MutationObserver(function () { drawChart(); })
        .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    } catch (e) { /* ignore */ }
  }

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) relWake();
    else if (state.running) reqWake();
  });

  G.addEventListener('resize', function () { drawChart(); });

  initBaro();
  render();
}

G.altPressureToHeight = altPressureToHeight;
G.altRefPressure = altRefPressure;
G.altMetresPerHpa = altMetresPerHpa;
G.altKpaToHpa = altKpaToHpa;
G.altToFeet = altToFeet;
G.altToMetres = altToMetres;
G.altDecimals = altDecimals;
G.altRound = altRound;
G.altTrackStats = altTrackStats;
G.altBuildGpx = altBuildGpx;
G.altBuildCsv = altBuildCsv;
G.altFileName = altFileName;

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAltimeter);
  } else {
    initAltimeter();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    altPressureToHeight: altPressureToHeight,
    altRefPressure: altRefPressure,
    altMetresPerHpa: altMetresPerHpa,
    altKpaToHpa: altKpaToHpa,
    altToFeet: altToFeet,
    altToMetres: altToMetres,
    altDecimals: altDecimals,
    altRound: altRound,
    altTrackStats: altTrackStats,
    altBuildGpx: altBuildGpx,
    altBuildCsv: altBuildCsv,
    altFileName: altFileName
  };
}
