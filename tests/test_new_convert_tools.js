// 单测：2026-11 新增的 9 个工具的纯函数（不依赖 DOM）
//   cidr / user-agent / punycode / url-parser / coordinate
//   number-to-chinese / markdown-table / unit-converter / htpasswd
// 覆盖：标准换算向量（人工核对过的权威值）/ 边界（/31 /32 /0、零、负数、空串）/ 异常输入。
// 运行：node tests/test_new_convert_tools.js
const assert = require('assert');
const path = require('path');
const J = (f) => require(path.join(__dirname, '..', 'src', 'js', f + '.js'));

const CIDR = J('cidr');
const UA = J('user-agent');
const PUNY = J('punycode');
const URLP = J('url-parser');
const COORD = J('coordinate');
const NUM = J('number-to-chinese');
const MD = J('markdown-table');
const UNIT = J('unit-converter');
const HT = J('htpasswd');

let pass = 0;
const fails = [];
function eq(actual, expected, msg) {
    try { assert.deepStrictEqual(actual, expected); pass++; }
    catch (e) {
        fails.push(msg + '\n    期望 ' + JSON.stringify(expected) + '\n    实际 ' + JSON.stringify(actual));
    }
}
function ok(cond, msg) {
    if (cond) { pass++; } else { fails.push(msg); }
}
function near(actual, expected, tol, msg) {
    const d = Math.abs(actual - expected);
    if (isFinite(d) && d <= tol) { pass++; return; }
    fails.push(msg + '\n    期望 ' + expected + ' ±' + tol + '\n    实际 ' + actual);
}
function hex(buf) {
    return Array.prototype.map.call(buf, (x) => ('0' + (x & 0xff).toString(16)).slice(-2)).join('');
}

// ============================================================ cidr
eq(CIDR.cidrIpToInt('192.168.1.130'), 3232235906, 'cidr: ip → int');
eq(CIDR.cidrIpToInt('0.0.0.0'), 0, 'cidr: 0.0.0.0 → 0');
eq(CIDR.cidrIpToInt('255.255.255.255'), 4294967295, 'cidr: 广播地址 → 2^32-1（无符号）');
eq(CIDR.cidrIpToInt('8.8.8.8'), 134744072, 'cidr: 8.8.8.8');
eq(CIDR.cidrIpToInt('256.1.1.1'), null, 'cidr: 越界八位组返回 null');
eq(CIDR.cidrIpToInt('1.2.3'), null, 'cidr: 少一段返回 null');
eq(CIDR.cidrIpToInt('1.2.3.4.5'), null, 'cidr: 多一段返回 null');
eq(CIDR.cidrIpToInt('a.b.c.d'), null, 'cidr: 非数字返回 null');
eq(CIDR.cidrIpToInt('01.2.3.4'), CIDR.cidrIpToInt('1.2.3.4'), 'cidr: 前导零按十进制解释，不当作八进制');

eq(CIDR.cidrIntToIp(3232235906), '192.168.1.130', 'cidr: int → ip');
eq(CIDR.cidrIntToIp(4294967295), '255.255.255.255', 'cidr: 最大值 → 255.255.255.255');

eq(CIDR.cidrPrefixToMask(24), 4294967040, 'cidr: /24 掩码');
eq(CIDR.cidrPrefixToMask(0), 0, 'cidr: /0 掩码为 0');
eq(CIDR.cidrMaskToPrefix(4294967040), 24, 'cidr: 掩码 → /24');
eq(CIDR.cidrMaskToPrefix(0), 0, 'cidr: 0.0.0.0 → /0');
eq(CIDR.cidrMaskToPrefix(2147483903), -1, 'cidr: 非连续掩码返回 -1');
for (let p = 0; p <= 32; p++) {
    eq(CIDR.cidrMaskToPrefix(CIDR.cidrPrefixToMask(p)), p, 'cidr: /' + p + ' 前缀↔掩码往返');
}

const r26 = CIDR.cidrInfo('192.168.1.130/26');
eq(r26.valid, true, 'cidr: /26 合法');
eq([r26.network, r26.broadcast, r26.first, r26.last, r26.usable, r26.total],
   ['192.168.1.128', '192.168.1.191', '192.168.1.129', '192.168.1.190', 62, 64],
   'cidr: /26 网络/广播/首末可用/可用数');
