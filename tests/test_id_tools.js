// 单测：src/js/id-tools.js 的纯函数（不依赖 DOM）
const assert = require('assert');
const path = require('path');
const I = require(path.join(__dirname, '..', 'src', 'js', 'id-tools.js'));

let pass = 0, fail = 0;
function eq(actual, expected, msg) {
    try { assert.deepStrictEqual(actual, expected); pass++; }
    catch (e) { fail++; console.error('✗ ' + msg + '\n   期望 ' + JSON.stringify(expected) + '\n   实际 ' + JSON.stringify(actual)); }
}
function ok(cond, msg) { try { assert.ok(cond); pass++; } catch (e) { fail++; console.error('✗ ' + msg); } }
function approx(a, b, delta, msg) { ok(Math.abs(a - b) <= delta, msg + ' (' + a + ' vs ' + b + ')'); }

// ============================================================ UUID
// 格式校验
ok(I.uuidValidate('123e4567-e89b-12d3-a456-426614174000'), 'uuid 合法(带连字符)');
ok(I.uuidValidate('123E4567E89B12D3A456426614174000'), 'uuid 合法(大写无连字符)');
ok(!I.uuidValidate('123e4567-e89b-12d3-a456-42661417400'), 'uuid 长度不足');
ok(!I.uuidValidate('123e4567-e89b-12d3-a456-42661417400g'), 'uuid 含非 hex');
ok(!I.uuidValidate('not-a-uuid'), 'uuid 明显非法');

// 版本 / 变体识别
eq(I.uuidGetVersion('123e4567-e89b-12d3-a456-426614174000'), 1, 'uuid v1 版本');
eq(I.uuidGetVersion('123e4567-e89b-42d3-a456-426614174000'), 4, 'uuid v4 版本');
eq(I.uuidGetVariant('123e4567-e89b-42d3-a456-426614174000'), 'RFC4122', 'uuid v4 变体');

// 解析
let p1 = I.uuidParse('123e4567-e89b-12d3-a456-426614174000');
ok(p1.valid && p1.version === 1 && p1.variant === 'RFC4122', 'uuid v1 解析');
eq(p1.node, '426614174000', 'uuid v1 节点(48bit)');
ok(typeof p1.timestampMs === 'number' && p1.timestampMs > 0, 'uuid v1 时间戳为正当数字');
eq(I.uuidParse('garbage').valid, false, 'uuid 解析非法返回 invalid');
// v1 时间戳向量（RFC 4122 示例 UUID，应落在 1995–2000）
let p1b = I.uuidParse('f81d4fae-7dec-11d0-a765-00a0c91e6bf6');
ok(p1b.valid && p1b.version === 1, 'uuid RFC 示例 v1 解析');
ok(['1995', '1996', '1997', '1998', '1999', '2000'].indexOf(p1b.date.substr(0, 4)) >= 0, 'uuid RFC 示例 v1 年份≈1996–2000 (' + p1b.date + ')');
let p4 = I.uuidParse('123e4567-e89b-42d3-a456-426614174000');
eq(p4.version, 4, 'uuid v4 解析版本');
ok(!('timestampMs' in p4), 'uuid v4 无时间戳字段');

// 生成 v4
let g = I.uuidV4();
ok(I.uuidValidate(g), 'uuidV4 格式合法');
eq(I.uuidGetVersion(g), 4, 'uuidV4 版本=4');
eq(I.uuidGetVariant(g), 'RFC4122', 'uuidV4 变体=RFC4122');

// ============================================================ Snowflake
const TW = I.SF_PRESETS.twitter, DC = I.SF_PRESETS.discord;
// 已知向量（第三方核对）：1888944671579078978 -> 2025-02-10 13:34:39.256 UTC
let sf1 = I.sfDecode('1888944671579078978', TW);
ok(sf1.valid, 'snowflake twitter 向量合法');
eq(sf1.timestampMs, 1739194479256, 'snowflake twitter 向量时间戳');
ok(sf1.date.indexOf('2025-02-10') === 0, 'snowflake twitter 向量日期');
// Discord 预设：epoch 必须是公认的 1420070400000（2016-01-01）；用往返而非外部向量，避免来源误差
eq(I.SF_PRESETS.discord.epoch, 1420070400000, 'snowflake discord 纪元=1420070400000');
let dts = 1791849043547;
let denc = I.sfEncode(dts, 123, 456, DC);
ok(denc.valid, 'snowflake discord 编码合法');
eq(I.sfDecode(denc.id, DC).timestampMs, dts, 'snowflake discord 往返时间戳一致');

