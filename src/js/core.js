// core.js — Global state, editor management, theme, navigation
"use strict";
// ============================================================
// GLOBAL STATE & UTILS
// ============================================================
const editors = {};
const NL = '\n';                    // newline constant - use instead of '\n' everywhere
const CM_OPTS = () => {
  const d = document.documentElement.getAttribute('data-theme') === 'dark';
  return { mode: {name:'javascript',json:true}, theme: d?'monokai':'default',
    lineNumbers:true, matchBrackets:true, autoCloseBrackets:true, foldGutter:true,
    gutters:['CodeMirror-linenumbers','CodeMirror-foldgutter'],
    tabSize:2, indentUnit:2, lineWrapping:true, viewportMargin:Infinity };
};
function createCM(id, ro) {
  if (editors[id]) return editors[id];
  const ta = document.getElementById(id); if (!ta) return null;
  const e = CodeMirror.fromTextArea(ta, {...CM_OPTS(), readOnly:ro?'nocursor':false});
  editors[id] = e;
  // Size editor to fill available space
  resizeEditor(e);
  return e;
}
function resizeEditor(e) {
  const wrap = e.getWrapperElement().parentElement;
  if (!wrap) return;
  // If parent is input-editor-wrap, calculate available height
  if (wrap.classList.contains('input-editor-wrap')) {
    const panel = wrap.closest('.input-panel');
    if (panel) {
      const panelRect = panel.getBoundingClientRect();
      const header = panel.querySelector('.input-panel-header');
      const headerH = header ? header.getBoundingClientRect().height : 40;
      const availH = panelRect.height - headerH;
      if (availH > 200) e.setSize(null, availH);
      else e.setSize(null, 400);
    }
  } else {
    // Card editors etc: use parent height
    const h = wrap.clientHeight;
    if (h > 50) e.setSize(null, h);
  }
}
function resizeAllEditors() {
  Object.values(editors).forEach(e => {
    const wrap = e.getWrapperElement().parentElement;
    if (wrap && wrap.classList.contains('input-editor-wrap')) resizeEditor(e);
  });
}
window.addEventListener('resize', resizeAllEditors);
function getVal(id) { const e = editors[id]; if (e) return e.getValue(); const ta = document.getElementById(id); return ta ? ta.value : ''; }
function setVal(id, v) { const e = editors[id]; if (e) { e.setValue(v); return; } const ta = document.getElementById(id); if (ta) ta.value = v; }
function clearVal(id) { setVal(id, ''); }
function clearInput(id) { clearVal(id); }
function clearTa(id) { const ta = document.getElementById(id); if (ta) ta.value = ''; }
function refreshEditors() { Object.values(editors).forEach(e => e.refresh()); }

