// 浏览器里 G 就是 window；Node 单测里退化成空对象，保证纯函数可直接 require。
var G = (typeof window !== 'undefined') ? window : {};

// user-agent.js — UA 字符串解析（浏览器 / 版本 / 内核 / 系统 / 设备 / 爬虫）
// 纯函数 + 页面；不联网、不读取任何服务端信息，全部在本地用正则拆解。

// 已知客户端工具与爬虫：这些「浏览器」不是用户，排在浏览器识别之前判断。
var UA_BOTS = [
  [/Googlebot-Image/i, 'Googlebot-Image'], [/Googlebot/i, 'Googlebot'],
  [/bingbot/i, 'bingbot'], [/Baiduspider/i, 'Baiduspider'], [/YisouSpider/i, 'YisouSpider'],
  [/Sogou web spider/i, 'Sogou'], [/360Spider/i, '360Spider'], [/YandexBot/i, 'YandexBot'],
  [/DuckDuckBot/i, 'DuckDuckBot'], [/Applebot/i, 'Applebot'], [/PetalBot/i, 'PetalBot'],
  [/Bytespider/i, 'Bytespider'], [/GPTBot/i, 'GPTBot'], [/ClaudeBot/i, 'ClaudeBot'],
  [/AhrefsBot/i, 'AhrefsBot'], [/SemrushBot/i, 'SemrushBot'], [/MJ12bot/i, 'MJ12bot'],
  [/facebookexternalhit/i, 'facebookexternalhit'], [/Twitterbot/i, 'Twitterbot'],
  [/Slackbot/i, 'Slackbot'], [/curl\//i, 'curl'], [/Wget/i, 'Wget'],
  [/python-requests/i, 'python-requests'], [/python-urllib/i, 'python-urllib'],
  [/Go-http-client/i, 'Go-http-client'], [/okhttp/i, 'OkHttp'], [/axios/i, 'axios'],
  [/PostmanRuntime/i, 'Postman'], [/Apache-HttpClient/i, 'Apache HttpClient'],
  [/Java\//i, 'Java'], [/node-fetch/i, 'node-fetch'], [/libwww-perl/i, 'libwww-perl'],
  [/HeadlessChrome/i, 'HeadlessChrome'], [/PhantomJS/i, 'PhantomJS'],
];

// 浏览器：顺序敏感——Chromium 系的自称里都带 Safari/Chrome，必须先匹配更具体的那个。
var UA_BROWSERS = [
  [/MicroMessenger\/([\d.]+)/i, 'WeChat'],
  [/QQBrowser\/([\d.]+)/i, 'QQBrowser'],
  [/MQQBrowser\/([\d.]+)/i, 'QQBrowser'],
  [/UCBrowser\/([\d.]+)/i, 'UCBrowser'],
  [/HuaweiBrowser\/([\d.]+)/i, 'HuaweiBrowser'],
  [/MiuiBrowser\/([\d.]+)/i, 'MiuiBrowser'],
  [/DingTalk\/([\d.]+)/i, 'DingTalk'],
  [/AlipayClient\/([\d.]+)/i, 'Alipay'],
  [/Weibo\/([\d.]+)/i, 'Weibo'],
  [/Edg(?:e|A|iOS)?\/([\d.]+)/i, 'Edge'],
  [/OPR\/([\d.]+)/i, 'Opera'],
  [/Opera[ /]([\d.]+)/i, 'Opera'],
  [/SamsungBrowser\/([\d.]+)/i, 'Samsung Internet'],
  [/Vivaldi\/([\d.]+)/i, 'Vivaldi'],
  [/YaBrowser\/([\d.]+)/i, 'Yandex Browser'],
  [/Firefox\/([\d.]+)/i, 'Firefox'],
  [/FxiOS\/([\d.]+)/i, 'Firefox'],
  [/CriOS\/([\d.]+)/i, 'Chrome'],
  [/Chrome\/([\d.]+)/i, 'Chrome'],
  [/MSIE ([\d.]+)/i, 'IE'],
  [/Trident\/7\.0.*rv:([\d.]+)/i, 'IE'],
  [/Version\/([\d.]+).*Safari/i, 'Safari'],
  [/Safari\/([\d.]+)/i, 'Safari'],
];

// 渲染内核：靠版本号分界（Chrome 28 起换 Blink，Opera 15 起也换）
function uaEngine(ua, browser, version) {
  var major = parseInt(version, 10) || 0;
  if (browser === 'IE') return 'Trident';
  if (browser === 'Firefox') return 'Gecko';
  if (browser === 'Edge' || browser === 'Vivaldi' || browser === 'Opera') {
    // 老 Edge（EdgeHTML）UA 里没有 Chrome/，新版 Edg/ 是 Chromium
    if (/Edge\//.test(ua) && !/Chrome\//.test(ua)) return 'EdgeHTML';
    return major >= 15 || /Edg\//.test(ua) ? 'Blink' : 'Presto';
  }
  if (browser === 'Chrome' || browser === 'Samsung Internet' || browser === 'UCBrowser' ||
      browser === 'QQBrowser' || browser === 'HuaweiBrowser' || browser === 'MiuiBrowser' ||
      browser === 'YaBrowser' || browser === 'WeChat' || browser === 'DingTalk' ||
      browser === 'Alipay' || browser === 'Weibo') {
    // 微信/QQ 等套壳浏览器的内核版本要看它内嵌的 Chrome/ 号
    var c = /Chrome\/(\d+)/.exec(ua) || /Chromium\/(\d+)/.exec(ua);
    var cm = c ? parseInt(c[1], 10) : major;
    return cm >= 28 ? 'Blink' : 'WebKit';
  }
  if (/AppleWebKit/.test(ua)) return 'WebKit';
  return '';
}

function uaOs(ua) {
  var m;
  if ((m = /Windows NT ([\d.]+)/.exec(ua))) {
    var map = { '10.0': 'Windows 10 / 11', '6.3': 'Windows 8.1', '6.2': 'Windows 8',
                '6.1': 'Windows 7', '6.0': 'Windows Vista', '5.1': 'Windows XP',
                '5.0': 'Windows 2000' };
    return { name: map[m[1]] || ('Windows ' + m[1]), version: m[1] === '10.0' ? '' : '' };
  }
  if (/Windows Phone/.test(ua)) return { name: 'Windows Phone', version: '' };
  if ((m = /Android[ /]([\d.]+)/.exec(ua))) return { name: 'Android', version: m[1] };
  if (/Android/.test(ua)) return { name: 'Android', version: '' };
  if ((m = /(?:iPhone|iPad|iPod).*?OS ([\d_]+)/.exec(ua))) {
    return { name: /iPad/.test(ua) ? 'iPadOS' : 'iOS', version: m[1].replace(/_/g, '.') };
  }
  if ((m = /Mac OS X ([\d_.]+)/.exec(ua))) {
    return { name: 'macOS', version: m[1].replace(/_/g, '.') };
  }
  if ((m = /CrOS [^ ]+ ([\d.]+)/.exec(ua))) return { name: 'ChromeOS', version: m[1] };
  if (/Ubuntu/.test(ua)) return { name: 'Ubuntu', version: '' };
  if (/Fedora/.test(ua)) return { name: 'Fedora', version: '' };
  if (/Linux/.test(ua)) return { name: 'Linux', version: '' };
  return { name: '', version: '' };
}

function uaDevice(ua) {
  if (/iPad|Tablet|PlayBook|Silk/i.test(ua) && !/Mobile/i.test(ua)) return 'tablet';
  if (/iPad/.test(ua)) return 'tablet';
  if (/Mobile|iPhone|iPod|Android.*Mobile|Windows Phone|BlackBerry|IEMobile/i.test(ua)) return 'mobile';
  if (/Android/.test(ua)) return 'tablet';      // 安卓平板通常没有 Mobile 段
  if (/TV|SmartTV|AppleTV|HbbTV/.test(ua)) return 'tv';
  if (/bot|spider|crawler/i.test(ua)) return 'bot';
  return 'desktop';
}

function uaArch(ua) {
  if (/arm64|aarch64/i.test(ua)) return 'ARM64';
  if (/WOW64|Win64|x64|x86_64/i.test(ua)) return 'x86-64';
  if (/iPhone|iPad|Android.*arm/i.test(ua)) return 'ARM';
  if (/i686|i386|x86/i.test(ua)) return 'x86';
  return '';
}

// 主入口：返回结构化结果
function uaParse(input) {
  var ua = String(input == null ? '' : input).trim();
  if (!ua) return { valid: false, reason: 'empty' };

  var bot = '';
  for (var i = 0; i < UA_BOTS.length; i++) {
    if (UA_BOTS[i][0].test(ua)) { bot = UA_BOTS[i][1]; break; }
  }

  var browser = '', version = '';
  for (var j = 0; j < UA_BROWSERS.length; j++) {
    var m = UA_BROWSERS[j][0].exec(ua);
    if (m) {
      browser = UA_BROWSERS[j][1];
      version = m[1] || '';
      break;
    }
  }
  // 老 Edge 的 Edg/ 之外还有 Edge/18.x（EdgeHTML），UA_BROWSERS 里已含 Edge
  if (!browser && /Chrome\//.test(ua)) { browser = 'Chrome'; version = (/Chrome\/([\d.]+)/.exec(ua) || [])[1] || ''; }

  var os = uaOs(ua);
  var engine = uaEngine(ua, browser, version);
  var device = uaDevice(ua);

  return {
    valid: true,
    ua: ua,
    length: ua.length,
    browser: browser,
    version: version,
    major: parseInt(version, 10) || 0,
    engine: engine,
    os: os.name,
    osVersion: os.version,
    device: bot ? 'bot' : device,
    arch: uaArch(ua),
    bot: bot,
    // 移动端标记：用于判断「该给用户看哪套布局」这类问题
    isMobile: device === 'mobile' || device === 'tablet'
  };
}

// ---------------------------------------------------------------- 页面
function uaTL() { return G.__TL__ || {}; }

function uaFillPresets() {
  var box = document.getElementById('uaPresets');
  if (!box) return;
  var L = uaTL();
  var list = (L && L.presets) || [];
  var html = '';
  for (var i = 0; i < list.length; i++) {
    // 只放序号，不放 UA 原文：UA 里可能带引号，塞进属性会把 HTML 拆断
    html += '<button class="tl-chip" type="button" data-idx="' + i + '">' +
      escHtml(list[i][0]) + '</button>';
  }
  box.innerHTML = html;
  box.addEventListener('click', function (e) {
    var b = e.target.closest('[data-idx]');
    if (!b) return;
    var idx = parseInt(b.getAttribute('data-idx'), 10);
    var cur = (uaTL().presets || [])[idx];
    if (!cur) return;
    setVal('uaInput', cur[1]);
    uaRender();
  });
}

function uaRender() {
  var L = uaTL();
  var box = document.getElementById('uaResult');
  if (!box) return;
  var raw = getVal('uaInput');
  var r = uaParse(raw);
  if (!raw.trim()) {
    box.innerHTML = '<div class="tl-hint">' + escHtml(L.hint || '') + '</div>';
    return;
  }
  if (!r.valid) {
    box.innerHTML = '<div class="tl-err">' + escHtml(L.err_empty || '') + '</div>';
    return;
  }

  var rows = [];
  if (r.bot) rows.push([L.r_bot, r.bot]);
  rows.push([L.r_browser, (r.browser || L.unknown) + (r.version ? ' ' + r.version : '')]);
  rows.push([L.r_engine, r.engine || L.unknown]);
  rows.push([L.r_os, (r.os || L.unknown) + (r.osVersion ? ' ' + r.osVersion : '')]);
  rows.push([L.r_device, L['dev_' + r.device] || r.device]);
  rows.push([L.r_arch, r.arch || L.unknown]);
  rows.push([L.r_len, String(r.length)]);

  var html = '<table class="dt-table"><tbody>';
  for (var i = 0; i < rows.length; i++) {
    html += '<tr><th style="width:32%">' + escHtml(rows[i][0]) + '</th><td>' + escHtml(rows[i][1]) + '</td></tr>';
  }
  html += '</tbody></table>';
  box.innerHTML = html;
}

G.uaRender = uaRender;
G.uaClear = function () { setVal('uaInput', ''); uaRender(); };
G.uaCurrent = function () {
  var ua = navigator.userAgent || '';
  setVal('uaInput', ua);
  uaRender();
};

function initUA() {
  var input = document.getElementById('uaInput');
  if (!input) return;
  uaFillPresets();
  // 首次进入直接填当前浏览器的 UA：大多数人来这一页就是想「看看自己这条是什么」
  if (!input.value) input.value = navigator.userAgent || '';
  uaRender();
  input.addEventListener('input', uaRender);
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUA);
  } else {
    initUA();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { uaParse: uaParse, uaEngine: uaEngine, uaOs: uaOs,
                     uaDevice: uaDevice, uaArch: uaArch };
}
