// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// coordinate.js — 中国大陆地图坐标互转：WGS-84（GPS 原始）↔ GCJ-02（国测局/火星/高德腾讯）↔ BD-09（百度）
// 算法为业界通用的公开实现：WGS→GCJ 用克拉索夫斯基椭球偏移公式，GCJ→WGS 用迭代逼近反解。
// 境外坐标不做偏移（算法本身只在中国范围内成立）。

var COORD_PI = 3.1415926535897932384626;
var COORD_A = 6378245.0;                       // 椭球长半轴
var COORD_EE = 0.00669342162296594323;         // 第一偏心率平方
var COORD_X_PI = COORD_PI * 3000.0 / 180.0;

// 是否在偏移生效范围内（这就是「为什么国内地图不能直接用 GPS 坐标」的边界）
function coordOutOfChina(lng, lat) {
  return !(lng > 73.66 && lng < 135.05 && lat > 3.86 && lat < 53.55);
}

function coordTransformLat(x, y) {
  var ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
  ret += (20.0 * Math.sin(6.0 * x * COORD_PI) + 20.0 * Math.sin(2.0 * x * COORD_PI)) * 2.0 / 3.0;
  ret += (20.0 * Math.sin(y * COORD_PI) + 40.0 * Math.sin(y / 3.0 * COORD_PI)) * 2.0 / 3.0;
  ret += (160.0 * Math.sin(y / 12.0 * COORD_PI) + 320 * Math.sin(y * COORD_PI / 30.0)) * 2.0 / 3.0;
  return ret;
}

function coordTransformLng(x, y) {
  var ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
  ret += (20.0 * Math.sin(6.0 * x * COORD_PI) + 20.0 * Math.sin(2.0 * x * COORD_PI)) * 2.0 / 3.0;
  ret += (20.0 * Math.sin(x * COORD_PI) + 40.0 * Math.sin(x / 3.0 * COORD_PI)) * 2.0 / 3.0;
  ret += (150.0 * Math.sin(x / 12.0 * COORD_PI) + 300.0 * Math.sin(x / 30.0 * COORD_PI)) * 2.0 / 3.0;
  return ret;
}

function coordWgsToGcj(lng, lat) {
  if (coordOutOfChina(lng, lat)) return [lng, lat];
  var dLat = coordTransformLat(lng - 105.0, lat - 35.0);
  var dLng = coordTransformLng(lng - 105.0, lat - 35.0);
  var radLat = lat / 180.0 * COORD_PI;
  var magic = Math.sin(radLat);
  magic = 1 - COORD_EE * magic * magic;
  var sqrtMagic = Math.sqrt(magic);
  dLat = (dLat * 180.0) / ((COORD_A * (1 - COORD_EE)) / (magic * sqrtMagic) * COORD_PI);
  dLng = (dLng * 180.0) / (COORD_A / sqrtMagic * Math.cos(radLat) * COORD_PI);
  return [lng + dLng, lat + dLat];
}

// 正解没有闭式反函数，迭代逼近：每轮用当前估计值再正向偏移一次，把误差减掉。
// 10 轮足够收敛到 1e-9 度（约 0.1 毫米），实际 2–3 轮已到 1e-7。
function coordGcjToWgs(lng, lat) {
  if (coordOutOfChina(lng, lat)) return [lng, lat];
  var wLng = lng, wLat = lat;
  for (var i = 0; i < 10; i++) {
    var g = coordWgsToGcj(wLng, wLat);
    var dLng = g[0] - lng, dLat = g[1] - lat;
    wLng -= dLng; wLat -= dLat;
    if (Math.abs(dLng) < 1e-9 && Math.abs(dLat) < 1e-9) break;
  }
  return [wLng, wLat];
}

