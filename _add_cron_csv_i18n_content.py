# -*- coding: utf-8 -*-
"""给 8 个语言内容文件补 cron-generator / csv-to-sql-insert 完整短 SEO 字段。"""

ENTRIES = {
    'content_es.py': "TOOLS_ES", 'content_fr.py': "TOOLS_FR",
    'content_de.py': "TOOLS_DE", 'content_ptbr.py': "TOOLS_PTBR",
    'content_ru.py': "TOOLS_RU", 'content_id.py': "TOOLS_ID",
    'content_ja.py': "TOOLS_JA", 'content_ko.py': "TOOLS_KO",
}

DATA = {
    'content_es.py': (
        """    'cron-generator': {
        'nav': 'Generador cron',
        'title': 'Generador de expresiones cron — Crontab de Linux visual | DevTools',
        'description': 'Genera expresiones cron online: elige valores para los cinco campos (minuto, hora, día, mes, día de la semana) y obtén al instante una expresión crontab estándar de 5 campos, con pasos */n incluidos. Copia o descarga. Todo en tu navegador.',
        'keywords': 'generador expresiones cron,generador cron,generador crontab,tarea cron linux,constructor cron,expresion crontab,expresion programada',
        'h1': 'Generador de expresiones cron',
    },
    'csv-to-sql-insert': {
        'nav': 'CSV a SQL',
        'title': 'CSV a INSERT SQL — Genera sentencias masivas online | DevTools',
        'description': 'Convierte CSV a sentencias SQL INSERT online: la primera fila es la lista de columnas, las celdas vacías pasan a NULL, las comillas simples se escapan duplicándolas y las comas entre comillas se procesan bien. Genera INSERT ejecutables, todo en tu navegador.',
        'keywords': 'csv a sql,csv a insert,csv a sql insert,generador insert sql,importar csv a sql,insert masivo,csv a base de datos',
        'h1': 'Generador de CSV a SQL INSERT',
    },
"""),
    'content_fr.py': (
        """    'cron-generator': {
        'nav': 'Générateur cron',
        'title': "Générateur d'expressions cron — Crontab Linux visuel | DevTools",
        'description': "Générez des expressions cron en ligne : choisissez les valeurs des cinq champs (minute, heure, jour, mois, jour de la semaine) et obtenez instantanément une expression crontab standard à 5 champs, pas */n inclus. Copiez ou téléchargez. Tout dans votre navigateur.",
        'keywords': 'generateur expression cron,generateur cron,generateur crontab,tache cron linux,constructeur cron,expression crontab,expression planifiee',
        'h1': "Générateur d'expressions cron",
    },
    'csv-to-sql-insert': {
        'nav': 'CSV vers SQL',
        'title': 'CSV vers INSERT SQL — Génère des instructions en masse | DevTools',
        'description': "Convertissez du CSV en instructions SQL INSERT en ligne : la première ligne devient la liste des colonnes, les cellules vides deviennent NULL, les apostrophes sont doublées et les virgules entre guillemets sont parsées correctement. Générez des INSERT exécutables, dans votre navigateur.",
        'keywords': 'csv vers sql,csv vers insert,csv vers sql insert,generateur insert sql,importer csv en sql,insert massif,csv vers base de donnees',
        'h1': 'Générateur CSV vers SQL INSERT',
    },
"""),
    'content_de.py': (
        """    'cron-generator': {
        'nav': 'Cron-Generator',
        'title': 'Cron-Ausdruck-Generator — visueller Linux-Crontab-Builder | DevTools',
        'description': 'Cron-Ausdrücke online generieren: Werte für die fünf Felder (Minute, Stunde, Tag, Monat, Wochentag) wählen und sofort einen Standard-5-Feld-Crontab-Ausdruck erhalten, inklusive */n-Schritten. Kopieren oder herunterladen. Läuft komplett im Browser.',
        'keywords': 'cron ausdruck generator,cron generator,crontab generator,linux cron job,cron ausdruck erstellen,crontab ausdruck,zeitplan ausdruck',
        'h1': 'Cron-Ausdruck-Generator',
    },
    'csv-to-sql-insert': {
        'nav': 'CSV zu SQL',
        'title': 'CSV zu SQL INSERT — Bulk-INSERT-Statements online | DevTools',
        'description': 'Wandle CSV online in SQL-INSERT-Statements um: die erste Zeile wird zur Spaltenliste, leere Zellen werden NULL, einfache Anführungszeichen werden verdoppelt und Kommas in Anführungszeichen werden korrekt geparst. Generiere ausführbare INSERTs, alles im Browser.',
        'keywords': 'csv zu sql,csv zu insert,csv zu sql insert,sql insert generator,csv in sql importieren,bulk insert,csv zu datenbank',
        'h1': 'CSV-zu-SQL-INSERT-Generator',
    },
"""),
    'content_ptbr.py': (
        """    'cron-generator': {
        'nav': 'Gerador cron',
        'title': 'Gerador de expressões cron — Crontab Linux visual | DevTools',
        'description': 'Gere expressões cron online: escolha valores para os cinco campos (minuto, hora, dia, mês, dia da semana) e obtenha na hora uma expressão crontab padrão de 5 campos, com passos */n inclusos. Copie ou baixe. Tudo no seu navegador.',
        'keywords': 'gerador expressoes cron,gerador cron,gerador crontab,tarefa cron linux,construtor cron,expressao crontab,expressao agendada',
        'h1': 'Gerador de expressões cron',
    },
    'csv-to-sql-insert': {
        'nav': 'CSV para SQL',
        'title': 'CSV para INSERT SQL — Gere instruções em massa online | DevTools',
        'description': 'Converta CSV em instruções SQL INSERT online: a primeira linha vira a lista de colunas, células vazias viram NULL, aspas simples são escapadas dobrando e vírgulas entre aspas são interpretadas corretamente. Gere INSERT executáveis, tudo no navegador.',
        'keywords': 'csv para sql,csv para insert,csv para sql insert,gerador insert sql,importar csv para sql,insert em massa,csv para banco de dados',
        'h1': 'Gerador de CSV para SQL INSERT',
    },
"""),
    'content_ru.py': (
        """    'cron-generator': {
        'nav': 'Генератор cron',
        'title': 'Генератор cron-выражений — визуальный конструктор crontab Linux | DevTools',
        'description': 'Создавайте cron-выражения онлайн: выберите значения для пяти полей (минута, час, день, месяц, день недели) и сразу получите стандартное 5-полевое выражение crontab со встроенными шагами */n. Копируйте или скачивайте. Всё в браузере.',
        'keywords': 'генератор cron выражений,генератор cron,генератор crontab,задача cron linux,конструктор cron,cron выражение,выражение расписания',
        'h1': 'Генератор cron-выражений',
    },
    'csv-to-sql-insert': {
        'nav': 'CSV в SQL',
        'title': 'CSV в SQL INSERT — массовая генерация INSERT онлайн | DevTools',
        'description': 'Преобразуйте CSV в SQL INSERT онлайн: первая строка становится списком столбцов, пустые ячейки — NULL, одинарные кавычки удваиваются, а запятые в кавычках обрабатываются корректно. Генерируйте исполняемые INSERT, всё в браузере.',
        'keywords': 'csv в sql,csv в insert,csv в sql insert,генератор sql insert,импорт csv в sql,массовый insert,csv в базу данных',
        'h1': 'Генератор CSV в SQL INSERT',
    },
"""),
    'content_id.py': (
        """    'cron-generator': {
        'nav': 'Generator cron',
        'title': 'Generator Ekspresi Cron — Crontab Linux Visual | DevTools',
        'description': 'Buat ekspresi cron online: pilih nilai untuk lima field (menit, jam, hari, bulan, hari dalam seminggu) dan dapatkan ekspresi crontab standar 5 field seketika, dengan langkah */n bawaan. Salin atau unduh. Semua di browser Anda.',
        'keywords': 'generator ekspresi cron,generator cron,generator crontab,tugas cron linux,penyusun cron,ekspresi crontab,ekspresi jadwal',
        'h1': 'Generator Ekspresi Cron',
    },
    'csv-to-sql-insert': {
        'nav': 'CSV ke SQL',
        'title': 'CSV ke INSERT SQL — Buat Pernyataan Massal Online | DevTools',
        'description': 'Ubah CSV menjadi pernyataan SQL INSERT online: baris pertama menjadi daftar kolom, sel kosong menjadi NULL, tanda kutip tunggal digandakan, dan koma dalam kutip diparses dengan benar. Buat INSERT yang siap dijalankan, semuanya di browser Anda.',
        'keywords': 'csv ke sql,csv ke insert,csv ke sql insert,generator insert sql,impor csv ke sql,insert massal,csv ke basis data',
        'h1': 'Generator CSV ke SQL INSERT',
    },
"""),
    'content_ja.py': (
        """    'cron-generator': {
        'nav': 'Cron生成',
        'title': 'Cron 式ジェネレーター — Linux crontab を視覚的に生成 | DevTools',
        'description': 'Cron 式をオンライン生成：5つのフィールド（分・時・日・月・曜日）を選ぶだけで、標準的な5フィールドの crontab 式が即座に完成。*/n ステップも内蔵。コピーまたはダウンロードできます。すべてブラウザ内で実行。',
        'keywords': 'cron 式 生成,cron ジェネレーター,crontab 生成,linux cron ジョブ,cron 式 ビルダー,crontab 式,スケジュール 式',
        'h1': 'Cron 式ジェネレーター',
    },
    'csv-to-sql-insert': {
        'nav': 'CSV→SQL',
        'title': 'CSV から SQL INSERT 変換 — 一括 INSERT 文をオンライン生成 | DevTools',
        'description': 'CSV を SQL INSERT 文にオンライン変換：1行目が列名リストになり、空セルは NULL、単一引用符は二重にエスケープ、引用符内のカンマも正しく解析。実行可能な INSERT をまとめて生成します。すべてブラウザ内で処理。',
        'keywords': 'csv sql 変換,csv insert 生成,csv to sql insert,sql insert ジェネレーター,csv sql インポート,一括 insert,csv データベース',
        'h1': 'CSV から SQL INSERT ジェネレーター',
    },
"""),
    'content_ko.py': (
        """    'cron-generator': {
        'nav': 'Cron 생성기',
        'title': 'Cron 표현식 생성기 — 리눅스 crontab 비주얼 빌더 | DevTools',
        'description': 'Cron 표현식을 온라인으로 생성하세요: 다섯 필드(분·시·일·월·요일) 값을 선택하면 표준 5필드 crontab 표현식이 즉시 완성됩니다. */n 단계 내장. 복사 또는 다운로드. 모든 처리는 브라우저에서 이루어집니다.',
        'keywords': 'cron 표현식 생성기,cron 생성기,crontab 생성기,리눅스 cron 작업,cron 표현식 빌더,crontab 표현식,스케줄 표현식',
        'h1': 'Cron 표현식 생성기',
    },
    'csv-to-sql-insert': {
        'nav': 'CSV → SQL',
        'title': 'CSV → SQL INSERT 변환 — 대량 INSERT 문 온라인 생성 | DevTools',
        'description': 'CSV를 SQL INSERT 문으로 온라인 변환: 첫 행이 열 목록이 되고, 빈 셀은 NULL, 작은따옴표는 두 번 escapes, 따옴표 안의 쉼표도 올바르게 파싱합니다. 실행 가능한 INSERT를 대량 생성, 모든 처리는 브라우저에서.',
        'keywords': 'csv sql 변환,csv insert 생성,csv to sql insert,sql insert 생성기,csv sql 가져오기,대량 insert,csv 데이터베이스',
        'h1': 'CSV → SQL INSERT 생성기',
    },
"""),
}

import io
import re

base = r'D:\workspace\dev-tools\src'
for fname, entry in DATA.items():
    dictname = ENTRIES[fname]
    p = base + '\\' + fname
    src = io.open(p, encoding='utf-8').read()
    if "'cron-generator'" in src:
        print('SKIP (exists):', fname)
        continue
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
    head = src[:k].rstrip('\n')
    assert head.endswith('},'), fname + ' tail: ' + head[-40:]
    new = head + '\n' + entry.rstrip('\n') + '\n}\n' + src[k + 2:]
    io.open(p, 'w', encoding='utf-8', newline='\n').write(new)
    print('OK:', fname)
