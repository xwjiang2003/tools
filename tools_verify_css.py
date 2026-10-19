# -*- coding: utf-8 -*-
"""Verify: base.css + group files == original style.css minus dead code.

1) Line-level: every surviving original line appears in exactly one group file.
2) Rule-level: normalized rule text sets are identical.
3) Page-level: every CSS class used by a page (static HTML + module JS, incl.
   string-concatenated classes) is covered by that page's assigned groups.
"""
import io
import os
import re
import subprocess
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'css')
ORIG_GIT = 'HEAD:src/css/style.css'   # style.css 已拆分删除，基准从 git HEAD 取

DEAD_LINES = {84, 86, 87, 88, 127, 128, 136}
REWRITE_LINES = {196, 197, 472, 473, 474, 475, 476}

GROUPS = ['base', 'json', 'diff', 'regex', 'generator', 'liveclock', 'time',
          'baseconv', 'worldclock', 'hotnews', 'cheatsheet', 'snippets',
          'blog', 'evergreen', 'legal']

try:
    orig_text = subprocess.check_output(
        ['git', 'show', ORIG_GIT],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        shell=True).decode('utf-8')
except Exception as e:                                        # noqa: BLE001
    print('cannot read baseline %s: %s' % (ORIG_GIT, e))
    sys.exit(2)
orig = orig_text.split('\n')

group_text = {}
for g in GROUPS:
    p = os.path.join(SRC, g + '.css')
    with io.open(p, 'r', encoding='utf-8') as f:
        group_text[g] = f.read()

# ---------- 1) line-level membership ----------
# multiset of non-empty, non-comment-body lines per group (comments kept loose)
def strip_header(text):
    return '\n'.join(text.split('\n')[1:])  # drop our file header comment

pool = {}
for g, t in group_text.items():
    for ln in strip_header(t).split('\n'):
        s = ln.rstrip()
        if s.strip():
            pool.setdefault(s, []).append(g)

missing = []
for n, line in enumerate(orig, 1):
    s = line.rstrip()
    if not s.strip() or n in DEAD_LINES or n in REWRITE_LINES:
        continue
    if s not in pool or not pool[s]:
        missing.append((n, s[:70]))
    else:
        pool[s].pop()

extra = {k: v for k, v in pool.items() if v}

print('== line-level ==')
print('missing from groups: %d' % len(missing))
for n, s in missing:
    print('  L%d: %s' % (n, s))
print('extra in groups (not in surviving orig): %d' % len(extra))
for k, v in list(extra.items())[:20]:
    print('  %s -> %s' % (k[:70], v))

# ---------- 2) rule-level normalized comparison ----------
def norm_rules(text):
    """Split into normalized rule chunks on '}' (handles multi-line rules)."""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    text = re.sub(r'\s+', ' ', text)
    chunks = [c.strip() for c in text.split('}') if c.strip()]
    return chunks

orig_alive = '\n'.join(l for n, l in enumerate(orig, 1)
                       if n not in DEAD_LINES and n not in REWRITE_LINES)
# rewritten lines replaced by their split fragments already live in groups
orig_rules = set(norm_rules(orig_alive))
all_groups_rules = set()
for g, t in group_text.items():
    all_groups_rules.update(norm_rules(t))

only_orig = orig_rules - all_groups_rules
only_new = all_groups_rules - orig_rules
print('== rule-level ==')
print('orig-only rules: %d, groups-only rules: %d' % (len(only_orig), len(only_new)))
for r in sorted(only_orig)[:10]:
    print('  ORIG: %s' % r[:90])
for r in sorted(only_new)[:10]:
    print('  NEW : %s' % r[:90])

