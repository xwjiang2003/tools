# -*- coding: utf-8 -*-
"""Go 课程图文板块（/go-course/）：课程元数据 + 构建期渲染。

与博客同哲学：正文以 HTML 片段烘焙进静态页（正文数据在 course_lessons.py，
由仓库根目录 convert_lessons.py 从本地讲义 Markdown 生成），不依赖 JS 注入。

多语言：zh（全部 41 课）+ en（已翻译的课，lessons-en 目录）。页面由
build.py 生成对应语言版本；hreflang / 语言切换器由 build.py 的 apply_common 处理。

板块结构：
  go-course/              课程中心页（6 模块 × 41 课导航 + 课程简介）
  go-course/<slug>/       单课图文页（学习目标 / 讲解 / 高亮代码 / 避坑 / 练习折叠 / 小结）
  en/go-course/ 等语言前缀同理
"""

from course_lessons import LESSON_BODIES, LESSON_BODIES_EN

COURSE_INDEX = 'go-course/'

# 课程语言：zh（默认/无前缀）+ en（已翻译部分课）。其余语言暂不生成课程页。
COURSE_LANGS = ['zh', 'en']

# 课程模块与课表（zh）。标题与难度取自课程大纲（00-课程大纲.md）。
# phase（阶段/难度）：入门 / 基础 / 核心 / 工程 / 进阶 / 实战
MODULES = [
    {
        'id': 'm01',
        'name': 'Go 语言入门与开发环境',
        'phase': '入门',
        'goal': '装好环境，掌握基础语法、函数与内置容器，能写百行级小程序',
        'lessons': [
            ('m01-l01', 'Go 语言是什么：起源、设计哲学与适用场景'),
            ('m01-l02', '开发环境搭建：安装 Go、GOROOT/GOPATH/GOPROXY 与 go env'),
            ('m01-l03', '第一个 Go 程序与 go 命令详解：module 与工程初识'),
            ('m01-l04', 'Go 基础语法：变量、常量、基本类型与类型转换'),
            ('m01-l05', '运算符、流程控制与作用域'),
            ('m01-l06', '函数基础：多返回值、命名返回值与可变参数'),
            ('m01-l07', '数组、切片与 map：最常用的三种容器'),
            ('m01-l08', '字符串与 Unicode：rune、byte 与 strings 包'),
            ('m01-l09', '模块一综合实战：命令行单词统计工具 mini-wc'),
        ],
    },
    {
        'id': 'm02',
        'name': '复合数据类型与面向对象',
        'phase': '基础',
        'goal': '掌握指针、结构体、方法、接口、错误处理、泛型，形成 Go 式设计思维',
        'lessons': [
            ('m02-l01', '指针与内存：&、*、逃逸分析初识'),
            ('m02-l02', '结构体与方法：Go 的面向对象基石'),
            ('m02-l03', '接口：隐式实现、空接口与类型断言'),
            ('m02-l04', '组合优于继承：嵌入、接口组合与设计套路'),
            ('m02-l05', '错误处理：error 接口、错误包装与 sentinel error'),
            ('m02-l06', '泛型：类型参数、约束与泛型实践'),
        ],
    },
    {
        'id': 'm03',
        'name': '并发编程',
        'phase': '核心',
        'goal': '吃透 goroutine / channel / select / sync / context，能写正确的并发程序',
        'lessons': [
            ('m03-l01', '并发模型：Goroutine 与 GMP 调度器'),
            ('m03-l02', 'Channel 详解：通信、缓冲与方向'),
            ('m03-l03', 'Select 与超时控制：多路复用实战'),
            ('m03-l04', 'sync 包：Mutex、RWMutex、WaitGroup、Once'),
            ('m03-l05', 'Context：超时、取消与请求域数据'),
            ('m03-l06', '并发模式与陷阱：worker pool、errgroup、数据竞争检测'),
        ],
    },
    {
        'id': 'm04',
        'name': '工程化与标准库实战',
        'phase': '工程',
        'goal': '会用 module、测试、JSON、IO、时间、CLI、HTTP，能交付可维护的服务',
        'lessons': [
            ('m04-l01', '包与项目结构：module、internal 与依赖管理'),
            ('m04-l02', '单元测试与基准测试：testing 包全解'),
            ('m04-l03', '接口 Mock、依赖注入与 testdouble'),
            ('m04-l04', 'JSON 序列化：encoding/json 深入'),
            ('m04-l05', '文件与 IO：os、io、bufio、embed'),
            ('m04-l06', '时间处理：time 包与定时任务'),
            ('m04-l07', '命令行工具实战：flag、cobra 与日志 log/slog'),
            ('m04-l08', '网络编程基础：net、TCP/HTTP 客户端与服务端'),
        ],
    },
    {
        'id': 'm05',
        'name': '进阶主题与性能优化',
        'phase': '进阶',
        'goal': '反射、unsafe、pprof、GC、lint、设计模式，能定位并解决性能问题',
        'lessons': [
            ('m05-l01', '反射 reflect：原理、用法与代价'),
            ('m05-l02', 'unsafe、内存对齐与零拷贝技巧'),
            ('m05-l03', '性能优化：pprof、benchmark 与逃逸分析实战'),
            ('m05-l04', '内存管理与 GC：三色标记、GC 调优'),
            ('m05-l05', '代码质量与工具链：lint、静态分析与 CI'),
            ('m05-l06', '设计模式与惯用法：Go 风格的模式精选'),
        ],
    },
    {
        'id': 'm06',
        'name': '分布式与云原生实战',
        'phase': '实战',
        'goal': 'gRPC、数据库、缓存/消息队列、可观测性、容器化，完成毕业项目',
        'lessons': [
            ('m06-l01', 'gRPC 与 Protocol Buffers 入门'),
            ('m06-l02', '数据库编程：database/sql、连接池与 ORM'),
            ('m06-l03', '缓存与消息队列：Redis 与 Kafka 集成'),
            ('m06-l04', '微服务可观测性：日志、指标、链路追踪'),
            ('m06-l05', '容器化与部署：Docker 多阶段构建与 K8s 部署'),
            ('m06-l06', '综合毕业项目：高并发短链接服务（完整实现）'),
        ],
    },
]

