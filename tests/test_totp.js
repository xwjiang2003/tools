// 单测：TOTP 纯函数（不依赖 DOM / Web Crypto）
// 关键：用 Node 的 crypto 算出真实 HMAC，再喂给 totpHotp，直接对 RFC 6238 附录 B
// 的官方测试向量 —— 这样验证的是整套动态截断实现，而不是「自己算的自己验」。
// 运行：node tests/test_totp.js
const assert = require('assert');
const nodeCrypto = require('crypto');
const path = require('path');
const T = require(path.join(__dirname, '..', 'src', 'js', 'totp.js'));

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

// ---------------------------------------------------------------- 参数清洗
eq(T.totpDigits('6'), 6, 'digits: 6');
eq(T.totpDigits('8'), 8, 'digits: 8');
eq(T.totpDigits('5'), 6, 'digits: 小于 6 回落默认');
eq(T.totpDigits('9'), 6, 'digits: 大于 8 回落默认');
eq(T.totpDigits('abc'), 6, 'digits: 非数字回落默认');
eq(T.totpDigits(null), 6, 'digits: null 回落默认');

eq(T.totpPeriod('30'), 30, 'period: 30');
eq(T.totpPeriod('60'), 60, 'period: 60');
eq(T.totpPeriod('0'), 30, 'period: 0 回落默认');
eq(T.totpPeriod('-5'), 30, 'period: 负数回落默认');
eq(T.totpPeriod('999'), 30, 'period: 超上限回落默认');

eq(T.totpAlgo('SHA1'), 'SHA-1', 'algo: SHA1');
eq(T.totpAlgo('sha-1'), 'SHA-1', 'algo: 小写带横线');
eq(T.totpAlgo('SHA256'), 'SHA-256', 'algo: SHA256');
eq(T.totpAlgo('sha512'), 'SHA-512', 'algo: 小写 SHA512');
eq(T.totpAlgo('md5'), 'SHA-1', 'algo: 未知算法回落 SHA-1');
eq(T.totpAlgo(null), 'SHA-1', 'algo: null 回落 SHA-1');

// ---------------------------------------------------------------- Base32
eq(T.totpBase32Clean('jbsw y3dp-ebfg'), 'JBSWY3DPEBFG', 'base32: 去空格与连字符并大写');
eq(T.totpBase32Clean('JBSWY3DP===='), 'JBSWY3DP', 'base32: 去掉填充等号');
eq(T.totpBase32Clean(null), '', 'base32: null → 空串');

