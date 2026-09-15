# -*- coding: utf-8 -*-
"""站点级配置：只在构建与提交脚本之间共享的常量。"""

# IndexNow 的 key。
#
# 这是「无账号」把 URL 推给搜索引擎的唯一通道，Bing / Yandex / Seznam / Naver 共享提交结果。
# key 本身不是机密（它就是要公开挂在网站上供对方回抓校验的），但必须保持稳定：
# 一旦改动，之前建立的校验关系失效，需要重新提交。
#
# 校验文件放在主机根目录 https://devtools.help/<key>.txt，即官方「强烈建议」的 Option 1。
# 本站的发布目录根就是主机根，所以该文件由 build.py 生成到 docs/ 下。
INDEXNOW_KEY = '9f4c1d7a2e8b5306ac1f7d9e4b2a8c30'

# 主机根地址。2026-09 起本站迁到自定义域名 devtools.help，
# 该域名绑在 tools 仓库上、直接由域名根提供服务，所以本站的发布目录根 == 主机根。
# IndexNow 的 host 与 keyLocation、构建时生成的 robots/sitemap 都基于它。
ROOT_SITE_URL = 'https://devtools.help/'
KEY_LOCATION = f'{ROOT_SITE_URL}{INDEXNOW_KEY}.txt'

# GitHub Pages 自定义域名。build.py 会把它写成 docs/CNAME ——
# 注意 build.py 每次构建都会 rmtree(docs)，手放的 CNAME 会被删掉，所以必须由构建生成。
CUSTOM_DOMAIN = 'devtools.help'

# 提交端点。IndexNow 约定：提交给任一参与方即自动共享给其他参与方，
# 这里逐个提交一遍，是为了拿到各家独立的返回码、便于排查。
ENDPOINTS = [
    ('IndexNow', 'https://api.indexnow.org/indexnow'),
    ('Bing', 'https://www.bing.com/indexnow'),
    ('Yandex', 'https://yandex.com/indexnow'),
    ('Seznam', 'https://search.seznam.cz/indexnow'),
]
