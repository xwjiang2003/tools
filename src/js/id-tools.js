// id-tools.js — 衍生 ID 换算簇：UUID / Snowflake / TID / MongoDB ObjectId / Firebase Push ID
// 纯函数 + 页面初始化；浏览器与 Node（单测）共用。
// 全部解析函数返回 {valid:false, reason} 而非抛异常，便于 UI 友好提示。

// ---------------------------------------------------------------- i18n
// 语言感知：中文页直接显示原串；英文页优先用 ID_MSG 映射，且构建期 localize() 已把源码里的
// 中文串整体替换为英文，双重保险保证英文页零中文残留。
var ID_MSG = {
    'UUID 格式无效': 'Invalid UUID',
    '请输入 UUID': 'Enter a UUID',
    '版本': 'Version',
    '变体': 'Variant',
    '时间戳': 'Timestamp',
    '节点': 'Node',
    '序列': 'Sequence',
    '数据中心': 'Datacenter',
    '工作节点': 'Worker',
    '已生成 UUID v4': 'Generated UUID v4',
    'Snowflake ID 格式无效（请输入纯数字）': 'Invalid Snowflake ID (digits only)',
    '时间字段超出范围（ID 位数超过配置）': 'Timestamp field overflow (ID too long)',
    '节点 / 序列超出范围': 'Node / Sequence out of range',
    'Twitter ID 格式无效（请输入纯数字）': 'Invalid Twitter ID (digits only)',
    '该 ID 早于 Snowflake 纪元，无法反推时间': 'This ID predates the Snowflake epoch; no embedded time',
    'ObjectId 格式无效（需 24 位十六进制）': 'Invalid ObjectId (need 24 hex chars)',
    'Firebase ID 格式无效（需 20 位合法字符）': 'Invalid Firebase ID (need 20 valid chars)',
    '生成': 'Generate',
    '解析': 'Parse',
    '解码': 'Decode',
    '构造': 'Build',
    '复制': 'Copy',
    '结果': 'Result',
    '无效': 'Invalid',
    '有效': 'Valid',
    '创建时间': 'Created',
    '时间戳(毫秒)': 'Timestamp (ms)',
    '随机后缀': 'Random suffix',
    '请先输入内容': 'Enter something first',
    '生成时间': 'Generated time',
    '机器标识': 'Machine',
    '进程标识': 'PID',
    '计数器': 'Counter',
    '毫秒': 'ms',
    '位数过长': 'too many digits',
    '早于 Snowflake 的纯自增 ID': 'pre-Snowflake sequential ID',
    '无法生成（时间早于纪元或超出 41 位）': 'Cannot build (time before epoch or > 41 bits)',
    '无法生成（时间过早或超出范围）': 'Cannot build (time too early or out of range)',
};

function idMsg(zh) {
    var code = (document.documentElement.lang || 'zh-CN').slice(0, 2);
    if (code === 'en' && typeof ID_MSG !== 'undefined' && ID_MSG[zh]) return ID_MSG[zh];
    return zh;
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
}

// ================================================================ UUID
function uuidValidate(s) {
    if (typeof s !== 'string') return false;
    s = s.trim();
    var hex = s.replace(/-/g, '');
    if (hex.length !== 32) return false;
    return /^[0-9a-fA-F]{32}$/.test(hex);
}

function uuidGetVersion(s) {
    var hex = s.replace(/-/g, '');
    return parseInt(hex[12], 16);
}

function uuidGetVariant(s) {
    var n = parseInt(s.replace(/-/g, '')[16], 16);
    if ((n & 0x8) === 0) return 'NCS';
    if ((n & 0xC) === 0x8) return 'RFC4122';
    if ((n & 0xE) === 0xC) return 'Microsoft';
    return 'Reserved';
}

// 100-ns 间隔：1582-10-15 → 1970-01-01
var UUID_GREG = 122192928000000000;

function uuidParse(s) {
    var res = { valid: false };
    if (!uuidValidate(s)) return res;
    var hex = s.replace(/-/g, '');
    var ver = uuidGetVersion(s);
    var variant = uuidGetVariant(s);
    res.valid = true;
    res.version = ver;
    res.variant = variant;
    if (ver === 1 || ver === 2) {
        var tl = parseInt(hex.substr(0, 8), 16);
        var tm = parseInt(hex.substr(8, 4), 16);
        var th = parseInt(hex.substr(12, 4), 16);
        var ts = (th & 0x0FFF) * 0x1000000000000 + tm * 0x100000000 + tl; // 60-bit 100ns ticks: hi<<48 | mid<<32 | low
        // 转为 Unix 毫秒：先扣除 1582→1970 的 100ns 间隔偏移，再 100ns→ms(÷10000)
        var ms = (ts - UUID_GREG) / 10000;
        res.timestampMs = ms;
        res.date = new Date(ms).toISOString();
        res.node = hex.substr(20, 12);
    }
    return res;
}

