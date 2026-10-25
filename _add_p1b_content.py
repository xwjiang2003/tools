# -*- coding: utf-8 -*-
"""插入 P1 批次两个新工具页（sql-formatter / markdown-to-html）的中英内容条目
与 8 语言短字段，并修正 csv-to-sql-insert seealso 里的 './' 死链。
幂等：已存在同名条目时跳过。
"""
import io, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

ZH_BLOCK = """        'slug': 'sql-formatter',
        'path': 'sql-formatter/',
        'nav': 'SQL 格式化',
        'title': 'SQL 在线格式化工具 - 关键字大写、缩进与子句换行 | DevTools',
        'description': (
            '免费在线 SQL 格式化工具：自动换行、缩进与关键字大写，支持 SELECT、多表 JOIN、子查询、'
            'INSERT、UPDATE 与 CREATE TABLE 等常用语句。缩进宽度可选 2/4 空格，可保留原始大小写，'
            '纯浏览器本地处理，SQL 内容不上传服务器。'
        ),
        'keywords': (
            'sql格式化,在线sql格式化,sql美化工具,sql beautifier,sql关键字大写,'
            'sql换行缩进,sql format online,数据库语句格式化'
        ),
        'h1': 'SQL 在线格式化工具',
        'intro': [
            '写成一行的 SQL 难以 review，这个工具把它还原成可读的结构：每个主要子句独立成行，'
            '字段列表与条件逐行排列，JOIN、ON、AND 按层级缩进，关键字统一大写——'
            '子查询、INSERT、UPDATE、CREATE TABLE 也按同一套规则处理。',
            '缩进宽度（2/4 空格）与是否大写关键字都可选，输出只改排版、不改语义。'
            '全部计算在浏览器本地完成，数据库语句不会离开你的设备。',
        ],
        'features': [
            ('子句级换行', 'SELECT、FROM、WHERE、GROUP BY、ORDER BY、HAVING、LIMIT 等主要子句各自独立成行。'),
            ('条件与 JOIN 缩进', 'AND / OR / ON 等条件按层级缩进，多表 JOIN 与子查询的层次一目了然。'),
            ('大小写可选', '关键字可统一大写或保留原样，标识符与字符串字面量永不被改写。'),
            ('缩进可调', '2 空格或 4 空格一键切换，适配不同团队的代码规范。'),
            ('多语句支持', '整段脚本按分号拆分，每条语句各自完整格式化，互不串行。'),
            ('纯本地运行', '解析与排版都在浏览器内完成，SQL 不上传、不落盘。'),
        ],
        'steps': [
            '在左侧粘贴需要格式化的 SQL，可以是一条语句也可以是整个脚本。',
            '按需调整「大写」与「Indent」选项。',
            '点「格式化」，右侧得到排版后的 SQL。',
            '点「复制」或「下载」取走结果，贴回数据库客户端执行。',
        ],
        'faq': [
            ('使用这个页面会收集我的数据吗？',
             '不会。页面内容要么在构建时就写进 HTML，要么全部在你的浏览器本地完成计算，'
             '输入内容不会发送到任何服务器；除了页脚访问量统计（百度统计与不蒜子，见隐私政策），'
             '本站不收集你的任何行为数据。'),
            ('会改变 SQL 的含义吗？',
             '不会。工具只调整空白与换行：关键字大小写、缩进、子句换行。'
             '字符串字面量、注释与标识符的原始内容都会原样保留，语义与输入完全一致。'),
            ('支持哪些 SQL 方言？',
             '排版规则按通用 SQL 设计，覆盖 MySQL、PostgreSQL、SQLite、SQL Server 的常见写法：'
             '多词关键字（GROUP BY、LEFT OUTER JOIN）、限定名（schema.table）、'
             '三种引号（单引号字符串、双引号标识符、反引号标识符）都能正确识别。'),
            ('为什么注释的位置变了？',
             '行注释（-- 与 #）和块注释（/* */）会作为独立内容原样保留，'
             '但所在的行会随所属子句重新排版；注释文字本身不会被修改。'),
            ('函数里的逗号为什么不换行？',
             '括号内的逗号按函数参数处理，保持行内（如 count(a, b)）；只有 SELECT 列表、'
             'GROUP BY 等顶层列表的逗号才逐行排列，避免把函数调用拆碎。'),
        ],
        'seealso': [
            ('代码格式化工具（HTML / CSS / JS / SQL）', 'formatter/'),
            ('CSV 转 SQL INSERT 语句', 'csv-to-sql-insert/'),
            ('JSON 与 CSV 双向转换（JSON 工具箱）', 'json/'),
            ('Go 命令速查表', 'go-cheatsheet/'),
            ('常用代码片段（Go / Python / JS / SQL / Git）', 'snippets/'),
        ],
    },
    {
        'slug': 'markdown-to-html',
        'path': 'markdown-to-html/',
        'nav': 'MD 转 HTML',
        'title': 'Markdown 转 HTML - 在线转换器，支持表格与代码块 | DevTools',
        'description': (
            '在线 Markdown 转 HTML：标题、有序无序列表、表格、围栏代码块、引用、链接与图片全支持，'
            '输出干净的语义化 HTML。可复制代码片段或下载完整网页文件，纯浏览器本地转换，内容不上传。'
        ),
        'keywords': (
            'markdown转html,markdown to html,在线markdown转换,md转html,'
            'markdown转换器,markdown预览,markdown html 转换'
        ),
        'h1': 'Markdown 转 HTML 工具',
        'intro': [
            '把 Markdown 实时转换成干净的语义化 HTML：标题层级、列表、表格、围栏代码块、'
            '引用块、分隔线以及行内的加粗、斜体、删除线、行内代码、链接与图片都有对应标签。'
            '右侧可切换「预览」直接看渲染效果。',
            '所有文本先做 HTML 转义再套 Markdown 规则，链接与图片的 URL 会校验协议——'
            '粘贴进来的 HTML 或 javascript: 链接不会逃逸成可执行代码。转换全程在浏览器完成，'
            'Markdown 原文不会发送到任何服务器。',
        ],
        'features': [
            ('完整块级语法', '标题、列表（含一层嵌套）、表格、代码块、引用、分隔线、段落。'),
            ('行内语法齐全', '加粗、斜体、删除线、行内代码、链接、图片，代码内容不参与行内替换。'),
            ('XSS 安全', '文本先转义后渲染，javascript: / data: 协议的链接与图片会被拦截。'),
            ('表格对齐', '支持左对齐、右对齐、居中三种列对齐方式的表格转换。'),
            ('片段或整页', '结果区可直接复制 HTML 片段，下载则得到带完整文档结构的 .html 文件。'),
            ('纯本地转换', '没有后端接口，Markdown 内容不出浏览器，断网也能用。'),
        ],
        'steps': [
            '在左侧粘贴 Markdown 文本，点「示例」可以先看一份完整演示。',
            '点「转换」，右侧按「预览」开关显示渲染结果或 HTML 源码。',
            '点「复制」拿走 HTML 片段，或点「下载」保存完整网页文件。',
        ],
        'faq': [
            ('使用这个页面会收集我的数据吗？',
             '不会。页面内容要么在构建时就写进 HTML，要么全部在你的浏览器本地完成计算，'
             '输入内容不会发送到任何服务器；除了页脚访问量统计（百度统计与不蒜子，见隐私政策），'
             '本站不收集你的任何行为数据。'),
            ('转换结果可以直接用到生产页面吗？',
             '可以。输出是标准的语义化 HTML（h1-h6、p、ul/ol/li、table、pre/code、blockquote），'
             '样式完全由你自己的 CSS 决定；下载选项还会附带完整的 DOCTYPE 与 viewport 声明。'),
            ('支持 GFM 的删除线和表格吗？',
             '支持。~~删除线~~、| 表格 |、围栏代码块（```）都在支持范围内，'
             '任务列表（- [ ]）暂不支持，会按普通列表渲染。'),
            ('为什么我粘贴的 HTML 标签消失了？',
             '为了安全，所有文本都会先做 HTML 转义：<div> 会显示为 &lt;div&gt; 而不是被当成真标签。'
             '这是刻意的设计——本工具只把 Markdown 语法转成 HTML，不执行你粘贴的 HTML。'),
            ('代码块里的 Markdown 语法会被处理吗？',
             '不会。围栏代码块与行内代码的内容按纯文本转义输出，'
             '里面的 **、[link] 等都会原样显示，不会被误渲染。'),
        ],
        'seealso': [
            ('代码格式化工具（HTML / CSS / JS / SQL）', 'formatter/'),
            ('JSON 与 YAML 双向转换', 'yaml/'),
            ('JSON 与 TOML 双向转换', 'toml/'),
            ('JSON 与 CSV 双向转换（JSON 工具箱）', 'json/'),
            ('常用代码片段（Go / Python / JS / SQL / Git）', 'snippets/'),
        ],
    },
    {
"""

