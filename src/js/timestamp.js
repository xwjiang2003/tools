// timestamp.js — Unix timestamp converter
// ============================================================
// 4. TIMESTAMP PAGE
// ============================================================
let tsCurrentFmt = 'iso';

function initTimestampPage() {
  document.querySelectorAll('#tsOpBtns .op-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('#tsOpBtns .op-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      tsCurrentFmt = btn.dataset.op;
      document.getElementById('tsResultTitle').textContent = {iso:'ISO 8601 格式', rfc:'RFC 2822 格式', local:'本地格式', utc:'UTC 格式'}[tsCurrentFmt];
      updateTsDisplay();
    };
  });
  document.getElementById('dtInput').value = new Date().toISOString().slice(0, 16);
  updateTsDisplay();
  setInterval(updateTsClock, 1000);
}

function updateTsClock() {
  const now = new Date();
  document.getElementById('liveClock').textContent = Math.floor(now.getTime() / 1000).toLocaleString();
  document.getElementById('liveClockMs').textContent = now.getTime().toLocaleString();
  updateTsDisplay();
}

function updateTsDisplay() {
  const now = new Date();
  const tz = document.getElementById('tsTimezone').value;
  let d;
  try {
    if (tz === 'local' || tz === 'UTC') {
      d = tz === 'UTC' ? new Date(now.toUTCString()) : now;
    } else {
      d = new Date(now.toLocaleString('en-US', { timeZone: tz }));
    }
  } catch (e) { d = now; }
  let result = '';
  switch (tsCurrentFmt) {
    case 'iso': result = d.toISOString(); break;
    case 'rfc': result = d.toUTCString().replace('GMT', '+0000'); break;
    case 'local': result = d.toString(); break;
    case 'utc': result = d.toUTCString(); break;
  }
  document.getElementById('tsCurrentTime').textContent = result;
}

function tsToDate() {
  const input = document.getElementById('tsInput').value.trim();
  if (!input) { document.getElementById('tsToDateResult').textContent = '请输入时间戳'; return; }
  let ts = parseInt(input);
  if (ts > 1e15) ts = Math.floor(ts / 1000);
  const d = new Date(ts * 1000);
  if (isNaN(d.getTime())) { document.getElementById('tsToDateResult').textContent = '无效的时间戳'; return; }
  document.getElementById('tsToDateResult').innerHTML =
    '<b>本地:</b> ' + d.toString() + '<br><b>UTC:</b> ' + d.toUTCString() + '<br><b>ISO8601:</b> ' + d.toISOString() + '<br>' +
    '<b>年:</b> ' + d.getFullYear() + ' <b>月:</b> ' + (d.getMonth()+1) + ' <b>日:</b> ' + d.getDate() + ' ' +
    '<b>时:</b> ' + d.getHours() + ' <b>分:</b> ' + d.getMinutes() + ' <b>秒:</b> ' + d.getSeconds() + ' ' +
    '<b>星期:</b> ' + ['日','一','二','三','四','五','六'][d.getDay()];
}

function dateToTs() {
  const input = document.getElementById('dtInput').value;
  if (!input) { document.getElementById('dateToTsResult').textContent = '请选择日期时间'; return; }
  const d = new Date(input);
  document.getElementById('dateToTsResult').innerHTML =
    '<b>秒:</b> ' + Math.floor(d.getTime()/1000) + '<br><b>毫秒:</b> ' + d.getTime() + '<br><b>ISO8601:</b> ' + d.toISOString();
}