# 英文版课程模块（仅已翻译/可用语言。标题与模块描述为英文讲义/大纲对应翻译）
MODULES_EN = [
    {
        'id': 'm01',
        'name': 'Go Language Intro & Dev Environment',
        'phase': 'Beginner',
        'goal': 'Set up the environment, master basic syntax, functions and built-in containers, and write small programs of ~100 lines',
        'lessons': [
            ('m01-l01', 'What Is Go: Origins, Design Philosophy and Use Cases'),
            ('m01-l02', 'Setting Up the Environment: Installing Go, GOROOT/GOPATH/GOPROXY and go env'),
            ('m01-l03', 'Your First Go Program and the go Command: Modules and Project Basics'),
            ('m01-l04', 'Go Basics: Variables, Constants, Primitive Types and Type Conversion'),
            ('m01-l05', 'Operators, Control Flow and Scope'),
            ('m01-l06', 'Functions: Multiple Returns, Named Returns and Variadic Parameters'),
            ('m01-l07', 'Arrays, Slices and Maps: The Three Essential Containers'),
            ('m01-l08', 'Strings and Unicode: rune, byte and the strings Package'),
            ('m01-l09', 'Module 1 Project: A CLI Word Counter mini-wc'),
        ],
    },
    {
        'id': 'm02',
        'name': 'Composite Data Types & Object-Oriented Design',
        'phase': 'Basics',
        'goal': 'Master pointers, structs, methods, interfaces, error handling and generics to form a Go-style design mindset',
        'lessons': [
            ('m02-l01', 'Pointers and Memory: &, * and an Intro to Escape Analysis'),
            ('m02-l02', 'Structs and Methods: The Foundation of Go OOP'),
            ('m02-l03', 'Interfaces: Implicit Implementation, Empty Interfaces and Type Assertions'),
            ('m02-l04', 'Composition over Inheritance: Embedding, Interface Composition and Design Patterns'),
            ('m02-l05', 'Error Handling: The error Interface, Error Wrapping and Sentinel Errors'),
            ('m02-l06', 'Generics: Type Parameters, Constraints and Practice'),
        ],
    },
    {
        'id': 'm03',
        'name': 'Concurrency',
        'phase': 'Core',
        'goal': 'Deeply understand goroutines, channels, select, sync and context, and write correct concurrent programs',
        'lessons': [
            ('m03-l01', 'Concurrency Model: Goroutines and the GMP Scheduler'),
            ('m03-l02', 'Channels: Communication, Buffering and Direction'),
            ('m03-l03', 'Select and Timeouts: Multiplexing in Practice'),
            ('m03-l04', 'The sync Package: Mutex, RWMutex, WaitGroup, Once'),
            ('m03-l05', 'Context: Timeouts, Cancellation and Request-Scoped Data'),
            ('m03-l06', 'Concurrency Patterns and Pitfalls: Worker Pools, errgroup and Race Detection'),
        ],
    },
    {
        'id': 'm04',
        'name': 'Engineering & Standard Library in Practice',
        'phase': 'Engineering',
        'goal': 'Use modules, testing, JSON, I/O, time, CLI and HTTP to deliver maintainable services',
        'lessons': [
            ('m04-l01', 'Packages and Project Structure: Modules, internal and Dependency Management'),
            ('m04-l02', 'Unit Tests and Benchmarks: The testing Package'),
            ('m04-l03', 'Interface Mocks, Dependency Injection and Test Doubles'),
            ('m04-l04', 'JSON Serialization: encoding/json in Depth'),
            ('m04-l05', 'Files and I/O: os, io, bufio, embed'),
            ('m04-l06', 'Time Handling: The time Package and Scheduled Tasks'),
            ('m04-l07', 'CLI Tools in Practice: flag, cobra and log/slog'),
            ('m04-l08', 'Network Programming Basics: net, TCP/HTTP Clients and Servers'),
        ],
    },
    {
        'id': 'm05',
        'name': 'Advanced Topics & Performance Tuning',
        'phase': 'Advanced',
        'goal': 'Reflection, unsafe, pprof, GC, lint and design patterns — locate and solve performance problems',
        'lessons': [
            ('m05-l01', 'Reflection (reflect): Principles, Usage and Cost'),
            ('m05-l02', 'unsafe, Memory Alignment and Zero-Copy Tricks'),
            ('m05-l03', 'Performance Tuning: pprof, Benchmarks and Escape Analysis in Practice'),
            ('m05-l04', 'Memory Management and GC: Tricolor Marking and GC Tuning'),
            ('m05-l05', 'Code Quality and Tooling: lint, Static Analysis and CI'),
            ('m05-l06', 'Design Patterns and Idioms: Selected Go-Style Patterns'),
        ],
    },
    {
        'id': 'm06',
        'name': 'Distributed Systems & Cloud-Native in Practice',
        'phase': 'Practice',
        'goal': 'gRPC, databases, caching/message queues, observability and containerization — complete the capstone project',
        'lessons': [
            ('m06-l01', 'gRPC and Protocol Buffers'),
            ('m06-l02', 'Database Programming: database/sql, Connection Pools and ORMs'),
            ('m06-l03', 'Caching and Message Queues: Redis and Kafka Integration'),
            ('m06-l04', 'Microservice Observability: Logs, Metrics and Tracing'),
            ('m06-l05', 'Containerization and Deployment: Docker Multi-Stage Builds and K8s'),
            ('m06-l06', 'Capstone Project: A High-Concurrency Short-URL Service'),
        ],
    },
]

