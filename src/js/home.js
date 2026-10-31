// home.js — 首页（导航门户）交互：实时时间戳 + 工具即时筛选。
// 只在首页加载（build.py PAGE_MODULES['home']），不进入其它页面。
//
// 两条硬约束（沿用全站约定）：
//   1. 本文件会被内联进 10 个语言版本的首页，**不能出现任何中文字面量**，
//      否则 check.py 的「非 CJK 语种页零中文」会失败。文案一律由构建期写入 HTML。
//   2. 首屏不依赖本文件：所有工具链接都是静态 <a>，JS 只做「筛选 + 时钟」这类增强；
//      JS 失败时页面仍是完整可用的导航页（对爬虫也同理）。

(function () {
  'use strict';

  function pad(n, w) {
    var s = String(n);
    while (s.length < w) s = '0' + s;
    return s;
  }

  // ---------------- 实时时间戳（hero 右侧卡片）----------------
  function startClock() {
    var secEl = document.getElementById('homeEpoch');
    var msEl = document.getElementById('homeEpochMs');
    if (!secEl && !msEl) return;

    function tick() {
      var now = new Date();
      var t = now.getTime();
      if (secEl) secEl.textContent = String(Math.floor(t / 1000));
      if (msEl) msEl.textContent = pad(t, 13);
    }
    tick();
    // 毫秒位要看着在跳，200ms 一次足够（10 次/秒比 1 次/秒自然，又不会吃 CPU）
    setInterval(tick, 200);
  }

  // ---------------- 工具即时筛选 ----------------
  function initFilter() {
    var root = document.getElementById('homeRoot');
    var input = document.getElementById('homeSearch');
    if (!root || !input) return;

    var cats = [].slice.call(root.querySelectorAll('.home-cat'));
    var tiles = [].slice.call(root.querySelectorAll('.home-tile'));

    // 预先建索引：名称 + 说明（含 data-k 里的关键词/标题），全部转小写只做一次
    var index = tiles.map(function (el) {
      return {
        el: el,
        text: ((el.getAttribute('data-k') || '') + ' ' + el.textContent).toLowerCase()
      };
    });

    // 分类标题右侧的计数徽标：筛选时改成"命中数"，清空后还原成总数
    var badges = cats.map(function (c) {
      var b = c.querySelector('.home-cat-count');
      if (b && b.dataset.total === undefined) b.dataset.total = b.textContent;
      return b;
    });

    function syncCounts() {
      cats.forEach(function (c, i) {
        var b = badges[i];
        var n = c.querySelectorAll('.home-tile:not([hidden])').length;
        // data-n 同时改：CSS 用 .home-cat[data-n="1"] 把单个结果铺满整行
        if (!c.hidden) c.setAttribute('data-n', String(n));
        if (b) b.textContent = c.hidden ? b.dataset.total : String(n);
      });
    }

    function apply(q) {
      q = q.trim().toLowerCase();
      if (!q) {
        index.forEach(function (it) { it.el.hidden = false; });
        cats.forEach(function (c) { c.hidden = false; });
        root.classList.remove('is-filtering', 'no-hit');
        badges.forEach(function (b) { if (b) b.textContent = b.dataset.total; });
        cats.forEach(function (c, i) {
          if (badges[i]) c.setAttribute('data-n', badges[i].dataset.total);
        });
        return;
      }
      root.classList.add('is-filtering');
      // 多个关键词用空格分隔，全部命中才算匹配（"时间 戳" 也能筛出来）
      var words = q.split(/\s+/).filter(Boolean);
      var total = 0;
      index.forEach(function (it) {
        var hit = words.every(function (w) { return it.text.indexOf(w) !== -1; });
        it.el.hidden = !hit;
        if (hit) total++;
      });
      cats.forEach(function (c) {
        c.hidden = !c.querySelector('.home-tile:not([hidden])');
      });
      syncCounts();
      root.classList.toggle('no-hit', total === 0);
      root.setAttribute('data-hit', String(total));
    }

    input.addEventListener('input', function () { apply(input.value); });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        var first = root.querySelector('.home-tile:not([hidden])');
        if (first) {
          e.preventDefault();
          window.location.href = first.getAttribute('href');
        }
      } else if (e.key === 'Escape') {
        input.value = '';
        apply('');
        input.blur();
      }
    });

    // "/" 直接聚焦搜索框（开发者工具的通用习惯）
    document.addEventListener('keydown', function (e) {
      var tag = (e.target && e.target.tagName) || '';
      if (e.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA') {
        e.preventDefault();
        input.focus();
      }
    });
  }

  function init() {
    startClock();
    initFilter();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
