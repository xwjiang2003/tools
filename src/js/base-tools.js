// base-tools.js — 进制/radix 换算簇：任意进制转换 / 二进制 / 十六进制
// 纯函数 + 页面初始化；浏览器与 Node（单测）共用。
// 全程 BigInt 任意精度，避免 2^53 精度丢失；解析失败统一返回 {valid:false, reason}，不抛异常。
// 命名遵循「面向用户」原则：中文用「进制」，不用 radix 黑话；英文以 Base Converter 为主。

// ---------------------------------------------------------------- i18n
// 语言感知：中文页直接显示原串；英文页优先 BASE_MSG 映射，且构建期 localize() 已把源码中文串
// 整体替换为英文，双保险保证英文页零中文残留。
var BASE_MSG = {
    '进制必须在 2~36 之间': 'Base must be between 2 and 36',
    '含有无效字符（不属于所选进制的数字）': 'Contains invalid digits for the selected base',
    '输入过长（超过 4096 位）': 'Input too long (over 4096 digits)',
    '数值过大，已跳过全进制表': 'Value too large; all-base table skipped',
    '二进制只含 0 和 1': 'Binary uses only 0 and 1',
    '十六进制只含 0-9 与 a-f': 'Hex uses only 0-9 and a-f',
    '源进制': 'From base',
    '目标进制': 'To base',
    '自动识别': 'Auto-detect',
    '转换结果': 'Converted',
    '各进制表示': 'Value in every base (2-36)',
    '十进制 (10)': 'Decimal (10)',
    '二进制 (2)': 'Binary (2)',
    '八进制 (8)': 'Octal (8)',
    '十六进制 (16)': 'Hexadecimal (16)',
    '位宽': 'Bit length',
    '按 4 位分组': 'Grouped by 4 bits',
    '按 8 位分组（字节）': 'Grouped by 8 bits (bytes)',
    '字节数': 'Bytes',
    '整字节': 'whole bytes',
    '非整字节': 'not a whole number of bytes',
};

function baseMsg(zh) {
    var code = (document.documentElement.lang || 'zh-CN').slice(0, 2);
    if (code === 'en' && typeof BASE_MSG !== 'undefined' && BASE_MSG[zh]) return BASE_MSG[zh];
    return zh;
}

// datetime-tools.js / id-tools.js 可能已定义；做守卫以防重复声明
if (typeof escapeHtml === 'undefined') {
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }
}
if (typeof debounce === 'undefined') {
    function debounce(fn, ms) {
        var t = null;
        return function () { clearTimeout(t); t = setTimeout(fn, ms); };
    }
}

// ================================================================ 纯函数
var BASE_DIGITS = '0123456789abcdefghijklmnopqrstuvwxyz';

// 单个字符对应的数值（0-9→0-9，a-z→10-35，大小写不敏感）；非法返回 -1
function baseDigitVal(ch) {
    return BASE_DIGITS.indexOf(String(ch).toLowerCase());
}

function baseValid(base) {
    return typeof base === 'number' && isFinite(base) && Math.floor(base) === base && base >= 2 && base <= 36;
}

// 解析某进制字符串为 BigInt；失败返回 null。容忍前后空白、下划线/空格分组、正负号、0x/0b/0o 前缀。
function radixParse(str, base) {
    if (!baseValid(base)) return null;
    var s = String(str).trim().replace(/[\s_]/g, '');
    if (s === '') return null;
    var neg = false;
    if (s.charAt(0) === '+') s = s.slice(1);
    else if (s.charAt(0) === '-') { neg = true; s = s.slice(1); }
    s = s.replace(/^0[xXbBoO]/, ''); // 去掉常见前缀
    if (s === '') return null;
    var val = 0n;
    var B = BigInt(base);
    for (var i = 0; i < s.length; i++) {
        var d = baseDigitVal(s.charAt(i));
        if (d < 0 || d >= base) return null;
        val = val * B + BigInt(d);
    }
    return neg ? -val : val;
}

// 把 BigInt 格式化为某进制字符串（小写）；base 非法返回 null
function radixFormat(value, base) {
    if (!baseValid(base)) return null;
    var v = (typeof value === 'bigint') ? value : BigInt(value);
    if (v === 0n) return '0';
    var neg = v < 0n;
    if (neg) v = -v;
    var B = BigInt(base);
    var out = '';
    while (v > 0n) {
        out = BASE_DIGITS.charAt(Number(v % B)) + out;
        v = v / B;
    }
    return (neg ? '-' : '') + out;
}