# 已发布图文页：跟随 B 站视频进度（空间合集「Go语言从入门到精通」已更 26 集）。
# 批量转换 + 构建后自动全量。
PUBLISHED = (
    'm01-l01', 'm01-l02', 'm01-l03', 'm01-l04', 'm01-l05', 'm01-l06',
    'm01-l07', 'm01-l08', 'm01-l09', 'm02-l01', 'm02-l02', 'm02-l03',
    'm02-l04', 'm02-l05', 'm02-l06',
    'm03-l01', 'm03-l02', 'm03-l03', 'm03-l04', 'm03-l05', 'm03-l06',
    'm04-l01', 'm04-l02', 'm04-l03', 'm04-l04', 'm04-l05',
)

# 配套视频（B 站链接，来自 UP 主 jxw_go 空间合集，2026-10-29 核对 26 集）
VIDEO = {
    'm01-l01': 'https://www.bilibili.com/video/BV1CNa36HET6',
    'm01-l02': 'https://www.bilibili.com/video/BV19yaG6kEfi',
    'm01-l03': 'https://www.bilibili.com/video/BV1nfa76BEdH',
    'm01-l04': 'https://www.bilibili.com/video/BV1DmaH6aEZz',
    'm01-l05': 'https://www.bilibili.com/video/BV12JaW6bED7',
    'm01-l06': 'https://www.bilibili.com/video/BV1ZiaW6mEXN',
    'm01-l07': 'https://www.bilibili.com/video/BV1BiaW6mEEB',
    'm01-l08': 'https://www.bilibili.com/video/BV1YFYN6WEmh',
    'm01-l09': 'https://www.bilibili.com/video/BV1GAYN6pEyU',
    'm02-l01': 'https://www.bilibili.com/video/BV1Z4a66ZE73',
    'm02-l02': 'https://www.bilibili.com/video/BV1wXHS6qE8a',
    'm02-l03': 'https://www.bilibili.com/video/BV1HPpb6kE7e',
    'm02-l04': 'https://www.bilibili.com/video/BV1NKpG6TEr3',
    'm02-l05': 'https://www.bilibili.com/video/BV1N7pD6VEGv',
    'm02-l06': 'https://www.bilibili.com/video/BV1kmpk6SEnC',
    'm03-l01': 'https://www.bilibili.com/video/BV1BPJS6pEwt',
    'm03-l02': 'https://www.bilibili.com/video/BV1dCnM6qEwQ',
    'm03-l03': 'https://www.bilibili.com/video/BV15ynJ6qEx1',
    'm03-l04': 'https://www.bilibili.com/video/BV1penc6hER7',
    'm03-l05': 'https://www.bilibili.com/video/BV1Pknz66ExB',
    'm03-l06': 'https://www.bilibili.com/video/BV1munm6PEpb',
    'm04-l01': 'https://www.bilibili.com/video/BV1EznY67EDM',
    'm04-l02': 'https://www.bilibili.com/video/BV1punR67ERM',
    'm04-l03': 'https://www.bilibili.com/video/BV1jpnR6BEDn',
    'm04-l04': 'https://www.bilibili.com/video/BV1yLx56UEne',
    'm04-l05': 'https://www.bilibili.com/video/BV1AEx56mEHY',
}

