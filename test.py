#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器端功能测试：把每个工具真正跑一遍，用已知正确值校验。

起因：MD5 曾经对任意输入都返回同一个常量，而 check.py 只查语法、查不出这种行为错误。
所以这里不查"页面能不能打开"，而是驱动真实 UI 并比对输出。

做法：往构建产物里注入一段测试脚本，跑完把结果写进 <pre id="__testout">，
再用 headless Chrome dump-dom 取回来。不依赖 iframe，也不依赖 --virtual-time 的时序。

用法:
  python3 test.py            # 测试 dist/（默认，中文站）
  python3 test.py --en       # 测试 docs/en/ 英文站
"""

import json
import re
import subprocess
import sys
import threading
import http.server
import functools
import socketserver
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
PORT = 8891

# ---------------------------------------------------------------- 测试脚本

HARNESS = r"""
function __t(name, got, want) {
  got = String(got); want = String(want);
  __res.push({ name: name, ok: got === want, got: got.slice(0, 120), want: want.slice(0, 120) });
}
function __ok(name, cond, detail) {
  __res.push({ name: name, ok: !!cond, got: detail === undefined ? (cond ? 'ok' : 'fail') : String(detail).slice(0,120), want: 'ok' });
}
function __tick(ms) { return new Promise(function (r) { setTimeout(r, ms || 60); }); }
async function __act(fn) { fn(); await __tick(); }
// 页面 init 在 DOMContentLoaded 后 300ms 执行，JSON 页还会再嵌一层 300ms 的
// 演示数据定时器（合计约 600ms）。等待必须长于所有这些定时器，否则演示数据会在
// 测试动作之后把结果覆盖掉，出现「时好时坏」的假失败。取 1600ms 留足余量。
async function __ready() { await __tick(1600); }
// JSON 页额外等演示数据真正写入，确保那个 300ms 定时器已经跑完，
// 否则它可能在两次断言之间插进来把结果覆盖掉（曾导致时好时坏的假失败）。
async function __readyJson() {
  for (var i = 0; i < 80; i++) {
    try { if (typeof getVal === 'function' && getVal('mainJsonInput') === demoJson) return; } catch (e) {}
    await __tick(100);
  }
}
"""

TESTS = {}

TESTS['index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  await __readyJson();
  var out = document.getElementById('jsonResultContent');
  var R = function () { return out.textContent; };

  await __act(function () { setVal('mainJsonInput', '{"b":1,"a":[3,2,1]}'); runJsonOp('format'); });
  __ok('JSON 格式化：输出含换行与缩进', R().indexOf('\n') > 0 && R().indexOf('"b": 1') > 0, R().slice(0,60));

  await __act(function () { runJsonOp('compress'); });
  __t('JSON 压缩：压成一行', R().trim(), '{"b":1,"a":[3,2,1]}');

  await __act(function () { setVal('mainJsonInput', '{"a":1}'); runJsonOp('validate'); });
  __ok('JSON 校验：合法输入通过', R().indexOf('✅') >= 0, R().slice(0,60));

  await __act(function () { setVal('mainJsonInput', '{a:1}'); runJsonOp('validate'); });
  __ok('JSON 校验：非法输入报错', R().indexOf('✅') < 0 && R().length > 0, R().slice(0,60));

  await __act(function () { setVal('mainJsonInput', '{"b":1,"a":2,"c":3}'); runJsonOp('sort'); });
  var s = R();
  __ok('JSON 排序：key 按 A-Z', s.indexOf('"a"') < s.indexOf('"b"') && s.indexOf('"b"') < s.indexOf('"c"'), s.replace(/\s+/g,' ').slice(0,60));

  await __act(function () { setVal('mainJsonInput', 'a"b\\nc'); runJsonOp('escape'); });
  var esc = R();
  await __act(function () { setVal('mainJsonInput', esc.trim()); runJsonOp('unescape'); });
  __ok('JSON 转义/去转义：可往返', R().indexOf('a"b') >= 0, 'esc=' + esc.slice(0,40) + ' unesc=' + R().slice(0,40));

  await __act(function () {
    setVal('jsonpathInput', JSON.stringify({store:{books:[{title:'深入理解计算机系统',price:128}]}}));
    document.getElementById('jsonpathExpr').value = '$.store.books[0].title';
    doJsonPath();
  });
  var jp = document.getElementById('jsonpathResult').textContent;
  __ok('JSONPath：取到嵌套字段', jp.indexOf('深入理解计算机系统') >= 0, jp.replace(/\s+/g,' ').slice(0,80));

  await __act(function () { switchJsonTab('convert'); });
  await __act(function () {
    setVal('convertInput', '[{"a":1,"b":2},{"a":3,"b":4}]');
    document.getElementById('convertFrom').value = 'json';
    document.getElementById('convertTo').value = 'csv';
    doConvert();
  });
  var csv = (typeof getVal === 'function' ? getVal('convertOutput') : '') || '';
  __ok('JSON → CSV：含表头与数据行', csv.indexOf('a') >= 0 && csv.indexOf('1') >= 0 && csv.indexOf('4') >= 0, csv.replace(/\n/g,'|').slice(0,80));

  await __act(function () { switchJsonTab('basic'); });
  await __act(function () { setVal('mainJsonInput', '{"x":[1,2]}'); runJsonOp('tree'); });
  __ok('JSON 树视图：生成节点', document.getElementById('jsonResultContent').innerHTML.indexOf('json-tree') >= 0
        || document.querySelectorAll('#jsonResultContent .tree-node, #jsonResultContent ul').length > 0,
        document.getElementById('jsonResultContent').innerHTML.slice(0,60));

  __done();
})().catch(function (e) { __fail(e); });
"""