EN_BLOCK = """    'sql-formatter': {
        'nav': 'SQL Formatter',
        'title': 'SQL Formatter Online — Pretty-Print SQL Free | DevTools',
        'description': (
            'Free online SQL formatter: line breaks, indentation and keyword casing for SELECT, '
            'multi-table JOIN, subqueries, INSERT, UPDATE and CREATE TABLE. Indent width 2 or 4 spaces, '
            'optional keyword uppercasing, everything runs locally in your browser.'
        ),
        'keywords': (
            'sql formatter,online sql formatter,sql beautifier,sql format online,'
            'sql keyword uppercase,sql pretty print,format sql query'
        ),
        'h1': 'SQL Formatter Online',
        'intro': [
            'One-line SQL is hard to review. This tool restores its structure: every major clause on its '
            'own line, field lists and conditions one per line, JOIN / ON / AND indented by level, and '
            'keywords uppercased — subqueries, INSERT, UPDATE and CREATE TABLE follow the same rules.',
            'Indent width (2 or 4 spaces) and keyword casing are both optional, and the output only '
            'changes layout, never meaning. Everything runs locally in your browser; your SQL never '
            'leaves the page.',
        ],
        'features': [
            ('Clause-level breaks', 'SELECT, FROM, WHERE, GROUP BY, ORDER BY, HAVING, LIMIT and friends each get their own line.'),
            ('Condition & JOIN indent', 'AND / OR / ON nest by level, so multi-table joins and subqueries read cleanly.'),
            ('Optional casing', 'Uppercase keywords or keep the original spelling; identifiers and string literals are never touched.'),
            ('Indent width', 'Switch between 2 and 4 spaces to match your team style guide.'),
            ('Multi-statement ready', 'A whole script is split on semicolons and each statement is formatted on its own.'),
            ('Runs locally', 'Parsing and layout happen in the browser — no upload, no server round-trip.'),
        ],
        'steps': [
            'Paste the SQL you want formatted into the left panel — one statement or a whole script.',
            'Adjust the "大写" (uppercase) and Indent options if needed.',
            'Hit 格式化 (Format) and read the result on the right.',
            'Copy or download the result and paste it back into your database client.',
        ],
        'faq': [
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs '
             'locally in your browser, so your input is never sent to any server. Apart from the footer '
             'traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site '
             'collects nothing about your visit.'),
            ('Does formatting change the meaning of my SQL?',
             'No. Only whitespace and line breaks change: keyword casing, indentation and clause breaks. '
             'String literals, comments and identifiers are preserved exactly as written.'),
            ('Which SQL dialects are supported?',
             'The layout rules target common SQL and cover the usual MySQL, PostgreSQL, SQLite and SQL '
             'Server syntax: multi-word keywords (GROUP BY, LEFT OUTER JOIN), qualified names '
             '(schema.table) and all three quote styles are recognised.'),
            ('Why did my comments move?',
             'Line comments (-- and #) and block comments (/* */) are kept verbatim as their own tokens, '
             'but the line they sit on is re-indented with the surrounding clause. Comment text itself '
             'is never modified.'),
            ('Why does the comma inside a function not break the line?',
             'Commas inside parentheses are treated as function arguments and stay inline (count(a, b)); '
             'only top-level lists such as the SELECT list or GROUP BY break one item per line, so '
             'function calls are never torn apart.'),
        ],
        'seealso': [
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
            ('CSV to SQL INSERT generator', 'csv-to-sql-insert/'),
            ('JSON and CSV converter', 'json/'),
            ('Go toolchain cheatsheet', 'go-cheatsheet/'),
            ('Code snippets (Go / Python / JS / SQL / Git)', 'snippets/'),
        ],
    },
    'markdown-to-html': {
        'nav': 'MD to HTML',
        'title': 'Markdown to HTML — Online MD Converter | DevTools',
        'description': (
            'Convert Markdown to HTML online: headings, ordered and unordered lists, tables, fenced code '
            'blocks, quotes, links and images all render to clean semantic HTML. Copy the fragment or '
            'download a full page — everything runs locally in your browser.'
        ),
        'keywords': (
            'markdown to html,online markdown converter,md to html,markdown converter,'
            'markdown preview,markdown html,convert markdown'
        ),
        'h1': 'Markdown to HTML Converter',
        'intro': [
            'Turn Markdown into clean semantic HTML in real time: heading levels, lists, tables, fenced '
            'code blocks, block quotes, horizontal rules and inline bold, italic, strikethrough, code, '
            'links and images all get their proper tags. Toggle 预览 (preview) to see the rendered page.',
            'All text is HTML-escaped before the Markdown rules run, and link or image URLs are '
            'scheme-checked — pasted HTML or javascript: links cannot escape into executable markup. '
            'Conversion happens entirely in the browser; your Markdown is never sent anywhere.',
        ],
        'features': [
            ('Full block syntax', 'Headings, lists (one nesting level), tables, code fences, quotes, rules and paragraphs.'),
            ('Complete inline set', 'Bold, italic, strikethrough, inline code, links and images; code content is never re-parsed.'),
            ('XSS-safe', 'Text is escaped first and javascript: / data: URLs are rejected, so nothing executes.'),
            ('Table alignment', 'Left, right and centre column alignment in Markdown tables.'),
            ('Fragment or page', 'Copy just the HTML fragment, or download a complete .html file with DOCTYPE and viewport.'),
            ('Runs locally', 'No backend call at all — works offline once the page has loaded.'),
        ],
        'steps': [
            'Paste Markdown into the left panel; the 示例 (sample) button loads a full demo.',
            'Hit 转换 (Convert) and read the result on the right as preview or source.',
            'Copy the HTML fragment, or download it as a complete web page file.',
        ],
        'faq': [
            ('Does this page collect my data?',
             'No. The content is either baked into the HTML at build time or every calculation runs '
             'locally in your browser, so your input is never sent to any server. Apart from the footer '
             'traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site '
             'collects nothing about your visit.'),
            ('Can I use the output on a production page?',
             'Yes. The output is standard semantic HTML (h1-h6, p, ul/ol/li, table, pre/code, '
             'blockquote) and carries no styling of its own; the download option even wraps it in a '
             'full document with DOCTYPE and viewport.'),
            ('Are GFM strikethrough and tables supported?',
             'Yes. ~~strikethrough~~, | tables | and ``` fenced code are all supported. Task lists '
             '(- [ ]) are not, and render as plain list items.'),
            ('Why did the HTML tags I pasted disappear?',
             'For safety every text run is HTML-escaped first, so <div> shows up as &lt;div&gt; instead '
             'of becoming a real tag. This is deliberate: the tool converts Markdown syntax to HTML, '
             'it does not execute the HTML you paste.'),
            ('Is Markdown syntax inside code blocks processed?',
             'No. Fenced code blocks and inline code are escaped as plain text, so ** and [link] '
             'inside them display literally instead of being rendered.'),
        ],
        'seealso': [
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
            ('JSON and YAML converter', 'yaml/'),
            ('JSON and TOML converter', 'toml/'),
            ('JSON and CSV converter', 'json/'),
            ('Code snippets (Go / Python / JS / SQL / Git)', 'snippets/'),
        ],
    },
"""

