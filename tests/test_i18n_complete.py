# -*- coding: utf-8 -*-
"""i18n 字典完备性测试。

背景：EN 是基准字典（540 条），其余 8 种语言（ja/ko/es/pt-BR/fr/de/ru/id）
2026-10-19 之前各只有 162 条，剩余 ~379 条界面串在新语页回落英文。本次补齐后
本测试在源码层锁死不变量，防止后续新增中文文案时漏翻。

localize() 的行为前提（build.py）：
  · 按「长度降序的整词替换」改写整页 HTML + 内联 JS；
  · 键 = 中文原文，键的首尾空格会被原样替换 → 译文必须保留同样的首尾空格，
    否则拼接出来的句子会缺空格或粘字（如 '已转换 ' + 120 + ' 行'）；
  · 未命中时回落到 EN，所以任何一条缺失都表现为「英文混进新语页」。

本测试校验：
  A. 8 种语言的键集合 == EN 的键集合（不多不少）；
  B. 每条译文非空、去空白后不与源相同；
  C. 译文首尾空格与源键严格一致（拼接安全）；
  D. 纯拉丁／西里尔语言（es/pt-BR/fr/de/ru/id）译文不含汉字；
     ja 允许日文汉字但不得含简体专用字；ko 不得含汉字；
  E. 代码标识符不翻译：$1 / {n} / P1DT12H / SHA-256 等占位与专名在译文中保留；
  F. 源键中的数字与 emoji 在译文中保留；
  G. 同一字典内无重复键（源码层重复键会被 Python 静默覆盖）。
"""
# -*- coding: utf-8 -*-
import re
import sys
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / 'src'
sys.path.insert(0, str(SRC))
import i18n  # noqa: E402

LANGS = ['JA', 'KO', 'ES', 'PTBR', 'FR', 'DE', 'RU', 'ID']
LATIN_ONLY = ['ES', 'PTBR', 'FR', 'DE', 'RU', 'ID']  # 这些语言译文里出现汉字即为漏翻

CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')
# 只在简体中文里使用、日文不用（或改用别的字形）的字。只收「日文里绝不会出现」的字，
# 避免把「解 / 除 / 示」这类中日共用的汉字误判为漏翻。
SIMPLIFIED_ONLY = set('这个说时国东车门问间对开发后从来动过还学样几为书买卖长马鸟鱼风飞龙'
                      '华汉气电视频网络应该体积单击开关闭户页签删确认显隐读写粘贴转换编'
                      '压缩试验证错资讯选择题录们')
EMOJI = re.compile('[\U0001F300-\U0001FAFF\u2600-\u27bf\u2b00-\u2bff\ufe0f\u2705\u274c\u26a0]')
PLACEHOLDER = re.compile(r'\$\d|\{\w+\}|P\d|UTC|SHA-\d+|MD5|UUID|JSON|JWT|CSV|TOML|YAML|HTML|CSS|AES|HMAC|RGB|HSL|ID\b')

# 专名／记号：各语言写法本就相同，译文与源相同属正确，不算漏翻
SAME_OK = {'RGB', 'HSL', 'UTC', 'JD', 'ID', 'JWT', 'JSON', 'API', 'URL'}
# 日语里汉字写法与中文一致的常用界面词（日文正式写法就是这些字形）
# 日语正式写法与中文同形（汉字词 + 时间单位），译文与源相同即正确
JA_SAME_OK = {
    '生成', '分割', '生成中...', '位置', '解析', '数字', '段落', '平年', '北京',
    '年', '月', '日', '分', '秒', '年:', '月:', '日:', '分:', '秒:',
    ' 行', ' 行: ', ' 分 ', ' 秒', ' | 行: ', '第 ', '行 ...', '行: 0',
}

SP = chr(32)  # 显式空格字面量：避免编辑/传输链路吞掉源码里的裸空格

PASS = FAIL = 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print('FAIL: ' + msg)


def src_dup_keys(name):
    """源码层扫描重复键：Python dict 字面量重复键会被静默覆盖。"""
    text = (SRC / 'i18n.py').read_text('utf-8')
    m = re.search(r'^' + name + r' = \{\n(.*?)^\}', text, re.S | re.M)
    if not m:
        return ['<%s 字典块未找到>' % name]
    keys = re.findall(r"^\s*'((?:[^'\\]|\\.)*)':", m.group(1), re.M)
    seen, dups = set(), []
    for k in keys:
        k = k.replace("\\'", "'").replace('\\\\', '\\')
        if k in seen:
            dups.append(k)
        seen.add(k)
    return dups


def test_key_sets_equal():
    """A: 键集合完全一致。"""
    en = set(i18n.EN)
    check(len(en) > 400, 'EN 字典条目过少（%d），疑似被截断' % len(en))
    for name in LANGS:
        d = getattr(i18n, name)
        miss = sorted(en - set(d))
        extra = sorted(set(d) - en)
        check(not miss, '%s 缺少 %d 条：%s' % (name, len(miss), [x[:20] for x in miss[:5]]))
        check(not extra, '%s 多余 %d 条（EN 里没有对应键）：%s'
              % (name, len(extra), [x[:20] for x in extra[:5]]))


