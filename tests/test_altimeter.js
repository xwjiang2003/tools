// 单测：altimeter 的纯函数（不依赖 DOM / 传感器）
// 覆盖：标准大气换算向量、往返一致性、单位换算、精度小数位、轨迹统计（含抖动过滤）、
//       GPX / CSV 结构与转义、文件名、以及各种无效输入必须返回 null 而不是 NaN。
// 运行：node tests/test_altimeter.js
const assert = require('assert');
const path = require('path');
const A = require(path.join(__dirname, '..', 'src', 'js', 'altimeter.js'));

let pass = 0;
const fails = [];
function eq(actual, expected, msg) {
    try { assert.deepStrictEqual(actual, expected); pass++; }
    catch (e) {
        fails.push(msg + '\n    期望 ' + JSON.stringify(expected) + '\n    实际 ' + JSON.stringify(actual));
    }
}
function ok(cond, msg) {
    if (cond) pass++;
    else fails.push(msg);
}
function near(actual, expected, tol, msg) {
    const d = Math.abs(actual - expected);
    if (isFinite(d) && d <= tol) { pass++; return; }
    fails.push(msg + '\n    期望 ' + expected + ' ±' + tol + '\n    实际 ' + actual);
}

// ============================================================ 气压 → 高度
// 国际标准大气（ISA）参考值：1013.25 hPa = 0 m、900 hPa ≈ 988 m、500 hPa ≈ 5574 m
near(A.altPressureToHeight(1013.25, 1013.25), 0, 1e-9, 'alt: 基准气压处高度为 0');
near(A.altPressureToHeight(900, 1013.25), 988.3, 0.5, 'alt: 900 hPa ≈ 988 m（ISA）');
near(A.altPressureToHeight(500, 1013.25), 5574.0, 2, 'alt: 500 hPa ≈ 5574 m（ISA）');
near(A.altPressureToHeight(700, 1013.25), 3012.0, 8, 'alt: 700 hPa ≈ 3012 m（ISA）');
ok(A.altPressureToHeight(900, 1013.25) > 0, 'alt: 气压降低则高度为正');
ok(A.altPressureToHeight(1020, 1013.25) < 0, 'alt: 气压高于基准高度为负（低于海平面）');

// 无效输入必须是 null，不能是 NaN
eq(A.altPressureToHeight(0, 1013.25), null, 'alt: 气压 0 → null');
eq(A.altPressureToHeight(-5, 1013.25), null, 'alt: 负气压 → null');
eq(A.altPressureToHeight(900, 0), null, 'alt: 基准 0 → null');
eq(A.altPressureToHeight('abc', 1013.25), null, 'alt: 非数字 → null');
eq(A.altPressureToHeight(null, null), null, 'alt: null → null');
eq(A.altPressureToHeight('900', '1013.25'), A.altPressureToHeight(900, 1013.25),
   'alt: 数字字符串按数字处理');

// ============================================================ 反推基准气压
near(A.altRefPressure(900, A.altPressureToHeight(900, 1013.25)), 1013.25, 0.05,
     'alt: 反推 P0 应回到 1013.25');
near(A.altRefPressure(900, 988.3), 1013.2, 1, 'alt: 900 hPa / 988.3 m → P0 ≈ 1013 hPa');
eq(A.altRefPressure(900, 44330), null, 'alt: 高度等于 44330 → 分母为 0 → null');
eq(A.altRefPressure(900, 50000), null, 'alt: 高度超过 44330 → null');
eq(A.altRefPressure(0, 100), null, 'alt: 气压 0 → null');

// 正反解互为逆运算：由 h 反推 P0，再用该 P0 算回 h（误差应在亚毫米级）
[860, 920, 1000].forEach(function (p) {
    const p0 = 1013.25;
    const h = A.altPressureToHeight(p, p0);
    near(A.altPressureToHeight(p, A.altRefPressure(p, h)), h, 1e-6,
         'alt: 正反解一致 p=' + p);
});

