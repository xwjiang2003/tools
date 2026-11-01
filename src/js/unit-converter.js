// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// unit-converter.js — 单位换算（长度/面积/体积/质量/温度/数据量/速度/时间/压力/能量/功率/角度）
// 单位一律用国际通用符号（m / kg / MiB…），符号本身不需要翻译，页面只翻译「类别名」，
// 因此这段代码里没有可被误翻的中文，也不依赖任何线上接口。

// 每类的基准单位与倍率（value × factor = 基准值）
var UNIT_CATS = {
  length: { base: 'm', units: [
    ['mm', 0.001], ['cm', 0.01], ['m', 1], ['km', 1000],
    ['in', 0.0254], ['ft', 0.3048], ['yd', 0.9144], ['mi', 1609.344], ['nmi', 1852]] },
  area: { base: 'm²', units: [
    ['mm²', 0.000001], ['cm²', 0.0001], ['m²', 1], ['km²', 1000000], ['ha', 10000],
    ['in²', 0.00064516], ['ft²', 0.09290304], ['yd²', 0.83612736], ['acre', 4046.8564224]] },
  volume: { base: 'L', units: [
    ['mL', 0.001], ['L', 1], ['m³', 1000], ['cm³', 0.001],
    ['fl oz (US)', 0.0295735295625], ['cup (US)', 0.2365882365],
    ['pt (US)', 0.473176473], ['qt (US)', 0.946352946], ['gal (US)', 3.785411784],
    ['gal (UK)', 4.54609]] },
  mass: { base: 'kg', units: [
    ['mg', 0.000001], ['g', 0.001], ['kg', 1], ['t', 1000],
    ['oz', 0.028349523125], ['lb', 0.45359237], ['st', 6.35029318], ['ton (US)', 907.18474]] },
  temperature: { base: '°C', special: true, units: [
    ['°C', 1], ['°F', 1], ['K', 1], ['°R', 1]] },
  data: { base: 'B', units: [
    ['bit', 0.125], ['B', 1], ['KB', 1000], ['MB', 1e6], ['GB', 1e9], ['TB', 1e12], ['PB', 1e15],
    ['KiB', 1024], ['MiB', 1048576], ['GiB', 1073741824], ['TiB', 1099511627776]] },
  speed: { base: 'm/s', units: [
    ['mm/s', 0.001], ['m/s', 1], ['km/h', 1 / 3.6], ['mph', 0.44704],
    ['kn', 0.514444444], ['ft/s', 0.3048], ['Mach', 340.29]] },
  time: { base: 's', units: [
    ['ns', 1e-9], ['µs', 1e-6], ['ms', 0.001], ['s', 1], ['min', 60], ['h', 3600],
    ['d', 86400], ['wk', 604800], ['yr (365d)', 31536000]] },
  pressure: { base: 'Pa', units: [
    ['Pa', 1], ['hPa', 100], ['kPa', 1000], ['MPa', 1e6], ['bar', 1e5],
    ['mbar', 100], ['atm', 101325], ['psi', 6894.757293168], ['mmHg', 133.322387415]] },
  energy: { base: 'J', units: [
    ['J', 1], ['kJ', 1000], ['cal', 4.184], ['kcal', 4184],
    ['Wh', 3600], ['kWh', 3.6e6], ['BTU', 1055.05585262], ['eV', 1.602176634e-19]] },
  power: { base: 'W', units: [
    ['mW', 0.001], ['W', 1], ['kW', 1000], ['MW', 1e6],
    ['hp (mech)', 745.6998715823], ['PS', 735.49875], ['BTU/h', 0.2930710702]] },
  angle: { base: '°', units: [
    ['°', 1], ['rad', 57.29577951308232], ['grad', 0.9], ['turn', 360],
    ['arcmin', 1 / 60], ['arcsec', 1 / 3600]] }
};

// 温度不能靠倍率（有零点偏移），单独走公式，基准用 °C
function unitTempToC(v, unit) {
  if (unit === '°C') return v;
  if (unit === '°F') return (v - 32) * 5 / 9;
  if (unit === 'K') return v - 273.15;
  if (unit === '°R') return (v - 491.67) * 5 / 9;
  return NaN;
}
function unitTempFromC(c, unit) {
  if (unit === '°C') return c;
  if (unit === '°F') return c * 9 / 5 + 32;
  if (unit === 'K') return c + 273.15;
  if (unit === '°R') return (c + 273.15) * 9 / 5;
  return NaN;
}

// 单个换算
function unitConvert(cat, from, to, value) {
  var c = UNIT_CATS[cat];
  if (!c) return NaN;
  var v = Number(value);
  if (!isFinite(v)) return NaN;
  if (c.special) return unitTempFromC(unitTempToC(v, from), to);
  var fFrom = null, fTo = null;
  for (var i = 0; i < c.units.length; i++) {
    if (c.units[i][0] === from) fFrom = c.units[i][1];
    if (c.units[i][0] === to) fTo = c.units[i][1];
  }
  if (fFrom == null || fTo == null) return NaN;
  return v * fFrom / fTo;
}