TESTS['diff/index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  document.getElementById('textDiffInputA').value = 'line1\nline2\nline3';
  document.getElementById('textDiffInputB').value = 'line1\nCHANGED\nline3\nline4';
  await __act(function () { doTextDiff(); });
  var el = document.getElementById('textDiffResult');
  __ok('文本比对：识别新增行', el.querySelectorAll('.diff-unified-add').length > 0, '新增 ' + el.querySelectorAll('.diff-unified-add').length);
  __ok('文本比对：识别删除行', el.querySelectorAll('.diff-unified-remove').length > 0, '删除 ' + el.querySelectorAll('.diff-unified-remove').length);
  __ok('文本比对：统计文字更新', document.getElementById('diffStatsLabel').textContent.length > 4, document.getElementById('diffStatsLabel').textContent);

  document.getElementById('textDiffInputB').value = 'line1\nline2\nline3';
  await __act(function () { doTextDiff(); });
  __ok('文本比对：完全相同时无差异行',
       el.querySelectorAll('.diff-unified-add').length === 0 &&
       el.querySelectorAll('.diff-unified-remove').length === 0,
       document.getElementById('diffStatsLabel').textContent);
  __done();
})().catch(function (e) { __fail(e); });
"""

TESTS['encode/index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  var out = document.getElementById('encodeResult');
  var R = function () { return out.textContent.trim(); };
  async function op(which, mode, text) {
    document.querySelectorAll('#encodeOpBtns .op-btn').forEach(function (b) {
      b.classList.toggle('active', b.dataset.op === which);
    });
    encodeCurrentOp = which; encodeMode = mode;
    document.getElementById('encodeInput').value = text;
    runEncodeOp(mode);
    await __tick();
    return R();
  }

  __t('Base64 编码', await op('base64', 'encode', 'hello'), 'aGVsbG8=');
  __t('Base64 解码', await op('base64', 'decode', 'aGVsbG8='), 'hello');
  __t('Base64 中文往返', await op('base64', 'decode', await op('base64', 'encode', '中文测试')), '中文测试');
  __t('URL 编码', await op('url', 'encode', 'a b&c'), 'a%20b%26c');
  __t('URL 中文往返', await op('url', 'decode', await op('url', 'encode', '中文 空格')), '中文 空格');
  __t('Unicode 中文往返', await op('unicode', 'decode', await op('unicode', 'encode', '你好')), '你好');
  __t('HTML 实体往返', await op('htmlentity', 'decode', await op('htmlentity', 'encode', '<b>&</b>')), '<b>&</b>');
  __t('Hex 中文往返', await op('hex', 'decode', await op('hex', 'encode', '中文')), '中文');
  __done();
})().catch(function (e) { __fail(e); });
"""

