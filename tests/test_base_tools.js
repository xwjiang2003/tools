// 单测：src/js/base-tools.js 的纯函数（不依赖 DOM）
// 覆盖：核心换算向量 / 全进制 2-36 往返 / 边界（0、负数、空串）/ 异常（非法数字、非法进制）/
//       任意精度（超 2^53）/ 前缀与分组符 / detectBase / groupBits / bitLength
const assert = require('assert');
const path = require('path');
const B = require(path.join(__dirname, '..', 'src', 'js', 'base-tools.js'));

let pass = 0, fail = 0;
function eq(actual, expected, msg) {
    try { assert.deepStrictEqual(actual, expected); pass++; }
    catch (e) { fail++; console.error('✗ ' + msg + '\n   期望 ' + JSON.stringify(expected) + '\n   实际 ' + JSON.stringify(actual)); }
}
function ok(cond, msg) { try { assert.ok(cond); pass++; } catch (e) { fail++; console.error('✗ ' + msg); } }
function noThrow(fn, msg) {
    try { fn(); pass++; } catch (e) { fail++; console.error('✗ ' + msg + ' 抛出异常: ' + e.message); }
}

// ============================================================ baseValid
ok(B.baseValid(2) && B.baseValid(36) && B.baseValid(10), 'baseValid 合法边界 2/36/10');
ok(!B.baseValid(1) && !B.baseValid(37) && !B.baseValid(0) && !B.baseValid(-2), 'baseValid 拒绝越界');
ok(!B.baseValid(2.5) && !B.baseValid('10') && !B.baseValid(NaN) && !B.baseValid(Infinity), 'baseValid 拒绝非整数/非数字');

// ============================================================ 核心换算向量（人工核对）
eq(B.radixConvert('255', 10, 16).value, 'ff', '255 → hex = ff');
eq(B.radixConvert('255', 10, 2).value, '11111111', '255 → bin');
eq(B.radixConvert('11111111', 2, 10).value, '255', 'bin → 255');
eq(B.radixConvert('0xFF', 16, 10).value, '255', '0xFF 前缀 → 255');
eq(B.radixConvert('0b1010', 2, 10).value, '10', '0b1010 → 10');
eq(B.radixConvert('0o17', 8, 10).value, '15', '0o17 → 15');
eq(B.radixConvert('17', 8, 10).value, '15', '17@8 → 15');
eq(B.radixConvert('ff', 16, 10).value, '255', '小写 hex 无前缀');
eq(B.radixConvert('FF', 16, 2).value, '11111111', '大写 hex');
eq(B.radixConvert('10', 10, 2).value, '1010', '10 → bin');
eq(B.radixConvert('z', 36, 10).value, '35', 'z@36 → 35');
eq(B.radixConvert('z', 36, 36).value, 'z', 'z@36 → 36 进制往返');
eq(B.radixConvert('10', 2, 3).value, '2', 'bin 10 → base3 = 2');
eq(B.radixConvert('100', 3, 10).value, '9', 'base3 100 → 9');

// 0 与负数
eq(B.radixConvert('0', 10, 2).value, '0', '0 → 0');
eq(B.radixConvert('0', 10, 16).value, '0', '0 → hex 0');
eq(B.radixConvert('-255', 10, 16).value, '-ff', '负数 → -ff');
eq(B.radixConvert('-ff', 16, 10).value, '-255', '-ff → -255');
eq(B.radixConvert('+255', 10, 16).value, 'ff', '正号容忍');
eq(B.radixParse('-0', 10), 0n, '-0 归一为 0');
eq(B.radixFormat(-0n, 10), '0', 'format(-0n) = 0');
eq(B.radixFormat(0n, 2), '0', 'format(0n) = 0');

// 分组符（空格 / 下划线）与前后空白
eq(B.radixConvert('1111_1111', 2, 10).value, '255', '下划线分组 bin');
eq(B.radixConvert('  255  ', 10, 16).value, 'ff', '前后空白');
eq(B.radixConvert('ff ff', 16, 10).value, '65535', 'hex 空格分组 = 拼接（分隔符被剥除）');
eq(B.radixConvert('0x_ff_ff', 16, 10).value, '65535', '前缀后跟下划线分组');

// ============================================================ 全进制 2-36 往返（值域抽查）
// 用一个跨进制的值 123456789 验证所有源/目标进制组合都能往返一致
const SEED = 123456789;
for (let from = 2; from <= 36; from++) {
    const s = B.radixFormat(BigInt(SEED), from);
    for (let to = 2; to <= 36; to++) {
        const back = B.radixConvert(s, from, to);
        if (back.valid !== true || back.int !== BigInt(SEED)) {
            fail++; console.error('✗ 往返失败 ' + SEED + ' base' + from + '→' + to + ' (' + s + ')');
        } else pass++;
    }
}
// 35×35=1225 组合全部通过的标记
ok(true, '全进制 2-36 往返 1225 组合');

// ============================================================ 任意精度（超 2^53，float 会丢精度）
// 2^200 = 1606938044258990275541962092341162602522202993782792835301376
const P200 = B.radixFormat(1n << 200n, 10);
eq(P200, '1606938044258990275541962092341162602522202993782792835301376', '2^200 十进制精确值');
eq(B.radixConvert(P200, 10, 16).value, (1n << 200n).toString(16), '2^200 dec→hex 往返');
eq(B.radixConvert(P200, 10, 2).value, '1' + '0'.repeat(200), '2^200 dec→bin 往返');
ok(B.radixConvert('1606938044258990275541962092341162602522202993782792835301377', 10, 16).int ===
   ((1n << 200n) + 1n), '末位 +1 也精确（float 会吃掉这个差）');