// ============================================================
// THEME
// ============================================================
(function(){
  const saved = localStorage.getItem('devtools-theme');
  if (saved === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
  document.getElementById('themeToggle').onclick = () => {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('devtools-theme', next);
    const isDark = next === 'dark';
    Object.values(editors).forEach(e => e.setOption('theme', isDark ? 'monokai' : 'default'));
  };
})();

// ============================================================
// TOAST & UTILS
// ============================================================
function toast(msg, type) {
  const c = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = 'toast toast-' + (type || 'success'); t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => { t.style.opacity='0'; t.style.transition='opacity .3s'; setTimeout(()=>t.remove(),300); }, 2000);
}
function copyTextById(id) {
  const el = document.getElementById(id);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent || el.value || '').then(()=>toast('已复制'), ()=>toast('复制失败','error'));
}
// 把文本结果导出成文件下载（Blob + 临时 a[download]，纯前端，不经过服务器）。
function downloadText(filename, text, mime) {
  if (!text) { toast('没有可下载的结果'); return; }
  try {
    const blob = new Blob([text], { type: (mime || 'text/plain') + ';charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    // 延迟清理：headless 下若立即 remove + revoke，浏览器会取消正在进行的 blob 下载。
    setTimeout(() => { a.remove(); URL.revokeObjectURL(url); }, 4000);
    toast('已下载 ' + filename);
  } catch (e) {
    toast('下载失败');
  }
}
function escHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function formatBytes(b) { return b < 1024 ? b + ' B' : (b / 1024).toFixed(1) + ' KB'; }
function safeParse(str) { try { return { success:true, data:JSON.parse(str) }; } catch(e) { return { success:false, error:e.message }; } }

// ============================================================
// PAGE NAVIGATION
// ============================================================
// 顶部导航已是真实链接：每个工具一个独立 URL、独立 HTML，各自只包含自己的 UI，
// 因此不再需要客户端标签切换。当前页由构建时写入的 <html data-page="..."> 指明。
const pageInited = {};
function currentPage() {
  return document.documentElement.getAttribute('data-page') || 'json';
}
function initPage(name) {
  if (pageInited[name]) return;
  pageInited[name] = true;
  switch (name) {
    case 'json': initJsonPage(); break;
    case 'diff': initDiffPage(); break;
    case 'encode': initEncodePage(); break;
    case 'regex': initRegexPage(); break;
    case 'timestamp': initTimestampPage(); break;
    case 'batch': initBatchPage(); break;
    case 'timestamp-list': initTimestampListPage(); break;
    case 'timezones': initTimezonesPage(); break;
    case 'weeknumbers': initWeeknumbersPage(); break;
    case 'daynumbers': initDaynumbersPage(); break;
    case 'years': initYearsPage(); break;
    case 'world-clock': initWorldClockPage(); break;
    case 'countdown': initCountdownPage(); break;
    case 'date-difference': initDateDifferencePage(); break;
    case 'date-calculator': initDateCalculatorPage(); break;
    case 'duration': initDurationPage(); break;
    case 'uuid': initUuidPage(); break;
    case 'snowflake': initSnowflakePage(); break;
    case 'tid': initTidPage(); break;
    case 'objectid': initObjectIdPage(); break;
    case 'firebase': initFirebasePage(); break;
    case 'base': initBasePage(); break;
    case 'binary': initBinaryPage(); break;
    case 'hex': initHexPage(); break;
    case 'hash': initHashPage(); break;
    case 'formatter': initFormatterPage(); break;
    case 'string': initStringPage(); break;
    case 'generator': initGeneratorPage(); break;
  }
}

// ============================================================
// INIT
// ============================================================
function init() {
  const name = currentPage();
  setTimeout(() => { initPage(name); resizeAllEditors(); }, 300);
}

document.addEventListener('DOMContentLoaded', init);

// ============================================================
// 全站工具搜索 + 最近使用
// ============================================================
(function () {
  var STORE_KEY = 'devtools-recent';
  var MAX_RECENT = 8;     // 持久化保留的最近使用工具上限
  var SHOW_RECENT = 6;    // 搜索空态 / 导航下拉里展示的条数

  // ---- localStorage 读写（隐私模式等不可用时静默降级）----
  function loadRecent() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY) || '{}'); }
    catch (e) { return {}; }
  }
  function saveRecent(obj) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(obj)); } catch (e) {}
  }

  // 记录一次工具使用：频率 + 最近时间戳
  function recordToolUse(slug) {
    if (!slug) return;
    var rec = loadRecent();
    var e = rec[slug] || { count: 0, last: 0 };
    e.count += 1; e.last = Date.now();
    rec[slug] = e;
    saveRecent(rec);
  }

  // 按使用频率降序、频率相同按最近使用降序
  function getRecentSorted() {
    var rec = loadRecent();
    var arr = Object.keys(rec).map(function (k) {
      return { slug: k, count: rec[k].count, last: rec[k].last };
    });
    arr.sort(function (a, b) { return b.count - a.count || b.last - a.last; });
    return arr;
  }

  function metaOf(slug) {
    var idx = window.__TOOL_INDEX__ || [];
    for (var i = 0; i < idx.length; i++) if (idx[i].slug === slug) return idx[i];
    return null;
  }

  function pageLang() {
    var l = (document.documentElement.getAttribute('lang') || 'zh-CN').toLowerCase();
    return l.indexOf('en') === 0 ? 'en' : 'zh';
  }

  function itemLabel(m) { var f = m[pageLang()]; return (f && f.l) || (m.en && m.en.l) || m.slug; }
  function itemTitle(m) { var f = m[pageLang()]; return (f && f.t) || (m.en && m.en.t) || ''; }
  function itemGroup(m) { return m.g || ''; }

  // ---- 渲染：导航下拉「最近使用」面板 ----
  function renderRecentPanel() {
    var panel = document.getElementById('recentPanel');
    if (!panel) return;
    var sorted = getRecentSorted().slice(0, MAX_RECENT);
    if (!sorted.length) {
      panel.innerHTML = '<div class="nav-panel-empty">暂无使用记录</div>';
      return;
    }
    var html = '';
    for (var i = 0; i < sorted.length; i++) {
      var m = metaOf(sorted[i].slug);
      if (!m) continue;
      html += '<a class="nav-panel-item" href="' + escHtml(m.href) + '">' + escHtml(itemLabel(m)) + '</a>';
    }
    html += '<button class="recent-clear" type="button" id="recentClear">清除记录</button>';
    panel.innerHTML = html;
    var clr = document.getElementById('recentClear');
    if (clr) clr.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      clearHistory();
    });
  }

  // 清空使用记录：同步刷新导航下拉面板与（若打开的）搜索浮层
  function clearHistory() {
    saveRecent({});
    renderRecentPanel();
    renderSearch(input ? input.value : '');
  }

  // ---- 渲染：搜索结果 / 空态（最近使用）----
  var overlay = null, input = null, results = null;
  function buildResultItem(m) {
    return '<a class="search-item" href="' + escHtml(m.href) + '">' +
             '<span class="search-item-label">' + escHtml(itemLabel(m)) + '</span>' +
             (itemGroup(m) ? '<span class="search-item-group">' + escHtml(itemGroup(m)) + '</span>' : '') +
             (itemTitle(m) ? '<span class="search-item-title">' + escHtml(itemTitle(m)) + '</span>' : '') +
           '</a>';
  }

  function renderSearch(q) {
    if (!results) return;
    var idx = window.__TOOL_INDEX__ || [];
    q = (q || '').trim().toLowerCase();
    if (!q) {
      var sorted = getRecentSorted().slice(0, SHOW_RECENT);
      var h = '<div class="search-section-title">最近使用</div>';
      if (!sorted.length) {
        h += '<div class="search-empty">暂无使用记录<br>使用过的工具会显示在这里</div>';
      } else {
        for (var i = 0; i < sorted.length; i++) {
          var m = metaOf(sorted[i].slug); if (!m) continue;
          h += buildResultItem(m);
        }
        h += '<button class="recent-clear search-clear" type="button" id="searchClear">清除记录</button>';
      }
      results.innerHTML = h;
      var sc = document.getElementById('searchClear');
      if (sc) sc.addEventListener('click', clearHistory);
      return;
    }
    var hits = [];
    for (var j = 0; j < idx.length; j++) {
      var d = idx[j];
      var hay = ((d.zh.l || '') + (d.zh.t || '') + (d.zh.k || '') +
                 (d.en.l || '') + (d.en.t || '') + (d.en.k || '')).toLowerCase();
      if (hay.indexOf(q) !== -1) hits.push(d);
    }
    if (!hits.length) {
      results.innerHTML = '<div class="search-empty">没有找到相关工具</div>';
      return;
    }
    var out = '<div class="search-section-title">搜索结果（' + hits.length + '）</div>';
    for (var k = 0; k < hits.length; k++) out += buildResultItem(hits[k]);
    results.innerHTML = out;
  }

  function openSearch() {
    if (!overlay) return;
    overlay.hidden = false;
    document.body.classList.add('search-open');
    if (input) { input.value = ''; renderSearch(''); setTimeout(function () { input.focus(); }, 30); }
  }
  function closeSearch() {
    if (!overlay) return;
    overlay.hidden = true;
    document.body.classList.remove('search-open');
    if (input) input.blur();
  }

  function initSearch() {
    overlay = document.getElementById('searchOverlay');
    input = document.getElementById('searchInput');
    results = document.getElementById('searchResults');
    var btn = document.getElementById('searchBtn');
    if (btn) btn.addEventListener('click', openSearch);
    if (overlay) {
      Array.prototype.forEach.call(overlay.querySelectorAll('[data-search-close]'), function (el) {
        el.addEventListener('click', closeSearch);
      });
    }
    if (input) {
      input.addEventListener('input', function () { renderSearch(input.value); });
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          var first = results && results.querySelector('.search-item');
          if (first) window.location.href = first.getAttribute('href');
        } else if (e.key === 'Escape') {
          closeSearch();
        }
      });
    }
    // "/" 快捷键打开搜索（输入框 / 编辑器内不触发）
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey) {
        var t = e.target;
        var tag = t && t.tagName ? t.tagName.toLowerCase() : '';
        var editing = tag === 'input' || tag === 'textarea' || (t && t.isContentEditable) ||
                      (t && t.closest && t.closest('.CodeMirror'));
        if (!editing && overlay && overlay.hidden) { e.preventDefault(); openSearch(); }
      }
    });
  }

  // 页面初始化：记录当前工具的使用 + 渲染最近使用面板 + 初始化搜索
  function initSearchAndRecent() {
    var p = currentPage();
    var slug = (p && p.indexOf('blog') === 0) ? 'blog' : p;
    if (metaOf(slug)) recordToolUse(slug);
    renderRecentPanel();
    initSearch();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearchAndRecent);
  } else {
    initSearchAndRecent();
  }
})();