eq(r26.type, 'private', 'cidr: 192.168/16 判为私有');
eq(r26.mask, '255.255.255.192', 'cidr: /26 掩码点分');
eq(r26.cidr, '192.168.1.128/26', 'cidr: 归一化后的网段写法');

const r31 = CIDR.cidrInfo('10.0.0.0/31');
eq([r31.usable, r31.total, r31.first, r31.last], [2, 2, '10.0.0.0', '10.0.0.1'],
   'cidr: /31 点到点链路两个地址都可用（RFC 3021）');
const r32 = CIDR.cidrInfo('10.0.0.7/32');
eq([r32.usable, r32.network, r32.broadcast], [1, '10.0.0.7', '10.0.0.7'], 'cidr: /32 单主机');
const r28 = CIDR.cidrInfo('172.16.5.10/28');
eq([r28.network, r28.broadcast, r28.usable], ['172.16.5.0', '172.16.5.15', 14], 'cidr: /28 段');
eq(CIDR.cidrInfo('192.168.1.0/255.255.255.0').prefix, 24, 'cidr: 点分掩码写法等价 /24');
eq(CIDR.cidrInfo('192.168.1.9').prefix, 32, 'cidr: 无斜杠按 /32');
eq(CIDR.cidrInfo('').reason, 'empty', 'cidr: 空输入');
eq(CIDR.cidrInfo('1.2.3.400/24').reason, 'ip', 'cidr: 非法 IP');
eq(CIDR.cidrInfo('10.0.0.0/33').reason, 'prefix', 'cidr: /33 非法');
eq(CIDR.cidrInfo('10.0.0.0/255.0.255.0').reason, 'mask', 'cidr: 非连续掩码');
eq(CIDR.cidrToBinary(3232235906), '11000000.10101000.00000001.10000010', 'cidr: 二进制串');

eq(CIDR.cidrIpType('10.1.2.3'), 'private', 'cidr: 10/8 私有');
eq(CIDR.cidrIpType('172.20.0.1'), 'private', 'cidr: 172.16/12 私有');
eq(CIDR.cidrIpType('172.32.0.1'), 'public', 'cidr: 172.32 不在私有段');
eq(CIDR.cidrIpType('127.0.0.1'), 'loopback', 'cidr: 回环');
eq(CIDR.cidrIpType('169.254.3.4'), 'linklocal', 'cidr: 链路本地');
eq(CIDR.cidrIpType('100.100.1.1'), 'cgnat', 'cidr: 运营商 NAT');
eq(CIDR.cidrIpType('224.0.0.1'), 'multicast', 'cidr: 组播');
eq(CIDR.cidrIpType('255.255.255.255'), 'broadcast', 'cidr: 受限广播（不得被 reserved 吃掉）');
eq(CIDR.cidrIpType('8.8.8.8'), 'public', 'cidr: 公网地址');
eq(CIDR.cidrIpClass('8.8.8.8'), 'A', 'cidr: A 类');
eq(CIDR.cidrIpClass('130.1.1.1'), 'B', 'cidr: B 类');
eq(CIDR.cidrIpClass('200.1.1.1'), 'C', 'cidr: C 类');

// ============================================================ user-agent
const UA_CHROME = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    + '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
const UA_EDGE = UA_CHROME + ' Edg/120.0.2210.91';
const UA_IOS = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 '
    + '(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';
const UA_WX = 'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) '
    + 'Version/4.0 Chrome/111.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.42';
const UA_GOOGLEBOT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)';
const UA_CURL = 'curl/8.4.0';

const chrome = UA.uaParse(UA_CHROME);
eq([chrome.browser, chrome.major, chrome.engine, chrome.os, chrome.device],
   ['Chrome', 120, 'Blink', 'Windows 10 / 11', 'desktop'], 'ua: Chrome on Windows');
eq(chrome.isMobile, false, 'ua: 桌面不算移动端');
eq(chrome.bot, '', 'ua: 正常浏览器不判为爬虫');

const edge = UA.uaParse(UA_EDGE);
eq([edge.browser, edge.major], ['Edge', 120], 'ua: Edg/ 必须先于 Chrome 命中');
eq(UA.uaParse(UA_IOS).browser, 'Safari', 'ua: iOS Safari');
eq([UA.uaParse(UA_IOS).os, UA.uaParse(UA_IOS).device], ['iOS', 'mobile'], 'ua: iPhone 判为 iOS 移动端');
eq(UA.uaParse(UA_WX).browser, 'WeChat', 'ua: 微信内置浏览器优先识别');
eq([UA.uaParse(UA_GOOGLEBOT).bot, UA.uaParse(UA_GOOGLEBOT).device], ['Googlebot', 'bot'],
   'ua: Googlebot 标为爬虫');
