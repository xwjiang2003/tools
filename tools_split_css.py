# -*- coding: utf-8 -*-
"""Split src/css/style.css into base.css + per-page-group files (one-off migration).

Line numbers are 1-based, closed intervals, against the ORIGINAL style.css.
Dead code lines are dropped. Mixed @media rules (L196/L197/L472-476) are split
manually into the rewritten forms below.
"""
import io
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'css')
ORIG = os.path.join(SRC, 'style.css')

with io.open(ORIG, 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')  # keep trailing '' after final newline

def L(n):
    """1-based line fetch."""
    return lines[n - 1]

# ---- dead code (verified: no HTML/JS reference anywhere in src/) ----
DEAD = {
    84,   # .special-tools
    86,   # .tool-card-header
    87,   # .tool-card-body
    88,   # .tool-card-body .CodeMirror
    127,  # .regex-highlight
    128,  # .regex-highlight-focus
    136,  # .pwd-strength-bar
}

# ---- group assignments: list of (start, end) 1-based closed intervals ----
GROUPS = {
    'json': [(59, 60), (75, 81), (89, 101), (115, 117), (185, 187)],
    'diff': [(137, 154)],
    'regex': [(129, 131)],
    'generator': [(121, 121), (134, 135)],
    'liveclock': [(132, 133)],
    'time': [(452, 455), (466, 471)],
    'baseconv': [(504, 511)],
    'worldclock': [(518, 550)],
    'hotnews': [(216, 256)],
    'cheatsheet': [(257, 288)],
    'snippets': [(289, 322)],
    'blog': [(323, 355)],
    'evergreen': [(478, 502), (514, 517)],
    'legal': [(193, 195)],
}

# ---- rewritten fragments for mixed rules (original line -> replacement text) ----
# L196: split seo-content (base) from seo-tools (json)
REWRITE = {
    196: {
        'base': '@media(max-width:900px){.seo-content{padding:20px 16px}.seo-content h1{font-size:19px}}',
        'json': '@media(max-width:900px){.seo-tools{columns:1}}',
    },
    197: {
        'base': '@media(max-width:900px){.tool-layout{flex-direction:column}.ops-panel{width:100%}}',
        'json': '@media(max-width:900px){.input-editor-wrap{min-height:350px}}',
    },
    472: {
        'base': '@media(max-width:900px){',
    },
    473: {
        'base': '  .dt-table{display:block;overflow-x:auto;white-space:nowrap}',
    },
    474: {
        'base': '  .dt-table td{white-space:nowrap}',
    },
    475: {
        'time': '  .dt-big{font-size:38px}',
    },
    476: {
        'base': '}',
    },
}

GROUP_OF = {}
for g, spans in GROUPS.items():
    for (a, b) in spans:
        for n in range(a, b + 1):
            GROUP_OF[n] = g

out = {g: [] for g in GROUPS}
out['base'] = []
skipped_dead = []
rewrites = []

for n in range(1, len(lines) + 1):
    line = L(n)
    if n in DEAD:
        skipped_dead.append((n, line.strip()[:60]))
        continue
    if n in REWRITE:
        for g, text in REWRITE[n].items():
            out[g].append(text)
            rewrites.append((n, g, text[:60]))
        continue
    g = GROUP_OF.get(n, 'base')
    out[g].append(line)

# sanity: every original non-dead, non-rewrite line must be emitted exactly once
emitted = sum(len(v) for v in out.values())
expected = len(lines) - len(skipped_dead) - len([n for n in REWRITE])
expected += sum(len(v) for v in REWRITE.values())
assert emitted == expected, 'emitted %d != expected %d' % (emitted, expected)

HEADER = u'/* %s — auto-split from style.css (2026-10-19 per-page asset trimming). */\n'
NAMES = {
    'base': u'base layout / chrome (all pages)',
    'json': u'JSON & CSV editor tools (json pages only)',
    'diff': u'text diff tool',
    'regex': u'regex tester tool',
    'generator': u'random generator tool',
    'liveclock': u'live clock (timestamp page)',
    'time': u'date/time family tools',
    'baseconv': u'radix converter (base/binary/hex)',
    'worldclock': u'world clock dial view',
    'hotnews': u'trending news page',
    'cheatsheet': u'Go cheatsheet page',
    'snippets': u'code snippets library',
    'blog': u'blog index & articles',
    'evergreen': u'evergreen year reference pages',
    'legal': u'privacy page',
}

total = 0
for g in ['base'] + sorted(k for k in GROUPS if k != 'base'):
    body = '\n'.join(out[g]).strip('\n')
    if not body:
        print('EMPTY group: %s' % g)
        continue
    text = (HEADER % NAMES[g]) + body + '\n'
    path = os.path.join(SRC, g + '.css')
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    total += len(text.encode('utf-8'))
    print('%-12s %6d B  %4d lines -> %s.css' % (g, len(text.encode('utf-8')), body.count('\n') + 1, g))

print('---- total %d B (orig style.css %d B, dead dropped %d lines)' % (
    total, os.path.getsize(ORIG), len(skipped_dead)))
for n, t in skipped_dead:
    print('  dead L%d: %s' % (n, t))
for n, g, t in rewrites:
    print('  split L%d -> %s: %s' % (n, g, t))