// ============================================================
// MOBILE NAV（窄屏抽屉）
// ============================================================
// 桌面端这段完全不起作用：CSS 里 .nav-toggle 是 display:none，.top-nav 保持原样。
// 窄屏下把导航收进 ☰ 抽屉，分类下拉从浮层改成原地展开（配合 style.css 的媒体查询）。
//
// 为什么不用 :focus-within 纯 CSS：移动浏览器点击 <button> 是否获得焦点行为不一致，
// 靠焦点展开会时灵时不灵；"点外面关闭"更是只有 JS 能做。
(function () {
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('topNav');
  var header = document.querySelector('.header');
  if (!toggle || !nav || !header) return;

  function isOpen() { return document.body.classList.contains('nav-open'); }
  function setOpen(open) {
    document.body.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (!open) {
      // 收起抽屉时把展开的分类也一并复位，下次打开是干净的初始状态
      Array.prototype.forEach.call(nav.querySelectorAll('.nav-dropdown.open'), function (dd) {
        dd.classList.remove('open');
      });
    }
  }

  toggle.addEventListener('click', function () { setOpen(!isOpen()); });

  // 抽屉里的分类：点分类名原地展开/收起，同时只留一个展开的
  Array.prototype.forEach.call(nav.querySelectorAll('.nav-dropdown'), function (dd) {
    var trig = dd.querySelector('.nav-trigger');
    if (!trig) return;
    trig.addEventListener('click', function () {
      var willOpen = !dd.classList.contains('open');
      Array.prototype.forEach.call(nav.querySelectorAll('.nav-dropdown.open'), function (o) {
        if (o !== dd) o.classList.remove('open');
      });
      dd.classList.toggle('open', willOpen);
    });
  });

  // 点 drawer 以外的地方关闭。header 内的点击（含 ☰ 本身）都交给上面的处理器
  document.addEventListener('click', function (e) {
    if (isOpen() && !header.contains(e.target)) setOpen(false);
  });

  // Esc 关闭并把焦点还给 ☰，键盘用户不会迷失位置
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen()) { setOpen(false); toggle.focus(); }
  });

  // 抽屉里点链接：跨页跳转会重载页面、自然关闭；同页锚点不会，所以手动关一次
  Array.prototype.forEach.call(nav.querySelectorAll('a'), function (a) {
    a.addEventListener('click', function () { setOpen(false); });
  });

  // 转到桌面宽度时清掉状态：否则从横屏转竖屏再转回来，body.nav-open 会残留，
  // 桌面上打开着抽屉布局（虽然桌面媒体查询不生效，但 aria-expanded 会误导读屏软件）
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900 && isOpen()) setOpen(false);
  });
})();