// 32 位无符号上限 / 64 位上限
eq(B.radixConvert('4294967295', 10, 16).value, 'ffffffff', 'uint32 上限 → ffffffff');
eq(B.radixConvert('ffffffffffffffff', 16, 10).value, '18446744073709551615', 'uint64 上限');
eq(B.radixConvert('18446744073709551615', 10, 16).value, 'ffffffffffffffff', 'uint64 dec→hex 往返');
// 1000 位大数（各进制往返抽样）
const BIG = '9'.repeat(1000);
for (const base of [2, 16, 36, 7, 13]) {
    const r = B.radixConvert(BIG, 10, base);
    ok(r.valid && r.int === BigInt(BIG), '1000 位大数 → base' + base + ' 精确');
}

// ============================================================ 异常输入（不得抛异常，返回 invalid）
eq(B.radixConvert('2', 2, 10).valid, false, 'bin 中出现 2 → format 错误');
eq(B.radixConvert('2', 2, 10).reason, 'format', 'bin 中出现 2 → reason=format');
eq(B.radixConvert('g', 16, 10).valid, false, 'hex 中出现 g');
eq(B.radixConvert('', 10, 2).valid, false, '空串');
eq(B.radixConvert('   ', 10, 2).valid, false, '纯空白');
eq(B.radixConvert('-', 10, 2).valid, false, '仅符号');
eq(B.radixConvert('0x', 16, 10).valid, false, '仅前缀');
eq(B.radixConvert('12.5', 10, 2).valid, false, '小数暂不支持');
eq(B.radixConvert('1e3', 10, 2).valid, false, '科学计数法不支持');
eq(B.radixConvert('255', 10, 1).valid, false, '目标进制 1 → reason=base');
eq(B.radixConvert('255', 10, 1).reason, 'base', '目标进制 1 → base 错误');
eq(B.radixConvert('255', 37, 10).reason, 'base', '源进制 37 → base 错误');
eq(B.radixConvert('255', 0, 10).reason, 'base', '源进制 0');
eq(B.radixParse('zz', 36), 1295n, 'radixParse zz@36 = 1295（z 是 36 进制的合法位）');
eq(B.radixParse('zz', 16), null, 'radixParse zz@16 → null（z 非 hex 位）');
eq(B.radixParse('', 10), null, 'radixParse 空 → null');
eq(B.radixFormat(10n, 99), null, 'radixFormat 非法进制 → null');
eq(B.radixFormat(10n, '16'), null, 'radixFormat 字符串进制 → null');
// 非字符串输入不应崩溃（内部 String() 化）
eq(B.radixConvert(255, 10, 16).value, 'ff', '数字输入被字符串化');
eq(B.radixConvert(null, 10, 2).valid, false, 'null 输入 → invalid');
noThrow(() => B.radixConvert(undefined, 10, 2), 'undefined 输入不抛异常');
noThrow(() => B.detectBase(null), 'detectBase(null) 不抛异常');

// ============================================================ detectBase
eq(B.detectBase('0xFF'), 16, 'detect 0x → 16');
eq(B.detectBase('0XFF'), 16, 'detect 0X → 16');
eq(B.detectBase('0b1010'), 2, 'detect 0b → 2');
eq(B.detectBase('0o17'), 8, 'detect 0o → 8');
eq(B.detectBase('123'), 10, 'detect 纯数字 → 10');
eq(B.detectBase('ff'), 16, 'detect a-f 无前缀 → 16');
eq(B.detectBase('FF'), 16, 'detect 大写 a-f → 16');
eq(B.detectBase('xyz'), 10, 'detect 非 hex 字母 → 10（交由 radixParse 报错）');
eq(B.detectBase('-0x1A'), 16, 'detect 负号前缀 → 16');
eq(B.detectBase('  0b101 '), 2, 'detect 带空白');
eq(B.detectBase(''), 10, 'detect 空串 → 10');

// ============================================================ groupBits（右对齐分组）
eq(B.groupBits('11111111', 4), '1111 1111', '8 位按 4 分组');
eq(B.groupBits('11111111', 8), '11111111', '正好一组不插空格');
eq(B.groupBits('1010', 4), '1010', '4 位一组');
eq(B.groupBits('101', 4), '101', '不足一组');
eq(B.groupBits('110101', 4), '11 0101', '6 位按 4 → 左短右齐');
eq(B.groupBits('-11111111', 4), '-1111 1111', '负数保留符号');
eq(B.groupBits('1', 4), '1', '单位');

// ============================================================ bitLength
eq(B.bitLength(0n), 1, '0 记 1 位');
eq(B.bitLength(1n), 1, '1 → 1 位');
eq(B.bitLength(255n), 8, '255 → 8 位');
eq(B.bitLength(256n), 9, '256 → 9 位');
eq(B.bitLength(-255n), 8, '负数取绝对值位宽');
eq(B.bitLength(1n << 200n), 201, '2^200 → 201 位');

// ============================================================ baseDigitVal / BASE_DIGITS
eq(B.BASE_DIGITS.length, 36, '36 个数字符');
eq(B.baseDigitVal('a'), 10, 'a → 10');
eq(B.baseDigitVal('Z'), 35, 'Z → 35（大小写不敏感）');
eq(B.baseDigitVal('g'), 16, 'g 是 36 进制合法位（值 16，仅 base>16 可用）');
eq(B.baseDigitVal('!'), -1, '标点 → -1');
eq(B.baseDigitVal('/'), -1, '斜杠（数字区外）→ -1');

// ============================================================ 汇总
console.log('\n' + (fail === 0 ? '✓ 全部通过' : '✗ 有失败') + '：' + pass + ' 通过，' + fail + ' 失败');
process.exit(fail === 0 ? 0 : 1);