# ---------- 3) page-level class coverage ----------
# datetime-tools.js is one module holding 11 page initializers; wc-* classes are
# emitted ONLY by initWorldClockPage/wcTicks (function-level audit), so the other
# 10 time-family pages legitimately exclude them.
PAGE_EXCLUDE = {
    'batch': {'wc-'}, 'timestamp-list': {'wc-'}, 'timezones': {'wc-'},
    'weeknumbers': {'wc-'}, 'daynumbers': {'wc-'}, 'years': {'wc-'},
    'countdown': {'wc-'}, 'date-difference': {'wc-'}, 'date-calculator': {'wc-'},
    'duration': {'wc-'},
}
PAGE_CSS = {
    'json': ['json'], 'csv': [], 'diff': ['diff'], 'regex': ['regex'],
    'generator': ['generator'], 'timestamp': ['liveclock'],
    'batch': ['time'], 'timestamp-list': ['time'], 'timezones': ['time'],
    'weeknumbers': ['time'], 'daynumbers': ['time'], 'years': ['time'],
    'world-clock': ['time', 'worldclock'], 'countdown': ['time'],
    'date-difference': ['time'], 'date-calculator': ['time'],
    'duration': ['time'],
    'uuid': [], 'snowflake': [], 'tid': [], 'objectid': [], 'firebase': [],
    'base': ['baseconv'], 'binary': ['baseconv'], 'hex': ['baseconv'],
    'hash': [], 'formatter': [], 'string': [], 'encode': [],
    'yaml': [], 'toml': [], 'jwt': [], 'color': [], 'case': [],
    'hotnews': ['hotnews'], 'go-cheatsheet': ['cheatsheet'], 'snippets': ['snippets'],
    'blog': ['blog'], 'evergreen': ['evergreen'], 'privacy': ['legal'],
}
# JS modules per page (for dynamic classes); core.js helpers are base-only
PAGE_MODULES = {
    'json': ['json-tools'], 'diff': ['text-diff'], 'regex': ['regex'],
    'generator': ['generator'], 'timestamp': ['timestamp'],
    'batch': ['datetime-tools'], 'timestamp-list': ['datetime-tools'],
    'timezones': ['datetime-tools'], 'weeknumbers': ['datetime-tools'],
    'daynumbers': ['datetime-tools'], 'years': ['datetime-tools'],
    'world-clock': ['datetime-tools'], 'countdown': ['datetime-tools'],
    'date-difference': ['datetime-tools'], 'date-calculator': ['datetime-tools'],
    'duration': ['datetime-tools'],
    'uuid': ['id-tools'], 'snowflake': ['id-tools'], 'tid': ['id-tools'],
    'objectid': ['id-tools'], 'firebase': ['id-tools'],
    'base': ['base-tools'], 'binary': ['base-tools'], 'hex': ['base-tools'],
    'hash': ['hash'], 'formatter': ['formatter'], 'string': ['string-tools'],
    'encode': ['encode'],
}
# classes produced by string concatenation inside JS (grep-invisible)
JS_CONCAT_CLASSES = {
    'text-diff': {'word-add', 'word-remove'},
    'json-tools': {'validate-card success', 'validate-card error'},
    'id-tools': {'hash-output err', 'hash-output warn'},
    'base-tools': {'hash-output err', 'hash-output warn'},
}

def classes_of_text(text):
    """Extract class tokens from HTML/JS text (class="a b c" and class='a b')."""
    found = set()
    for m in re.finditer(r'class=["\']([^"\']+)["\']', text):
        for tok in m.group(1).split():
            found.add(tok)
    # concatenated classes: class="word-' + side
    for m in re.finditer(r'class=["\']([a-z0-9-]+-)["\']\s*\+\s*(\w+)', text):
        found.add(m.group(1) + 'DYNAMIC')
    for m in re.finditer(r'class=["\']([a-z0-9-]+)\s*["\']\s*\+\s*(\w+)', text):
        found.add(m.group(1) + 'DYNAMIC')
    return found

def classes_in_css(group_names):
    """All class selectors defined by the given css groups (+ base)."""
    cls = set()
    for g in ['base'] + group_names:
        t = group_text[g]
        t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
        for m in re.finditer(r'\.([a-zA-Z][a-zA-Z0-9_-]*)', t):
            cls.add(m.group(1))
    return cls