ok(UA.uaParse(UA_CURL).bot !== '' || UA.uaParse(UA_CURL).browser === 'curl',
   'ua: curl 应被识别（命令行工具或爬虫桶）');
eq(UA.uaParse('').valid, false, 'ua: 空串无效');
ok(UA.uaEngine(UA_CHROME, 'Chrome', '120.0') === 'Blink', 'ua: engine 单独可用');
eq(UA.uaOs(UA_IOS), { name: 'iOS', version: '17.0' }, 'ua: os 单独可用（含版本）');
ok(UA.uaDevice(UA_IOS) === 'mobile', 'ua: device 单独可用');

// ============================================================ punycode
eq(PUNY.punyDecodeLabel('fsqu00a'), '例子', 'punycode: RFC 3492 解码');
eq(PUNY.punyDecodeLabel('mnchen-3ya'), 'münchen', 'punycode: 变音符解码');
eq(PUNY.punyDecodeLabel('bcher-kva'), 'bücher', 'punycode: 德语解码');
eq(PUNY.punyDecodeDomain('xn--fsqu00a.xn--0zwm56d'), '例子.测试', 'punycode: 整域名解码');
eq(PUNY.punyDecodeDomain('example.com'), 'example.com', 'punycode: 纯 ASCII 原样返回');

const p1 = PUNY.punyInfo('例子.测试');
eq(p1.ascii, 'xn--fsqu00a.xn--0zwm56d', 'punycode: 编码方向（借浏览器 IDNA）');
eq(p1.unicode, '例子.测试', 'punycode: 中文保持可读形式');
eq(p1.isIdn, true, 'punycode: 判定为国际化域名');
eq(p1.labels.length, 2, 'punycode: 按点拆分标签');
const p2 = PUNY.punyInfo('xn--mnchen-3ya.de');
eq([p2.unicode, p2.ascii], ['münchen.de', 'xn--mnchen-3ya.de'], 'punycode: 解码方向');
eq(PUNY.punyInfo('example.com').isIdn, false, 'punycode: 纯 ASCII 不算 IDN');
eq(PUNY.punyHostOf('https://例子.测试/a?b=1').unicode, '例子.测试', 'punycode: 从完整 URL 取主机名');
eq(PUNY.punyCharLen('例子'), 2, 'punycode: 码点长度而非 UTF-16 长度');

// ============================================================ url-parser
const u = URLP.urlParseInfo('https://a.com:8443/p/q?a=1&b=%20x#h');
eq([u.scheme, u.host, u.port, u.path, u.hash], ['https', 'a.com', '8443', '/p/q', '#h'],
   'url: 拆解各段');
eq(u.params, [{ k: 'a', v: '1' }, { k: 'b', v: ' x' }], 'url: 参数解码成可读值');
eq(u.origin, 'https://a.com:8443', 'url: origin');
const u2 = URLP.urlParseInfo('example.com/x');
eq([u2.scheme, u2.host, u2.addedScheme], ['https', 'example.com', true],
   'url: 缺协议时补 https 并标记');
eq(URLP.urlRebuild({ scheme: 'https', host: 'a.com', port: '', path: '/x', params: [{ k: 'a', v: '1 2' }] }),
   'https://a.com/x?a=1%202', 'url: 重组时参数按 encodeURIComponent 编码');
eq(URLP.urlReadable('https://a.com/%E4%B8%AD'), 'https://a.com/中', 'url: 可读形式');
eq(URLP.urlParseInfo('').valid, false, 'url: 空输入无效');

