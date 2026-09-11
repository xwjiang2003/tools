// text-diff.js — Generic text diff (like Beyond Compare)

function initDiffPage() {
  // Load demo data（用户已经开始输入就不要覆盖）
  const a = document.getElementById('textDiffInputA');
  const b = document.getElementById('textDiffInputB');
  if (a.value.trim() || b.value.trim()) { setTimeout(doTextDiff, 200); return; }
  a.value =
    'function hello(name) {\n  console.log("Hello, " + name);\n  return true;\n}\n\nfunction goodbye() {\n  console.log("Bye!");\n  return false;\n}\n\nvar x = 100;\nvar y = 200;';
  document.getElementById('textDiffInputB').value =
    'function hello(name, age) {\n  console.log("Hello, " + name);\n  console.log("Age: " + age);\n  return true;\n}\n\nfunction goodbye() {\n  console.log("Goodbye!");\n  return false;\n}\n\nvar x = 100;\nvar z = 300;';
  setTimeout(doTextDiff, 200);
}

function doTextDiff() {
  const a = document.getElementById('textDiffInputA').value;
  const b = document.getElementById('textDiffInputB').value;
  const resultEl = document.getElementById('textDiffResult');
  const statsEl = document.getElementById('diffStatsLabel');

  if (!a.trim() && !b.trim()) {
    resultEl.innerHTML = '<span style="color:var(--text-muted)">请输入文本</span>';
    statsEl.textContent = '差异结果';
    return;
  }

  const caseSensitive = document.getElementById('diffCaseSensitive').checked;
  const ignoreWS = document.getElementById('diffIgnoreWS').checked;
  const viewMode = document.getElementById('diffViewMode').value;

  let linesA = a.split(NL);
  let linesB = b.split(NL);

  if (!caseSensitive) { linesA = linesA.map(l => l.toLowerCase()); linesB = linesB.map(l => l.toLowerCase()); }
  if (ignoreWS) { linesA = linesA.map(l => l.replace(/\s+/g, ' ').trim()); linesB = linesB.map(l => l.replace(/\s+/g, ' ').trim()); }

  const diff = computeDiff(linesA, linesB);
  const adds = diff.filter(d => d.type === 'add').length;
  const rems = diff.filter(d => d.type === 'remove').length;
  statsEl.textContent = '差异结果 — 新增 ' + adds + ' 行, 删除 ' + rems + ' 行';

  if (adds === 0 && rems === 0) {
    resultEl.innerHTML = '<div style="padding:12px;color:var(--success);font-weight:500">✅ 两个文本完全一致</div>';
    return;
  }

  if (viewMode === 'sidebyside') {
    resultEl.innerHTML = renderSideBySide(diff, a, b);
  } else {
    resultEl.innerHTML = renderUnified(diff);
  }
}

function computeDiff(la, lb) {
  const n = la.length, m = lb.length;
  const dp = Array.from({ length: n + 1 }, () => Array(m + 1).fill(0));
  for (let i = 1; i <= n; i++)
    for (let j = 1; j <= m; j++)
      dp[i][j] = la[i - 1] === lb[j - 1] ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1]);

  const result = [];
  let i = n, j = m;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && la[i - 1] === lb[j - 1]) {
      result.unshift({ type: 'equal', value: la[i - 1], lineA: i, lineB: j });
      i--; j--;
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      result.unshift({ type: 'add', value: lb[j - 1], lineB: j });
      j--;
    } else {
      result.unshift({ type: 'remove', value: la[i - 1], lineA: i });
      i--;
    }
  }
  return result;
}

