"""工具页内联脚本不变量测试。

背景 bug（2026-10-15 修复）：src/index.html 模板把 {{TOOL}} 放在 <main>，
而 core.js 与各 js 模块的 <script> 在 </footer> 之后 —— 工具 body 里的内联
IIFE 永远先于 core.js 执行。导致两类故障：
  1. IIFE 末尾的初始渲染调用（如 csvConvert()）在解析期执行，其内部的
     getVal()/setVal() 尚未定义 → 每次加载都抛 ReferenceError（控制台红字）；
  2. onclick="csvConvert()" 引用 IIFE 局部函数，全局作用域找不到 → 主按钮
     点击报 "is not defined"（清空/示例按钮因显式 window. 挂载而幸免）。
受损面：csv/toml/yaml/case/jwt（两类全中）+ color（仅第 1 类）。

本测试在源码层强制修复后的不变量，防止回归：
  A. 每个 onclick="fn(" 引用的函数必须全局可解析（core.js/js 模块顶层
     function 声明、window. 挂载、或页面自身 window. 挂载）；
  B. 内联 IIFE 末尾的裸初始调用必须被 readyState 守卫包裹
     （document.readyState==='loading' → DOMContentLoaded 延迟）。
"""
import re
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / 'src'
TOOLS = SRC / 'tools'
JS = SRC / 'js'

# core.js + 全部 js 模块的顶层 function 声明与 window. 挂载 = 全局可用函数
GLOBAL_FUNCS = set()
for f in [JS / 'core.js'] + sorted(JS.glob('*.js')):
    t = f.read_text('utf-8')
    GLOBAL_FUNCS |= set(re.findall(r'^function\s+(\w+)\s*\(', t, re.M))
    GLOBAL_FUNCS |= set(re.findall(r'window\.(\w+)\s*=', t))

PASS = FAIL = 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print('FAIL: ' + msg)


def test_onclick_resolvable():
    """不变量 A：onclick 目标必须全局可解析。"""
    for f in sorted(TOOLS.glob('*.html')):
        t = f.read_text('utf-8')
        onclick_fns = set(re.findall(r'onclick="(\w+)\(', t))
        exposed = set(re.findall(r'window\.(\w+)\s*=', t))
        for fn in onclick_fns:
            check(fn in GLOBAL_FUNCS or fn in exposed,
                  '%s: onclick=%s 既非全局函数也未 window 挂载（IIFE 局部函数不可点击）' % (f.name, fn))


def test_init_call_guarded():
    """不变量 B：IIFE 末尾裸初始调用必须 readyState 守卫。

    工具脚本先于 core.js 执行，初始渲染若在解析期跑，内部 getVal/setVal 必抛
    ReferenceError。合法形态只有一种：readyState 守卫 + DOMContentLoaded。
    """
    guarded = re.compile(
        r"if\s*\(\s*document\.readyState\s*===\s*'loading'\s*\)\s*\{"
        r"\s*document\.addEventListener\s*\(\s*'DOMContentLoaded'\s*,\s*(\w+)\s*\)"
        r"\s*\}\s*else\s*\{\s*\1\(\)\s*;?\s*\}")
    for f in sorted(TOOLS.glob('*.html')):
        t = f.read_text('utf-8')
        scripts = re.findall(r'<script>(.*?)</script>', t, re.S)
        if not scripts:
            continue
        s = scripts[0]
        # IIFE 末尾形如 "  fn();\n})();" 的裸调用（守卫形态不会匹配此模式）
        bare = re.findall(r'\n\s*(\w+)\(\)\s*;?\s*\n\s*\}\)\(\);', s)
        for fn in bare:
            check(False, '%s: IIFE 末尾裸调用 %s() 未加 readyState 守卫'
                  '（解析期先于 core.js 执行，内部 getVal/setVal 会抛 ReferenceError）'
                  % (f.name, fn))
        # 有守卫的页面，守卫形态必须存在
        if guarded.search(s):
            check(True, '')


def test_fixed_pages_exposed():
    """6 个修复页的主操作函数必须 window 挂载（onclick 入口）。"""
    expected = {
        'csv.html': 'csvConvert',
        'toml.html': 'tomlConvert',
        'yaml.html': 'yamlConvert',
        'case.html': 'caseConvert',
        'jwt.html': 'jwtDecode',
    }
    for name, fn in expected.items():
        t = (TOOLS / name).read_text('utf-8')
        check(('window.%s=%s;' % (fn, fn)) in t,
              '%s: 缺少 window.%s 挂载' % (name, fn))


def test_no_bare_init_anywhere():
    """兜底：任何工具页内联脚本不得在 IIFE 末尾留裸初始调用（含 color 的 render）。"""
    for f in sorted(TOOLS.glob('*.html')):
        t = f.read_text('utf-8')
        scripts = re.findall(r'<script>(.*?)</script>', t, re.S)
        if not scripts:
            continue
        s = scripts[0]
        bare = re.findall(r'\n\s*(\w+)\(\)\s*;?\s*\n\s*\}\)\(\);', s)
        check(not bare, '%s: 仍有未守卫的初始调用 %s' % (f.name, bare))


if __name__ == '__main__':
    test_onclick_resolvable()
    test_init_call_guarded()
    test_fixed_pages_exposed()
    test_no_bare_init_anywhere()
    print('\n%d passed, %d failed' % (PASS, FAIL))
    raise SystemExit(1 if FAIL else 0)