// 进制互转：str@from → to。返回 {valid, value, int} 或 {valid:false, reason}
function radixConvert(str, from, to) {
    if (!baseValid(from) || !baseValid(to)) return { valid: false, reason: 'base' };
    var v = radixParse(str, from);
    if (v === null) return { valid: false, reason: 'format' };
    return { valid: true, value: radixFormat(v, to), int: v };
}

// 自动识别源进制：0x→16 / 0b→2 / 0o→8；纯数字→十进制；含 a-f 但无前缀→十六进制；否则十进制。
function detectBase(str) {
    var s = String(str).trim().replace(/^[+-]/, '');
    if (/^0[xX]/.test(s)) return 16;
    if (/^0[bB]/.test(s)) return 2;
    if (/^0[oO]/.test(s)) return 8;
    if (/^[0-9]+$/.test(s)) return 10;
    if (/^[0-9a-fA-F]+$/.test(s)) return 16;
    return 10;
}

// 二进制串从右侧起按 n 位分组（保留符号）
function groupBits(binStr, n) {
    var neg = binStr.charAt(0) === '-';
    var s = neg ? binStr.slice(1) : binStr;
    var out = '';
    for (var i = 0; i < s.length; i++) {
        if (i > 0 && (s.length - i) % n === 0) out += ' ';
        out += s.charAt(i);
    }
    return (neg ? '-' : '') + out;
}

// 位宽（数值部分的二进制位数，0 记 1 位）
function bitLength(v) {
    var m = v < 0n ? -v : v;
    return m === 0n ? 1 : m.toString(2).length;
}

function baseRow(label, value) {
    return '<tr><td class="dt-k">' + escapeHtml(label) + '</td><td class="dt-v mono">' + escapeHtml(String(value)) + '</td></tr>';
}

// 源/目标进制下拉：填充 2~36（数字标签，语言中立）+ 可选「自动识别」
function fillBaseSelect(sel, withAuto) {
    if (!sel) return;
    var html = '';
    if (withAuto) html += '<option value="auto">' + escapeHtml(baseMsg('自动识别')) + '</option>';
    for (var b = 2; b <= 36; b++) html += '<option value="' + b + '">' + b + '</option>';
    sel.innerHTML = html;
    sel.value = withAuto ? 'auto' : '10';
}

// ================================================================ 页面初始化
function initBasePage() {
    var root = document.getElementById('baseTool');
    if (!root) return;
    var input = document.getElementById('baseInput');
    var fromSel = document.getElementById('baseFrom');
    var toSel = document.getElementById('baseTo');
    var result = document.getElementById('baseResult');
    var allBox = document.getElementById('baseAll');
    fillBaseSelect(fromSel, true);
    fillBaseSelect(toSel, false);

    function baseOf(sel) {
        var v = sel.value;
        return v === 'auto' ? 'auto' : parseInt(v, 10);
    }
    function run() {
        var v = input.value.trim();
        if (!v) { result.innerHTML = ''; allBox.innerHTML = ''; return; }
        if (v.replace(/[\s_]/g, '').length > 4096) {
            result.innerHTML = '<div class="hash-output err">' + baseMsg('输入过长（超过 4096 位）') + '</div>';
            allBox.innerHTML = '';
            return;
        }
        var from = baseOf(fromSel);
        var f = from === 'auto' ? detectBase(v) : from;
        var to = baseOf(toSel);
        var r = radixConvert(v, f, to);
        if (!r.valid) {
            result.innerHTML = '<div class="hash-output err">' +
                (r.reason === 'base' ? baseMsg('进制必须在 2~36 之间') : baseMsg('含有无效字符（不属于所选进制的数字）')) + '</div>';
            allBox.innerHTML = '';
            return;
        }
        result.innerHTML = '<div class="base-main-out">' + escapeHtml(r.value) + '</div>';
        // 全进制表：数值过大时降级跳过，避免 35 次大数除法卡顿
        if (bitLength(r.int) > 8192) {
            allBox.innerHTML = '<div class="hash-output warn">' + baseMsg('数值过大，已跳过全进制表') + '</div>';
            return;
        }
        var html = '<table class="dt-batch-table base-all-table"><tbody>';
        for (var b = 2; b <= 36; b++) {
            html += '<tr><td class="dt-k" style="width:52px">' + b + '</td><td class="dt-v mono">' + escapeHtml(radixFormat(r.int, b)) + '</td></tr>';
        }
        html += '</tbody></table>';
        allBox.innerHTML = html;
    }
    input.oninput = function () { debounce(run, 150)(); };
    fromSel.onchange = run;
    toSel.onchange = run;
    run();
}