function renderUnified(diff) {
  let html = '<div class="diff-unified">';
  let lineA = 1, lineB = 1;
  let hunkStarted = false;

  for (let i = 0; i < diff.length; i++) {
    const d = diff[i];

    // Show context: 3 lines before/after changes
    const hasChangeNearby = diff.slice(Math.max(0, i - 3), Math.min(diff.length, i + 4))
      .some(x => x.type !== 'equal');

    if (d.type === 'equal' && !hasChangeNearby) {
      if (!hunkStarted) {
        html += '<div class="diff-unified-header">... 跳过 ' + (lineB - (d.lineB || 1)) + ' 行 ...</div>';
        hunkStarted = true;
      }
      lineA++; lineB++;
      continue;
    }
    hunkStarted = false;

    if (d.type === 'add') {
      html += '<div class="diff-unified-line diff-unified-add">+ ' + escHtml(d.value) + '</div>';
      lineB++;
    } else if (d.type === 'remove') {
      html += '<div class="diff-unified-line diff-unified-remove">- ' + escHtml(d.value) + '</div>';
      lineA++;
    } else {
      html += '<div class="diff-unified-line diff-unified-equal">  ' + escHtml(d.value) + '</div>';
      lineA++; lineB++;
    }
  }
  html += '</div>';
  return html;
}

function renderSideBySide(diff, originalA, originalB) {
  let html = '<table class="diff-side-table"><colgroup><col style="width:3%"><col style="width:43%"><col style="width:4%"><col style="width:3%"><col style="width:43%"></colgroup>';
  let i = 0;
  while (i < diff.length) {
    const d = diff[i];

    if (d.type === 'equal') {
      const nA = d.lineA || 0, nB = d.lineB || 0;
      html += '<tr><td class="diff-side-num">' + nA + '</td><td>' + escHtml(d.value) + '</td>';
      html += '<td class="diff-side-num">' + nB + '</td><td>' + escHtml(d.value) + '</td></tr>';
      i++;
    } else if (d.type === 'remove' && i + 1 < diff.length && diff[i + 1].type === 'add') {
      // Paired change: show word diff
      const rem = d, add = diff[i + 1];
      const wordDiff = computeWordDiff(rem.value, add.value);
      html += '<tr>';
      html += '<td class="diff-side-num">' + (rem.lineA || '') + '</td>';
      html += '<td class="diff-side-remove">' + formatWordDiff(wordDiff, 'remove') + '</td>';
      html += '<td class="diff-side-num">' + (add.lineB || '') + '</td>';
      html += '<td class="diff-side-add">' + formatWordDiff(wordDiff, 'add') + '</td>';
      html += '</tr>';
      i += 2;
    } else if (d.type === 'remove') {
      html += '<tr>';
      html += '<td class="diff-side-num">' + (d.lineA || '') + '</td>';
      html += '<td class="diff-side-remove">' + escHtml(d.value) + '</td>';
      html += '<td class="diff-side-num"></td><td class="diff-side-empty"></td>';
      html += '</tr>';
      i++;
    } else if (d.type === 'add') {
      html += '<tr>';
      html += '<td class="diff-side-num"></td><td class="diff-side-empty"></td>';
      html += '<td class="diff-side-num">' + (d.lineB || '') + '</td>';
      html += '<td class="diff-side-add">' + escHtml(d.value) + '</td>';
      html += '</tr>';
      i++;
    }
  }
  html += '</table>';
  return html;
}

function computeWordDiff(a, b) {
  // Simple character-level diff for inline highlighting
  const wordsA = a.split(/(\s+)/g);
  const wordsB = b.split(/(\s+)/g);
  const result = [];
  let i = 0, j = 0;
  while (i < wordsA.length || j < wordsB.length) {
    if (i < wordsA.length && j < wordsB.length && wordsA[i] === wordsB[j]) {
      result.push({ type: 'equal', value: wordsA[i] });
      i++; j++;
    } else if (i < wordsA.length) {
      result.push({ type: 'remove', value: wordsA[i] });
      i++;
      if (j < wordsB.length) { result.push({ type: 'add', value: wordsB[j] }); j++; }
    } else if (j < wordsB.length) {
      result.push({ type: 'add', value: wordsB[j] });
      j++;
    }
  }
  return result;
}

function formatWordDiff(wordDiff, side) {
  return wordDiff.map(w => {
    if (w.type === 'equal') return escHtml(w.value);
    if (w.type === side) return '<span class="word-' + side + '">' + escHtml(w.value) + '</span>';
    return '';
  }).join('');
}

function updateDiffView() {
  doTextDiff();
}

function copyTextDiffResult() {
  const el = document.getElementById('textDiffResult');
  navigator.clipboard.writeText(el.textContent || '').then(
    () => toast('已复制'), () => toast('复制失败', 'error')
  );
}
