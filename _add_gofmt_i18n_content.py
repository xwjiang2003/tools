# -*- coding: utf-8 -*-
"""给 8 个语言的内容文件补 gofmt-online 短 SEO 字段（nav/title/description/keywords/h1）。
长正文按既有设计回退英文（content_en.TOOLS_EN）。插入到各 TOOLS_XX 字典末尾。
"""
import io
import re

ENTRIES = {
    'content_es.py': (
        "TOOLS_ES",
        """    'gofmt-online': {
        'nav': 'Formateador Go',
        'title': 'Formateador Go en línea — gofmt gratis, en el navegador | DevTools',
        'description': 'Formatea código Go en línea con reglas gofmt reales: el paquete oficial go/format de Go compilado a WebAssembly y ejecutado en tu navegador. Nada se sube a ningún servidor.',
        'keywords': 'formateador go,gofmt en linea,formatear codigo go,gofmt herramienta,go beautifier,formateador golang,formatear go online',
        'h1': 'Formateador Go en línea (gofmt)',
    },
"""),
    'content_fr.py': (
        "TOOLS_FR",
        """    'gofmt-online': {
        'nav': 'Formateur Go',
        'title': 'Formateur Go en ligne — gofmt gratuit, dans le navigateur | DevTools',
        'description': "Formatez du code Go en ligne avec les vraies règles gofmt : le paquet go/format officiel de Go compilé en WebAssembly et exécuté dans votre navigateur. Rien n'est envoyé sur un serveur.",
        'keywords': 'formateur go,gofmt en ligne,formater code go,gofmt outil,embellisseur go,formateur golang,formater go en ligne',
        'h1': 'Formateur Go en ligne (gofmt)',
    },
"""),
    'content_de.py': (
        "TOOLS_DE",
        """    'gofmt-online': {
        'nav': 'Go-Formatter',
        'title': 'Go-Formatter online — gofmt kostenlos, im Browser | DevTools',
        'description': 'Formatiere Go-Code online mit echten gofmt-Regeln: das offizielle go/format-Paket von Go, zu WebAssembly kompiliert und in deinem Browser ausgeführt. Nichts wird hochgeladen.',
        'keywords': 'go formatter,gofmt online,go code formatieren,gofmt werkzeug,go verschönerer,golang formatter,go formatieren online',
        'h1': 'Go-Formatter online (gofmt)',
    },
"""),
    'content_ptbr.py': (
        "TOOLS_PTBR",
        """    'gofmt-online': {
        'nav': 'Formatador Go',
        'title': 'Formatador Go online — gofmt grátis, no navegador | DevTools',
        'description': 'Formate código Go online com regras reais de gofmt: o pacote oficial go/format do Go compilado para WebAssembly e executado no seu navegador. Nada é enviado ao servidor.',
        'keywords': 'formatador go,gofmt online,formatar codigo go,gofmt ferramenta,embelezador go,formatador golang,formatar go online',
        'h1': 'Formatador Go online (gofmt)',
    },
"""),
    'content_ru.py': (
        "TOOLS_RU",
        """    'gofmt-online': {
        'nav': 'Форматтер Go',
        'title': 'Форматтер Go онлайн — gofmt бесплатно, в браузере | DevTools',
        'description': 'Форматируйте Go-код онлайн по настоящим правилам gofmt: официальный пакет go/format языка Go, скомпилированный в WebAssembly и работающий в вашем браузере. Ничего не загружается на сервер.',
        'keywords': 'форматтер go,gofmt онлайн,форматировать go код,gofmt инструмент,украситель go,golang форматтер,форматировать go онлайн',
        'h1': 'Форматтер Go онлайн (gofmt)',
    },
"""),
    'content_id.py': (
        "TOOLS_ID",
        """    'gofmt-online': {
        'nav': 'Formatter Go',
        'title': 'Formatter Go online — gofmt gratis, di browser | DevTools',
        'description': 'Format kode Go online dengan aturan gofmt asli: paket resmi go/format dari Go yang dikompilasi ke WebAssembly dan berjalan di browser Anda. Tidak ada yang diunggah ke server.',
        'keywords': 'formatter go,gofmt online,format kode go,alat gofmt,perapi go,formatter golang,format go online',
        'h1': 'Formatter Go online (gofmt)',
    },
"""),
    'content_ja.py': (
        "TOOLS_JA",
        """    'gofmt-online': {
        'nav': 'Goフォーマッタ',
        'title': 'Goフォーマッタ オンライン — gofmt 無料、ブラウザで実行 | DevTools',
        'description': '本物の gofmt ルールで Go コードをオンライン整形：Go 公式 go/format パッケージを WebAssembly にコンパイルし、ブラウザ内で実行します。コードがサーバーに送信されることはありません。',
        'keywords': 'gofmt オンライン,go フォーマッタ,go コード整形,gofmt ツール,go 美化,golang フォーマッタ,go 整形 オンライン',
        'h1': 'Goフォーマッタ オンライン（gofmt）',
    },
"""),
    'content_ko.py': (
        "TOOLS_KO",
        """    'gofmt-online': {
        'nav': 'Go 포맷터',
        'title': 'Go 포맷터 온라인 — gofmt 무료, 브라우저에서 실행 | DevTools',
        'description': '실제 gofmt 규칙으로 Go 코드를 온라인으로 서식 지정: Go 공식 go/format 패키지를 WebAssembly로 컴파일하여 브라우저에서 실행합니다. 코드가 서버로 업로드되지 않습니다.',
        'keywords': 'gofmt 온라인,go 포맷터,go 코드 서식,gofmt 도구,go 미화,golang 포맷터,go 서식 온라인',
        'h1': 'Go 포맷터 온라인(gofmt)',
    },
"""),
}

base = r'D:\workspace\dev-tools\src'
for fname, (dictname, entry) in ENTRIES.items():
    p = base + '\\' + fname
    with io.open(p, 'r', encoding='utf-8') as f:
        src = f.read()
    if "'gofmt-online'" in src:
        print('SKIP (exists):', fname)
        continue
    # 找 TOOLS_XX 字典的结尾右括号：最后一个独立的 "}\n" 行前的 "    },\n"
    m = re.search(r'\n\}\n', src[::-1][::-1])  # 占位，不用
    # 直接定位字典结尾：从 dictname 声明开始括号配对
    i = src.find(dictname + ' = {')
    j = src.find('{', i)
    depth = 0
    quote = None
    esc = False
    k = j
    while k < len(src):
        c = src[k]
        if quote:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == quote:
                quote = None
        else:
            if c == '"' or c == "'":
                quote = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
        k += 1
    # k 处是字典的结束 }；把它前面的 "    },\n" 补上新条目
    head = src[:k].rstrip('\n')
    assert head.endswith('},'), fname + ' tail: ' + head[-30:]
    new = head + '\n' + entry.rstrip('\n') + '\n}\n' + src[k + 2:]
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new)
    print('OK:', fname)