def page_html(slug):
    for cand in (os.path.join(SRC, '..', 'tools', slug + '.html'),
                 os.path.join(SRC, '..', slug + '.html'),
                 os.path.join(SRC, '..', 'index.html')):
        if os.path.exists(cand):
            with io.open(cand, 'r', encoding='utf-8') as f:
                return f.read()
    return ''

problems = []
for slug, groups in PAGE_CSS.items():
    used = set()
    html = page_html(slug)
    if html:
        # strip script/style blocks: JS strings must come from module files
        h = re.sub(r'<script.*?</script>', '', html, flags=re.S)
        h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
        used |= classes_of_text(h)
    excl = PAGE_EXCLUDE.get(slug, set())
    used = {c for c in used if not any(c.startswith(p) for p in excl)}
    for mod in PAGE_MODULES.get(slug, []):
        mp = os.path.join(SRC, '..', 'js', mod + '.js')
        if os.path.exists(mp):
            with io.open(mp, 'r', encoding='utf-8') as f:
                mt = f.read()
            used |= classes_of_text(mt)
            used |= JS_CONCAT_CLASSES.get(mod, set())
            used = {c for c in used if not any(c.startswith(p) for p in excl)}
    avail = classes_in_css(groups)
    # unknown-to-css classes are fine (e.g. .dot, .title in demo content);
    # we only care that classes WITH css rules are covered
    defined = set()
    for g in ['base'] + [x for x in GROUPS if x != 'base']:
        t = re.sub(r'/\*.*?\*/', '', group_text[g], flags=re.S)
        for m in re.finditer(r'\.([a-zA-Z][a-zA-Z0-9_-]*)', t):
            defined.add(m.group(1))
    uncovered = {c for c in used if c in defined and c not in avail}
    if uncovered:
        problems.append((slug, sorted(uncovered)))

print('== page-level ==')
print('pages with uncovered classes: %d' % len(problems))
for slug, cs in problems:
    print('  %-14s missing: %s' % (slug, ', '.join(cs)))

# The 9 extra chunks are the intentional @media splits (semantics preserved,
# verified by hand against original L196/L197/L472-476).
EXPECTED_SPLIT_LINES = {
    '@media(max-width:900px){.seo-content{padding:20px 16px}.seo-content h1{font-size:19px}}',
    '@media(max-width:900px){.tool-layout{flex-direction:column}.ops-panel{width:100%}}',
    '@media(max-width:900px){',
    '.dt-table{display:block;overflow-x:auto;white-space:nowrap}',
    '.dt-table td{white-space:nowrap}',
    '.dt-big{font-size:38px}',
    '@media(max-width:900px){.seo-tools{columns:1}}',
    '@media(max-width:900px){.input-editor-wrap{min-height:350px}}',
}
EXPECTED_SPLIT_CHUNKS = {
    '.dt-big{font-size:38px',
    '.dt-table td{white-space:nowrap',
    '.ops-panel{width:100%',
    '.seo-content h1{font-size:19px',
    '@media(max-width:900px){ .dt-table{display:block;overflow-x:auto;white-space:nowrap',
    '@media(max-width:900px){.input-editor-wrap{min-height:350px',
    '@media(max-width:900px){.seo-content{padding:20px 16px',
    '@media(max-width:900px){.seo-tools{columns:1',
    '@media(max-width:900px){.tool-layout{flex-direction:column',
}
unexpected_new = {r for r in only_new if r not in EXPECTED_SPLIT_CHUNKS}
unexpected_extra = {k: v for k, v in extra.items()
                    if k.strip() != '}' and k.strip() not in EXPECTED_SPLIT_LINES}
ok = (not missing) and (not only_orig) and (not unexpected_new) and (not unexpected_extra) and (not problems)
print('unexpected new chunks: %d, unexpected extra lines: %d' % (len(unexpected_new), len(unexpected_extra)))
for r in sorted(unexpected_new):
    print('  BADNEW: %s' % r[:90])
for k in unexpected_extra:
    print('  BADEXTRA: %s' % k[:90])
print('VERDICT:', 'PASS' if ok else 'FAIL')

sys.exit(0 if ok else 1)