TESTS['regex/index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  document.getElementById('regexPattern').value = '\\d+';
  document.getElementById('regexInput').value = 'a1 b22 c333';
  await __act(function () { liveRegex(); });
  __ok('正则：匹配数量正确', document.getElementById('regexMatchCount').textContent.indexOf('3') >= 0,
       document.getElementById('regexMatchCount').textContent);
  __ok('正则：结果列出匹配项', document.querySelectorAll('#regexResult .match-group').length === 3,
       '命中 ' + document.querySelectorAll('#regexResult .match-group').length + ' 组');

  document.getElementById('regexPattern').value = '(\\w+)@(\\w+)\\.com';
  document.getElementById('regexInput').value = 'mail: bob@example.com';
  await __act(function () { liveRegex(); });
  __ok('正则：捕获分组被展示',
       document.getElementById('regexResult').textContent.indexOf('bob') >= 0 &&
       document.getElementById('regexResult').textContent.indexOf('example') >= 0,
       document.getElementById('regexResult').textContent.replace(/\s+/g,' ').slice(0,80));
  __done();
})().catch(function (e) { __fail(e); });
"""

TESTS['timestamp/index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  document.getElementById('tsInput').value = '1700000000';
  await __act(function () { tsToDate(); });
  var r1 = document.getElementById('tsToDateResult').textContent;
  __ok('时间戳 → 日期：1700000000 应为 2023-11-14/15', /2023-11-1[45]/.test(r1), r1.slice(0,80));

  document.getElementById('tsInput').value = '1700000000000';
  await __act(function () { tsToDate(); });
  __ok('毫秒时间戳：同样解析为 2023-11-1x', /2023-11-1[45]/.test(document.getElementById('tsToDateResult').textContent),
       document.getElementById('tsToDateResult').textContent.slice(0,80));

  document.getElementById('dtInput').value = '2023-11-15T10:00';
  await __act(function () { dateToTs(); });
  var r2 = document.getElementById('dateToTsResult').textContent;
  // 不能用 \b：英文标签是 "ms:"，与数字直接相连，\b 在数字与字母之间不成立
  __ok('日期 → 时间戳：输出 10 位秒级数字', /(?:^|\D)1\d{9}(?:\D|$)/.test(r2), r2.slice(0,80));

  await __act(function () {});
  __ok('实时时钟：显示当前时间戳', /^\d{10}$/.test(document.getElementById('liveClock').textContent.trim()),
       document.getElementById('liveClock').textContent);
  __done();
})().catch(function (e) { __fail(e); });
"""