function uuidV4() {
    var bytes = new Uint8Array(16);
    if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
        crypto.getRandomValues(bytes);
    } else {
        for (var i = 0; i < 16; i++) bytes[i] = Math.floor(Math.random() * 256);
    }
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    var h = [];
    for (var j = 0; j < 16; j++) h.push(bytes[j].toString(16).padStart(2, '0'));
    return h.slice(0, 4).join('') + '-' + h.slice(4, 6).join('') + '-' + h.slice(6, 8).join('') +
        '-' + h.slice(8, 10).join('') + '-' + h.slice(10, 16).join('');
}

// ================================================================ Snowflake
var SF_PRESETS = {
    twitter: { epoch: 1288834974657, tsBits: 41, nodeBits: 10, stepBits: 12 },
    discord: { epoch: 1420070400000, tsBits: 41, nodeBits: 10, stepBits: 12 },
};

// 通用 Snowflake 解码：idStr 为十进制字符串（必须字符串传入，避免 2^53 精度丢失）
function sfDecode(idStr, cfg) {
    var s = String(idStr).trim();
    if (!/^\d+$/.test(s)) return { valid: false, reason: 'format' };
    var id = BigInt(s);
    var total = cfg.tsBits + cfg.nodeBits + cfg.stepBits;
    if (id >> BigInt(total) !== 0n) return { valid: false, reason: 'overflow' };
    var stepMask = (1n << BigInt(cfg.stepBits)) - 1n;
    var nodeMask = (1n << BigInt(cfg.nodeBits)) - 1n;
    var step = id & stepMask;
    var node = (id >> BigInt(cfg.stepBits)) & nodeMask;
    var ts = id >> BigInt(cfg.nodeBits + cfg.stepBits);
    var timestampMs = Number(ts) + cfg.epoch;
    return {
        valid: true, step: Number(step), node: Number(node),
        timestampMs: timestampMs, date: new Date(timestampMs).toISOString(), epoch: cfg.epoch,
    };
}

function sfEncode(tsMs, node, step, cfg) {
    var ts = BigInt(Math.floor(tsMs)) - BigInt(cfg.epoch);
    if (ts < 0n) return { valid: false, reason: 'time-before-epoch' };
    if (ts >= (1n << BigInt(cfg.tsBits))) return { valid: false, reason: 'time-overflow' };
    var n = BigInt(node), st = BigInt(step);
    if (n < 0n || n >= (1n << BigInt(cfg.nodeBits))) return { valid: false, reason: 'node-overflow' };
    if (st < 0n || st >= (1n << BigInt(cfg.stepBits))) return { valid: false, reason: 'step-overflow' };
    var id = (ts << BigInt(cfg.nodeBits + cfg.stepBits)) | (n << BigInt(cfg.stepBits)) | st;
    return { valid: true, id: id.toString() };
}

// ================================================================ TID (Twitter / X)
var TWITTER_EPOCH = 1288834974657;
var TWITTER_PRE = 29700859247; // 该值及更小的 ID 早于 Snowflake，是纯自增数字

function tidToTime(idStr) {
    var s = String(idStr).trim();
    if (!/^\d+$/.test(s)) return { valid: false, reason: 'format' };
    var id = BigInt(s);
    if (id <= BigInt(TWITTER_PRE)) return { valid: true, predates: true };
    return sfDecode(s, { tsBits: 41, nodeBits: 10, stepBits: 12, epoch: TWITTER_EPOCH });
}

function timeToTid(ms) {
    return sfEncode(ms, 0, 0, { tsBits: 41, nodeBits: 10, stepBits: 12, epoch: TWITTER_EPOCH });
}

// ================================================================ MongoDB ObjectId
function oidValidate(s) {
    return /^[0-9a-fA-F]{24}$/.test(String(s).trim());
}

