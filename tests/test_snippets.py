# -*- coding: utf-8 -*-
"""单测：src/snippets.py 的数据完整性与渲染正确性。

覆盖：数据约定（标题/说明双语、代码无中文、id 唯一）、渲染结构
（卡片数/复制按钮/tabs/搜索索引）、英文页零中文、HTML 安全
（代码不得含 </script> 之类会破坏内联脚本的序列）。
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
import snippets as S  # noqa: E402

CJK = re.compile(r'[\u4e00-\u9fff]')

pass_n = 0
fail_n = 0


def eq(actual, expected, msg):
    global pass_n, fail_n
    if actual == expected:
        pass_n += 1
    else:
        fail_n += 1
        print(f'✗ {msg}\n   期望 {expected!r}\n   实际 {actual!r}')


def ok(cond, msg):
    global pass_n, fail_n
    if cond:
        pass_n += 1
    else:
        fail_n += 1
        print(f'✗ {msg}')


# ============================================================ 数据完整性
eq(len(S.SECTIONS), 6, '六个语言分组')
ids = [s['id'] for s in S.SECTIONS]
eq(len(ids), len(set(ids)), '分组 id 唯一')
eq(ids, ['go', 'python', 'js', 'shell', 'sql', 'git'], '分组顺序与 id')
eq(S.total_snippets(), 46, '共 46 条片段')
for s in S.SECTIONS:
    ok(s['name']['zh'] and s['name']['en'], f'{s["id"]} 分组名双语非空')
    ok(s['desc']['zh'] and s['desc']['en'], f'{s["id"]} 分组说明双语非空')
    ok(len(s['items']) >= 6, f'{s["id"]} 每组至少 6 条')

n = 0
for s in S.SECTIONS:
    for it in s['items']:
        n += 1
        tag = f'#{n} {s["id"]}/{it["title"]["zh"]}'
        for f in ('title', 'desc'):
            ok(isinstance(it[f], dict) and it[f].get('zh') and it[f].get('en'),
               f'{tag} {f} 双语非空')
        ok(it['code'] and it['code'].strip(), f'{tag} code 非空')
        # 约定：代码中英共用一份且注释统一英文，不得出现中文
        ok(not CJK.search(it['code']), f'{tag} code 无中文（注释统一英文）')
        # HTML/JS 安全：代码不得含会破坏内联脚本或标签的序列
        for bad in ('</script', '<script', '<!--'):
            ok(bad not in it['code'].lower(), f'{tag} code 不含 {bad}')
eq(n, 46, '遍历到 46 条')

# ============================================================ 渲染：中文页
zh = S.render_body('zh')
eq(zh.count('class="snp-item"'), 46, 'zh 卡片 46')
eq(zh.count('snp-copy'), 46, 'zh 复制按钮 46')
eq(zh.count('data-snp-lang='), 7, 'zh 语言标签 7（全部 + 6 语言）')
eq(zh.count('class="snp-group"'), 6, 'zh 分组 6')
ok('id="snpSearch"' in zh, 'zh 搜索框存在')
ok('id="snpNohit"' in zh, 'zh 无匹配提示存在')
ok('没有匹配的代码片段' in zh, 'zh 无匹配文案')
ok('更新于' in zh and S.UPDATED in zh, 'zh meta 含更新时间')
ok('共 46 条' in zh, 'zh meta 含总数')
ok('copyTextById' in zh, 'zh 复制走 core.js copyTextById')
ok('addEventListener' in zh, 'zh 内联筛选脚本存在')

# ============================================================ 渲染：英文页
en = S.render_body('en')
eq(en.count('class="snp-item"'), 46, 'en 卡片 46')
eq(en.count('class="snp-group"'), 6, 'en 分组 6')
eq(en.count('snp-copy'), 46, 'en 复制按钮 46')
ok(not CJK.findall(en), f'en 正文零中文: {CJK.findall(en)[:5]}')
ok('Search titles' in en, 'en 搜索框占位符')
ok('No matching snippets' in en, 'en 无匹配文案')
ok('46 snippets' in en, 'en meta 含总数')

# ============================================================ 复制按钮 id 唯一且与 onclick 对应
for name, body in (('zh', zh), ('en', en)):
    ids_found = re.findall(r'id="(snp-code-\d+)"', body)
    eq(len(ids_found), 46, f'{name} code id 46 个')
    eq(len(ids_found), len(set(ids_found)), f'{name} code id 唯一')
    ok(all(f"copyTextById('{i}')" in body for i in ids_found), f'{name} 每个 id 都有对应 onclick')

# ============================================================ 搜索索引 data-hay
# 每条卡片都应带 data-hay，且包含标题与代码关键词（当前语言）
hay_count = zh.count('data-hay=')
eq(hay_count, 46, 'zh data-hay 46 条')
ok('data-hay="读取环境变量（带默认值）' in zh, 'zh 索引含标题')
ok('context.WithTimeout' in zh, 'zh 索引含代码内容')
# 英文页不得把中文塞进索引
m = re.search(r'data-hay="([^"]*)"', en)
ok(m and not CJK.search(m.group(1)), 'en 索引无中文')

# ============================================================ 分组 data-lang 与标签对应
for s in S.SECTIONS:
    ok(f'data-lang="{s["id"]}"' in zh, f'zh 分组 {s["id"]} data-lang')
    ok(f'data-snp-lang="{s["id"]}"' in zh, f'zh 标签 {s["id"]} 对应')

# ============================================================ TEXT 双语齐全
# total 允许英文为空串：英文版由 unit（' snippets'）承载措辞，
# 渲染为 '' + '46' + ' snippets'；中文版才是 '共 ' + '46' + ' 条'。
for lang in ('zh', 'en'):
    t = S.TEXT[lang]
    for k in ('lead', 'updated', 'unit', 'tip', 'search', 'all', 'nohit', 'copy'):
        ok(t.get(k), f'TEXT[{lang}].{k} 非空')
ok(S.TEXT['zh']['total'], 'TEXT[zh].total 非空（共 ）')
ok(S.TEXT['en']['total'] == '', 'TEXT[en].total 为空串（由 unit 承载）')
# 英文 TEXT 不得含中文
for k, v in S.TEXT['en'].items():
    ok(not CJK.search(v), f'TEXT[en].{k} 无中文')

print(f'\n{"✅ 全部通过" if fail_n == 0 else "❌ 有失败"}：{pass_n} 通过，{fail_n} 失败')
sys.exit(0 if fail_n == 0 else 1)
