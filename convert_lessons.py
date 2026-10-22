#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把本地 Go 课程讲义（Markdown）转换为课程图文正文数据。

讲义源：D:\\AI\\go学习\\course\\lessons\\*.md  —— 唯一内容源，改讲义后重跑本脚本再重新构建
产物：src/course_lessons.py（LESSON_BODIES: slug -> body HTML 片段）

正文由构建期烘焙进静态页（与博客同哲学），不依赖 JS 注入；
代码块用 pygments 在构建期着色（Go / 无语言标记的 text 块）。

用法：
  python convert_lessons.py            # 转换全部 41 课
  python convert_lessons.py m01-l01    # 只转换指定课
"""

import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
SRC = ROOT / 'src'
LESSONS_DIR = Path(r'D:\AI\go学习\course\lessons')
OUT_FILE = SRC / 'course_lessons.py'

# 讲义章节标题 → 区块类型（按出现顺序匹配，标题含关键词即命中）
SECTION_RULES = [
    ('学习目标', 'goal'),
    ('知识讲解', 'body'),
    ('示例代码', 'body'),
    ('常见错误', 'warn'),
    ('最佳实践', 'tip'),
    ('练习题', 'exercise'),
    ('参考答案', 'answers'),
    ('本课小结', 'summary'),
]

MD = markdown.Markdown(
    extensions=['fenced_code', 'codehilite', 'tables', 'sane_lists', 'attr_list'],
    extension_configs={'codehilite': {'css_class': 'hl', 'guess_lang': False}},
    output_format='html5',
)


def md_to_html(text):
    MD.reset()
    return MD.convert(text).strip()


def split_head_and_sections(raw):
    """把讲义拆成 (头部引用块 markdown, [(章节标题, 类型, 章节 markdown)])。

    头部 = 第一个 `## ` 之前的内容；其中第一行的 `# 课程标题` 被剥离——
    页面 h1 由 course.py 的渲染函数输出，避免页面出现两个 h1。
    """
    m = re.search(r'^## ', raw, re.M)
    if m:
        head = raw[:m.start()].strip()
        rest = raw[m.start():].strip()
    else:
        head, rest = raw.strip(), ''
    head_lines = [ln for ln in head.splitlines() if not ln.startswith('# ')]
    head = '\n'.join(head_lines).strip()
    parts = re.split(r'^(## .+)$', rest, flags=re.M)   # 保留分隔符
    sections = []
    for i in range(1, len(parts), 2):
        title = parts[i][2:].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ''
        kind = 'body'
        for key, k in SECTION_RULES:
            if key in title:
                kind = k
                break
        sections.append((title, kind, content))
    return head, sections


def build_body(head, sections):
    """按类型组装课程页正文 HTML 片段（不含页面的 h1 / 元信息，那些由 course.py 渲染）。"""
    out = []
    if head:
        out.append('<div class="course-head">')
        out.append(md_to_html(head))
        out.append('</div>')
    for title, kind, content in sections:
        html = md_to_html(content)
        if kind == 'goal':
            out.append(f'<h2>{title}</h2>')
            out.append(f'<div class="course-goal">{html}</div>')
        elif kind == 'warn':
            out.append(f'<h2>{title}</h2>')
            out.append(f'<div class="course-warn">{html}</div>')
        elif kind == 'tip':
            out.append(f'<h2>{title}</h2>')
            out.append(f'<div class="course-tip">{html}</div>')
        elif kind == 'answers':
            out.append(f'<h2>{title}</h2>')
            out.append('<details class="course-answers">')
            out.append('<summary>参考答案（点击展开 / 收起）</summary>')
            out.append(html)
            out.append('</details>')
        elif kind == 'summary':
            out.append(f'<h2>{title}</h2>')
            out.append(f'<div class="course-summary">{html}</div>')
        else:
            out.append(f'<h2>{title}</h2>')
            out.append(html)
    return '\n'.join(out)


def convert_one(slug):
    path = LESSONS_DIR / f'{slug}.md'
    raw = path.read_text(encoding='utf-8')
    head, sections = split_head_and_sections(raw)
    return build_body(head, sections)


def main():
    args = sys.argv[1:]
    files = sorted(LESSONS_DIR.glob('*.md'))
    if args:
        files = [LESSONS_DIR / f'{a}.md' for a in args if (LESSONS_DIR / f'{a}.md').exists()]

    bodies = {}
    for f in files:
        slug = f.stem
        body = convert_one(slug)
        bodies[slug] = body
        print(f'  ✓ {slug}  ({len(body)} chars)')

    header = (
        '# -*- coding: utf-8 -*-\n'
        '"""课程正文数据（由 convert_lessons.py 从本地讲义 Markdown 生成，勿手改）。\n'
        '\n'
        '键：课时 slug（如 m01-l01）；值：课程页正文 HTML 片段。\n'
        '生成后需在 dev-tools 仓库重新构建（python build.py）才会生效。\n'
        '"""\n'
        'LESSON_BODIES = {\n'
    )
    lines = [header]
    for slug in sorted(bodies):
        lines.append(f'    {slug!r}: {bodies[slug]!r},\n')
    lines.append('}\n')
    OUT_FILE.write_text(''.join(lines), encoding='utf-8')
    print(f'\n已写入 {OUT_FILE}（{len(bodies)} 课）')


if __name__ == '__main__':
    main()