# 8 语言短字段：slug -> (nav, title, description, keywords, h1)
SHORT = {
    'sql-formatter': {
        'ja': ('SQLフォーマッタ', 'SQL 整形ツール オンライン — SELECT/INSERT を美しく | DevTools',
               'SELECT、JOIN、サブクエリ、INSERT、CREATE TABLE に対応した無料の SQL 整形ツール。キーワードの大文字化とインデント幅を選べます。処理はすべてブラウザ内で完結。',
               'sql 整形,sql フォーマッタ,sql 美化,オンライン sql,sql インデント,クエリ 整形', 'SQL フォーマッタ オンライン'),
        'ko': ('SQL 포맷터', 'SQL 포맷터 온라인 — SELECT/INSERT 예쁘게 | DevTools',
               'SELECT, JOIN, 서브쿼리, INSERT, CREATE TABLE을 지원하는 무료 SQL 포맷터. 키워드 대문자와 들여쓰기 너비를 선택할 수 있고, 모든 처리는 브라우저에서 이루어집니다.',
               'sql 포맷,sql 포맷터,sql 정렬,온라인 sql,sql 포맷팅,sql 예쁘게', 'SQL 포맷터 온라인'),
        'es': ('Formateador SQL', 'Formateador SQL online — Embellece consultas | DevTools',
               'Formateador SQL gratuito en línea: saltos de línea, sangría y mayúsculas en palabras clave para SELECT, JOIN, subconsultas, INSERT y CREATE TABLE. Todo se procesa en tu navegador.',
               'formateador sql,sql online,formatear sql,sql beautifier,sql formato,sql indentar', 'Formateador SQL online'),
        'pt-BR': ('Formatador SQL', 'Formatador SQL online — Deixe o código limpo | DevTools',
               'Formatador SQL gratuito: quebras de linha, indentação e palavras-chave em maiúsculas para SELECT, JOIN, subconsultas, INSERT e CREATE TABLE. Tudo funciona no seu navegador.',
               'formatador sql,sql online,formatar sql,sql beautifier,sql indentação,formatar consulta sql', 'Formatador SQL online'),
        'fr': ('Formateur SQL', 'Formateur SQL en ligne — Embellir vos requêtes | DevTools',
               'Formateur SQL gratuit en ligne : retours à la ligne, indentation et mots-clés en majuscules pour SELECT, JOIN, sous-requêtes, INSERT et CREATE TABLE. Tout tourne dans votre navigateur.',
               'formateur sql,sql en ligne,formater sql,sql beautifier,indentation sql,mise en forme sql', 'Formateur SQL en ligne'),
        'de': ('SQL-Formatter', 'SQL-Formatter online — Queries übersichtlich | DevTools',
               'Kostenloser SQL-Formatter online: Zeilenumbrüche, Einrückung und Großschreibung für SELECT, JOIN, Unterabfragen, INSERT und CREATE TABLE. Alles läuft im Browser.',
               'sql formatter,sql online,sql formatieren,sql beautifier,sql einrücken,sql query formatieren', 'SQL-Formatter online'),
        'ru': ('SQL-форматтер', 'SQL-форматтер онлайн — Красивый SQL код | DevTools',
               'Бесплатный онлайн-форматтер SQL: переносы строк, отступы и заглавные ключевые слова для SELECT, JOIN, подзапросов, INSERT и CREATE TABLE. Всё работает в браузере.',
               'sql форматтер,форматировать sql,sql онлайн,sql beautifier,отступы sql,формат sql запроса', 'SQL-форматтер онлайн'),
        'id': ('Format SQL', 'Format SQL online — Rapikan query Anda | DevTools',
               'Format SQL gratis online: pemisahan baris, indentasi, dan huruf besar kata kunci untuk SELECT, JOIN, subquery, INSERT, dan CREATE TABLE. Semua diproses di browser Anda.',
               'format sql,sql online,format sql online,sql beautifier,indentasi sql,merapikan sql', 'Format SQL online'),
    },
    'markdown-to-html': {
        'ja': ('MD→HTML', 'Markdown → HTML 変換 - テーブル対応オンライン | DevTools',
               'Markdown を HTML に変換する無料オンラインツール。見出し、リスト、テーブル、コードブロック、引用、リンクと画像に対応。変換はすべてブラウザ内で完結します。',
               'markdown html,markdown 変換,md html,markdown to html,html 変換,markdown テーブル', 'Markdown → HTML 変換ツール'),
        'ko': ('MD→HTML', 'Markdown → HTML 변환 - 테이블 지원 | DevTools',
               'Markdown을 HTML로 변환하는 무료 온라인 도구. 제목, 목록, 표, 코드 블록, 인용, 링크와 이미지를 지원하며 모든 변환은 브라우저에서 처리됩니다.',
               'markdown html,markdown 변환,md html,마크다운 html,markdown to html,html 변환기', 'Markdown → HTML 변환기'),
        'es': ('MD a HTML', 'Markdown a HTML — Convertidor online | DevTools',
               'Convierte Markdown a HTML online y gratis: encabezados, listas, tablas, bloques de código, citas, enlaces e imágenes. Todo se convierte en tu navegador.',
               'markdown a html,convertidor markdown,md a html,markdown online,convertir markdown,markdown tabla', 'Convertidor de Markdown a HTML'),
        'pt-BR': ('MD para HTML', 'Markdown para HTML — Conversor online | DevTools',
               'Converta Markdown para HTML online e de graça: títulos, listas, tabelas, blocos de código, citações, links e imagens. Tudo roda no seu navegador.',
               'markdown para html,conversor markdown,md para html,markdown online,converter markdown,markdown tabela', 'Conversor de Markdown para HTML'),
        'fr': ('MD vers HTML', 'Markdown vers HTML — Convertisseur en ligne | DevTools',
               'Convertissez Markdown en HTML en ligne et gratuitement : titres, listes, tableaux, blocs de code, citations, liens et images. Tout se passe dans votre navigateur.',
               'markdown vers html,convertisseur markdown,md vers html,markdown en ligne,convertir markdown,markdown tableau', 'Convertisseur Markdown vers HTML'),
        'de': ('MD zu HTML', 'Markdown zu HTML — Online-Konverter | DevTools',
               'Markdown kostenlos online in HTML umwandeln: Überschriften, Listen, Tabellen, Codeblöcke, Zitate, Links und Bilder. Alles läuft direkt im Browser.',
               'markdown zu html,markdown konverter,md zu html,markdown online,markdown umwandeln,markdown tabelle', 'Markdown-zu-HTML-Konverter'),
        'ru': ('MD в HTML', 'Markdown в HTML — Онлайн-конвертер | DevTools',
               'Бесплатный онлайн-конвертер Markdown в HTML: заголовки, списки, таблицы, блоки кода, цитаты, ссылки и изображения. Всё работает в браузере.',
               'markdown в html,конвертер markdown,md в html,markdown онлайн,преобразовать markdown,markdown таблица', 'Конвертер Markdown в HTML'),
        'id': ('MD ke HTML', 'Markdown ke HTML — Konverter online | DevTools',
               'Konversi Markdown ke HTML online gratis: judul, daftar, tabel, blok kode, kutipan, tautan, dan gambar. Semua diproses di browser Anda.',
               'markdown ke html,konverter markdown,md ke html,markdown online,konversi markdown,markdown tabel', 'Konverter Markdown ke HTML'),
    },
}