# 中心页文案（按语言）
COURSE_TEXT = {
    'zh': {
        'index_title': 'Go 语言从入门到精通：6 大模块 41 课图文教程 | DevTools',
        'index_desc': (
            '零基础到高级工程实践的 Go 完整学习路线：6 大模块 41 课，每课含学习目标、'
            '知识讲解、可运行示例代码、常见错误避坑、最佳实践与练习题，配套 B 站视频课程。'
        ),
        'index_kw': 'Go教程,Go语言入门,Go并发,Go工程化,Go性能优化,Go云原生,Go课程',
        'h1': 'Go 语言从入门到精通',
        'lead': '零基础到高级工程实践 · 6 大模块 41 课 · 每课：目标 / 讲解 / 可运行代码 / 避坑 / 练习',
    },
    'en': {
        'index_title': 'Go from Zero to Pro: 41-Lesson Illustrated Tutorial in 6 Modules | DevTools',
        'index_desc': (
            'A complete Go learning path from zero to advanced engineering practice: 6 modules, 41 lessons, '
            'each with learning objectives, explanations, runnable example code, common-mistake pitfalls, '
            'best practices and exercises, paired with a Bilibili video course.'
        ),
        'index_kw': 'Go tutorial,Learn Go,Go concurrency,Go engineering,Go performance,Go cloud-native,Go course',
        'h1': 'Go from Zero to Pro',
        'lead': 'Zero to advanced engineering practice · 6 modules · 41 lessons · each: objectives / explanations / runnable code / pitfalls / exercises',
    },
}

