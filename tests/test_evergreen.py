# -*- coding: utf-8 -*-
"""年度常青页生成器的单元测试。

覆盖：闰年/天数/ISO 周数算法、日历单元格数、英文页零中文、跨年标记本地化、
以及对外清单（路径数 / 导航年份）。直接跑：python tests/test_evergreen.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
import evergreen as E  # noqa: E402

CJK = re.compile(r'[\u4e00-\u9fff]')

PASS = 0
FAIL = 0


def ok(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f'  ❌ {msg}')


def eq(a, b, msg):
    ok(a == b, f'{msg} (expected {b!r}, got {a!r})')


# ------------------------------------------------------------ 算法

def test_algorithms():
    # 闰年
    eq(E.is_leap(2024), True, '2024 闰年')
    eq(E.is_leap(2025), False, '2025 平年')
    eq(E.is_leap(2000), True, '2000 闰年(400)')
    eq(E.is_leap(1900), False, '1900 平年(100 非 400)')
    # 天数
    eq(E.days_in_year(2024), 366, '2024 366 天')
    eq(E.days_in_year(2025), 365, '2025 365 天')
    # ISO 周数（与 Python isocalendar 交叉验证 + 已知事实）
    expect = {2023: 52, 2024: 52, 2025: 52, 2026: 53, 2027: 52, 2028: 52, 2029: 52, 2030: 52}
    for y, w in expect.items():
        eq(E.iso_week_count(y), w, f'{y} ISO 周数={w}')
    # iso_monday：第 1 周周一必然 <= 1 月 7 日且为周一
    from datetime import date, timedelta
    for y in E.YEAR_RANGE:
        m1 = E.iso_monday(y, 1)
        eq(m1.isoweekday(), 1, f'{y} 第1周周一是周一')
        # ISO 第 1 周周一落在 [上年12-29, 本年1-4] 之间（可能跨年）
        ok(date(y - 1, 12, 29) <= m1 <= date(y, 1, 4), f'{y} 第1周周一区间正确')
        # 最后一周的周日 >= 12 月 24 日
        ml = E.iso_monday(y, E.iso_week_count(y)) + timedelta(days=6)
        ok(ml >= date(y, 12, 24), f'{y} 最后一周覆盖年末')


# ------------------------------------------------------------ 渲染完整性

def test_render_counts():
    for t, y, slug, path in E.evergreen_entries():
        body = E.render_body(t, y, 'zh', '../../')
        if t == 'calendar':
            n = body.count('data-date="20')  # 排除 today 脚本里的 [data-date="
            eq(n, E.days_in_year(y), f'calendar {y} 格子数=天数')
        if t == 'days':
            # 表头外每行一天
            rows = body.count('<tr>') - 1
            eq(rows, E.days_in_year(y), f'days {y} 行数=天数')
        if t == 'weeks':
            rows = body.count('<tr>') - 1
            eq(rows, E.iso_week_count(y), f'weeks {y} 行数=周数')


# ------------------------------------------------------------ 英文零中文

def test_english_no_cjk():
    for t, y, slug, path in E.evergreen_entries():
        base = '../../../en/'
        body = E.render_body(t, y, 'en', base)
        seo = E.render_seo(t, y, 'en', base)
        m = E.meta(t, y, 'en')
        blob = [body, m['title'], m['description'], m['keywords'], m['h1']]
        blob += seo['intro']
        blob += [name for name, _ in seo['features']]
        blob += seo['steps']
        blob += [q for q, _ in seo['faq']] + [a for _, a in seo['faq']]
        blob += [txt for txt, _ in seo['seealso']]
        for chunk in blob:
            ok(not CJK.search(chunk), f'en {t}/{y} 零中文: {chunk[:30]!r}')


# ------------------------------------------------------------ 跨年标记本地化

def test_crossyear_localized():
    # 至少存在一个跨年周（如 2025 第 1 周从 2024-12-29 起）
    zh = E.render_body('weeks', 2025, 'zh', '../../')
    en = E.render_body('weeks', 2025, 'en', '../../')
    ok('跨年' in zh, 'weeks 2025 zh 含跨年')
    ok('cross-year' in en, 'weeks 2025 en 含 cross-year')
    ok('跨年' not in en, 'weeks 2025 en 不含中文跨年')


# ------------------------------------------------------------ 对外清单

def test_exports():
    eq(len(E.evergreen_entries()), len(E.YEAR_RANGE) * len(E.TYPES), '条目数 = 年份×类型')
    eq(len(E.evergreen_paths()), len(E.YEAR_RANGE) * len(E.TYPES), '路径数一致')
    ok(E.nav_year() in E.YEAR_RANGE, 'nav_year 落在范围内')
    items = E.evergreen_nav_items('en')
    eq(len(items), len(E.TYPES), 'en 导航条目数')
    eq(items[0][0], f'{E.nav_year()} Calendar', 'en 导航首标签(带年份)')


if __name__ == '__main__':
    test_algorithms()
    test_render_counts()
    test_english_no_cjk()
    test_crossyear_localized()
    test_exports()
    print(f'\n{"✅" if FAIL == 0 else "❌"} 通过 {PASS} 项，失败 {FAIL} 项')
    sys.exit(1 if FAIL else 0)