// ============================================================ 单位
near(A.altKpaToHpa(101.325), 1013.25, 1e-9, 'unit: 101.325 kPa = 1013.25 hPa');
eq(A.altKpaToHpa(null), null, 'unit: kPa null → null');
near(A.altToFeet(1000), 3280.8399, 1e-3, 'unit: 1000 m = 3280.84 ft');
near(A.altToMetres(3280.8399), 1000, 1e-3, 'unit: 3280.84 ft = 1000 m');
near(A.altToMetres(5280), 1609.344, 1e-3, 'unit: 5280 ft = 1609.344 m（1 英里）');
eq(A.altToFeet('x'), null, 'unit: 非数字 → null');

// 1 hPa ≈ 8.3 m（海平面附近），这是页面里那句说明的依据
near(A.altMetresPerHpa(1013.25, 1013.25), 8.3, 0.2, 'unit: 海平面 1 hPa ≈ 8.3 m');
ok(A.altMetresPerHpa(500, 1013.25) > 14, 'unit: 500 hPa 附近 1 hPa > 14 m');
near(A.altMetresPerHpa(300, 1013.25), 22.34, 0.05, 'unit: 300 hPa 附近 1 hPa ≈ 22.3 m');
eq(A.altMetresPerHpa(0, 1013.25), null, 'unit: 无效气压 → null');

// ============================================================ 小数位
eq(A.altDecimals(null), 0, 'acc: 无精度只给整数');
eq(A.altDecimals(undefined), 0, 'acc: undefined 只给整数');
eq(A.altDecimals(30), 0, 'acc: ±30 m → 0 位小数');
eq(A.altDecimals(1), 0, 'acc: ±1 m → 0 位小数');
eq(A.altDecimals(0.5), 1, 'acc: ±0.5 m → 1 位小数');
eq(A.altDecimals(0.1), 1, 'acc: ±0.1 m → 1 位小数');
eq(A.altDecimals('abc'), 0, 'acc: 非数字 → 0 位');

eq(A.altRound(1286.44, 0), 1286, 'round: 0 位');
eq(A.altRound(1286.45, 1), 1286.5, 'round: 1 位');
eq(A.altRound(-0.04, 1), 0, 'round: 负小数归零');
eq(A.altRound(null, 0), null, 'round: null → null');

// ============================================================ 轨迹统计
const track = [
    { t: 0, ele: 100 },
    { t: 1000, ele: 103 },
    { t: 2000, ele: 99 },
    { t: 3000, ele: 105 }
];
const s = A.altTrackStats(track, { threshold: 2, window: 600000 });
eq(s.asc, 9, 'stats: 爬升 3 + 6 = 9');
eq(s.desc, 4, 'stats: 下降 4');
eq(s.n, 4, 'stats: 4 个有效点');
near(s.vSpeed, 5 / (3 / 60), 0.01, 'stats: 垂直速度 = 5 m / 3 s');

// 阈值过滤：±1 m 来回抖动不该计入爬升
const jitter = [
    { t: 0, ele: 100 }, { t: 1000, ele: 101 }, { t: 2000, ele: 100.4 },
    { t: 3000, ele: 100.9 }, { t: 4000, ele: 100 }
];
const sj = A.altTrackStats(jitter, { threshold: 2 });
eq(sj.asc, 0, 'stats: 抖动不计爬升');
eq(sj.desc, 0, 'stats: 抖动不计下降');

// 无 ele 的点被跳过，且不打断累计
const mixed = [
    { t: 0, ele: 100 }, { t: 1000, ele: null }, { t: 2000, ele: 104 }, { t: 3000, ele: 104 }
];
const sm = A.altTrackStats(mixed, { threshold: 2, window: 600000 });
eq(sm.n, 3, 'stats: 跳过无海拔点');
eq(sm.asc, 4, 'stats: 跳过无海拔点后仍累计爬升');

// 垂直速度窗口：60 s 外的高差不算进速度
const longTrack = [];
for (let i = 0; i <= 120; i++) longTrack.push({ t: i * 1000, ele: 100 + i * 0.5 });
const sl = A.altTrackStats(longTrack, { threshold: 2, window: 60000 });
near(sl.vSpeed, 30, 1.5, 'stats: 60 s 窗口内 30 m 爬升 → 30 m/min');