# 单课/渲染界面文案（按语言）
UI = {
    'zh': {
        'lesson_of': '第 {i}/{t} 课 · {mod}',
        'video_link': '🎬 配套视频讲解（B 站）',
        'video_coming': '配套视频讲解 · 制作中，先看图文版',
        'prev': '← 上一课：{t}',
        'next': '下一课：{t} →',
        'first': '← 已是第一课',
        'last': '已是最后一课 →',
        'todo_badge': '制作中',
        'mod_count': '{n} 课',
        'meta_title': '{t}（第 {i} 课图文教程）| DevTools Go 课程',
        'meta_desc': 'Go 课程第 {i} 课：{t}。含学习目标、知识讲解、可运行示例代码、常见错误避坑、最佳实践与练习参考答案，配套 B 站视频。',
        'meta_kw': 'Go,{t},Go 教程,Go 学习,{mod}',
        'in_lang': 'zh-CN',
    },
    'en': {
        'lesson_of': 'Lesson {i}/{t} · {mod}',
        'video_link': '🎬 Companion Video (Bilibili)',
        'video_coming': 'Companion video coming soon — read the illustrated version for now',
        'prev': '← Previous: {t}',
        'next': 'Next: {t} →',
        'first': '← Already the first lesson',
        'last': 'Last lesson →',
        'todo_badge': 'In Progress',
        'mod_count': '{n} lessons',
        'meta_title': '{t} (Lesson {i} Illustrated Tutorial) | DevTools Go Course',
        'meta_desc': 'Go course lesson {i}: {t}. Learning objectives, explanations, runnable example code, common-mistake pitfalls, best practices and exercise answers, paired with a Bilibili video.',
        'meta_kw': 'Go,{t},Go tutorial,Learn Go,{mod}',
        'in_lang': 'en',
    },
}


def lesson_path(slug):
    return f'{COURSE_INDEX}{slug}/'


def _modules(lang):
    return MODULES_EN if lang == 'en' else MODULES


def _ui(lang):
    return UI.get(lang, UI['zh'])


def _flat_lessons(lang='zh'):
    """展平全部课程（按模块顺序），附带所属模块信息。"""
    out = []
    for mod in _modules(lang):
        for slug, title in mod['lessons']:
            out.append({'slug': slug, 'title': title, 'module': mod})
    return out


def _bodies(lang):
    return LESSON_BODIES_EN if lang == 'en' else LESSON_BODIES


def lesson_meta(slug, lang='zh'):
    """单课 SEO 元数据 + 渲染所需信息。"""
    flat = _flat_lessons(lang)
    idx = next(i for i, l in enumerate(flat) if l['slug'] == slug)
    les = flat[idx]
    mod = les['module']
    u = _ui(lang)
    published = slug in PUBLISHED and slug in _bodies(lang)
    return {
        'slug': slug,
        'title': u['meta_title'].format(t=les['title'], i=idx + 1),
        'h1': les['title'],
        'module_id': mod['id'],
        'module_name': mod['name'],
        'phase': mod['phase'],
        'index': idx + 1,
        'total': len(flat),
        'published': published,
        'description': u['meta_desc'].format(i=idx + 1, t=les['title']),
        'keywords': u['meta_kw'].format(t=les['title'], mod=mod['name']),
        'date': '2026-10-22',
        'prev': flat[idx - 1] if idx > 0 else None,
        'next': flat[idx + 1] if idx + 1 < len(flat) else None,
    }


def _esc(s):
    import html as html_mod
    return html_mod.escape(str(s if s is not None else ''), quote=True)


def render_course_index(base='', lang='zh'):
    """课程中心页：课程简介 + 6 模块导航 + 课表（已发布课链接，其余标注制作中）。"""
    ct = COURSE_TEXT.get(lang, COURSE_TEXT['zh'])
    u = _ui(lang)
    out = ['<div class="course-home">']
    out.append('  <div class="course-home-head">')
    out.append(f'    <h1>{_esc(ct["h1"])}</h1>')
    out.append(f'    <p class="course-home-lead">{_esc(ct["lead"])}</p>')
    out.append('  </div>')

    out.append('  <div class="course-modules">')
    bodies = _bodies(lang)
    for mod in _modules(lang):
        n = len(mod['lessons'])
        done = sum(1 for slug, _ in mod['lessons'] if slug in PUBLISHED and slug in bodies)
        out.append('    <div class="course-mod">')
        out.append(f'      <div class="course-mod-head"><span class="course-phase">{_esc(mod["phase"])}</span>'
                   f'<span class="course-mod-name">{_esc(mod["name"])}</span>'
                   f'<span class="course-mod-count">{_esc(u["mod_count"].format(n=n))}</span></div>')
        out.append(f'      <p class="course-mod-goal">{_esc(mod["goal"])}</p>')
        out.append('      <ul class="course-mod-lessons">')
        for slug, title in mod['lessons']:
            if slug in PUBLISHED and slug in bodies:
                out.append(f'        <li><a href="{_esc(base + lesson_path(slug))}">'
                           f'<span class="course-lesson-id">{_esc(slug)}</span>'
                           f'{_esc(title)}</a></li>')
            else:
                out.append(f'        <li class="course-todo"><span class="course-lesson-id">{_esc(slug)}</span>'
                           f'{_esc(title)}<em class="course-badge">{_esc(u["todo_badge"])}</em></li>')
        out.append('      </ul>')
        out.append('    </div>')
        out.append('')
    out.append('  </div>')
    out.append('</div>')
    return '\n'.join(out)