// RFC 4648 测试向量：'12345678901234567890' 的 Base32
const b32 = T.totpBase32Decode('GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
ok(b32.ok, 'base32: 合法串解码成功');
eq(Buffer.from(b32.bytes).toString('ascii'), '12345678901234567890', 'base32: 与 RFC 4648 向量一致');
eq(b32.bytes.length, 20, 'base32: 20 字节');

// 小写 + 空格分组也要能解（用户粘贴的常态）
const b32b = T.totpBase32Decode('gezd gnbv gy3t qojq gezd gnbv gy3t qojq');
eq(Buffer.from(b32b.bytes).toString('ascii'), '12345678901234567890', 'base32: 小写分组形式等价');

// 非法字符：0、1、8、9 不在 Base32 字母表里 —— 这是最常见的粘贴错误
for (const bad of ['0', '1', '8', '9', '@', '!']) {
    const r = T.totpBase32Decode('JBSW' + bad + 'Y3DP');
    ok(!r.ok, 'base32: 非法字符 ' + bad + ' 被拒绝');
    eq(r.bad, bad, 'base32: 报出第一个非法字符 ' + bad);
}
ok(!T.totpBase32Decode('').ok, 'base32: 空串不通过');
ok(T.totpBase32Decode('').empty === true, 'base32: 空串标记 empty');
ok(!T.totpBase32Decode('   ').ok, 'base32: 纯空白不通过');
// 5 位以下解不出整字节，必须判失败而不是给一个空密钥
ok(!T.totpBase32Decode('A').ok, 'base32: 单字符解不出字节');

// ---------------------------------------------------------------- 计数器
eq(T.totpCounter(0, 30), 0, 'counter: t=0');
eq(T.totpCounter(59000, 30), 1, 'counter: t=59s');
eq(T.totpCounter(60000, 30), 2, 'counter: t=60s 进入下一格');
eq(T.totpCounter(30000, 60), 0, 'counter: 周期 60 时 t=30s 仍在第 0 格');
eq(T.totpCounter(60000, 60), 1, 'counter: 周期 60 时 t=60s 进入第 1 格');

eq(T.totpRemaining(0, 30), 30, 'remain: 刚跨步时是整周期');
eq(T.totpRemaining(1000, 30), 29, 'remain: 过 1 秒');
eq(T.totpRemaining(29000, 30), 1, 'remain: 最后一秒');
eq(T.totpRemaining(30000, 30), 30, 'remain: 跨步后回到整周期');
eq(T.totpRemaining(59000, 60), 1, 'remain: 周期 60 的最后一秒');
ok(T.totpRemaining(0, 30) > 0, 'remain: 永不返回 0');

// 计数器字节：8 字节大端
eq(Array.from(T.totpCounterBytes(0)), [0, 0, 0, 0, 0, 0, 0, 0], 'counterBytes: 0');
eq(Array.from(T.totpCounterBytes(1)), [0, 0, 0, 0, 0, 0, 0, 1], 'counterBytes: 1');
eq(Array.from(T.totpCounterBytes(256)), [0, 0, 0, 0, 0, 0, 1, 0], 'counterBytes: 256 进位');
eq(Array.from(T.totpCounterBytes(4294967296)),
    [0, 0, 0, 1, 0, 0, 0, 0], 'counterBytes: 2^32 进入高 4 字节');
eq(T.totpCounterBytes(4294967296).length, 8, 'counterBytes: 固定 8 字节');

// ---------------------------------------------------------------- RFC 6238 官方向量
// secret 直接按 ASCII 取字节，与 RFC 里写的种子完全一致
function hmac(secretAscii, counter, algo) {
    const buf = Buffer.alloc(8);
    buf.writeUInt32BE(Math.floor(counter / 4294967296), 0);
    buf.writeUInt32BE(counter % 4294967296, 4);
    return nodeCrypto.createHmac(algo, Buffer.from(secretAscii, 'ascii')).update(buf).digest();
}

const RFC_TIMES = [59, 1111111109, 1111111111, 1234567890, 2000000000, 20000000000];

// SHA-1：种子 '12345678901234567890'（20 字节）
const S1 = '12345678901234567890';
const EXP1 = ['94287082', '07081804', '14050471', '89005924', '69279037', '65353130'];
for (let i = 0; i < RFC_TIMES.length; i++) {
    const counter = T.totpCounter(RFC_TIMES[i] * 1000, 30);
    const code = T.totpHotp(hmac(S1, counter, 'sha1'), 8);
    eq(code, EXP1[i], 'RFC 6238 SHA-1 T=' + RFC_TIMES[i]);
    // 6 位是 8 位的后 6 位
    eq(T.totpHotp(hmac(S1, counter, 'sha1'), 6), EXP1[i].slice(-6),
        'RFC 6238 SHA-1 6 位 T=' + RFC_TIMES[i]);
}

// SHA-256：种子 '12345678901234567890123456789012'（32 字节）
const S256 = '12345678901234567890123456789012';
const EXP256 = ['46119246', '68084774', '67062674', '91819424', '90698825', '77737706'];
for (let i = 0; i < RFC_TIMES.length; i++) {
    const counter = T.totpCounter(RFC_TIMES[i] * 1000, 30);
    eq(T.totpHotp(hmac(S256, counter, 'sha256'), 8), EXP256[i], 'RFC 6238 SHA-256 T=' + RFC_TIMES[i]);
}

// SHA-512：种子 64 字节
const S512 = '1234567890123456789012345678901234567890123456789012345678901234';
const EXP512 = ['90693936', '25091201', '99943326', '93441116', '38618901', '47863826'];
for (let i = 0; i < RFC_TIMES.length; i++) {
    const counter = T.totpCounter(RFC_TIMES[i] * 1000, 30);
    eq(T.totpHotp(hmac(S512, counter, 'sha512'), 8), EXP512[i], 'RFC 6238 SHA-512 T=' + RFC_TIMES[i]);
}

// 从 Base32 解出来的字节，必须与直接取 ASCII 的结果完全一致（串起两条链路）
const fromB32 = T.totpBase32Decode('GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
const ctr = T.totpCounter(59000, 30);
eq(T.totpHotp(hmac(Buffer.from(fromB32.bytes).toString('ascii'), ctr, 'sha1'), 8),
    '94287082', '链路: Base32 → 字节 → HMAC → 截断 与 RFC 一致');

// ---------------------------------------------------------------- 截断实现细节
eq(T.totpHotp(new Uint8Array(0), 6), '', 'hotp: 过短的 HMAC 不崩，返回空');
eq(T.totpHotp(null, 6), '', 'hotp: null 不崩');
eq(T.totpHotp(new Uint8Array(19), 6), '', 'hotp: 20 字节以下直接拒绝');
// 高位必须被抹掉：不 & 0x7f 的话 0xffffffff 在 JS 位运算里是 -1，取模后得到负数
const evil = new Uint8Array(20);
evil[19] = 0;                       // 偏移 0
evil[0] = 0xff; evil[1] = 0xff; evil[2] = 0xff; evil[3] = 0xff;
// 0x7fffffff = 2147483647 → % 1e8 = 47483647
eq(T.totpHotp(evil, 8), '47483647', 'hotp: 最高位被抹掉（0x7fffffff 而非负数）');
ok(/^\d+$/.test(T.totpHotp(evil, 8)), 'hotp: 结果永远是非负十进制串');
// 前导零必须补足位数
const zero = new Uint8Array(20);
zero[19] = 0;
eq(T.totpHotp(zero, 6), '000000', 'hotp: 前导零补足 6 位');
eq(T.totpHotp(zero, 8), '00000000', 'hotp: 前导零补足 8 位');

// ---------------------------------------------------------------- 展示格式
eq(T.totpFormat('123456'), '123 456', 'format: 6 位分两段');
eq(T.totpFormat('12345678'), '1234 5678', 'format: 8 位分两段');
eq(T.totpFormat('12345'), '12345', 'format: 不足 6 位不分组');
eq(T.totpFormat(''), '', 'format: 空串');
eq(T.totpFormat(null), '', 'format: null');

// ---------------------------------------------------------------- otpauth 解析
const u1 = T.totpParseUri('otpauth://totp/ACME%20Co:alice@example.com' +
    '?secret=JBSWY3DPEHPK3PXP&issuer=ACME%20Co&algorithm=SHA1&digits=6&period=30');
ok(u1 && u1.ok, 'uri: 标准链接可解析');
eq(u1.secret, 'JBSWY3DPEHPK3PXP', 'uri: 取到 secret');
eq(u1.issuer, 'ACME Co', 'uri: issuer 解码');
eq(u1.account, 'alice@example.com', 'uri: account 去掉 issuer 前缀');
eq(u1.digits, 6, 'uri: digits');
eq(u1.period, 30, 'uri: period');
eq(u1.algorithm, 'SHA-1', 'uri: algorithm');

const u2 = T.totpParseUri('otpauth://totp/alice?secret=JBSWY3DP&period=60&digits=8&algorithm=SHA256');
eq(u2.issuer, '', 'uri: 无 issuer 的 label 不瞎猜');
eq(u2.account, 'alice', 'uri: 无 issuer 时整个 label 就是账号');
eq(u2.period, 60, 'uri: period=60');
eq(u2.digits, 8, 'uri: digits=8');
eq(u2.algorithm, 'SHA-256', 'uri: SHA256');

// 大小写：某些 App 会写成 OTpauth://TOTP/
eq(T.totpParseUri('OTPAUTH://TOTP/x?secret=JBSWY3DP').ok, true, 'uri: scheme 与类型大小写不敏感');

// hotp 必须明确拒绝：它需要计数器，本页没有计数器输入
const uh = T.totpParseUri('otpauth://hotp/x?secret=JBSWY3DP&counter=1');
ok(uh && uh.ok === false && uh.reason === 'type', 'uri: hotp 被识别并拒绝');

// 非 otpauth 输入不当作链接（否则普通 Base32 也会被误判）
eq(T.totpParseUri('JBSWY3DPEHPK3PXP'), null, 'uri: 裸密钥不当作链接');
eq(T.totpParseUri(''), null, 'uri: 空串');
eq(T.totpParseUri(null), null, 'uri: null');
// 畸形百分号编码不能抛
let threw = false;
try { T.totpParseUri('otpauth://totp/%E0%A4%A?secret=%zz&issuer=%'); } catch (e) { threw = true; }
ok(!threw, 'uri: 畸形百分号编码不抛异常');

// 缺 secret 时要返回 ok 但 secret 为空（交给界面报错），不能当成解析失败
const un = T.totpParseUri('otpauth://totp/x?digits=6');
ok(un && un.ok && un.secret === '', 'uri: 缺 secret 时 secret 为空串');

// ---------------------------------------------------------------- 反向构造
const built = T.totpBuildUri({
    secret: 'jbswy3dp ehpk3pxp', issuer: 'ACME Co', account: 'alice@example.com',
    digits: 6, period: 30, algorithm: 'SHA1'
});
ok(built.indexOf('otpauth://totp/') === 0, 'buildUri: 前缀正确');
ok(built.indexOf('secret=JBSWY3DPEHPK3PXP') > 0, 'buildUri: 密钥已规范化且不带空格');
ok(built.indexOf('digits=6') > 0, 'buildUri: 带 digits');
ok(built.indexOf('period=30') > 0, 'buildUri: 带 period');
ok(built.indexOf('algorithm=SHA1') > 0, 'buildUri: 算法写成 SHA1 而非 SHA-1');

// 往返：自己生成的链接必须能被自己解析回同样的参数
const back = T.totpParseUri(built);
ok(back && back.ok, 'buildUri: 往返可解析');
eq(back.secret, 'JBSWY3DPEHPK3PXP', 'buildUri: 往返 secret 一致');
eq(back.issuer, 'ACME Co', 'buildUri: 往返 issuer 一致');
eq(back.account, 'alice@example.com', 'buildUri: 往返 account 一致');
eq(back.period, 30, 'buildUri: 往返 period 一致');

// ---------------------------------------------------------------- 汇总
console.log('\n' + (fails.length ? '❌ 失败 ' + fails.length + ' 项 / 共 ' + (pass + fails.length) : '✅ 全部通过 ' + pass + ' 项'));
if (fails.length) {
    fails.forEach((f) => console.log('  - ' + f));
    process.exit(1);
}
