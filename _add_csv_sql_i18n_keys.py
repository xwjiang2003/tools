# -*- coding: utf-8 -*-
"""给 i18n.py 的 9 个字典补 2 个新键（csv-to-sql-insert 页面用）。

锚点：'请输入内容' 在各字典均存在，新键插在锚点行之后（独立成行，语法安全）。
"""
import io
import re

NEW = {
    '表名': {
        'EN': 'Table name', 'JA': 'テーブル名', 'KO': '테이블 이름',
        'ES': 'Nombre de la tabla', 'PTBR': 'Nome da tabela',
        'FR': 'Nom de la table', 'DE': 'Tabellenname',
        'RU': 'Имя таблицы', 'ID': 'Nama tabela',
    },
    '至少需要表头行和一行数据': {
        'EN': 'at least a header row and one data row',
        'JA': 'ヘッダー行とデータ行がそれぞれ1行必要です',
        'KO': '헤더 행과 데이터 행이 각각 한 줄 이상 필요합니다',
        'ES': 'se necesitan al menos una fila de encabezado y una fila de datos',
        'PTBR': 'são necessários pelo menos um cabeçalho e uma linha de dados',
        'FR': "au moins une ligne d'en-tête et une ligne de données sont requises",
        'DE': 'mindestens eine Kopfzeile und eine Datenzeile erforderlich',
        'RU': 'нужны как минимум строка заголовка и одна строка данных',
        'ID': 'minimal satu baris header dan satu baris data',
    },
}

DICTS = ['EN', 'JA', 'KO', 'ES', 'PTBR', 'FR', 'DE', 'RU', 'ID']
ANCHOR = '请输入内容'

p = r'D:\workspace\dev-tools\src\i18n.py'
src = io.open(p, encoding='utf-8').read()

lines = src.split('\n')
out = []
inserted = set()
for line in lines:
    out.append(line)
    m = re.match(r"^(\s*)'" + ANCHOR + r"':\s*(.+),$", line)
    if m:
        # 判断本行属于哪个字典：向后找最近的 ^DICT = {
        idx = len(out) - 1
        cur = None
        for j in range(idx, -1, -1):
            dm = re.match(r"^([A-Z]+) = \{", out[j])
            if dm:
                cur = dm.group(1)
                break
        if cur in DICTS and cur not in inserted:
            for key in ['表名', '至少需要表头行和一行数据']:
                v = NEW[key][cur]
                if "'" in v:
                    out.append('    "%s": "%s",' % (key, v))
                else:
                    out.append("    '%s': '%s'," % (key, v))
            inserted.add(cur)
            print('inserted into', cur)

new_src = '\n'.join(out)
io.open(p, 'w', encoding='utf-8', newline='\n').write(new_src)
print('done, dicts inserted:', len(inserted))
