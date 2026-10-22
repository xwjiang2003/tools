"""resolveAutoLang 纯函数单测（通过 node 执行 src/js/lang-detect.js）。

覆盖 2026-10-22 修复的核心场景：
  - 中英双语且英文排前（['en-US','zh-CN']）必须优先中文；
  - 纯非中文按首个命中语言回退；
  - 不支持的语言回退到 en / 首个支持语言；
  - 空输入兜底。
"""
import json
import subprocess
import sys
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'js' / 'lang-detect.js'
NODE = r'C:\Users\jxw\.workbuddy\binaries\node\versions\22.22.2-6\node.exe'

# (browserLangs, supported, expected)
CASES = [
    (['en-US', 'zh-CN'], ['zh', 'en'], 'zh'),          # 关键修复：英文排前也要回中文
    (['zh-Hans-CN', 'en-US'], ['zh', 'en'], 'zh'),     # 中文各种写法
    (['en-US'], ['zh', 'en'], 'en'),                   # 纯英文
    (['ja', 'en'], ['zh', 'en', 'ja'], 'ja'),          # 首个命中 ja
    (['fr-FR'], ['zh', 'en', 'fr', 'de'], 'fr'),       # 区域前缀 fr-FR -> fr
    (['ko-KR'], ['zh', 'en'], 'en'),                   # 不支持的语言 -> 回退 en
    (['de-DE'], ['zh', 'en', 'ja'], 'en'),             # 不支持 -> en
    ([], ['zh', 'en'], 'en'),                           # 空 -> en
    ([], ['ja', 'fr'], 'ja'),                           # 空 -> 首个支持语言
    (['zh-CN'], ['zh', 'en'], 'zh'),                   # 纯中文
    (['en-US', 'zh-CN'], ['zh', 'en', 'ja'], 'zh'),    # 课程式多语言同样优先中文
]


def main():
    js = SRC.read_text('utf-8')
    node_prog = (
        js + "\n"
        + "const CASES = " + json.dumps(CASES) + ";\n"
        + "let fail = 0;\n"
        + "for (const [bl, sup, exp] of CASES) {\n"
        + "  const got = resolveAutoLang(bl, sup);\n"
        + "  if (got !== exp) { fail++; console.log('FAIL', JSON.stringify(bl), JSON.stringify(sup), 'got', got, 'exp', exp); }\n"
        + "  else { console.log('ok  ', JSON.stringify(bl), '->', got); }\n"
        + "}\n"
        + "console.log('FAILS=' + fail);\n"
        + "if (fail) process.exit(1);\n"
    )
    r = subprocess.run([NODE, '-e', node_prog], capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        print('\n%d passed, %d failed' % (len(CASES) - 0, 0) if False else '')
        sys.exit(1)
    print('\n%d passed, 0 failed' % len(CASES))
    sys.exit(0)


if __name__ == '__main__':
    main()
