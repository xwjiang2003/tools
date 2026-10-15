# -*- coding: utf-8 -*-
"""年度常青页生成器。

产出 calendar / weeks / days / year 四种类型的「按年静态参考页」，覆盖一个年份区间
（YEAR_RANGE）。这些页面是纯静态、预先渲染好的参考数据（日历网格、周数表、年内天数表、
年份概况），用来吃长期存在的长尾搜索流量（"2026 年日历"、"week 42 2026 dates" 之类），
与现有的「交互式」工具（weeknumbers / daynumbers / years）形成互补。

语言策略：每个 (type, year) 同时产出中文正文与英文正文。英文页不再依赖 build.py 的
localize() 逐词替换——正文本身就是英文，localize 只负责把通用 chrome（导航 / 页脚 /
反馈弹窗）翻成英文，从而彻底规避「漏译残留中文片段」的问题。
"""
import html
from datetime import date, timedelta

# 覆盖过去几年 + 未来几年，给长期长尾搜索留足收录面。要扩年份只改这一行常量。
YEAR_RANGE = list(range(2023, 2031))   # 2023..2030（8 年）
TYPES = ('calendar', 'weeks', 'days', 'year')

MONTHS_ZH = [f'{i} 月' for i in range(1, 13)]
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December']
WD_SHORT_ZH = ['一', '二', '三', '四', '五', '六', '日']
WD_SHORT_EN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
WD_FULL_ZH = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
WD_FULL_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
              'Saturday', 'Sunday']

NAV_LABELS_EV = {
    'zh': {'calendar': '年度日历', 'weeks': '年度周数', 'days': '年内天数', 'year': '年度概况'},
    'en': {'calendar': 'Year Calendar', 'weeks': 'Week Numbers',
           'days': 'Day of Year', 'year': 'Year Facts'},
}


def e(s):
    return html.escape(str(s), quote=True)


# ------------------------------------------------------------ 日期算法