def render_lesson(slug, base='', lang='zh'):
    """单课图文页主体：元信息 + h1 + 配套视频 + 正文 + 上下课导航。"""
    m = lesson_meta(slug, lang)
    body = _bodies(lang).get(slug, '')
    video = VIDEO.get(slug)
    u = _ui(lang)

    out = ['<article class="course-post">']
    out.append('  <div class="course-meta">')
    out.append(f'    <span class="course-meta-mod">{_esc(u["lesson_of"].format(i=m["index"], t=m["total"], mod=m["module_name"]))}</span>')
    out.append(f'    <span class="course-meta-phase">{_esc(m["phase"])}</span>')
    out.append(f'    <span class="course-meta-id">{_esc(m["slug"])}</span>')
    out.append('  </div>')
    out.append(f'  <h1>{_esc(m["h1"])}</h1>')
    if video:
        out.append(f'    <div class="course-video"><a class="course-video-link" href="{_esc(video)}" '
                   f'target="_blank" rel="noopener">{_esc(u["video_link"])}</a></div>')
    else:
        out.append(f'    <div class="course-video course-video-coming">{_esc(u["video_coming"])}</div>')
    out.append('')
    out.append(body.strip())
    out.append('')
    out.append('  <div class="course-pager">')
    if m['prev']:
        out.append(f'    <a class="course-pager-prev" href="{_esc(base + lesson_path(m["prev"]["slug"]))}">'
                   f'{_esc(u["prev"].format(t=m["prev"]["title"]))}</a>')
    else:
        out.append(f'    <span class="course-pager-prev course-pager-none">{_esc(u["first"])}</span>')
    if m['next']:
        out.append(f'    <a class="course-pager-next" href="{_esc(base + lesson_path(m["next"]["slug"]))}">'
                   f'{_esc(u["next"].format(t=m["next"]["title"]))}</a>')
    else:
        out.append(f'    <span class="course-pager-next course-pager-none">{_esc(u["last"])}</span>')
    out.append('  </div>')
    out.append('</article>')
    return '\n'.join(out)


def course_index_jsonld(url, lang='zh'):
    """中心页 CollectionPage + ItemList 结构化数据。"""
    u = _ui(lang)
    ct = COURSE_TEXT.get(lang, COURSE_TEXT['zh'])
    bodies = _bodies(lang)
    items = []
    for l in _flat_lessons(lang):
        if l['slug'] in PUBLISHED and l['slug'] in bodies:
            items.append({
                '@type': 'ListItem',
                'position': items.__len__() + 1,
                'name': l['title'],
                'url': url + l['slug'] + '/',
            })
    return {
        '@type': 'CollectionPage',
        'name': ct['h1'],
        'url': url,
        'description': ct['index_desc'],
        'inLanguage': u['in_lang'],
        'isPartOf': {'@type': 'WebSite', 'name': 'DevTools'},
        'mainEntity': {
            '@type': 'ItemList',
            'itemListElement': items,
        },
    }


def lesson_jsonld(m, url, lang='zh'):
    """课程页 TechArticle 结构化数据。"""
    return {
        '@type': 'TechArticle',
        'headline': m['h1'],
        'description': m['description'],
        'url': url,
        'datePublished': m['date'],
        'dateModified': m['date'],
        'inLanguage': _ui(lang)['in_lang'],
        'isAccessibleForFree': True,
        'author': {'@type': 'Organization', 'name': 'DevTools'},
        'keywords': m['keywords'],
    }