def test_no_dup_keys():
    """G: 源码层无重复键。"""
    check(not src_dup_keys('EN'), 'EN 有重复键：%s' % src_dup_keys('EN')[:5])
    for name in LANGS:
        dups = src_dup_keys(name)
        check(not dups, '%s 源码层有重复键（后者会静默覆盖前者）：%s' % (name, dups[:5]))


def test_non_empty_and_different():
    """B: 译文非空且不复制中文。"""
    for name in ['EN'] + LANGS:
        for k, v in getattr(i18n, name).items():
            check(v.strip() != '', '%s: %r 译文为空' % (name, k))
            if name == 'EN' or k in SAME_OK:
                continue
            if name == 'JA' and k in JA_SAME_OK:
                continue
            check(v.strip() != k.strip(), '%s: %r 译文与中文源相同（未翻译）' % (name, k))


def test_whitespace_preserved():
    """C: 首尾空格与源键一致（拼接安全）。"""
    for name in ['EN'] + LANGS:
        for k, v in getattr(i18n, name).items():
            check((k[:1] == SP) == (v[:1] == SP),
                  '%s: %r 前导空格不一致 → %r' % (name, k, v))
            check((k[-1:] == SP) == (v[-1:] == SP),
                  '%s: %r 尾部空格不一致 → %r' % (name, k, v))


def test_no_chinese_in_translation():
    """D: 非中日语言不得残留汉字；ja 不得含简体专用字；ko 不得含汉字。"""
    for name in LATIN_ONLY:
        bad = [(k, v) for k, v in getattr(i18n, name).items() if CJK.search(v)]
        check(not bad, '%s 译文残留汉字 %d 条：%s'
              % (name, len(bad), [(k[:12], v[:20]) for k, v in bad[:5]]))

    ja_bad = []
    for k, v in i18n.JA.items():
        hits = [c for c in v if c in SIMPLIFIED_ONLY]
        # 中文键被整体保留时（如纯符号/数字键）跳过
        if hits and CJK.search(k):
            ja_bad.append((k[:12], v[:20], ''.join(hits)))
    check(not ja_bad, 'JA 译文含简体专用字 %d 条：%s' % (len(ja_bad), ja_bad[:5]))

    ko_bad = [(k, v) for k, v in i18n.KO.items() if CJK.search(v)]
    check(not ko_bad, 'KO 译文含汉字 %d 条：%s'
          % (len(ko_bad), [(k[:12], v[:20]) for k, v in ko_bad[:5]]))


def test_placeholders_kept():
    """E: 代码标识符与占位符不翻译。"""
    for name in ['EN'] + LANGS:
        for k, v in getattr(i18n, name).items():
            for tok in set(re.findall(r'\$\d|\{\w+\}|P\d\w+', k)):
                check(tok in v, '%s: %r 缺少占位符 %r → %r' % (name, k, tok, v))
            for tok in ('SHA-256', 'SHA-512', 'SHA-1'):
                if tok in k:
                    check(tok in v, '%s: %r 丢失标识符 %r → %r' % (name, k, tok, v))


def test_numbers_and_emoji_kept():
    """F: 数字与 emoji 保留。"""
    for name in ['EN'] + LANGS:
        for k, v in getattr(i18n, name).items():
            for num in set(re.findall(r'\d+', k)):
                # 数字在译文里可能被本地化写法改写（如 1800–2100 保留），此处只要求 4 位以上数字
                if len(num) >= 3:
                    check(num in v, '%s: %r 丢失数字 %r → %r' % (name, k, num, v))
            if EMOJI.search(k):
                check(EMOJI.search(v), '%s: %r 丢失 emoji → %r' % (name, k, v))


def test_sample_data_localized():
    """附加：中文示例人名/地区应本地化为各语言习惯写法，不能整体残留中文。"""
    samples = ['张三', '李四', '海淀区', '朴灵']
    for name in LATIN_ONLY + ['KO']:
        d = getattr(i18n, name)
        for s in samples:
            if s not in d:
                continue
            v = d[s]
            check(not CJK.search(v), '%s: 示例数据 %r 未本地化（残留汉字）→ %r' % (name, s, v))
    # 日语用日文姓名汉字，允许出现汉字，但必须是日式读法而非中文原串
    for s in samples:
        if s in i18n.JA:
            check(i18n.JA[s] != s, 'JA: 示例数据 %r 未本地化（直接复用中文）→ %r' % (s, i18n.JA[s]))


if __name__ == '__main__':
    test_key_sets_equal()
    test_no_dup_keys()
    test_non_empty_and_different()
    test_whitespace_preserved()
    test_no_chinese_in_translation()
    test_placeholders_kept()
    test_numbers_and_emoji_kept()
    test_sample_data_localized()
    print('\n%d passed, %d failed' % (PASS, FAIL))
    raise SystemExit(1 if FAIL else 0)