function coordGcjToBd(lng, lat) {
  var z = Math.sqrt(lng * lng + lat * lat) + 0.00002 * Math.sin(lat * COORD_X_PI);
  var theta = Math.atan2(lat, lng) + 0.000003 * Math.cos(lng * COORD_X_PI);
  return [z * Math.cos(theta) + 0.0065, z * Math.sin(theta) + 0.006];
}

function coordBdToGcj(lng, lat) {
  var x = lng - 0.0065, y = lat - 0.006;
  var z = Math.sqrt(x * x + y * y) - 0.00002 * Math.sin(y * COORD_X_PI);
  var theta = Math.atan2(y, x) - 0.000003 * Math.cos(x * COORD_X_PI);
  return [z * Math.cos(theta), z * Math.sin(theta)];
}

// 球面距离（haversine），用来量化「偏移了多少米」
function coordDistance(lng1, lat1, lng2, lat2) {
  var R = 6371008.8;
  var dLat = (lat2 - lat1) * COORD_PI / 180;
  var dLng = (lng2 - lng1) * COORD_PI / 180;
  var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * COORD_PI / 180) * Math.cos(lat2 * COORD_PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(a)));
}

// 主入口：给定经纬度与来源坐标系，一次算出三套坐标
function coordInfo(lng, lat, from) {
  var lngN = Number(lng), latN = Number(lat);
  if (!isFinite(lngN) || !isFinite(latN)) return { valid: false, reason: 'number' };
  if (Math.abs(lngN) > 180) return { valid: false, reason: 'lng' };
  if (Math.abs(latN) > 90) return { valid: false, reason: 'lat' };

  var gcj;
  if (from === 'gcj') gcj = [lngN, latN];
  else if (from === 'bd') gcj = coordBdToGcj(lngN, latN);
  else gcj = coordWgsToGcj(lngN, latN);       // 默认按 WGS-84 处理

  var wgs = coordGcjToWgs(gcj[0], gcj[1]);
  var bd = coordGcjToBd(gcj[0], gcj[1]);

  return {
    valid: true,
    from: from || 'wgs',
    wgs: wgs,
    gcj: gcj,
    bd: bd,
    outside: coordOutOfChina(lngN, latN),
    // 火星偏移量：从 WGS 到 GCJ 的直线距离，国内通常 300–800 米
    offsetWgsGcj: coordDistance(wgs[0], wgs[1], gcj[0], gcj[1]),
    offsetGcjBd: coordDistance(gcj[0], gcj[1], bd[0], bd[1])
  };
}

// ---------------------------------------------------------------- 页面
function coordTL() { return G.__TL__ || {}; }
var coordSource = 'wgs';

function coordFmt(n) { return Number(n).toFixed(6); }