TESTS['hash/index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  // ---- 纯函数：与公开测试向量比对 ----
  __t('MD5("")', md5(''), 'd41d8cd98f00b204e9800998ecf8427e');
  __t('MD5("abc")', md5('abc'), '900150983cd24fb0d6963f7d28e17f72');
  __t('MD5("中文")（UTF-8）', md5('中文'), 'a7bac2239fcdcb3a067903d8077c4a07');
  __t('MD5(56 字符边界)', md5('a'.repeat(56)), '3b0c8ac703f828b04c6c197006d17218');
  __ok('MD5：不同输入给出不同结果', md5('a') !== md5('b') && md5('') !== md5('a'), md5('a') + ' / ' + md5('b'));

  __t('SHA-1("abc")', await shaHash('SHA-1', 'abc'), 'a9993e364706816aba3e25717850c26c9cd0d89d');
  __t('SHA-256("abc")', await shaHash('SHA-256', 'abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  __t('SHA-512("abc")', await shaHash('SHA-512', 'abc'),
      'ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f');
  __t('SHA-256("中文")（UTF-8）', await shaHash('SHA-256', '中文'),
      '72726d8818f693066ceb69afa364218b692e62ea92b385782363780f47529c21');

  __t('HMAC-SHA256', await hmacHash('SHA-256', 'key', 'The quick brown fox jumps over the lazy dog'),
      'f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8');

  // ---- AES-GCM 加解密往返 ----
  var ct = await aesCrypt('my-secret-key', '机密内容 secret', 'encrypt');
  var pt = await aesCrypt('my-secret-key', ct, 'decrypt');
  __t('AES-GCM：解密还原明文', pt, '机密内容 secret');

  // ---- 走真实 UI ----
  document.getElementById('hashInput').value = 'abc';
  await __act(function () { document.querySelector('#hashOpBtns [data-op="md5"]').click(); });
  await __tick(200);
  __t('UI：MD5 结果正确', document.getElementById('hashResult').textContent.trim(), '900150983cd24fb0d6963f7d28e17f72');

  document.querySelector('#hashOpBtns [data-op="sha256"]').click();
  await __tick(200);
  __t('UI：SHA-256 结果正确', document.getElementById('hashResult').textContent.trim(),
      'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');

  // 换输入后必须变化（这正是当初报的 bug）
  document.getElementById('hashInput').value = 'abcd';
  await __act(function () { document.querySelector('#hashOpBtns [data-op="md5"]').click(); });
  await __tick(200);
  __ok('UI：换输入后哈希随之改变',
       document.getElementById('hashResult').textContent.trim() === 'e2fc714c4727ee9395f324cd2e7f331f',
       document.getElementById('hashResult').textContent.trim());
  __done();
})().catch(function (e) { __fail(e); });
"""

TESTS['formatter/index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  var R = function () { return document.getElementById('codeResult').textContent; };
  await __act(function () {
    document.getElementById('codeInput').value = '<div><p>hi</p><span>x</span></div>';
    document.getElementById('codeOpBtns').querySelector('[data-op="html"]').click();
    document.getElementById('codeIndent').value = '2';
    runCodeOp('format');
  });
  __ok('HTML 格式化：缩进换行', R().indexOf('\n') > 0 && R().indexOf('  <p>') >= 0, JSON.stringify(R().slice(0,50)));

  await __act(function () { runCodeOp('compress'); });
  __ok('HTML 压缩：压成一行', R().indexOf('\n') < 0 && R().indexOf('<div><p>hi</p>') >= 0, JSON.stringify(R()));

  await __act(function () {
    document.getElementById('codeInput').value = 'body{color:red;margin:0}';
    document.getElementById('codeOpBtns').querySelector('[data-op="css"]').click();
    runCodeOp('format');
  });
  __ok('CSS 格式化：展开规则', R().indexOf('\n') > 0 && R().indexOf('color') >= 0, JSON.stringify(R().slice(0,60)));

  await __act(function () {
    document.getElementById('codeInput').value = 'SELECT id,name FROM users WHERE age>18';
    document.getElementById('codeOpBtns').querySelector('[data-op="sql"]').click();
    runCodeOp('format');
  });
  __ok('SQL 格式化：关键字大写并换行', R().indexOf('\n') > 0 && /SELECT/i.test(R()), JSON.stringify(R().slice(0,60)));
  __done();
})().catch(function (e) { __fail(e); });
"""