// 空轨迹 / 单点
const empty = A.altTrackStats([], {});
eq(empty.asc, 0, 'stats: 空数组 asc=0');
eq(empty.desc, 0, 'stats: 空数组 desc=0');
eq(empty.vSpeed, 0, 'stats: 空数组 vSpeed=0');
eq(empty.n, 0, 'stats: 空数组 n=0');
const one = A.altTrackStats([{ t: 0, ele: 100 }], {});
eq(one.vSpeed, 0, 'stats: 单点没有速度');
eq(A.altTrackStats(null, {}).n, 0, 'stats: null 安全');

// ============================================================ GPX
const fixTrack = [
    { t: Date.UTC(2026, 10, 6, 7, 30, 0), lat: 39.907441, lon: 116.391283, ele: 43.2, vacc: 12, hacc: 8 },
    { t: Date.UTC(2026, 10, 6, 7, 30, 5), lat: 39.907500, lon: 116.391300, ele: null, vacc: null, hacc: 9 }
];
const gpx = A.altBuildGpx(fixTrack, 'Test & <Track>');
ok(gpx.indexOf('<?xml version="1.0" encoding="UTF-8"?>') === 0, 'gpx: XML 声明在最前');
ok(gpx.indexOf('version="1.1"') > 0, 'gpx: 版本 1.1');
ok(gpx.indexOf('xmlns="http://www.topografix.com/GPX/1/1"') > 0, 'gpx: 命名空间');
ok(gpx.indexOf('<trkpt lat="39.907441" lon="116.391283">') > 0, 'gpx: 六位小数坐标');
ok(gpx.indexOf('<ele>43.2</ele>') > 0, 'gpx: ele 保留一位小数');
ok(gpx.indexOf('<time>2026-11-06T07:30:00.000Z</time>') > 0, 'gpx: ISO 时间');
eq((gpx.match(/<trkpt /g) || []).length, 2, 'gpx: 两个轨迹点都保留');
// 第二个点没有海拔：不写 <ele>，但位置要留下
ok(gpx.indexOf('39.907500') > 0 && gpx.split('<ele>').length === 2,
   'gpx: 无海拔的点不写 ele 但仍记录坐标');
ok(gpx.indexOf('Test &amp; &lt;Track&gt;') > 0, 'gpx: 名称转义');
ok(gpx.indexOf('</gpx>') === gpx.length - 7, 'gpx: 以换行结尾的闭合标签');
eq((A.altBuildGpx([], 'x').match(/<trkpt /g) || []).length, 0, 'gpx: 空轨迹仍产出合法骨架');
ok(A.altBuildGpx([{ lat: NaN, lon: 1, ele: 1 }], 'x').indexOf('<trkpt') < 0,
   'gpx: 无效坐标被跳过');

// ============================================================ CSV
const csv = A.altBuildCsv(fixTrack);
const lines = csv.trim().split('\n');
eq(lines[0], 'time_iso,lat,lon,ele_m,ele_acc_m,horiz_acc_m', 'csv: 表头固定英文');
eq(lines.length, 3, 'csv: 表头 + 2 行数据');
eq(lines[1], '2026-11-06T07:30:00.000Z,39.907441,116.391283,43.2,12.0,8.0', 'csv: 首行内容');
eq(lines[2], '2026-11-06T07:30:05.000Z,39.907500,116.391300,,,9.0', 'csv: 缺失值留空列');
ok(csv.endsWith('\n'), 'csv: 以换行结尾');
eq(A.altBuildCsv([]), 'time_iso,lat,lon,ele_m,ele_acc_m,horiz_acc_m\n', 'csv: 空轨迹只有表头');

// ============================================================ 文件名
const fn = A.altFileName('altitude', Date.UTC(2026, 10, 6, 15, 13, 48), 'gpx');
eq(fn, 'altitude-2026-11-06_15-13-48.gpx', 'file: ISO 时间去冒号，Windows 可用');
ok(!/[:*?"<>|]/.test(fn), 'file: 不含 Windows 非法字符');

// ============================================================ 汇总
const total = pass + fails.length;
console.log('\n' + pass + '/' + total + ' 通过');
if (fails.length) {
    console.log('\n失败 ' + fails.length + ' 项：');
    fails.forEach((f, i) => console.log('  ' + (i + 1) + '. ' + f));
    process.exit(1);
}
console.log('全部通过');