function initBinaryPage() {
    var root = document.getElementById('binaryTool');
    if (!root) return;
    var input = document.getElementById('binaryInput');
    var result = document.getElementById('binaryResult');
    var extra = document.getElementById('binaryExtra');
    function run() {
        var v = input.value.trim();
        if (!v) { result.innerHTML = ''; if (extra) extra.innerHTML = ''; return; }
        var val = radixParse(v, 2);
        if (val === null) {
            result.innerHTML = '<div class="hash-output err">' + baseMsg('含有无效字符（不属于所选进制的数字）') +
                '（' + baseMsg('二进制只含 0 和 1') + '）</div>';
            if (extra) extra.innerHTML = '';
            return;
        }
        var bin = radixFormat(val, 2).replace('-', '');
        var html = '<table class="dt-batch-table"><tbody>';
        html += baseRow(baseMsg('十进制 (10)'), radixFormat(val, 10));
        html += baseRow(baseMsg('十六进制 (16)'), radixFormat(val, 16));
        html += baseRow(baseMsg('八进制 (8)'), radixFormat(val, 8));
        html += baseRow(baseMsg('位宽'), bin.length);
        html += '</tbody></table>';
        result.innerHTML = html;
        if (extra) {
            extra.innerHTML = '<table class="dt-batch-table"><tbody>' +
                baseRow(baseMsg('按 4 位分组'), groupBits(bin, 4)) +
                baseRow(baseMsg('按 8 位分组（字节）'), groupBits(bin, 8)) +
                '</tbody></table>';
        }
    }
    input.oninput = function () { debounce(run, 150)(); };
    run();
}

function initHexPage() {
    var root = document.getElementById('hexTool');
    if (!root) return;
    var input = document.getElementById('hexInput');
    var result = document.getElementById('hexResult');
    var extra = document.getElementById('hexExtra');
    function run() {
        var v = input.value.trim();
        if (!v) { result.innerHTML = ''; if (extra) extra.innerHTML = ''; return; }
        var val = radixParse(v, 16);
        if (val === null) {
            result.innerHTML = '<div class="hash-output err">' + baseMsg('含有无效字符（不属于所选进制的数字）') +
                '（' + baseMsg('十六进制只含 0-9 与 a-f') + '）</div>';
            if (extra) extra.innerHTML = '';
            return;
        }
        var hex = radixFormat(val, 16);
        var mag = hex.replace('-', '');
        var html = '<table class="dt-batch-table"><tbody>';
        html += baseRow(baseMsg('十进制 (10)'), radixFormat(val, 10));
        html += baseRow(baseMsg('二进制 (2)'), groupBits(radixFormat(val, 2).replace('-', ''), 4));
        html += baseRow(baseMsg('八进制 (8)'), radixFormat(val, 8));
        html += baseRow(baseMsg('十六进制 (16)'), hex);
        html += baseRow(baseMsg('字节数'), (mag.length % 2 === 0 ? mag.length / 2 + ' ' + baseMsg('整字节') : baseMsg('非整字节')));
        html += '</tbody></table>';
        result.innerHTML = html;
        if (extra) {
            // 次要面板：各进制速览（跳过超大数以保流畅）
            if (bitLength(val) > 8192) {
                extra.innerHTML = '<div class="hash-output warn">' + baseMsg('数值过大，已跳过全进制表') + '</div>';
            } else {
                var h = '<table class="dt-batch-table base-all-table"><tbody>';
                for (var b = 2; b <= 36; b++) {
                    if (b === 16) continue;
                    h += '<tr><td class="dt-k" style="width:52px">' + b + '</td><td class="dt-v mono">' + escapeHtml(radixFormat(val, b)) + '</td></tr>';
                }
                h += '</tbody></table>';
                extra.innerHTML = h;
            }
        }
    }
    input.oninput = function () { debounce(run, 150)(); };
    run();
}

// Node 单测导出（浏览器中 module 为 undefined，自动跳过）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        BASE_DIGITS: BASE_DIGITS,
        baseDigitVal: baseDigitVal, baseValid: baseValid,
        radixParse: radixParse, radixFormat: radixFormat, radixConvert: radixConvert,
        detectBase: detectBase, groupBits: groupBits, bitLength: bitLength,
    };
}
