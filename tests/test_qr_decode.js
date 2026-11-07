// 单测：qr-decode 的纯函数（不依赖 DOM / 图片 / jsQR）
// 覆盖：WiFi 转义、vCard 折行、MECARD、链接风险信号、解码尺度计划、
//       内容分类的每条分支，以及畸形 URI 编码不得抛异常（会炸掉整条解码链）。
// 运行：node tests/test_qr_decode.js
const assert = require('assert');
const path = require('path');
const Q = require(path.join(__dirname, '..', 'src', 'js', 'qr-decode.js'));

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

// ---------------------------------------------------------------- WiFi
const w1 = Q.qrParseWifi('WIFI:T:WPA;S:MyNet;P:p@ss;H:true;;');
eq(w1.ssid, 'MyNet', 'wifi: 解析 SSID');
eq(w1.pass, 'p@ss', 'wifi: 解析密码');
eq(w1.enc, 'WPA', 'wifi: 解析加密方式');
eq(w1.hidden, true, 'wifi: H:true → hidden');

const w2 = Q.qrParseWifi('WIFI:S:FreeNet;T:nopass;;');
eq(w2.pass, '', 'wifi: 开放网络无密码');
eq(w2.enc, 'nopass', 'wifi: 加密方式 nopass');
eq(w2.hidden, false, 'wifi: 未声明 H 时 hidden 为 false');

// 分号必须能被转义，否则带分号的密码会被截断——这是 WIFI: 格式最容易写错的地方
// 注意：源码里的 \\; 落到字符串里才是 \;，这正是二维码里实际的写法
const w3 = Q.qrParseWifi('WIFI:S:my\\;net;P:a\\;b\\\\c;;');
eq(w3.ssid, 'my;net', 'wifi: \\; 转义的分号不切断字段');
eq(w3.pass, 'a;b\\c', 'wifi: 反斜杠转义');

eq(Q.qrParseWifi('').ssid, '', 'wifi: 空串不抛异常');
eq(Q.qrParseWifi(null).ssid, '', 'wifi: null 不抛异常');

// ---------------------------------------------------------------- vCard
const v1 = Q.qrParseVcard(
    'BEGIN:VCARD\r\nVERSION:3.0\r\nFN:张三\r\nTEL:+8613800138000\r\n' +
    'EMAIL:z@example.com\r\nORG:某某公司\r\nTITLE:工程师\r\nURL:https://example.com\r\nEND:VCARD'
);
eq(v1.name, '张三', 'vcard: FN');
eq(v1.tel, '+8613800138000', 'vcard: TEL');
eq(v1.email, 'z@example.com', 'vcard: EMAIL');
eq(v1.org, '某某公司', 'vcard: ORG');
eq(v1.title, '工程师', 'vcard: TITLE');
eq(v1.site, 'https://example.com', 'vcard: URL');

// 折行续行：以空格开头的行要并回上一行
const v2 = Q.qrParseVcard('BEGIN:VCARD\nFN:张\n 三\nEND:VCARD');
eq(v2.name, '张三', 'vcard: 折行续行合并');

// 带参数前缀（TEL;TYPE=CELL:xxx）也要取到值
const v3 = Q.qrParseVcard('BEGIN:VCARD\nTEL;TYPE=CELL:12345\nEND:VCARD');
eq(v3.tel, '12345', 'vcard: TEL;TYPE= 参数不干扰取值');

// ---------------------------------------------------------------- MECARD
const m1 = Q.qrParseMecard('MECARD:N:李四;TEL:13900001111;EMAIL:l@example.com;ORG:A公司;;');
eq(m1.name, '李四', 'mecard: N');
eq(m1.tel, '13900001111', 'mecard: TEL');
eq(m1.email, 'l@example.com', 'mecard: EMAIL');

// ---------------------------------------------------------------- 链接风险
eq(Q.qrUrlRisks('https://example.com/a?b=1'), [], 'risk: 正常 https 无信号');
eq(Q.qrUrlRisks('http://example.com/'), ['http'], 'risk: 明文 http');
eq(Q.qrUrlRisks('https://192.168.1.1/login'), ['ip'], 'risk: 直连 IP');
eq(Q.qrUrlRisks('https://example.com@evil.com/'), ['userinfo'], 'risk: @ 伪装');
eq(Q.qrUrlRisks('https://bit.ly/abc'), ['short'], 'risk: 短链接');
eq(Q.qrUrlRisks('https://www.tinyurl.com/abc'), ['short'], 'risk: 带 www 的短链也能识别');
eq(Q.qrUrlRisks('https://evil.com@1.2.3.4:8443/'), ['userinfo', 'ip'], 'risk: 多个信号可叠加');
eq(Q.qrUrlRisks('not a url'), [], 'risk: 非 URL 返回空数组');
eq(Q.qrUrlRisks(''), [], 'risk: 空串返回空数组');

// ---------------------------------------------------------------- 解码尺度
const s1 = Q.qrScales(1200, 800);
eq(s1[0].maxSide, 1200, 'scales: 中等尺寸先用原尺寸');
eq(s1[0].pad, false, 'scales: 第一档不补白边');
ok(s1.some((a) => a.pad === true), 'scales: 必须有补白边的一档');

const s2 = Q.qrScales(4000, 3000);
ok(s2[0].maxSide <= 2000, 'scales: 超大图首档已缩小（' + s2[0].maxSide + '）');
ok(s2.length >= 4, 'scales: 大图给出多档');

