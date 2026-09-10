# -*- coding: utf-8 -*-
"""站点级配置：只在构建与提交脚本之间共享的常量。"""

# IndexNow 的 key。
#
# 这是「无账号」把 URL 推给搜索引擎的唯一通道，Bing / Yandex / Seznam / Naver 共享提交结果。
# key 本身不是机密（它就是要公开挂在网站上供对方回抓校验的），但必须保持稳定：
# 一旦改动，之前建立的校验关系失效，需要重新提交。
#
# 校验文件放在主机根目录 https://xwjiang2003.github.io/<key>.txt，即官方「强烈建议」的 Option 1。
# 一份 key 覆盖整个主机（根页面 + 未来任何项目站点）。
#
# 该文件由用户站点仓库 xwjiang2003.github.io 承载，不在本仓库的构建产物里 ——
# 主机级文件（robots.txt / sitemap.xml / IndexNow key）统一放那边，本仓库只管 /tools/。
INDEXNOW_KEY = '9f4c1d7a2e8b5306ac1f7d9e4b2a8c30'

# 校验文件放在主机根目录，即官方「强烈建议」的 Option 1：一份 key 覆盖整个主机
# （根页面 + 未来任何项目站点）。
#
# 该文件由用户站点仓库 xwjiang2003.github.io 承载，不在本仓库的构建产物里 ——
# 主机级文件（robots.txt / sitemap.xml / IndexNow key）统一放那边，本仓库只管 /tools/。
ROOT_SITE_URL = 'https://xwjiang2003.github.io/'
KEY_LOCATION = f'{ROOT_SITE_URL}{INDEXNOW_KEY}.txt'

# 提交端点。IndexNow 约定：提交给任一参与方即自动共享给其他参与方，
# 这里逐个提交一遍，是为了拿到各家独立的返回码、便于排查。
ENDPOINTS = [
    ('IndexNow', 'https://api.indexnow.org/indexnow'),
    ('Bing', 'https://www.bing.com/indexnow'),
    ('Yandex', 'https://yandex.com/indexnow'),
    ('Seznam', 'https://search.seznam.cz/indexnow'),
]
