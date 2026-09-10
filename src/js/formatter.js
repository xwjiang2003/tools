// formatter.js — HTML, CSS, JS, SQL, XML code formatter
// 注意：这里必须先声明 codeDemos 对象。此前直接写 codeDemos.js = ... 会抛
// ReferenceError，导致本文件后续所有函数（initFormatterPage / runCodeOp 等）
// 都没有被定义，代码格式化页整页不可用。
const codeDemos = {
  html: '<div class="card"><h2 class="title">标题</h2><p>正文内容</p><ul><li>项目一</li><li>项目二</li></ul></div>',
  css: '.card{padding:16px;border:1px solid #e1e5eb;border-radius:8px}.card .title{font-size:18px;color:#4a90d9;margin-bottom:8px}',
  js: 'function hello(name){if(name){console.log("Hello, "+name+"!");return{greeted:true,name:name}}else{console.log("Hello!");return{greeted:false}}',
  sql: 'SELECT u.id,u.name,u.email,o.total,o.created_at FROM users u INNER JOIN orders o ON u.id=o.user_id WHERE u.status=\'active\' AND o.total>100 GROUP BY u.id HAVING COUNT(o.id)>3 ORDER BY o.created_at DESC LIMIT 10',
  xml: '<root><users><user id="1"><name>张三</name><email>zhangsan@example.com</email></user><user id="2"><name>李四</name><email>lisi@example.com</email></user></users></root>'
};

// ============================================================
// 6. CODE FORMATTER PAGE
// ============================================================
let codeCurrentOp = 'html', codeCurrentMode = 'format';

function initFormatterPage() {
  document.querySelectorAll('#codeOpBtns .op-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('#codeOpBtns .op-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      codeCurrentOp = btn.dataset.op;
      updateCodeTitle();
    };
  });
}

function updateCodeTitle() {
  const names = {html:'HTML', css:'CSS', js:'JavaScript', sql:'SQL', xml:'XML'};
  document.getElementById('codeResultTitle').textContent = names[codeCurrentOp] + (codeCurrentMode === 'format' ? ' 格式化' : ' 压缩');
}

function runCodeOp(mode) {
  codeCurrentMode = mode;
  updateCodeTitle();
  const input = document.getElementById('codeInput').value;
  if (!input.trim()) { toast('请先输入代码','error'); return; }
  const indent = document.getElementById('codeIndent')?.value || '4';
  const istr = indent === 'tab' ? '\t' : ' '.repeat(parseInt(indent));
  let result = '';
  try {
    if (mode === 'compress') {
      result = input.replace(/\s+/g, ' ').trim();
      if (codeCurrentOp === 'css') result = result.replace(/\s*([{}:;,])\s*/g, '$1');
      else if (codeCurrentOp === 'html' || codeCurrentOp === 'xml') result = result.replace(/>\s+</g, '><');
      else if (codeCurrentOp === 'js') result = result.replace(/\s*([{}();,:])\s*/g, '$1');
      else if (codeCurrentOp === 'sql') result = result.replace(/\s+/g, ' ');
    } else {
      result = formatCode(input, codeCurrentOp, istr);
    }
    document.getElementById('codeResult').textContent = result;
    const inS = new TextEncoder().encode(input).length, outS = new TextEncoder().encode(result).length;
    document.getElementById('codeStats').innerHTML = '📝 ' + formatBytes(inS) + ' → ' + formatBytes(outS);
    document.getElementById('codeStats').style.display = 'flex';
    toast(mode === 'format' ? '格式化完成' : '压缩完成');
  } catch (e) {
    document.getElementById('codeResult').textContent = '❌ 错误: ' + e.message;
    toast('格式化失败','error');
  }
}

function loadCodeDemo() { document.getElementById('codeInput').value = codeDemos[codeCurrentOp] || codeDemos.html; }

function formatCode(input, type, indent) {
  switch (type) {
    case 'html': return formatHtml(input, indent);
    case 'css': return formatCss(input, indent);
    case 'js': return formatJs(input, indent);
    case 'sql': return formatSql(input, indent);
    case 'xml': return formatXml(input, indent);
    default: return input;
  }
}