function oidDecode(s) {
    s = String(s).trim();
    if (!oidValidate(s)) return { valid: false, reason: 'format' };
    var ts = parseInt(s.substr(0, 8), 16);
    return {
        valid: true, timestampSec: ts, date: new Date(ts * 1000).toISOString(),
        machine: s.substr(8, 6), pid: s.substr(14, 4), counter: s.substr(18, 6),
    };
}

function oidGenerate() {
    var ts = Math.floor(Date.now() / 1000).toString(16).padStart(8, '0');
    function r(n) { var x = ''; for (var i = 0; i < n; i++) x += Math.floor(Math.random() * 16).toString(16); return x; }
    // 4 字节时间 + 3 字节机器 + 2 字节进程 + 3 字节计数器 = 24 hex
    return ts + r(6) + r(4) + r(6);
}

// ================================================================ Firebase Push ID
// 字母表（顺序关键），8 位时间戳以「最高位在前」写入，保证字典序 ≈ 时间顺序
var FB_CHARS = '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz';

function fbValidate(s) {
    s = String(s).trim();
    if (s.length !== 20) return false;
    for (var i = 0; i < 20; i++) if (FB_CHARS.indexOf(s[i]) < 0) return false;
    return true;
}

function fbDecode(s) {
    s = String(s).trim();
    if (!fbValidate(s)) return { valid: false, reason: 'format' };
    var ts = 0;
    for (var i = 0; i < 8; i++) ts = ts * 64 + FB_CHARS.indexOf(s[i]); // 最高位在前
    return { valid: true, timestampMs: ts, date: new Date(ts).toISOString() };
}

function fbEncode(tsMs) {
    var n = Math.floor(tsMs);
    if (n < 0 || n >= Math.pow(64, 8)) return { valid: false, reason: 'range' };
    var arr = [];
    for (var i = 7; i >= 0; i--) { arr[i] = FB_CHARS[n % 64]; n = Math.floor(n / 64); }
    var id = arr.join('');
    for (var j = 0; j < 12; j++) id += FB_CHARS[Math.floor(Math.random() * 64)];
    return { valid: true, id: id };
}

// ================================================================ 展示辅助（浏览器）
function idFmtDate(ms) {
    var d = new Date(ms);
    var utc = d.toISOString();
    var local = d.toLocaleString();
    return utc + '  (UTC)<br><span style="opacity:.7">' + escapeHtml(local) + ' (本地)</span>';
}

function idRow(label, value) {
    return '<tr><td class="dt-k">' + escapeHtml(label) + '</td><td class="dt-v">' + escapeHtml(String(value)) + '</td></tr>';
}

// ================================================================ 页面初始化
function initUuidPage() {
    var root = document.getElementById('uuidTool');
    if (!root) return;
    var input = document.getElementById('uuidInput');
    var genBtn = document.getElementById('uuidGenBtn');
    var result = document.getElementById('uuidResult');
    function run() {
        var v = input.value.trim();
        if (!v) { result.innerHTML = ''; return; }
        if (!uuidValidate(v)) {
            result.innerHTML = '<div class="hash-output err">' + idMsg('UUID 格式无效') + '</div>';
            return;
        }
        var p = uuidParse(v);
        var html = '<table class="dt-batch-table"><tbody>';
        html += idRow(idMsg('有效'), '✓ RFC4122');
        html += idRow(idMsg('版本'), p.version);
        html += idRow(idMsg('变体'), p.variant);
        if (p.version === 1 || p.version === 2) {
            html += idRow(idMsg('时间戳') + ' (ms)', p.timestampMs);
            html += idRow(idMsg('创建时间'), idFmtDate(p.timestampMs));
            html += idRow(idMsg('节点'), p.node);
        }
        html += '</tbody></table>';
        result.innerHTML = html;
    }
    input.oninput = function () { debounce(run, 200)(); };
    if (genBtn) genBtn.onclick = function () {
        input.value = uuidV4(); run();
    };
    run();
}