TESTS['string/index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  var R = function () { return document.getElementById('strResult').textContent; };
  // which 是分类（用于渲染选项），realOp 是按钮实际调用的动作名，两者不同
  async function op(which, text, realOp) {
    document.getElementById('strInput').value = text;
    document.querySelectorAll('#strOpBtns .op-btn').forEach(function (b) {
      b.classList.toggle('active', b.dataset.op === which);
    });
    strCurrentOp = which;
    updateStrOptions();
    runStrOp(realOp || which);
    await __tick();
    return R().trim();
  }

  __t('大小写：转大写', await op('case', 'Hello World', 'upper'), 'HELLO WORLD');

  __t('去重：去掉重复行', await op('dedup', 'b\na\nb\nc\na'), 'b\na\nc');
  __t('排序：按行升序', await op('sort', 'c\na\nb', 'sort-asc'), 'a\nb\nc');

  document.getElementById('strInput').value = 'hello 世界';
  await __act(function () { autoStrCount(); });
  var st = document.getElementById('strStats').textContent;
  __ok('字符统计：字符数与字节数（UTF-8）', /8/.test(st) && /12/.test(st), st.trim());
  __done();
})().catch(function (e) { __fail(e); });
"""

TESTS['generator/index.html'] = HARNESS + r"""
(async function () {
  await __ready();
  var R = function () { return document.getElementById('genResult').textContent.trim(); };
  await __act(function () { genCurrentOp = 'uuid'; updateGenConfig(); });
  await __act(function () { runGenOp(); });
  var u = R().split('\n')[0];
  __ok('UUID v4：格式正确', /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(u), u);
  var u2 = (function () { runGenOp(); return R().split('\n')[0]; })();
  __ok('UUID：两次生成不重复', u !== u2, u + ' / ' + u2);

  await __act(function () { genCurrentOp = 'password'; updateGenConfig(); document.getElementById('pwdLen').value = '24'; });
  await __act(function () { runGenOp(); });
  __ok('随机密码：长度符合设置', R().split('\n')[0].length === 24, '长度=' + R().split('\n')[0].length);

  await __act(function () { genCurrentOp = 'sequence'; updateGenConfig(); });
  await __act(function () {
    document.getElementById('seqStart').value = '1';
    document.getElementById('seqEnd').value = '5';
    document.getElementById('seqStep').value = '1';
    runGenOp();
  });
  __ok('数字序列：1..5', R().replace(/\s+/g, ',').indexOf('1,2,3,4,5') >= 0, R().replace(/\s+/g,' ').slice(0,50));

  await __act(function () { genCurrentOp = 'randomdata'; updateGenConfig(); });
  await __act(function () { document.getElementById('rdType').value = 'email'; document.getElementById('rdCount').value = '3'; runGenOp(); });
  __ok('随机数据：生成 3 个邮箱', R().split('\n').filter(function (x) { return /@/.test(x); }).length === 3,
       R().replace(/\n/g,' | ').slice(0,80));
  __done();
})().catch(function (e) { __fail(e); });
"""

WRAPPER = """
<pre id="__testout"></pre>
<script>
var __res = [];
function __done() { document.getElementById('__testout').textContent = 'TESTJSON' + JSON.stringify(__res) + 'ENDTEST'; }
function __fail(e) { document.getElementById('__testout').textContent = 'TESTJSON' + JSON.stringify([{name:'脚本异常', ok:false, got:String(e && e.message || e), want:'无异常'}]) + 'ENDTEST'; }
__TESTSRC__
</script>
"""


def inject(html, src):
    return html.replace('</body>', WRAPPER.replace('__TESTSRC__', src) + '</body>', 1)


def run_chrome(url):
    cmd = ['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu',
           '--disable-dev-shm-usage', '--virtual-time-budget=9000', '--dump-dom', url]
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    return r.stdout.decode('utf-8', 'replace')


def main():
    base = 'en/' if '--en' in sys.argv else ''
    root = ROOT / 'dist' / base
    if not root.exists():
        print(f'❌ 目录不存在: {root}（先运行 python3 build.py）')
        return 1

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Quiet, directory=str(ROOT / 'dist'))

    class Server(socketserver.TCPServer):
        allow_reuse_address = True       # 必须在 bind 之前生效，所以要写在类上

    # 端口传 0 让系统分配空闲端口，避免上次异常退出留下的 TIME_WAIT 造成
    # "Address already in use"（这个坑踩过一次）
    httpd = Server(('127.0.0.1', 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    total = passed = 0
    failures = []
    try:
        for page, src in TESTS.items():
            print(f'  ... 正在测试 {page[:-11] or "JSON"}', flush=True)
            path = root / page
            if not path.exists():
                print(f'  ⚠️  跳过（不存在）: {page}')
                continue
            rel = path.relative_to(root)                 # 例如 diff/index.html
            tmp = path.with_name('__test_' + path.name)  # 与源页面同目录，避免相对路径失效
            tmp.write_text(inject(path.read_text('utf-8'), src), 'utf-8')
            rel_tmp = rel.with_name(tmp.name)
            try:
                dom = run_chrome(f'http://127.0.0.1:{port}/{base}{rel_tmp.as_posix()}'
                                 f'?lang={"en" if base else "zh"}')
                m = re.search(r'TESTJSON(.*?)ENDTEST', dom, re.S)
                if not m:
                    print(f'  ❌ {page}: 测试脚本未产出结果')
                    failures.append((page, '未产出结果', '', ''))
                    continue
                rows = json.loads(m.group(1))
            finally:
                tmp.unlink(missing_ok=True)

            bad = [r for r in rows if not r['ok']]
            total += len(rows)
            passed += len(rows) - len(bad)
            mark = '✅' if not bad else '❌'
            print(f'  {mark} {page[:-11] or "JSON":<12} {len(rows) - len(bad)}/{len(rows)} 通过', flush=True)
            for r in bad:
                failures.append((page, r['name'], r['got'], r['want']))
    finally:
        httpd.shutdown()

    print()
    if failures:
        print(f'❌ {len(failures)} 项失败（共 {total} 项）：')
        for page, name, got, want in failures:
            print(f'   [{page[:-11] or "json"}] {name}')
            print(f'        实际: {got}')
            print(f'        期望: {want}')
    else:
        print(f'✅ 全部 {total} 项功能测试通过')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