function formatHtml(input, indent) {
  let result = '', depth = 0;
  const tags = input.replace(/<!--[\s\S]*?-->/g, '').replace(/>\s+</g, '><').split(/(<[^>]+>)/g).filter(Boolean);
  const selfClosing = /^(<area|<base|<br|<col|<embed|<hr|<img|<input|<link|<meta|<param|<source|<track|<wbr)/i;
  for (let tag of tags) {
    tag = tag.trim(); if (!tag) continue;
    if (tag.startsWith('</')) { depth = Math.max(0, depth - 1); result += indent.repeat(depth) + tag + NL; }
    else if (tag.startsWith('<') && !selfClosing.test(tag) && !tag.endsWith('/>')) { result += indent.repeat(depth) + tag + NL; depth++; }
    else if (tag.startsWith('<')) { result += indent.repeat(depth) + tag + NL; }
    else { result += indent.repeat(depth) + tag + NL; }
  }
  return result.trim();
}

function formatCss(input, indent) {
  let result = '', depth = 0;
  const tokens = input.replace(/\/\*[\s\S]*?\*\//g, '').split(/([{;}])/g);
  for (const token of tokens) {
    const t = token.trim(); if (!t) continue;
    if (t === '{') { result += ' {' + NL; depth++; }
    else if (t === '}') { depth = Math.max(0, depth - 1); result += indent.repeat(depth) + '}' + NL; }
    else if (t === ';') { result += ';' + NL; }
    else if (t.includes(':')) { result += indent.repeat(depth) + t; }
    else { result += t; }
  }
  return result.trim();
}

function formatJs(input, indent) {
  let result = '', depth = 0, i = 0;
  while (i < input.length) {
    const ch = input[i];
    if (ch === '{' || ch === '[' || ch === '(') {
      result += ch + NL; depth++;
      result += indent.repeat(depth); i++;
    } else if (ch === '}' || ch === ']' || ch === ')') {
      depth = Math.max(0, depth - 1);
      result = result.trimEnd();
      result += NL + indent.repeat(depth) + ch; i++;
    } else if (ch === ';') {
      result += ';' + NL + indent.repeat(depth); i++;
    } else if (ch === ',' && depth > 0) {
      result += ', '; i++;
    } else { result += ch; i++; }
  }
  return result;
}

function formatSql(input, indent) {
  const keywords = ['SELECT','FROM','WHERE','AND','OR','JOIN','INNER JOIN','LEFT JOIN','RIGHT JOIN','ON','GROUP BY','HAVING','ORDER BY','LIMIT','INSERT INTO','VALUES','UPDATE','SET','DELETE FROM','CREATE TABLE','ALTER TABLE','DROP','UNION','ALL','AS','IN','NOT IN','BETWEEN','LIKE','IS NULL','IS NOT NULL','EXISTS','CASE','WHEN','THEN','ELSE','END'];
  let result = input.replace(/\s+/g, ' ').trim();
  keywords.forEach(kw => {
    const re = new RegExp('\\b' + kw.replace(/ /g, '\\s+') + '\\b', 'gi');
    result = result.replace(re, NL + kw.toUpperCase());
  });
  result = result.replace(/,\s*/g, ',' + NL + '  ');
  return result.replace(/^\n/, '').trim();
}

function formatXml(input, indent) {
  let result = '', depth = 0;
  const tags = input.replace(/>\s+</g, '><').split(/(<[^?][^>]*>)/g).filter(Boolean);
  for (let tag of tags) {
    tag = tag.trim(); if (!tag) continue;
    if (tag.startsWith('</')) { depth = Math.max(0, depth - 1); result += indent.repeat(depth) + tag + NL; }
    else if (tag.startsWith('<?')) { result += tag + NL; }
    else if (tag.endsWith('/>')) { result += indent.repeat(depth) + tag + NL; }
    else { result += indent.repeat(depth) + tag + NL; depth++; }
  }
  return result.trim();
}