// ============================================================ coordinate
ok(COORD.coordOutOfChina(116.4, 39.9) === false, 'coord: 北京在偏移范围内');
ok(COORD.coordOutOfChina(139.7, 35.7) === true, 'coord: 东京不在偏移范围内');
const c1 = COORD.coordInfo(116.397428, 39.90923, 'wgs');
eq(c1.valid, true, 'coord: 有效坐标');
const back = COORD.coordGcjToWgs(c1.gcj[0], c1.gcj[1]);
near(back[0], 116.397428, 1e-6, 'coord: GCJ → WGS 反解经度误差 < 1e-6（约 0.1 米）');
near(back[1], 39.90923, 1e-6, 'coord: GCJ → WGS 反解纬度误差 < 1e-6');
near(c1.offsetWgsGcj, 554.9, 5, 'coord: 北京 WGS→GCJ 偏移约 555 米');
const bdBack = COORD.coordBdToGcj(c1.bd[0], c1.bd[1]);
near(bdBack[0], c1.gcj[0], 1e-6, 'coord: BD-09 → GCJ-02 可逆（经度）');
near(bdBack[1], c1.gcj[1], 1e-6, 'coord: BD-09 → GCJ-02 可逆（纬度）');
near(COORD.coordDistance(116.397428, 39.90923, 116.397428, 39.90923), 0, 0.01,
   'coord: 同一坐标距离 0');
const tokyo = COORD.coordInfo(139.7, 35.7, 'wgs');
eq(tokyo.outside, true, 'coord: 境外不做偏移');
eq(tokyo.gcj, tokyo.wgs, 'coord: 境外 GCJ 与 WGS 相同');

// ============================================================ number-to-chinese
const CN = [
    ['0', '零'], ['1', '一'], ['10', '十'], ['12', '十二'], ['20', '二十'],
    ['101', '一百零一'], ['110', '一百一十'], ['1001', '一千零一'], ['1100', '一千一百'],
    ['100000', '十万'], ['1000000', '一百万'], ['10000000', '一千万'],
    ['100000000', '一亿'], ['100000001', '一亿零一'],
    ['999999999999', '九千九百九十九亿九千九百九十九万九千九百九十九'],
    ['1234567890123', '一万二千三百四十五亿六千七百八十九万零一百二十三'],
    ['-3.5', '负三点五'], ['3.14', '三点一四'], ['0.05', '零点零五'],
];
CN.forEach(([input, expect]) => eq(NUM.numToCn(input).text, expect, 'cn: ' + input + ' → ' + expect));
eq(NUM.numToCn('10000000000000').reason, 'range', 'cn: 14 位超出范围');
eq(NUM.numToCn('abc').reason, 'number', 'cn: 非数字');

const RMB = [
    ['0', '零元整'], ['0.05', '零元零伍分'], ['100.5', '壹佰元伍角整'],
    ['10.10', '拾元壹角整'], ['20', '贰拾元整'], ['1000000', '壹佰万元整'],
    ['9999999999999.99', '玖万玖仟玖佰玖拾玖亿玖仟玖佰玖拾玖万玖仟玖佰玖拾玖元玖角玖分'],
];
RMB.forEach(([input, expect]) => eq(NUM.numToRmb(input).text, expect, 'rmb: ' + input + ' → ' + expect));
eq(NUM.numToRmb('1.999').text, '壹元玖角玖分', 'rmb: 第三位小数截断不四舍五入');
eq(NUM.numToRmb('10000000000000').reason, 'range', 'rmb: 14 位超出范围');
eq(NUM.numNormalize(' １，２３４．５ '), '1234.5', 'cn: 全角数字与千分位清洗');

// ============================================================ markdown-table
eq(MD.mdCharWidth('a'), 1, 'md: ASCII 宽 1');
eq(MD.mdCharWidth('中'), 2, 'md: CJK 宽 2');
eq(MD.mdTextWidth('a中'), 3, 'md: 混排宽度');
eq(MD.mdDetectDelimiter('a\tb\n1\t2'), '\t', 'md: 制表符优先');
eq(MD.mdDetectDelimiter('a,b\n1,2'), ',', 'md: 逗号');
eq(MD.mdParseDelimited('a\tb\n1\t2'), [['a', 'b'], ['1', '2']], 'md: 分隔文本解析');
eq(MD.mdParseDelimited('"a,b",c', ','), [['a,b', 'c']], 'md: 引号内的分隔符不切分');
eq(MD.mdParseDelimited('"say ""hi""",x', ','), [['say "hi"', 'x']], 'md: 双引号转义');