function initSnowflakePage() {
    var root = document.getElementById('sfTool');
    if (!root) return;
    var preset = document.getElementById('sfPreset');
    var epochRow = document.getElementById('sfEpochRow');
    var epochInput = document.getElementById('sfEpoch');
    var idInput = document.getElementById('sfId');
    var decRes = document.getElementById('sfDecodeResult');
    var dateInput = document.getElementById('sfDate');
    var nodeInput = document.getElementById('sfNode');
    var stepInput = document.getElementById('sfStep');
    var encBtn = document.getElementById('sfEncodeBtn');
    var encRes = document.getElementById('sfEncodeResult');
    function cfg() {
        var name = preset.value;
        if (name === 'custom') return { epoch: parseInt(epochInput.value, 10) || 0, tsBits: 41, nodeBits: 10, stepBits: 12 };
        return SF_PRESETS[name];
    }
    function syncEpoch() { epochRow.style.display = preset.value === 'custom' ? '' : 'none'; }
    preset.onchange = function () { syncEpoch(); runDecode(); };
    if (epochInput) epochInput.oninput = runDecode;
    function runDecode() {
        var v = idInput.value.trim();
        if (!v) { decRes.innerHTML = ''; return; }
        var r = sfDecode(v, cfg());
        if (!r.valid) {
            decRes.innerHTML = '<div class="hash-output err">' +
                (r.reason === 'format' ? idMsg('Snowflake ID 格式无效（请输入纯数字）') :
                    idMsg('时间字段超出范围（ID 位数超过配置）')) + '</div>';
            return;
        }
        var html = '<table class="dt-batch-table"><tbody>';
        html += idRow(idMsg('时间戳') + ' (ms)', r.timestampMs);
        html += idRow(idMsg('创建时间'), idFmtDate(r.timestampMs));
        html += idRow(idMsg('节点'), r.node);
        html += idRow(idMsg('序列'), r.step);
        html += '</tbody></table>';
        decRes.innerHTML = html;
    }
    idInput.oninput = function () { debounce(runDecode, 200)(); };
    if (encBtn) encBtn.onclick = function () {
        var ms = dtParseDateInputSafe(dateInput.value);
        if (ms === null) { encRes.innerHTML = '<div class="hash-output err">' + idMsg('请先输入内容') + '</div>'; return; }
        var node = parseInt(nodeInput.value, 10) || 0;
        var step = parseInt(stepInput.value, 10) || 0;
        var r = sfEncode(ms, node, step, cfg());
        if (!r.valid) { encRes.innerHTML = '<div class="hash-output err">' + idMsg('无法生成（时间早于纪元或超出 41 位）') + '</div>'; return; }
        encRes.innerHTML = '<table class="dt-batch-table"><tbody>' +
            idRow('ID', r.id) + '</tbody></table>';
    };
    syncEpoch();
    runDecode();
}

function initTidPage() {
    var root = document.getElementById('tidTool');
    if (!root) return;
    var idInput = document.getElementById('tidId');
    var decRes = document.getElementById('tidResult');
    var dateInput = document.getElementById('tidDate');
    var encBtn = document.getElementById('tidEncodeBtn');
    var encRes = document.getElementById('tidEncodeResult');
    function runDecode() {
        var v = idInput.value.trim();
        if (!v) { decRes.innerHTML = ''; return; }
        var r = tidToTime(v);
        if (!r.valid) {
            decRes.innerHTML = '<div class="hash-output err">' + idMsg('Twitter ID 格式无效（请输入纯数字）') + '</div>';
            return;
        }
        if (r.predates) {
            decRes.innerHTML = '<div class="hash-output warn">' + idMsg('该 ID 早于 Snowflake 纪元，无法反推时间') +
                '（' + idMsg('早于 Snowflake 的纯自增 ID') + '）</div>';
            return;
        }
        var html = '<table class="dt-batch-table"><tbody>';
        html += idRow(idMsg('时间戳') + ' (ms)', r.timestampMs);
        html += idRow(idMsg('创建时间'), idFmtDate(r.timestampMs));
        html += idRow(idMsg('节点'), r.node);
        html += idRow(idMsg('序列'), r.step);
        html += '</tbody></table>';
        decRes.innerHTML = html;
    }
    idInput.oninput = function () { debounce(runDecode, 200)(); };
    if (encBtn) encBtn.onclick = function () {
        var ms = dtParseDateInputSafe(dateInput.value);
        if (ms === null) { encRes.innerHTML = '<div class="hash-output err">' + idMsg('请先输入内容') + '</div>'; return; }
        var r = timeToTid(ms);
        if (!r.valid) { encRes.innerHTML = '<div class="hash-output err">' + idMsg('无法生成（时间早于纪元或超出 41 位）') + '</div>'; return; }
        encRes.innerHTML = '<table class="dt-batch-table"><tbody>' + idRow('ID', r.id) + '</tbody></table>';
    };
    runDecode();
}