function coordRender() {
  var L = coordTL();
  var box = document.getElementById('coordResult');
  if (!box) return;
  var lng = getVal('coordLng'), lat = getVal('coordLat');
  if (!String(lng).trim() || !String(lat).trim()) {
    box.innerHTML = '<div class="tl-hint">' + escHtml(L.hint || '') + '</div>';
    return;
  }
  var r = coordInfo(lng, lat, coordSource);
  if (!r.valid) {
    var msg = L['err_' + r.reason] || L.err_generic || '';
    box.innerHTML = '<div class="tl-err">' + escHtml(msg) + '</div>';
    return;
  }

  var rows = [
    ['WGS-84', r.wgs, L.sys_wgs],
    ['GCJ-02', r.gcj, L.sys_gcj],
    ['BD-09', r.bd, L.sys_bd]
  ];
  var html = '<table class="dt-table"><thead><tr><th>' + escHtml(L.c_sys) + '</th><th>' +
    escHtml(L.c_lng) + '</th><th>' + escHtml(L.c_lat) + '</th><th>' + escHtml(L.c_use) +
    '</th></tr></thead><tbody>';
  for (var i = 0; i < rows.length; i++) {
    html += '<tr><td>' + escHtml(rows[i][0]) + '</td><td>' + coordFmt(rows[i][1][0]) +
      '</td><td>' + coordFmt(rows[i][1][1]) + '</td><td class="tl-wrap">' +
      escHtml(rows[i][2] || '') + '</td></tr>';
  }
  html += '</tbody></table>';

  html += '<table class="dt-table" style="margin-top:12px"><tbody>';
  html += '<tr><th style="width:44%">' + escHtml(L.r_offset1) + '</th><td>' +
    r.offsetWgsGcj.toFixed(1) + ' m</td></tr>';
  html += '<tr><th>' + escHtml(L.r_offset2) + '</th><td>' + r.offsetGcjBd.toFixed(1) + ' m</td></tr>';
  html += '<tr><th>' + escHtml(L.r_scope) + '</th><td>' +
    escHtml(r.outside ? L.scope_out : L.scope_in) + '</td></tr>';
  html += '</tbody></table>';

  // 直接给出可在高德/百度里粘贴的字符串，省得用户自己拼
  html += '<div class="tl-copyline"><span style="font-size:12.5px;color:var(--text-secondary);min-width:96px">' +
    escHtml(L.c_amap) + '</span><code>' + coordFmt(r.gcj[0]) + ',' + coordFmt(r.gcj[1]) +
    '</code><button class="btn btn-sm" data-copy="amap" type="button">' + escHtml(L.copy) + '</button></div>';
  html += '<div class="tl-copyline"><span style="font-size:12.5px;color:var(--text-secondary);min-width:96px">' +
    escHtml(L.c_baidu) + '</span><code>' + coordFmt(r.bd[0]) + ',' + coordFmt(r.bd[1]) +
    '</code><button class="btn btn-sm" data-copy="baidu" type="button">' + escHtml(L.copy) + '</button></div>';
  box.innerHTML = html;
  box.setAttribute('data-amap', coordFmt(r.gcj[0]) + ',' + coordFmt(r.gcj[1]));
  box.setAttribute('data-baidu', coordFmt(r.bd[0]) + ',' + coordFmt(r.bd[1]));
}

G.coordRender = coordRender;
G.coordClear = function () {
  setVal('coordLng', ''); setVal('coordLat', ''); coordRender();
};
G.coordSample = function () {
  setVal('coordLng', '116.391283'); setVal('coordLat', '39.907441'); coordRender();
};

function initCoord() {
  var lng = document.getElementById('coordLng');
  if (!lng) return;
  if (!lng.value) { lng.value = '116.391283'; document.getElementById('coordLat').value = '39.907441'; }
  coordRender();
  lng.addEventListener('input', coordRender);
  document.getElementById('coordLat').addEventListener('input', coordRender);

  var chips = document.getElementById('coordSys');
  if (chips) {
    chips.addEventListener('click', function (e) {
      var b = e.target.closest('[data-sys]');
      if (!b) return;
      coordSource = b.getAttribute('data-sys');
      Array.prototype.forEach.call(chips.querySelectorAll('[data-sys]'), function (x) {
        x.classList.toggle('active', x === b);
      });
      coordRender();
    });
  }

  var box = document.getElementById('coordResult');
  if (box) {
    box.addEventListener('click', function (e) {
      var b = e.target.closest('[data-copy]');
      if (!b) return;
      var v = box.getAttribute(b.getAttribute('data-copy') === 'amap' ? 'data-amap' : 'data-baidu');
      if (navigator.clipboard) {
        navigator.clipboard.writeText(v).then(function () {
          toast(coordTL().copied || 'OK');
        }, function () {
          toast(coordTL().copy_fail || 'Copy failed', 'error');
        });
      }
    });
  }
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCoord);
  } else {
    initCoord();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    coordOutOfChina: coordOutOfChina, coordWgsToGcj: coordWgsToGcj, coordGcjToWgs: coordGcjToWgs,
    coordGcjToBd: coordGcjToBd, coordBdToGcj: coordBdToGcj, coordDistance: coordDistance,
    coordInfo: coordInfo
  };
}