// 一次性换算到该类所有单位，返回 [[unit, value], ...]
function unitAll(cat, from, value) {
  var c = UNIT_CATS[cat];
  if (!c) return [];
  var out = [];
  for (var i = 0; i < c.units.length; i++) {
    out.push([c.units[i][0], unitConvert(cat, from, c.units[i][0], value)]);
  }
  return out;
}

// 结果格式化：最多 10 位有效数字，去掉浮点尾巴，整数部分加千分位，极端量级用科学计数法
function unitFmt(n) {
  if (n == null || !isFinite(n)) return '—';
  if (n === 0) return '0';
  var a = Math.abs(n);
  if (a >= 1e15 || a < 1e-9) {
    return n.toExponential(6).replace(/\.?0+e/, 'e');
  }
  var s = String(parseFloat(n.toPrecision(10)));
  if (s.indexOf('e') >= 0) return s;
  var neg = s.charAt(0) === '-';
  if (neg) s = s.slice(1);
  var parts = s.split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return (neg ? '-' : '') + parts.join('.');
}

// ---------------------------------------------------------------- 页面
function unitTL() { return G.__TL__ || {}; }
var unitCat = 'length', unitFrom = 'm', unitTo = 'km';

function unitFillUnits() {
  var c = UNIT_CATS[unitCat];
  var f = document.getElementById('unitFrom'), t = document.getElementById('unitTo');
  if (!f || !t) return;
  var opts = '';
  for (var i = 0; i < c.units.length; i++) {
    opts += '<option value="' + escAttr(c.units[i][0]) + '">' + escHtml(c.units[i][0]) + '</option>';
  }
  f.innerHTML = opts; t.innerHTML = opts;
  f.value = unitFrom = c.units[0][0];
  t.value = unitTo = c.units[Math.min(1, c.units.length - 1)][0];
}

function unitRender() {
  var L = unitTL();
  var box = document.getElementById('unitResult');
  if (!box) return;
  var v = getVal('unitValue');
  var num = Number(String(v).replace(/[\s,]/g, ''));
  if (!String(v).trim() || !isFinite(num)) {
    box.innerHTML = '<div class="tl-hint">' + escHtml(L.hint || '') + '</div>';
    return;
  }
  var res = unitConvert(unitCat, unitFrom, unitTo, num);
  var html = '<div class="unit-big">' + unitFmt(res) + ' <span class="unit-big-u">' +
    escHtml(unitTo) + '</span></div>' +
    '<div class="unit-eq">' + unitFmt(num) + ' ' + escHtml(unitFrom) + ' = ' +
    unitFmt(res) + ' ' + escHtml(unitTo) + '</div>';

  var all = unitAll(unitCat, unitFrom, num);
  html += '<table class="dt-table" style="margin-top:14px"><thead><tr><th>' +
    escHtml(L.c_unit) + '</th><th>' + escHtml(L.c_value) + '</th></tr></thead><tbody>';
  for (var i = 0; i < all.length; i++) {
    var cls = all[i][0] === unitFrom ? ' class="dt-now"' : '';
    html += '<tr' + cls + '><td>' + escHtml(all[i][0]) + '</td><td>' +
      unitFmt(all[i][1]) + '</td></tr>';
  }
  html += '</tbody></table>';
  box.innerHTML = html;
}

G.unitRender = unitRender;
G.unitSetCat = function (cat) {
  unitCat = cat;
  unitFillUnits();
  unitRender();
};

function initUnit() {
  var box = document.getElementById('unitResult');
  if (!box) return;
  unitFillUnits();
  var v = document.getElementById('unitValue');
  if (!v.value) v.value = '1';
  unitRender();
  v.addEventListener('input', unitRender);
  document.getElementById('unitFrom').addEventListener('change', function (e) {
    unitFrom = e.target.value; unitRender();
  });
  document.getElementById('unitTo').addEventListener('change', function (e) {
    unitTo = e.target.value; unitRender();
  });

  var cats = document.getElementById('unitCats');
  if (cats) {
    cats.addEventListener('click', function (e) {
      var b = e.target.closest('[data-cat]');
      if (!b) return;
      Array.prototype.forEach.call(cats.querySelectorAll('[data-cat]'), function (x) {
        x.classList.toggle('active', x === b);
      });
      unitCat = b.getAttribute('data-cat');
      unitFillUnits();
      unitRender();
    });
  }
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUnit);
  } else {
    initUnit();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { UNIT_CATS: UNIT_CATS, unitConvert: unitConvert, unitAll: unitAll,
                     unitFmt: unitFmt, unitTempToC: unitTempToC, unitTempFromC: unitTempFromC };
}