// 异常 / 边界
eq(I.sfDecode('abc', TW).valid, false, 'snowflake 非数字 invalid');
ok(I.sfDecode('1', TW).valid, 'snowflake id=1 合法(全 0 时间戳)');
eq(I.sfDecode('1'.repeat(25), TW).reason, 'overflow', 'snowflake 超 63 位 overflow');

// 编码往返
[1739194479256, 1791849043547, 1700000000000].forEach(function (ts) {
    let enc = I.sfEncode(ts, 5, 10, TW);
    ok(enc.valid, 'snowflake 编码 ' + ts + ' 合法');
    eq(I.sfDecode(enc.id, TW).timestampMs, ts, 'snowflake 往返时间戳一致 ' + ts);
});
// 编码边界
eq(I.sfEncode(100, 0, 0, TW).reason, 'time-before-epoch', 'snowflake 早于纪元');
eq(I.sfEncode(1288834974657 + Math.pow(2, 41), 0, 0, TW).reason, 'time-overflow', 'snowflake 时间超 41 位');
eq(I.sfEncode(2000000000000, 1024, 0, TW).reason, 'node-overflow', 'snowflake 节点超 10 位');
eq(I.sfEncode(2000000000000, 0, 4096, TW).reason, 'step-overflow', 'snowflake 序列超 12 位');

// ============================================================ TID (Twitter / X)
eq(I.tidToTime('1888944671579078978').timestampMs, 1739194479256, 'tid 向量时间戳');
let early = I.tidToTime('29700859247');
ok(early.valid && early.predates === true, 'tid 早于 Snowflake 边界 predates');
ok(I.tidToTime('29700859248').predates !== true, 'tid 边界+1 可解码');
eq(I.tidToTime('abc').valid, false, 'tid 非数字 invalid');
// 时间 → ID 往返
[1739194479256, 1700000000000].forEach(function (ts) {
    let r = I.timeToTid(ts);
    ok(r.valid, 'tid 编码 ' + ts + ' 合法');
    eq(I.tidToTime(r.id).timestampMs, ts, 'tid 往返时间戳一致 ' + ts);
});

// ============================================================ MongoDB ObjectId
ok(I.oidValidate('507f1f77bcf86cd799439011'), 'oid 合法');
ok(!I.oidValidate('507f1f77bcf86cd79943901'), 'oid 长度不足');
ok(!I.oidValidate('507f1f77bcf86cd79943901z'), 'oid 非 hex');
let o1 = I.oidDecode('507f1f77bcf86cd799439011');
ok(o1.valid, 'oid 解析合法');
eq(o1.machine, 'bcf86c', 'oid 机器标识');
eq(o1.pid, 'd799', 'oid 进程标识');
eq(o1.counter, '439011', 'oid 计数器');
ok(o1.timestampSec > 0 && o1.date.indexOf('20') === 0, 'oid 时间戳/日期');
eq(I.oidDecode('bad').valid, false, 'oid 解析非法返回 invalid');
let og = I.oidGenerate();
ok(I.oidValidate(og), 'oid 生成格式合法');

// ============================================================ Firebase Push ID
// 合法 / 非法 字符集
ok(I.fbValidate('M'.repeat(20)), 'fb 全合法字符 valid');
ok(!I.fbValidate('abc'), 'fb 长度不足 invalid');
ok(!I.fbValidate('M'.repeat(19) + '.'), 'fb 含非法字符 . invalid');
// 时间=0 时前 8 位应为全 '-'（PUSH_CHARS[0]='-'）
let fz = I.fbEncode(0);
ok(fz.valid && fz.id.substr(0, 8) === '--------', 'fb 时间0 前8位为 -');
eq(I.fbDecode('--------' + 'MZx0t0x0x0x0x'.substr(0, 12)).timestampMs, 0, 'fb 时间0 解码=0');
// 往返 + 向量
[0, 1739194479256, 1700000000000, 1600000000000].forEach(function (ts) {
    let r = I.fbEncode(ts);
    ok(r.valid && r.id.length === 20, 'fb 生成长度20 ' + ts);
    eq(I.fbDecode(r.id).timestampMs, ts, 'fb 往返时间戳一致 ' + ts);
});
eq(I.fbEncode(-1).valid, false, 'fb 负时间 invalid');
eq(I.fbEncode(Math.pow(64, 8)).valid, false, 'fb 时间越界 invalid');

// ============================================================ 汇总
console.log('\nID 工具单测：通过 ' + pass + '，失败 ' + fail);
if (fail > 0) process.exit(1);
