// 单测：src/js/datetime-tools.js 的纯函数（不依赖 DOM）
const assert = require('assert');
const path = require('path');
const D = require(path.join(__dirname, '..', 'src', 'js', 'datetime-tools.js'));

let pass = 0, fail = 0;
function eq(actual, expected, msg) {
  try { assert.deepStrictEqual(actual, expected); pass++; }
  catch (e) { fail++; console.error('✗ ' + msg + '\n   期望 ' + JSON.stringify(expected) + '\n   实际 ' + JSON.stringify(actual)); }
}
function ok(cond, msg) { try { assert.ok(cond); pass++; } catch (e) { fail++; console.error('✗ ' + msg); } }

// dtParseTimestamp：秒/毫秒自动识别
eq(D.dtParseTimestamp('1700000000'), { ok: true, value: 1700000000 }, 'ts 秒级');
eq(D.dtParseTimestamp('1700000000000').value, 1700000000, 'ts 毫秒级自动转秒');
eq(D.dtParseTimestamp(' 1700000000 '), { ok: true, value: 1700000000 }, 'ts 去空格');
eq(D.dtParseTimestamp('abc'), { ok: false, error: 'not_int' }, 'ts 非数字');
eq(D.dtParseTimestamp(''), { ok: false, error: 'empty' }, 'ts 空');
eq(D.dtParseTimestamp('-1700000000').value, -1700000000, 'ts 负数');

// dtZonedParts：固定时间戳在 UTC 下的分解
const p = D.dtZonedParts(1700000000, 'UTC');
eq([p.year, p.month, p.day, p.hour, p.minute, p.second],
   ['2023', '11', '14', '22', '13', '20'], 'UTC 分解 1700000000');
ok(D.dtZonedParts(NaN, 'UTC') === null, 'ts 非法返回 null');

// dtPartsToSeconds：与 Date.UTC 一致
eq(D.dtPartsToSeconds(2023, 11, 14, 22, 13, 20, 'UTC'), 1700000000, 'UTC 组秒一致');
// 本地时区组秒应为合理值（与 new Date 一致）
const localSec = D.dtPartsToSeconds(2023, 11, 14, 22, 13, 20, 'local');
const localRef = Math.floor(new Date(2023, 10, 14, 22, 13, 20).getTime() / 1000);
eq(localSec, localRef, '本地组秒一致');

// 上海时区：2023-11-15 06:13:20 UTC+8 = 2023-11-15 06:13:20? 验证相对 UTC
const sh = D.dtPartsToSeconds(2023, 11, 15, 6, 13, 20, 'Asia/Shanghai');
eq(sh, 1700000000, '上海时区组秒（东八区）');

// dtIsoWeek：已知值
// 2023-01-01 是周日 -> ISO 第 52 周(2022) ；2023-01-02 周一 -> 第1周
eq(D.dtIsoWeek(new Date(Date.UTC(2023, 0, 1))), { week: 52, year: 2022 }, 'ISO周 2023-01-01');
eq(D.dtIsoWeek(new Date(Date.UTC(2023, 0, 2))), { week: 1, year: 2023 }, 'ISO周 2023-01-02');
eq(D.dtIsoWeek(new Date(Date.UTC(2024, 11, 30))), { week: 1, year: 2025 }, 'ISO周 2024-12-30(跨年)');
eq(D.dtIsoWeek(new Date(Date.UTC(2021, 0, 1))), { week: 53, year: 2020 }, 'ISO周 2021-01-01(53周年)');

// dtDayOfYear
eq(D.dtDayOfYear(new Date(Date.UTC(2023, 0, 1))), 1, '年内第1天');
eq(D.dtDayOfYear(new Date(Date.UTC(2023, 11, 31))), 365, '年内第365天(平年)');
eq(D.dtDayOfYear(new Date(Date.UTC(2024, 11, 31))), 366, '年内第366天(闰年)');

// dtIsLeapYear
ok(D.dtIsLeapYear(2000) && D.dtIsLeapYear(2024) && !D.dtIsLeapYear(1900) && !D.dtIsLeapYear(2023), '闰年判断');

// dtParseIsoDuration / dtSecondsToIsoDuration
eq(D.dtParseIsoDuration('PT1H30M'), { ok: true, seconds: 5400 }, '解析 PT1H30M');
eq(D.dtParseIsoDuration('P1DT12H'), { ok: true, seconds: 129600 }, '解析 P1DT12H');
eq(D.dtParseIsoDuration('P1W'), { ok: true, seconds: 604800 }, '解析 P1W');
eq(D.dtParseIsoDuration(''), { ok: false, error: 'empty' }, '空时长');
eq(D.dtParseIsoDuration('1H'), { ok: false, error: 'bad_format' }, '坏时长格式');
ok(D.dtParseIsoDuration('P1Y2M3DT4H5M6S').ok, '解析完整时长');
eq(D.dtSecondsToIsoDuration(5400), 'PT1H30M', '秒->PT1H30M');
eq(D.dtSecondsToIsoDuration(0), 'PT0S', '0->PT0S');
eq(D.dtSecondsToIsoDuration(86400), 'P1D', '86400->P1D');
eq(D.dtSecondsToIsoDuration(-90), '-PT1M30S', '负-> -PT1M30S');
// 往返一致性：随机秒
let rng = 12345;
for (let i = 0; i < 200; i++) {
  rng = (rng * 1103515245 + 12345) & 0x7fffffff;
  const s = rng % 100000000;
  const back = D.dtParseIsoDuration(D.dtSecondsToIsoDuration(s));
  eq(back.seconds, s, 'ISO 往返 s=' + s);
}

// dtCountdown
const now = D.dtNowSeconds();
const c = D.dtCountdown(now + 90061);
eq([c.days, c.hours, c.mins, c.secs], [1, 1, 1, 1], '倒计时 90061s');
ok(D.dtCountdown(now - 10).past === true, '过去时间 past=true');

// dtDiffSeconds
const df = D.dtDiffSeconds(now, now + 90061);
eq([df.days, df.hours, df.mins, df.secs], [1, 1, 1, 1], '差值 90061s');

// dtAddDate
eq(D.dtAddDate({ y: 2024, m: 2, d: 28 }, { days: 1 }), { y: 2024, m: 2, d: 29 }, '闰年 0228+1=0229');
eq(D.dtAddDate({ y: 2023, m: 2, d: 28 }, { days: 1 }), { y: 2023, m: 3, d: 1 }, '平年 0228+1=0301');
eq(D.dtAddDate({ y: 2023, m: 1, d: 31 }, { months: 1 }), { y: 2023, m: 2, d: 28 }, '1月+1月=2月(平年)');
eq(D.dtAddDate({ y: 2023, m: 12, d: 31 }, { years: 1 }), { y: 2024, m: 12, d: 31 }, '跨年 +1年');

// dtBatchConvert
const rows1 = D.dtBatchConvert('1700000000\nabc\n2000000000', 'ts2date', 'UTC');
eq(rows1.length, 3, '批量 ts2date 3 行');
ok(rows1[0].ok && !rows1[1].ok && rows1[2].ok, '批量有效/无效判定');
const rows2 = D.dtBatchConvert('2023-11-14 22:13:20\n2023-11-15', 'date2ts', 'UTC');
eq(rows2[0].text, '1700000000', '批量 date2ts 首行');
eq(rows2[1].text, String(D.dtPartsToSeconds(2023, 11, 15, 0, 0, 0, 'UTC')), '批量 date2ts 仅日期');

console.log('\n通过 ' + pass + ' 项，失败 ' + fail + ' 项');
process.exit(fail ? 1 : 0);