const s3 = Q.qrScales(200, 200);
ok(s3.some((a) => a.maxSide > 200), 'scales: 小图要放大才有足够像素');
ok(s3.every((a) => a.maxSide >= 40), 'scales: 不产生小于 40 px 的无效档');

const s4 = Q.qrScales(0, 0);
ok(Array.isArray(s4) && s4.length > 0, 'scales: 零尺寸也不崩');
eq(Q.qrScales(40, 10).every((a) => a.maxSide >= 40), true, 'scales: 极小图同样不产生无效档');

// ---------------------------------------------------------------- 分类
const c1 = Q.qrClassify('https://devtools.help/altimeter/');
eq(c1.kind, 'url', 'classify: https → url');
eq(c1.labelKey, 'kind_url', 'classify: url 的标签键');
eq(c1.link, 'https://devtools.help/altimeter/', 'classify: url 可直接打开');
eq(c1.risks, [], 'classify: 正常网址无风险信号');

const c2 = Q.qrClassify('www.example.com');
eq(c2.kind, 'url', 'classify: www 开头按网址处理');
eq(c2.link, 'https://www.example.com', 'classify: www 补 https');

const c3 = Q.qrClassify('WIFI:T:WPA;S:Office;P:12345678;;');
eq(c3.kind, 'wifi', 'classify: WIFI: → wifi');
eq(c3.fields[0].key, 'f_ssid', 'classify: wifi 首个字段是网络名');
eq(c3.link, null, 'classify: wifi 没有可打开链接');

const c4 = Q.qrClassify('BEGIN:VCARD\nFN:王五\nTEL:123\nEND:VCARD');
eq(c4.kind, 'vcard', 'classify: BEGIN:VCARD → vcard');
eq(c4.labelKey, 'kind_vcard', 'classify: 名片标签键');

const c5 = Q.qrClassify('mailto:a@b.com?subject=%E4%BD%A0%E5%A5%BD&body=hi+there');
eq(c5.kind, 'mailto', 'classify: mailto → mailto');
eq(c5.fields[0].value, 'a@b.com', 'classify: mailto 收件人');
eq(c5.fields[1].value, '你好', 'classify: mailto 主题按 UTF-8 解码');
eq(c5.fields[2].value, 'hi there', 'classify: mailto 正文里的 + 还原为空格');

// 畸形百分号编码不能抛：二维码内容完全不受控
let threw = false;
try { Q.qrClassify('mailto:%E0%A4%A?subject=%zz'); } catch (e) { threw = true; }
ok(!threw, 'classify: 畸形 URI 编码不抛异常');
const c6 = Q.qrClassify('mailto:a@b.com?subject=%zz');
ok(c6.kind === 'mailto' && c6.fields.length >= 1, 'classify: 畸形编码仍返回可用结构');

const c7 = Q.qrClassify('tel:+8613800138000');
eq(c7.kind, 'tel', 'classify: tel → tel');
eq(c7.fields[0].value, '+8613800138000', 'classify: tel 号码');

const c8 = Q.qrClassify('SMSTO:10086:hello');
eq(c8.kind, 'sms', 'classify: SMSTO → sms');
eq(c8.fields[0].value, '10086', 'classify: sms 号码');
eq(c8.fields[1].value, 'hello', 'classify: sms 正文');

const c9 = Q.qrClassify('geo:39.9074,116.3912');
eq(c9.kind, 'geo', 'classify: geo → geo');
eq(c9.fields[0].value, '39.9074', 'classify: geo 纬度');
eq(c9.fields[1].value, '116.3912', 'classify: geo 经度');

const c10 = Q.qrClassify('otpauth://totp/ACME:alice?secret=JBSWY3DP&issuer=ACME');
eq(c10.kind, 'otpauth', 'classify: otpauth → otpauth');
eq(c10.fields[0].value, 'ACME', 'classify: otpauth 签发方');
eq(c10.fields[1].value, 'ACME:alice', 'classify: otpauth 账号');
ok(c10.secretHidden === true, 'classify: otpauth 标记为"含密钥"');
ok(c10.fields.every((f) => f.value !== 'JBSWY3DP'), 'classify: 密钥本身不得出现在展示字段里');

const c11 = Q.qrClassify('这是一段普通文本');
eq(c11.kind, 'text', 'classify: 纯文本');
eq(c11.text, '这是一段普通文本', 'classify: 纯文本内容');

const c12 = Q.qrClassify('   ');
eq(c12.kind, 'empty', 'classify: 空白 → empty');
eq(Q.qrClassify(null).kind, 'empty', 'classify: null → empty');

// BOM：少数生成器会把 BOM 塞进来，不该影响类型判断
eq(Q.qrClassify('\uFEFFhttps://example.com').kind, 'url', 'classify: 前导 BOM 不影响分类');

// 大小写不敏感：WIFI: / wifi: 都要认
eq(Q.qrClassify('wifi:S:x;;').kind, 'wifi', 'classify: 小写 wifi: 也识别');
eq(Q.qrClassify('Geo:1,2').kind, 'geo', 'classify: 大小写混合的 geo: 也识别');

// ---------------------------------------------------------------- 汇总
console.log('\n' + (fails.length ? '❌ 失败 ' + fails.length + ' 项 / 共 ' + (pass + fails.length) : '✅ 全部通过 ' + pass + ' 项'));
if (fails.length) {
    fails.forEach((f) => console.log('  - ' + f));
    process.exit(1);
}
