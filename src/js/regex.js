// regex.js — Regular expression tester
// ============================================================
// 3. REGEX PAGE
// ============================================================
function setRegexPattern(pattern) {
  document.getElementById('regexPattern').value = pattern;
  liveRegex();
}

function initRegexPage() {
  document.getElementById('regexInput').value = 'test@example.com\nadmin@site.cn\n\n联系电话: 13812345678\n网址: https://www.example.com/path';
  document.getElementById('regexPattern').value = '[\\w.-]+@[\\w.-]+\\.[a-z]{2,}';
  setTimeout(liveRegex, 200);
}

function liveRegex() {
  const pattern = document.getElementById('regexPattern').value;
  const input = document.getElementById('regexInput').value;
  const resultEl = document.getElementById('regexResult');
  const countEl = document.getElementById('regexMatchCount');
  const replaceEl = document.getElementById('regexReplaceResult');
  const replacePanel = document.getElementById('regexReplacePanel');

  if (!pattern.trim()) { resultEl.innerHTML = '<span style="color:var(--text-muted)">输入正则表达式</span>'; countEl.textContent = ''; replaceEl.innerHTML = ''; return; }
  try {
    let flags = '';
    if (document.getElementById('regexFlagG').checked) flags += 'g';
    if (document.getElementById('regexFlagI').checked) flags += 'i';
    if (document.getElementById('regexFlagM').checked) flags += 'm';
    if (document.getElementById('regexFlagS').checked) flags += 's';
    if (document.getElementById('regexFlagU').checked) flags += 'u';
    const re = new RegExp(pattern, flags);
    const matches = [...input.matchAll(re)];
    countEl.textContent = matches.length > 0 ? '(' + matches.length + ' 个匹配)' : '(无匹配)';

    if (matches.length === 0) {
      resultEl.innerHTML = '<span style="color:var(--text-secondary)">无匹配结果</span>';
    } else {
      const hasGroups = matches[0].length > 1;
      let html = '';
      matches.forEach((m, idx) => {
        html += '<div class="match-group"><span class="group-label">匹配 ' + (idx + 1) + ':</span> <span class="group-val">' + escHtml(m[0]) + '</span>';
        html += '<span style="font-size:10px;color:var(--text-muted);margin-left:8px">位置 ' + m.index + ', 长度 ' + m[0].length + '</span>';
        if (hasGroups) {
          for (let g = 1; g < m.length; g++) {
            html += '<div style="margin:2px 0 0 12px"><span class="group-label">组 ' + g + ':</span> <span class="group-val">' + (m[g] !== undefined ? escHtml(m[g]) : '&lt;未匹配&gt;') + '</span></div>';
          }
        }
        html += '</div>';
      });
      resultEl.innerHTML = html;
    }

    if (replacePanel.style.display !== 'none') {
      const replaceWith = document.getElementById('regexReplaceWith').value;
      try {
        const replaced = input.replace(re, replaceWith);
        replaceEl.innerHTML = '<pre style="margin:0;white-space:pre-wrap">' + escHtml(replaced) + '</pre>';
      } catch (e) { replaceEl.innerHTML = '<span style="color:var(--danger)">替换错误: ' + escHtml(e.message) + '</span>'; }
    }
  } catch (e) {
    resultEl.innerHTML = '<span style="color:var(--danger)">正则表达式错误: ' + escHtml(e.message) + '</span>';
    countEl.textContent = '(错误)';
  }
}

function toggleReplacePanel() {
  const panel = document.getElementById('regexReplacePanel');
  panel.style.display = panel.style.display === 'none' ? 'flex' : 'none';
  if (panel.style.display !== 'none') liveRegex();
}

