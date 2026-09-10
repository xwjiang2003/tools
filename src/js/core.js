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