def short_block(slug, lang):
    nav, title, desc, kw, h1 = SHORT[slug][lang]
    return (
        "    '%s': {\n"
        "        'nav': %r,\n"
        "        'title': %r,\n"
        "        'description': %r,\n"
        "        'keywords': %r,\n"
        "        'h1': %r,\n"
        "    },\n"
    ) % (slug, nav, title, desc, kw, h1)


def patch(path, is_dict, lang=None):
    src = io.open(path, encoding='utf-8').read()
    orig = src
    if lang is None:
        # 中英长文
        anchor = "        'slug': 'gofmt-online'," if not is_dict else "    'gofmt-online': {"
        block = ZH_BLOCK if not is_dict else EN_BLOCK
        if "'sql-formatter'" in src or "'slug': 'sql-formatter'" in src:
            print('%s: 已存在 sql-formatter，跳过' % path)
            return
        if anchor not in src:
            print('%s: !! 锚点未找到' % path)
            return
        src = src.replace(anchor, block + anchor, 1)
    else:
        blocks = []
        for slug in ('sql-formatter', 'markdown-to-html'):
            if ("'%s': {" % slug) in src:
                print('%s: 已存在 %s，跳过' % (path, slug))
                continue
            blocks.append(short_block(slug, lang))
        if not blocks:
            return
        anchor = "    'gofmt-online': {"
        if anchor not in src:
            print('%s: !! 锚点未找到' % path)
            return
        src = src.replace(anchor, ''.join(blocks) + anchor, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(src)
    print('%s: OK (%+d chars)' % (path, len(src) - len(orig)))


def fix_csv_seealso():
    path = os.path.join(ROOT, 'src', 'content.py')
    src = io.open(path, encoding='utf-8').read()
    bad = "('JSON 与 CSV 双向转换（JSON 工具箱）', './'),"
    if bad in src:
        src = src.replace(bad, "('JSON 与 CSV 双向转换（JSON 工具箱）', 'json/'),")
        io.open(path, 'w', encoding='utf-8', newline='\n').write(src)
        print('content.py: csv-to-sql-insert seealso ./ -> json/')
    else:
        print('content.py: csv seealso ./ 不存在或已修')


if __name__ == '__main__':
    fix_csv_seealso()
    patch(os.path.join(ROOT, 'src', 'content.py'), False)
    patch(os.path.join(ROOT, 'src', 'content_en.py'), True)
    # 文件后缀 -> SHORT 字典语言键
    LANG_MAP = [('ja', 'ja'), ('ko', 'ko'), ('es', 'es'), ('ptbr', 'pt-BR'),
                ('ru', 'ru'), ('id', 'id'), ('fr', 'fr'), ('de', 'de')]
    for suffix, key in LANG_MAP:
        patch(os.path.join(ROOT, 'src', 'content_%s.py' % suffix), True, key)
    print('done')
