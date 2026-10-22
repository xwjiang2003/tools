// lang-detect.js — 语言自动选择算法（单一来源）
//
// 为什么独立成文件：语言自动跳转的逻辑原本内联在 build.py 的三引号字符串里，
// 每页各生成一份、无法单测、改一处要重建全站。现在算法集中在这里，build.py
// 只负责把本文件内联进每个页面 <head>（保证首访早跳转、不闪），并注入每页的
// 数据（可选语言 + 各语言 URL）。改语言策略只动这一个文件。
//
// 优先级（2026-10-22 修正）：
//   浏览器语言列表里只要含中文（无论排第几），一律优先中文；
//   否则按首个命中的非中文支持语言回退。
//   这避免了 ['en-US','zh-CN'] 这类中英双语用户被误导进英文版。
//
// 注意：本文件被 build.py 以纯文本内联进 <head>，不依赖任何外部模块，也不碰 DOM。
function resolveAutoLang(browserLangs, supported) {
  browserLangs = browserLangs || [];
  supported = supported || [];
  var prefersZh = false;
  for (var i = 0; i < browserLangs.length; i++) {
    if ((browserLangs[i] || '').slice(0, 2).toLowerCase() === 'zh') {
      prefersZh = true;
      break;
    }
  }
  if (prefersZh) return 'zh';
  for (var j = 0; j < browserLangs.length; j++) {
    var p = (browserLangs[j] || '').slice(0, 2).toLowerCase();
    for (var k = 0; k < supported.length; k++) {
      if (supported[k] !== 'zh' && supported[k].toLowerCase().indexOf(p) === 0) {
        return supported[k];
      }
    }
  }
  return (supported.indexOf('en') >= 0) ? 'en' : supported[0];
}