function initObjectIdPage() {
    var root = document.getElementById('oidTool');
    if (!root) return;
    var input = document.getElementById('oidInput');
    var genBtn = document.getElementById('oidGenBtn');
    var result = document.getElementById('oidResult');
    function run() {
        var v = input.value.trim();
        if (!v) { result.innerHTML = ''; return; }
        if (!oidValidate(v)) {
            result.innerHTML = '<div class="hash-output err">' + idMsg('ObjectId 格式无效（需 24 位十六进制）') + '</div>';
            return;
        }
        var p = oidDecode(v);
        var html = '<table class="dt-batch-table"><tbody>';
        html += idRow(idMsg('时间戳') + ' (s)', p.timestampSec);
        html += idRow(idMsg('创建时间'), idFmtDate(p.timestampSec * 1000));
        html += idRow(idMsg('机器标识'), p.machine);
        html += idRow(idMsg('进程标识'), p.pid);
        html += idRow(idMsg('计数器'), p.counter);
        html += '</tbody></table>';
        result.innerHTML = html;
    }
    input.oninput = function () { debounce(run, 200)(); };
    if (genBtn) genBtn.onclick = function () { input.value = oidGenerate(); run(); };
    run();
}

function initFirebasePage() {
    var root = document.getElementById('fbTool');
    if (!root) return;
    var input = document.getElementById('fbInput');
    var genBtn = document.getElementById('fbGenBtn');
    var dateInput = document.getElementById('fbDate');
    var genDateBtn = document.getElementById('fbGenDateBtn');
    var result = document.getElementById('fbResult');
    function run() {
        var v = input.value.trim();
        if (!v) { result.innerHTML = ''; return; }
        if (!fbValidate(v)) {
            result.innerHTML = '<div class="hash-output err">' + idMsg('Firebase ID 格式无效（需 20 位合法字符）') + '</div>';
            return;
        }
        var p = fbDecode(v);
        var html = '<table class="dt-batch-table"><tbody>';
        html += idRow(idMsg('时间戳') + ' (ms)', p.timestampMs);
        html += idRow(idMsg('创建时间'), idFmtDate(p.timestampMs));
        html += idRow(idMsg('随机后缀'), v.substr(8));
        html += '</tbody></table>';
        result.innerHTML = html;
    }
    input.oninput = function () { debounce(run, 200)(); };
    function gen(tsMs) {
        var r = fbEncode(tsMs);
        if (!r.valid) { result.innerHTML = '<div class="hash-output err">' + idMsg('无法生成（时间过早或超出范围）') + '</div>'; return; }
        input.value = r.id; run();
    }
    if (genBtn) genBtn.onclick = function () { gen(Date.now()); };
    if (genDateBtn) genDateBtn.onclick = function () {
        var ms = dtParseDateInputSafe(dateInput.value);
        if (ms === null) { result.innerHTML = '<div class="hash-output err">' + idMsg('请先输入内容') + '</div>'; return; }
        gen(ms);
    };
    run();
}

// datetime-tools.js 已定义 debounce / escapeHtml；此处再定义一份以备 Node 单测环境
if (typeof debounce === 'undefined') {
    function debounce(fn, ms) {
        var t = null;
        return function () { clearTimeout(t); t = setTimeout(fn, ms); };
    }
}
// 安全解析 datetime-local 输入为毫秒（datetime-tools.dtParseDateInput 返回秒，这里统一成毫秒）
function dtParseDateInputSafe(val) {
    if (typeof dtParseDateInput === 'function') {
        var sec = dtParseDateInput(val, 'UTC');
        return sec === null ? null : sec * 1000;
    }
    if (!val) return null;
    var d = new Date(val);
    if (isNaN(d.getTime())) return null;
    return d.getTime();
}

// Node 单测导出（浏览器中 module 为 undefined，自动跳过）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        uuidValidate: uuidValidate, uuidGetVersion: uuidGetVersion, uuidGetVariant: uuidGetVariant,
        uuidParse: uuidParse, uuidV4: uuidV4,
        SF_PRESETS: SF_PRESETS, sfDecode: sfDecode, sfEncode: sfEncode,
        TWITTER_EPOCH: TWITTER_EPOCH, TWITTER_PRE: TWITTER_PRE, tidToTime: tidToTime, timeToTid: timeToTid,
        oidValidate: oidValidate, oidDecode: oidDecode, oidGenerate: oidGenerate,
        FB_CHARS: FB_CHARS, fbValidate: fbValidate, fbDecode: fbDecode, fbEncode: fbEncode,
    };
}
