# -*- coding: utf-8 -*-
"""首页（导航门户）的界面文案，按语言分开。

2026-10-31 改版：`/` 从「JSON 工具页」改成「工具导航门户」，JSON 工具迁到 /json/。

为什么文案单独放一个文件：首页的卡片标题与一句话说明来自既有数据
（NAV_LABELS / TOOL_BLURBS），这里只需要维护「门户自己的话」。放进 build.py
会把那个文件再撑大 300 行，且首页文案改动与构建逻辑改动混在一起不好 review。

翻译策略与全站一致：zh / en 为完整版本；其余语言给出 hero 与分区标题等
「第一屏可见」文案，长段说明（why / seo_p）回退英文——与这些语言的工具正文
本来就回退英文的做法保持一致，不会出现中文泄漏。
"""

HOME_TEXT = {
    'zh': {
        'eyebrow': 'DEVTOOLS.HELP · 纯浏览器运行',
        'h1': '开发者在线工具箱',
        'h1_sub': '{n} 个工具与专题，打开即用',
        'lead': (
            'JSON 格式化、正则在线测试、时间戳转换、Base64 编解码、哈希校验、进制转换……'
            '不用安装、不用注册。所有计算都在你的浏览器里完成，粘贴的内容不会上传服务器。'
        ),
        'search_ph': '搜索工具：时间戳 / 正则 / Base64 / UUID …',
        'search_hint': '输入关键词即时筛选，按回车打开第一个结果',
        'no_result': '没有匹配的工具，换个关键词试试',
        'quick': '常用工具',
        'quick_sub': '按日常使用频次挑选，点开即用',
        'browse': '按分类浏览全部工具',
        'browse_sub': '每个工具都是独立页面，带完整说明与常见问题',
        'live_t': '当前 Unix 时间戳',
        'live_ms': '毫秒 · 13 位',
        'stat_tools': '在线工具',
        'stat_langs': '种语言',
        'live_cta': '时间戳转换',
        'why': [
            ('数据不上传', '解析、转换、加密全部在浏览器本地执行，页面没有把输入发往后端的代码。'),
            ('免注册无广告', '没有弹窗、没有强制登录、没有"下载客户端"，打开就能用完就走。'),
            ('十种语言', '中、英、日、韩、西、葡、法、德、俄、印尼语，各自有独立 URL 与正文。'),
            ('断网也能用', '首次加载后离线仍可继续使用，适合内网环境、飞机上和临时排障。'),
        ],
        'seo_h2': '关于这个工具箱',
        'seo_p': [
            'devtools.help 是一个面向开发者的在线工具集合：JSON 格式化与转换、正则表达式在线测试、'
            'Unix 时间戳与日期互转、Base64 / URL / Unicode 编解码、MD5 / SHA 哈希与文件校验、'
            '2–36 任意进制转换、UUID 与 Snowflake ID 解析、Cron 表达式生成、代码格式化、'
            '时区与日历速查等等。每个工具都是独立页面，带完整的使用说明与常见问题，可以直接收藏或分享。',
            '这些工具的共同点是「一次性、即时、无副作用」：粘贴一段日志、一个令牌、一串时间戳，'
            '拿到结果就关掉页面。所以我们刻意不要求注册、不限制使用次数，也不把输入内容发往服务器——'
            '这一点你可以在浏览器开发者工具的 Network 面板里自行验证。',
        ],
    },
    'en': {
        'eyebrow': 'DEVTOOLS.HELP · RUNS IN YOUR BROWSER',
        'h1': 'Developer tools that open instantly',
        'h1_sub': '{n} tools and guides, no sign-up',
        'lead': (
            'JSON formatting, regex testing, Unix timestamps, Base64 and URL encoding, hashing, '
            'base conversion and more. Nothing to install, nothing to sign up for — every '
            'calculation runs in your browser and nothing you paste is uploaded.'
        ),
        'search_ph': 'Search tools: timestamp / regex / Base64 / UUID …',
        'search_hint': 'Filter as you type, press Enter to open the first match',
        'no_result': 'No tool matches that. Try a different keyword.',
        'quick': 'Most used tools',
        'quick_sub': 'Picked by everyday frequency — one click away',
        'browse': 'Browse all tools by category',
        'browse_sub': 'Every tool is its own page with full documentation and FAQ',
        'live_t': 'Current Unix timestamp',
        'live_ms': 'milliseconds · 13 digits',
        'stat_tools': 'online tools',
        'stat_langs': 'languages',
        'live_cta': 'Timestamp converter',
        'why': [
            ('Nothing is uploaded', 'Parsing, conversion and hashing all run locally; no page here posts your input to a server.'),
            ('No sign-up, no ads', 'No pop-ups, no forced login, no desktop download. Open it, use it, close it.'),
            ('Ten languages', 'Chinese, English, Japanese, Korean, Spanish, Portuguese, French, German, Russian and Indonesian — each with its own URL and content.'),
            ('Works offline', 'Once loaded, the tools keep working without a connection — handy on planes, intranets and during incident triage.'),
        ],
        'seo_h2': 'About this toolbox',
        'seo_p': [
            'devtools.help is a collection of online tools for developers: JSON formatting and conversion, '
            'regex testing, Unix timestamp and date conversion, Base64 / URL / Unicode encoding, MD5 and '
            'SHA hashing with file checksums, base conversion from 2 to 36, UUID and Snowflake ID decoding, '
            'cron expression building, code formatting, time zones and calendar reference pages. Every tool '
            'is a standalone page with documentation and an FAQ, ready to bookmark or share.',
            'What these tools have in common is that they are one-off, instant and side-effect free: paste a log '
            'line, a token or a timestamp, take the result and close the tab. That is why there is no account, '
            'no usage limit, and no upload — you can verify the last point yourself in the Network panel of your '
            'browser developer tools.',
        ],
    },
    'ja': {
        'eyebrow': 'DEVTOOLS.HELP · ブラウザだけで動作',
        'h1': 'オンライン開発ツール',
        'h1_sub': '{n} 個のツールと特集',
        'lead': (
            'JSON 整形、正規表現テスト、Unix タイムスタンプ変換、Base64 エンコード、ハッシュ計算、'
            '基数変換などをまとめました。インストールも登録も不要で、計算はすべてブラウザ内で完結します。'
        ),
        'search_ph': 'ツールを検索：タイムスタンプ / 正規表現 / Base64 …',
        'search_hint': '入力すると絞り込み、Enter で最初の結果を開きます',
        'no_result': '一致するツールがありません。別のキーワードをお試しください。',
        'quick': 'よく使うツール',
        'quick_sub': '利用頻度の高いものを厳選、クリックですぐ使えます',
        'browse': 'カテゴリからすべてのツールを見る',
        'browse_sub': '各ツールは独立したページで、使い方と FAQ を掲載しています',
        'live_t': '現在の Unix タイムスタンプ',
        'live_ms': 'ミリ秒 · 13 桁',
        'stat_tools': 'オンラインツール',
        'stat_langs': '言語',
        'live_cta': 'タイムスタンプ変換',
    },
    'ko': {
        'eyebrow': 'DEVTOOLS.HELP · 브라우저에서 실행',
        'h1': '온라인 개발자 도구',
        'h1_sub': '{n}개 도구와 콘텐츠',
        'lead': (
            'JSON 정리, 정규식 테스트, Unix 타임스탬프 변환, Base64 인코딩, 해시 계산, 진법 변환 등을 '
            '한곳에 모았습니다. 설치도 가입도 필요 없고, 모든 계산은 브라우저 안에서 끝납니다.'
        ),
        'search_ph': '도구 검색: 타임스탬프 / 정규식 / Base64 …',
        'search_hint': '입력하면 바로 걸러지고, Enter 로 첫 결과를 엽니다',
        'no_result': '일치하는 도구가 없습니다. 다른 키워드를 입력해 보세요.',
        'quick': '자주 쓰는 도구',
        'quick_sub': '사용 빈도가 높은 도구를 골랐습니다',
        'browse': '카테고리별 전체 도구',
        'browse_sub': '각 도구는 설명과 FAQ 를 갖춘 독립 페이지입니다',
        'live_t': '현재 Unix 타임스탬프',
        'live_ms': '밀리초 · 13자리',
        'stat_tools': '온라인 도구',
        'stat_langs': '개 언어',
        'live_cta': '타임스탬프 변환',
    },
    'es': {
        'eyebrow': 'DEVTOOLS.HELP · SE EJECUTA EN TU NAVEGADOR',
        'h1': 'Herramientas de desarrollo en línea',
        'h1_sub': '{n} herramientas y guías',
        'lead': (
            'Formateo de JSON, pruebas de expresiones regulares, marcas de tiempo Unix, codificación '
            'Base64 y URL, hashing y conversión de bases. Sin instalar nada: todo se calcula en tu navegador.'
        ),
        'search_ph': 'Buscar herramientas: timestamp / regex / Base64 …',
        'search_hint': 'Filtra mientras escribes; pulsa Enter para abrir el primer resultado',
        'no_result': 'Ninguna herramienta coincide. Prueba con otra palabra clave.',
        'quick': 'Herramientas más usadas',
        'quick_sub': 'Seleccionadas por uso diario, a un clic',
        'browse': 'Todas las herramientas por categoría',
        'browse_sub': 'Cada herramienta es una página propia con documentación y preguntas frecuentes',
        'live_t': 'Marca de tiempo Unix actual',
        'live_ms': 'milisegundos · 13 dígitos',
        'stat_tools': 'herramientas',
        'stat_langs': 'idiomas',
        'live_cta': 'Conversor de timestamps',
    },
    'pt-BR': {
        'eyebrow': 'DEVTOOLS.HELP · RODA NO SEU NAVEGADOR',
        'h1': 'Ferramentas de desenvolvimento online',
        'h1_sub': '{n} ferramentas e guias',
        'lead': (
            'Formatação de JSON, testes de expressões regulares, timestamps Unix, codificação Base64 e URL, '
            'hash e conversão de bases. Sem instalar nada: tudo é calculado no seu navegador.'
        ),
        'search_ph': 'Buscar ferramentas: timestamp / regex / Base64 …',
        'search_hint': 'Filtra enquanto você digita; pressione Enter para abrir o primeiro resultado',
        'no_result': 'Nenhuma ferramenta encontrada. Tente outra palavra-chave.',
        'quick': 'Ferramentas mais usadas',
        'quick_sub': 'Selecionadas pelo uso diário, a um clique',
        'browse': 'Todas as ferramentas por categoria',
        'browse_sub': 'Cada ferramenta é uma página própria, com explicação e perguntas frequentes',
        'live_t': 'Timestamp Unix atual',
        'live_ms': 'milissegundos · 13 dígitos',
        'stat_tools': 'ferramentas',
        'stat_langs': 'idiomas',
        'live_cta': 'Conversor de timestamp',
    },
    'fr': {
        'eyebrow': 'DEVTOOLS.HELP · DANS VOTRE NAVIGATEUR',
        'h1': 'Outils de développement en ligne',
        'h1_sub': '{n} outils et guides',
        'lead': (
            'Mise en forme JSON, test d’expressions régulières, horodatages Unix, encodage Base64 et URL, '
            'hachage, conversion de bases. Rien à installer : tout est calculé dans votre navigateur.'
        ),
        'search_ph': 'Rechercher un outil : timestamp / regex / Base64 …',
        'search_hint': 'Le filtre s’applique à la saisie ; Entrée ouvre le premier résultat',
        'no_result': 'Aucun outil ne correspond. Essayez un autre mot-clé.',
        'quick': 'Outils les plus utilisés',
        'quick_sub': 'Sélectionnés selon l’usage quotidien, à un clic',
        'browse': 'Tous les outils par catégorie',
        'browse_sub': 'Chaque outil a sa propre page, avec mode d’emploi et FAQ',
        'live_t': 'Horodatage Unix actuel',
        'live_ms': 'millisecondes · 13 chiffres',
        'stat_tools': 'outils',
        'stat_langs': 'langues',
        'live_cta': 'Convertisseur de timestamp',
    },
    'de': {
        'eyebrow': 'DEVTOOLS.HELP · LÄUFT IM BROWSER',
        'h1': 'Online-Werkzeuge für Entwickler',
        'h1_sub': '{n} Tools und Leitfäden',
        'lead': (
            'JSON formatieren, reguläre Ausdrücke testen, Unix-Zeitstempel umrechnen, Base64- und '
            'URL-Kodierung, Hashing, Basisumrechnung. Nichts zu installieren – alles läuft im Browser.'
        ),
        'search_ph': 'Tool suchen: Zeitstempel / Regex / Base64 …',
        'search_hint': 'Filtert beim Tippen, Enter öffnet das erste Ergebnis',
        'no_result': 'Kein Tool gefunden. Bitte einen anderen Begriff versuchen.',
        'quick': 'Meistgenutzte Tools',
        'quick_sub': 'Nach Alltagsnutzen ausgewählt, ein Klick entfernt',
        'browse': 'Alle Tools nach Kategorie',
        'browse_sub': 'Jedes Tool hat eine eigene Seite mit Anleitung und FAQ',
        'live_t': 'Aktueller Unix-Zeitstempel',
        'live_ms': 'Millisekunden · 13 Stellen',
        'stat_tools': 'Tools',
        'stat_langs': 'Sprachen',
        'live_cta': 'Zeitstempel-Umrechner',
    },
    'ru': {
        'eyebrow': 'DEVTOOLS.HELP · РАБОТАЕТ В БРАУЗЕРЕ',
        'h1': 'Онлайн-инструменты для разработчиков',
        'h1_sub': '{n} инструментов и подборок',
        'lead': (
            'Форматирование JSON, проверка регулярных выражений, метки времени Unix, кодирование Base64 '
            'и URL, хеширование, перевод систем счисления. Ничего устанавливать не нужно — всё считается в браузере.'
        ),
        'search_ph': 'Поиск инструмента: timestamp / regex / Base64 …',
        'search_hint': 'Фильтр по мере ввода, Enter открывает первый результат',
        'no_result': 'Ничего не найдено. Попробуйте другое слово.',
        'quick': 'Часто используемые инструменты',
        'quick_sub': 'Отобраны по ежедневной практике — в один клик',
        'browse': 'Все инструменты по категориям',
        'browse_sub': 'У каждого инструмента своя страница с описанием и ответами на вопросы',
        'live_t': 'Текущая метка времени Unix',
        'live_ms': 'миллисекунды · 13 цифр',
        'stat_tools': 'инструментов',
        'stat_langs': 'языков',
        'live_cta': 'Конвертер меток времени',
    },
    'id': {
        'eyebrow': 'DEVTOOLS.HELP · BERJALAN DI BROWSER',
        'h1': 'Alat pengembang online',
        'h1_sub': '{n} alat dan panduan',
        'lead': (
            'Format JSON, uji regex, konversi timestamp Unix, encode Base64 dan URL, hash, konversi basis '
            'angka. Tanpa instalasi dan tanpa daftar — semua perhitungan berjalan di browser Anda.'
        ),
        'search_ph': 'Cari alat: timestamp / regex / Base64 …',
        'search_hint': 'Menyaring saat Anda mengetik, tekan Enter untuk membuka hasil pertama',
        'no_result': 'Tidak ada alat yang cocok. Coba kata kunci lain.',
        'quick': 'Alat yang sering dipakai',
        'quick_sub': 'Dipilih berdasarkan pemakaian harian, sekali klik',
        'browse': 'Semua alat menurut kategori',
        'browse_sub': 'Setiap alat punya halaman sendiri dengan penjelasan dan FAQ',
        'live_t': 'Timestamp Unix saat ini',
        'live_ms': 'milidetik · 13 digit',
        'stat_tools': 'alat',
        'stat_langs': 'bahasa',
        'live_cta': 'Konverter timestamp',
    },
}

# 缺失字段回退英文（与全站「绝不回退中文」的策略一致）。
for _lang, _t in list(HOME_TEXT.items()):
    if _lang == 'en':
        continue
    for _k, _v in HOME_TEXT['en'].items():
        _t.setdefault(_k, _v)

for _lang in ('zh', 'en', 'ja', 'ko', 'es', 'pt-BR', 'fr', 'de', 'ru', 'id'):
    if _lang not in HOME_TEXT:                       # 兜底：新增语言不会 KeyError
        HOME_TEXT[_lang] = HOME_TEXT['en']