def is_leap(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def days_in_year(y):
    return 366 if is_leap(y) else 365


def iso_week_count(y):
    """某 ISO 年的周数（52 或 53）。Dec 28 永远落在当年最后一个 ISO 周里。"""
    d = date(y, 12, 31)
    w = d.isocalendar()[1]
    if w == 1:
        return date(y, 12, 28).isocalendar()[1]
    return w


def iso_monday(y, w):
    """ISO 年第 w 周的周一（可能落在相邻年，用于边界周）。"""
    jan4 = date(y, 1, 4)
    w1_mon = jan4 - timedelta(days=jan4.isoweekday() - 1)
    return w1_mon + timedelta(weeks=w - 1)


def _cal_cells(y, month):
    first = date(y, month, 1)
    start_blank = first.isoweekday() - 1
    if month == 12:
        ndays = (date(y + 1, 1, 1) - first).days
    else:
        ndays = (date(y, month + 1, 1) - first).days
    cells = [None] * start_blank + list(range(1, ndays + 1))
    while len(cells) % 7:
        cells.append(None)
    return [cells[i:i + 7] for i in range(0, len(cells), 7)]


# ------------------------------------------------------------ 导航片段

def _year_nav(year, type_, lang, base):
    lead = '查看其它年份：' if lang == 'zh' else 'Other years: '
    items = []
    for y in YEAR_RANGE:
        if y == year:
            items.append(f'<b>{y}</b>')
        else:
            items.append(f'<a href="{base}{type_}/{y}/">{y}</a>')
    return '<nav class="ev-years" aria-label="years">' + lead + ' '.join(items) + '</nav>'


def _sibling_nav(year, type_, lang, base):
    lead = '同年度其它页面：' if lang == 'zh' else 'Other pages for this year: '
    items = []
    for t in TYPES:
        if t == type_:
            continue
        items.append(f'<a href="{base}{t}/{year}/">{e(NAV_LABELS_EV[lang][t])}</a>')
    return '<nav class="ev-sib" aria-label="siblings">' + lead + ' · '.join(items) + '</nav>'


def _today_script():
    return ('<script>\n'
            '(function(){try{\n'
            'var t=new Date();\n'
            'var iso=t.getFullYear()+"-"+String(t.getMonth()+1).padStart(2,"0")+'
            '"-"+String(t.getDate()).padStart(2,"0");\n'
            'var el=document.querySelector(\'[data-date="\'+iso+\'"]\');\n'
            'if(el)el.classList.add("ev-today");\n'
            '}catch(e){}})();\n'
            '</script>')


# ------------------------------------------------------------ 正文渲染

def _month_title(y, m, lang):
    return f'{y} 年 {m} 月' if lang == 'zh' else f'{MONTHS_EN[m - 1]} {y}'


def _cal_header(lang):
    if lang == 'zh':
        return '<th class="ev-wk">周</th>' + ''.join(f'<th>{c}</th>' for c in WD_SHORT_ZH)
    return '<th class="ev-wk">Wk</th>' + ''.join(f'<th>{c}</th>' for c in WD_SHORT_EN)


def _render_calendar(year, lang, base):
    leap = is_leap(year)
    n = days_in_year(year)
    jan1, dec31 = date(year, 1, 1), date(year, 12, 31)
    wk = iso_week_count(year)
    if lang == 'zh':
        summary = (f'{year} 年共有 {n} 天，1 月 1 日是{e(WD_FULL_ZH[jan1.isoweekday() - 1])}，'
                   f'12 月 31 日是{e(WD_FULL_ZH[dec31.isoweekday() - 1])}，'
                   f'共 {wk} 个 ISO 周，属{"闰年" if leap else "平年"}。')
    else:
        summary = (f'{year} has {n} days. January 1 is {WD_FULL_EN[jan1.isoweekday() - 1]} '
                   f'and December 31 is {WD_FULL_EN[dec31.isoweekday() - 1]}. '
                   f'There are {wk} ISO weeks. '
                   f'{"Leap year." if leap else "Common year."}')
    parts = [f'<section class="ev-page">', f'<p class="ev-summary">{summary}</p>']
    parts.append(_year_nav(year, 'calendar', lang, base))
    parts.append('<div class="ev-cal-grid">')
    for month in range(1, 13):
        parts.append(f'<div class="ev-month"><div class="ev-month-title">'
                     f'{_month_title(year, month, lang)}</div>')
        parts.append('<table class="ev-cal"><thead><tr>' + _cal_header(lang) + '</tr></thead><tbody>')
        for row in _cal_cells(year, month):
            real = [d for d in row if d]
            iso_wk = row and date(year, month, real[0]).isocalendar()[1] if real else ''
            cells = ['<td class="ev-wk">' + (str(iso_wk) if iso_wk != '' else '') + '</td>']
            for d in row:
                if d is None:
                    cells.append('<td class="ev-empty"></td>')
                else:
                    iso = f'{year}-{month:02d}-{d:02d}'
                    cells.append(f'<td class="ev-day" data-date="{iso}">{d}</td>')
            parts.append('<tr>' + ''.join(cells) + '</tr>')
        parts.append('</tbody></table></div>')
    parts.append('</div>')
    parts.append(_today_script())
    parts.append('</section>')
    return ''.join(parts)


def _render_weeks(year, lang, base):
    leap = is_leap(year)
    n = days_in_year(year)
    wk = iso_week_count(year)
    jan1 = date(year, 1, 1)
    if lang == 'zh':
        summary = (f'{year} 年按 ISO 8601 共有 {wk} 周，'
                   f'第 1 周从 {iso_monday(year, 1)}（周一）开始。')
        heads = ['周次', '开始（周一）', '结束（周日）', '年内天数区间']
    else:
        summary = (f'{year} has {wk} ISO 8601 weeks. '
                   f'Week 1 starts on {iso_monday(year, 1)} (Monday).')
        heads = ['Week', 'Start (Mon)', 'End (Sun)', 'Day-of-year range']
    parts = [f'<section class="ev-page">', f'<p class="ev-summary">{summary}</p>']
    parts.append(_year_nav(year, 'weeks', lang, base))
    parts.append(_sibling_nav(year, 'weeks', lang, base))
    parts.append('<table class="dt-table"><thead><tr>'
                 + ''.join(f'<th>{h}</th>' for h in heads) + '</tr></thead><tbody>')
    for w in range(1, wk + 1):
        mon = iso_monday(year, w)
        sun = mon + timedelta(days=6)
        ds = (mon - jan1).days + 1
        de = (sun - jan1).days + 1
        cross = '跨年' if lang == 'zh' else 'cross-year'
        dor = f'{ds}–{de}' if (1 <= ds <= n and 1 <= de <= n) else cross
        parts.append(f'<tr><td>{w}</td><td>{mon}</td><td>{sun}</td><td>{dor}</td></tr>')
    parts.append('</tbody></table></section>')
    return ''.join(parts)


def _render_days(year, lang, base):
    n = days_in_year(year)
    if lang == 'zh':
        summary = f'{year} 年共 {n} 天，下表列出每一天对应的「年内第几天」与星期。'
        heads = ['年内第几天', '日期', '星期', 'ISO 周']
    else:
        summary = (f'{year} has {n} days. The table below maps each calendar date '
                   f'to its day-of-year and weekday.')
        heads = ['Day of year', 'Date', 'Weekday', 'ISO week']
    parts = [f'<section class="ev-page">', f'<p class="ev-summary">{summary}</p>']
    parts.append(_year_nav(year, 'days', lang, base))
    parts.append(_sibling_nav(year, 'days', lang, base))
    parts.append('<table class="dt-table"><thead><tr>'
                 + ''.join(f'<th>{h}</th>' for h in heads) + '</tr></thead><tbody>')
    jan1 = date(year, 1, 1)
    wd = WD_FULL_ZH if lang == 'zh' else WD_FULL_EN
    for doy in range(1, n + 1):
        d = jan1 + timedelta(days=doy - 1)
        parts.append(f'<tr><td>{doy}</td><td>{d}</td>'
                     f'<td>{wd[d.isoweekday() - 1]}</td><td>{d.isocalendar()[1]}</td></tr>')
    parts.append('</tbody></table></section>')
    return ''.join(parts)


def _render_year(year, lang, base):
    leap = is_leap(year)
    n = days_in_year(year)
    wk = iso_week_count(year)
    jan1, dec31 = date(year, 1, 1), date(year, 12, 31)
    mon1, sun1 = iso_monday(year, 1), iso_monday(year, 1) + timedelta(days=6)
    if lang == 'zh':
        summary = f'{year} 年概况如下。'
        rows = [
            ('是否闰年', '是（366 天）' if leap else '否（365 天）'),
            ('全年天数', str(n)),
            ('第一天（1 月 1 日）', f'{jan1} {WD_FULL_ZH[jan1.isoweekday() - 1]}'),
            ('最后一天（12 月 31 日）', f'{dec31} {WD_FULL_ZH[dec31.isoweekday() - 1]}'),
            ('ISO 周数', f'{wk} 周'),
            ('第 1 周（周一）', str(mon1)),
            ('第 1 周（周日）', str(sun1)),
        ]
    else:
        summary = f'Overview of the year {year}:'
        rows = [
            ('Leap year', 'Yes (366 days)' if leap else 'No (365 days)'),
            ('Total days', str(n)),
            ('First day (Jan 1)', f'{jan1} {WD_FULL_EN[jan1.isoweekday() - 1]}'),
            ('Last day (Dec 31)', f'{dec31} {WD_FULL_EN[dec31.isoweekday() - 1]}'),
            ('ISO weeks', str(wk)),
            ('Week 1 (Monday)', str(mon1)),
            ('Week 1 (Sunday)', str(sun1)),
        ]
    parts = [f'<section class="ev-page">', f'<p class="ev-summary">{summary}</p>']
    parts.append(_year_nav(year, 'year', lang, base))
    parts.append(_sibling_nav(year, 'year', lang, base))
    if lang == 'zh':
        parts.append('<table class="dt-table"><thead><tr><th>项目</th><th>数值</th></tr></thead><tbody>')
    else:
        parts.append('<table class="dt-table"><thead><tr><th>Item</th><th>Value</th></tr></thead><tbody>')
    for k, v in rows:
        parts.append(f'<tr><td>{e(k)}</td><td>{e(v)}</td></tr>')
    parts.append('</tbody></table></section>')
    return ''.join(parts)


def render_body(type_, year, lang, base):
    if type_ == 'calendar':
        return _render_calendar(year, lang, base)
    if type_ == 'weeks':
        return _render_weeks(year, lang, base)
    if type_ == 'days':
        return _render_days(year, lang, base)
    if type_ == 'year':
        return _render_year(year, lang, base)
    raise ValueError(type_)


# ------------------------------------------------------------ 元数据

def meta(type_, year, lang):
    y = str(year)
    if type_ == 'calendar':
        if lang == 'zh':
            return {'h1': f'{y} 年日历（含周数）',
                    'title': f'{y} 年日历 - 全年 12 个月日历含 ISO 周数 | DevTools',
                    'description': (f'在线 {y} 年日历：逐月展示全年 12 个月，'
                                    f'标注每周 ISO 周数、星期与闰年信息。纯静态页面，可全年查阅。'),
                    'keywords': f'{y}年日历,{y}日历,日历{y},年历{y},ISO周数日历'}
        return {'h1': f'{y} Calendar (with week numbers)',
                'title': f'{y} Calendar - Full year monthly calendar with ISO week numbers | DevTools',
                'description': (f'Online {y} calendar: all 12 months with ISO week numbers, '
                                f'weekdays and leap-year info. A static page you can refer to all year.'),
                'keywords': f'{y} calendar,calendar {y},year {y} calendar,iso week calendar'}
    if type_ == 'weeks':
        if lang == 'zh':
            return {'h1': f'{y} 年 ISO 周数总表',
                    'title': f'{y} 年 ISO 周数 - 全年每周起止日期 | DevTools',
                    'description': (f'在线 {y} 年 ISO 8601 周数表：逐周列出起始（周一）与结束（周日）日期，'
                                    f'以及跨年标注。'),
                    'keywords': f'{y}年周数,{y}年ISO周数,周数{y},ISO week {y}'}
        return {'h1': f'{y} ISO Week Numbers',
                'title': f'{y} ISO Week Numbers - start and end date of every week | DevTools',
                'description': (f'Online {y} ISO 8601 week table: the start (Monday) and end (Sunday) '
                                f'date of every week, with cross-year markers.'),
                'keywords': f'{y} week numbers,iso weeks {y},week {y}'}
    if type_ == 'days':
        if lang == 'zh':
            return {'h1': f'{y} 年年内第几天',
                    'title': f'{y} 年年内第几天 - 逐日映射日期与星期 | DevTools',
                    'description': (f'在线 {y} 年年内第几天表：把每一天映射为年第几天（1 月 1 日为第 1 天），'
                                    f'并标注星期与 ISO 周。'),
                    'keywords': f'{y}年内第几天,{y}年第几天,day of year {y}'}
        return {'h1': f'{y} Day of Year',
                'title': f'{y} Day of Year - every date mapped to its day number | DevTools',
                'description': (f'Online {y} day-of-year table: each calendar date mapped to its '
                                f'day number (Jan 1 = day 1), with weekday and ISO week.'),
                'keywords': f'{y} day of year,day number {y}'}
    if type_ == 'year':
        if lang == 'zh':
            return {'h1': f'{y} 年概况',
                    'title': f'{y} 年概况 - 闰年、天数、起止星期与 ISO 周数 | DevTools',
                    'description': (f'在线 {y} 年概况：是否闰年、全年天数、起止星期、ISO 周数与第 1 周区间，一页速查。'),
                    'keywords': f'{y}年概况,{y}年,闰年{y},年份{y}'}
        return {'h1': f'{y} Year Facts',
                'title': f'{y} Year Facts - leap year, days, start/end weekday, ISO weeks | DevTools',
                'description': (f'Online {y} year facts at a glance: leap year, total days, '
                                f'start/end weekday, ISO week count and week-1 range.'),
                'keywords': f'{y} year facts,year {y},leap year {y}'}
    raise ValueError(type_)


# ------------------------------------------------------------ SEO 内容

def _seo_calendar(year, lang, base):
    leap = is_leap(year)
    if lang == 'zh':
        intro = [
            f'{year} 年日历把全年 12 个月并排展示，每个日期格子都标注了它所在的 ISO 8601 周数'
            f'（左侧"周"列），方便对照"某天属于第几周"。',
            '页面为静态生成，年初到年末都可直接查阅，无需等待脚本计算。',
        ]
        features = [
            ('12 个月并排', '逐月展示，年初规划与年末对账都好用。'),
            ('ISO 周数标注', '每周左侧标注 ISO 周次，与欧洲企业系统口径一致。'),
            ('闰年自动识别', f'{year} 年{"是" if leap else "不是"}闰年，2 月有 {29 if leap else 28} 天。'),
        ]
        steps = [
            f'直接浏览本页即可查看 {year} 年任意日期与周数。',
            '使用上方"查看其它年份"可切换到相邻年份。',
        ]
        faq = [
            ('为什么有些周跨年？',
             'ISO 周以周四规则定第 1 周，因此第 1 周可能从上年 12 月底开始，'
             '最后一周也可能跨入次年 1 月。'),
            ('日历里的"周"数字是什么？',
             '左侧数字为该行日期所属的 ISO 8601 周次（周一为一周之始）。'),
        ]
    else:
        intro = [
            f'The {year} calendar shows all 12 months side by side. Every date cell is tagged with '
            f'its ISO 8601 week number (the "Wk" column on the left), so you can see which week a '
            f'date belongs to at a glance.',
            'The page is statically generated and can be consulted any time of the year '
            'without waiting for scripts to compute.',
        ]
        features = [
            ('12 months side by side', 'Shown month by month — handy for both annual planning and year-end reconciliation.'),
            ('ISO week numbers', 'Each week is tagged with its ISO week number, matching European enterprise systems.'),
            ('Leap-year aware', f'{year} {"is" if leap else "is not"} a leap year; February has {29 if leap else 28} days.'),
        ]
        steps = [
            f'Just browse this page to see any date and week number in {year}.',
            'Use "Other years" above to switch to an adjacent year.',
        ]
        faq = [
            ('Why do some weeks cross the year boundary?',
             'ISO weeks use the Thursday rule to pick week 1, so week 1 can start in late December '
             'of the previous year, and the last week can spill into January of the next.'),
            ('What does the "Wk" number mean?',
             'It is the ISO 8601 week number of the row (Monday is the first day of the week).'),
        ]
    return intro, features, steps, faq


def _seo_weeks(year, lang, base):
    wk = iso_week_count(year)
    if lang == 'zh':
        intro = [
            f'本页列出 {year} 年按 ISO 8601 划分的全部周次，以及每周的起始（周一）与结束（周日）日期。',
            '可与"年内第几天""年度日历"配合使用，做排期与对账。',
        ]
        features = [
            ('全周年次', f'共 {wk} 周，逐周列出起止日期。'),
            ('跨年标注', '年初/年末跨入相邻年的周会标注"跨年"，避免误读。'),
        ]
        steps = [
            f'浏览表格即可查看 {year} 年任意 ISO 周对应的日期区间。',
        ]
        faq = [
            ('ISO 周为什么有时是 53 周？',
             f'{year} 年有 {wk} 个 ISO 周；当 1 月 1 日所在周的大部分天数落在下一年时，该年会有 53 周。'),
        ]
    else:
        intro = [
            f'This page lists every ISO 8601 week of {year}, with the start (Monday) and '
            f'end (Sunday) date of each week.',
            'Pair it with "Day of Year" and the "Year Calendar" for scheduling and reconciliation.',
        ]
        features = [
            ('All weeks of the year', f'{wk} weeks in total, each with its start and end date.'),
            ('Cross-year markers', 'Weeks that spill into an adjacent year are marked "cross-year" to avoid misreading.'),
        ]
        steps = [
            f'Browse the table to see the date range of any ISO week in {year}.',
        ]
        faq = [
            ('Why does an ISO year sometimes have 53 weeks?',
             f'{year} has {wk} ISO weeks; when most days of the week containing Jan 1 fall in the '
             f'next year, that year gets 53 weeks.'),
        ]
    return intro, features, steps, faq


def _seo_days(year, lang, base):
    n = days_in_year(year)
    if lang == 'zh':
        intro = [
            f'本页把 {year} 年的每一天映射为"年内第几天"（1 月 1 日为第 1 天），并标注星期与 ISO 周。',
            '常用于日志格式、财务季度与天文计算中需要"年第几天"的场景。',
        ]
        features = [
            ('逐日映射', f'1 至 {n} 天，每天一行。'),
            ('星期与 ISO 周', '同时给出星期与所属 ISO 周次。'),
        ]
        steps = [
            f'查找某日期对应的年内第几天，直接在本表检索即可。',
        ]
        faq = [
            ('"年内第几天"和"儒略日"一样吗？',
             '不一样。这里是每年从 1 重新开始的"年第几天"；儒略日是从公元前 4713 年起的连续天数，'
             '跨年不归零。'),
        ]
    else:
        intro = [
            f'This page maps every day of {year} to its day-of-year (Jan 1 = day 1), '
            f'with the weekday and ISO week shown too.',
            'Useful whenever you need the "day number" for log formats, fiscal quarters '
            'or astronomical calculations.',
        ]
        features = [
            ('Day-by-day mapping', f'Days 1 to {n}, one row per day.'),
            ('Weekday and ISO week', 'Both the weekday and the ISO week number are shown.'),
        ]
        steps = [
            f'To find the day-of-year for a date, just look it up in this table.',
        ]
        faq = [
            ('Is "day of year" the same as "Julian day"?',
             'No. Day-of-year restarts from 1 every year; the Julian day is a continuous count '
             'from 4713 BC and does not reset across years.'),
        ]
    return intro, features, steps, faq


def _seo_year(year, lang, base):
    leap = is_leap(year)
    n = days_in_year(year)
    if lang == 'zh':
        intro = [
            f'本页汇总 {year} 年的关键日期事实：是否闰年、全年天数、起止星期、ISO 周数与第 1 周区间。',
        ]
        features = [
            ('闰年判定', f'{year} 年{"是" if leap else "不是"}闰年（{n} 天）。'),
            ('起止与周数', '列出首尾日星期与全年 ISO 周数。'),
        ]
        steps = [
            f'本页即 {year} 年的年份速查卡。',
        ]
        faq = [
            ('1900 为什么不是闰年？',
             '闰年规则有例外：能被 100 整除的年份须同时被 400 整除才是闰年。'
             '1900 能被 100 整除但不能被 400 整除，故为平年；2000 能被 400 整除，是闰年。'),
        ]
    else:
        intro = [
            f'This page summarizes the key date facts of {year}: leap year or not, total days, '
            f'start/end weekdays, ISO week count and the week-1 range.',
        ]
        features = [
            ('Leap-year check', f'{year} {"is" if leap else "is not"} a leap year ({n} days).'),
            ('Start, end and weeks', 'Lists the start/end weekdays and the total ISO week count.'),
        ]
        steps = [
            f'This page is a quick-reference card for the year {year}.',
        ]
        faq = [
            ('Why was 1900 not a leap year?',
             'The leap rule has an exception: a year divisible by 100 is a leap year only if it is '
             'also divisible by 400. 1900 is divisible by 100 but not by 400, so it is common; '
             '2000 is divisible by 400, so it is leap.'),
        ]
    return intro, features, steps, faq


def render_seo(type_, year, lang, base):
    intro, features, steps, faq = {
        'calendar': _seo_calendar, 'weeks': _seo_weeks,
        'days': _seo_days, 'year': _seo_year,
    }[type_](year, lang, base)
    seealso = _seealso(type_, year, lang, base)
    return {'intro': intro, 'features': features, 'steps': steps,
            'faq': faq, 'seealso': seealso}


def _seealso(type_, year, lang, base):
    items = []
    for t in TYPES:
        if t == type_:
            continue
        items.append((e(NAV_LABELS_EV[lang][t]) + f' {year}', f'{t}/{year}/'))
    idx = list(YEAR_RANGE).index(year)
    if idx > 0:
        py = YEAR_RANGE[idx - 1]
        items.append((f'{py} 年' if lang == 'zh' else str(py), f'{type_}/{py}/'))
    if idx < len(YEAR_RANGE) - 1:
        ny = YEAR_RANGE[idx + 1]
        items.append((f'{ny} 年' if lang == 'zh' else str(ny), f'{type_}/{ny}/'))
    return items


# ------------------------------------------------------------ 对外清单

def evergreen_entries():
    out = []
    for year in YEAR_RANGE:
        for t in TYPES:
            out.append((t, year, f'{t}-{year}', f'{t}/{year}/'))
    return out


def evergreen_paths():
    return [f'{t}/{y}/' for y in YEAR_RANGE for t in TYPES]


def nav_year():
    import datetime
    cur = datetime.date.today().year
    if cur in YEAR_RANGE:
        return cur
    cand = [y for y in YEAR_RANGE if y <= cur]
    return max(cand) if cand else YEAR_RANGE[0]


def evergreen_nav_items(lang):
    y = nav_year()
    return [(NAV_LABELS_EV[lang][t], f'{t}/{y}/') for t in TYPES]