const built = MD.mdBuildTable([['a', '名称'], ['1', 'x']]);
eq(built, '| a   | 名称 |\n| --- | ---- |\n| 1   | x    |', 'md: 按显示宽度对齐（CJK 占两列）');
const parsed = MD.mdParseTable('| a | b |\n| --- | --- |\n| 1 | 2 |');
eq(parsed, [['a', 'b'], ['1', '2']], 'md: Markdown 表格解析');
eq(MD.mdToDelimited([['a', 'b'], ['1', '2']], ','), 'a,b\n1,2', 'md: 反向导出分隔文本');
eq(MD.mdColumnIsNumeric([['h'], ['1'], ['2.5']], 0), true, 'md: 全数字列');
eq(MD.mdColumnIsNumeric([['h'], ['1'], ['x']], 0), false, 'md: 含非数字则不是数字列');
eq(MD.mdParseDelimited('a\tb\n\t\n'), [['a', 'b']], 'md: 丢掉尾部空白行');

// ============================================================ unit-converter
eq(UNIT.unitConvert('length', 'km', 'm', 1), 1000, 'unit: 1 km = 1000 m');
near(UNIT.unitConvert('length', 'mi', 'km', 1), 1.609344, 1e-9, 'unit: 1 mi = 1.609344 km');
near(UNIT.unitConvert('temperature', '°C', '°F', 100), 212, 1e-9, 'unit: 100°C = 212°F');
near(UNIT.unitConvert('temperature', '°C', 'K', 0), 273.15, 1e-9, 'unit: 0°C = 273.15K');
near(UNIT.unitConvert('temperature', '°F', '°C', 32), 0, 1e-9, 'unit: 32°F = 0°C');
eq(UNIT.unitConvert('data', 'MiB', 'KiB', 1), 1024, 'unit: 1 MiB = 1024 KiB');
eq(UNIT.unitConvert('mass', 'kg', 'g', 1), 1000, 'unit: 1 kg = 1000 g');
ok(isNaN(UNIT.unitConvert('nope', 'a', 'b', 1)), 'unit: 未知类别返回 NaN');
ok(isNaN(UNIT.unitConvert('length', 'xx', 'm', 1)), 'unit: 未知单位返回 NaN');
ok(UNIT.unitAll('length', 'm', 1).length === UNIT.UNIT_CATS.length
   || UNIT.unitAll('length', 'm', 1).length > 3, 'unit: unitAll 返回该类全部单位');
eq(UNIT.unitFmt(1234.5), '1,234.5', 'unit: 千分位格式化');
eq(UNIT.unitFmt(0.1 + 0.2), '0.3', 'unit: 去掉浮点尾巴');
eq(UNIT.unitFmt(0), '0', 'unit: 0');
eq(UNIT.unitFmt(NaN), '—', 'unit: NaN 显示占位符');
eq(Object.keys(UNIT.UNIT_CATS).length, 12, 'unit: 12 个类别');

// ============================================================ htpasswd
// openssl passwd -apr1 password（salt=abcdefgh）逐字节对照
eq(HT.htApr1('password', 'abcdefgh'), '$apr1$abcdefgh$FBwExRW4dCc8aL.OvjpIE1',
   'htpasswd: apr1 与 openssl 一致（ASCII）');
eq(HT.htApr1('中文密码', 'zzzzzzzz'), '$apr1$zzzzzzzz$LaTQ.aUa1cTfeQfXO51Bo.',
   'htpasswd: apr1 与 openssl 一致（UTF-8 多字节）');
eq(hex(HT.htMd5Bytes('abc')), '900150983cd24fb0d6963f7d28e17f72', 'htpasswd: MD5("abc") 标准向量');
eq(hex(HT.htMd5Bytes('')), 'd41d8cd98f00b204e9800998ecf8427e', 'htpasswd: MD5("") 标准向量');
eq(hex(HT.htMd5Bytes('中')), hex(HT.htMd5Bytes(new Uint8Array([0xe4, 0xb8, 0xad]))),
   'htpasswd: 字符串按 UTF-8 取字节（不是静默空数组）');
eq(Array.from(HT.htUtf8('中')), [228, 184, 173], 'htpasswd: UTF-8 编码');
eq(HT.htRandomSalt(8).length, 8, 'htpasswd: 随机盐长度');
ok(/^[A-Za-z0-9.\/]{8}$/.test(HT.htRandomSalt(8)), 'htpasswd: 盐只用 apr1 字母表');

// ============================================================ 汇总
const total = pass + fails.length;
console.log('\n' + pass + '/' + total + ' 通过');
if (fails.length) {
    console.log('\n失败 ' + fails.length + ' 项：');
    fails.forEach((f, i) => console.log('  ' + (i + 1) + '. ' + f));
    process.exit(1);
}
console.log('全部通过');
