// generator.js — UUID, password, QR code, Lorem Ipsum, sequence, random data
// ============================================================
// 8. GENERATOR PAGE
// ============================================================
let genCurrentOp = 'uuid';

function initGeneratorPage() {
  document.querySelectorAll('#genOpBtns .op-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('#genOpBtns .op-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      genCurrentOp = btn.dataset.op;
      updateGenConfig();
    };
  });
  updateGenConfig();
}

function updateGenConfig() {
  const cfg = document.getElementById('genConfig');
  const titles = {uuid:'UUID 生成', password:'随机密码', qrcode:'二维码生成', lorem:'Lorem Ipsum', sequence:'数字序列', randomdata:'随机数据'};
  document.getElementById('genResultTitle').textContent = titles[genCurrentOp] || '生成器';
  switch (genCurrentOp) {
    case 'uuid':
      cfg.innerHTML = '<label class="form-label">版本</label><select class="format-select" id="uuidVersion"><option value="4">UUID v4 (随机)</option><option value="1">UUID v1 (时间戳)</option></select><label class="form-label">数量</label><input type="number" class="num-input" id="uuidCount" value="5" min="1" max="100">';
      break;
    case 'password':
      cfg.innerHTML = '<label class="form-label">长度</label><input type="number" class="num-input" id="pwdLen" value="16" min="4" max="128"><label class="form-label">数量</label><input type="number" class="num-input" id="pwdCount" value="5" min="1" max="50"><div class="row"><label class="checkbox-label"><input type="checkbox" id="pwdUpper" checked> 大写字母</label><label class="checkbox-label"><input type="checkbox" id="pwdLower" checked> 小写字母</label><label class="checkbox-label"><input type="checkbox" id="pwdDigits" checked> 数字</label><label class="checkbox-label"><input type="checkbox" id="pwdSymbols"> 特殊字符</label></div>';
      break;
    case 'qrcode':
      cfg.innerHTML = '<label class="form-label">内容 (文本或URL)</label><input type="text" class="expr-input" id="qrContent" value="https://www.example.com" style="width:100%"><label class="form-label">尺寸 (px)</label><input type="number" class="num-input" id="qrSize" value="200" min="100" max="600">';
      break;
    case 'lorem':
      cfg.innerHTML = '<label class="form-label">类型</label><select class="format-select" id="loremType"><option value="paragraphs">段落</option><option value="sentences">句子</option><option value="words">单词</option></select><label class="form-label">数量</label><input type="number" class="num-input" id="loremCount" value="3" min="1" max="100">';
      break;
    case 'sequence':
      cfg.innerHTML = '<label class="form-label">起始值</label><input type="number" class="num-input" id="seqStart" value="1"><label class="form-label">结束值</label><input type="number" class="num-input" id="seqEnd" value="100"><label class="form-label">步长</label><input type="number" class="num-input" id="seqStep" value="1" min="1">';
      break;
    case 'randomdata':
      cfg.innerHTML = '<label class="form-label">数据类型</label><select class="format-select" id="rdType"><option value="name">中文姓名</option><option value="email">邮箱</option><option value="phone">手机号</option><option value="idcard">身份证号</option><option value="address">地址</option></select><label class="form-label">数量</label><input type="number" class="num-input" id="rdCount" value="10" min="1" max="100">';
      break;
  }
}

function runGenOp() {
  const el = document.getElementById('genResult');
  try {
    let result = '';
    switch (genCurrentOp) {
      case 'uuid':
        const ver = document.getElementById('uuidVersion')?.value;
        const cnt = parseInt(document.getElementById('uuidCount')?.value) || 5;
        if (ver === '1') { for (let i = 0; i < cnt; i++) result += uuidV1() + NL; }
        else { for (let i = 0; i < cnt; i++) result += crypto.randomUUID() + NL; }
        el.innerHTML = '<pre style="margin:0;white-space:pre-wrap">' + escHtml(result) + '</pre>';
        break;
      case 'password':
        const plen = parseInt(document.getElementById('pwdLen')?.value) || 16;
        const pcnt = parseInt(document.getElementById('pwdCount')?.value) || 5;
        let chars = '';
        if (document.getElementById('pwdUpper')?.checked) chars += 'ABCDEFGHJKLMNPQRSTUVWXYZ';
        if (document.getElementById('pwdLower')?.checked) chars += 'abcdefghjkmnpqrstuvwxyz';
        if (document.getElementById('pwdDigits')?.checked) chars += '23456789';
        if (document.getElementById('pwdSymbols')?.checked) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';
        if (!chars) chars = 'abcdefghjkmnpqrstuvwxyz23456789';
        const pwdArr = new Uint32Array(plen);
        for (let j = 0; j < pcnt; j++) {
          crypto.getRandomValues(pwdArr);
          result += Array.from(pwdArr, n => chars[n % chars.length]).join('') + NL;
        }
        el.innerHTML = '<pre style="margin:0;white-space:pre-wrap">' + escHtml(result) + '</pre>';
        break;
      case 'qrcode':
        const qrContent = document.getElementById('qrContent')?.value || '';
        const qrSize = parseInt(document.getElementById('qrSize')?.value) || 200;
        if (!qrContent) { el.innerHTML = '请输入二维码内容'; return; }
        el.innerHTML = '<div class="qr-container">生成中...</div>';
        const qrUrl = 'https://api.qrserver.com/v1/create-qr-code/?size=' + qrSize + 'x' + qrSize + '&data=' + encodeURIComponent(qrContent);
        el.innerHTML = '<div class="qr-container"><img src="' + qrUrl + '" alt="QR Code" style="max-width:100%"><span style="font-size:11px;color:var(--text-secondary)">' + escHtml(qrContent) + '</span><a href="' + qrUrl + '" download="qrcode.png" class="btn btn-sm">下载 PNG</a></div>';
        toast('生成完成');
        return;
      case 'lorem':
        const ltype = document.getElementById('loremType')?.value || 'paragraphs';
        const lcnt = parseInt(document.getElementById('loremCount')?.value) || 3;
        const loremWords = ['lorem','ipsum','dolor','sit','amet','consectetur','adipiscing','elit','sed','do','eiusmod','tempor','incididunt','ut','labore','et','dolore','magna','aliqua','enim','ad','minim','veniam','quis','nostrud','exercitation','ullamco','laboris','nisi','ut','aliquip','ex','ea','commodo','consequat','duis','aute','irure','dolor','in','reprehenderit','voluptate','velit','esse','cillum','fugiat','nulla','pariatur','excepteur','sint','occaecat','cupidatat','non','proident','sunt','culpa','qui','officia','deserunt','mollit','anim','id','est','laborum'];
        if (ltype === 'words') { for (let i = 0; i < lcnt; i++) result += loremWords[i % loremWords.length] + ' '; }
        else if (ltype === 'sentences') { for (let i = 0; i < lcnt; i++) { let s = ''; for (let j = 0; j < 8 + Math.floor(Math.random() * 12); j++) s += loremWords[Math.floor(Math.random() * loremWords.length)] + ' '; result += s.charAt(0).toUpperCase() + s.slice(1).trim() + '. '; } }
        else { for (let i = 0; i < lcnt; i++) { let p = ''; for (let j = 0; j < 4 + Math.floor(Math.random() * 6); j++) { let s = ''; for (let k = 0; k < 6 + Math.floor(Math.random() * 10); k++) s += loremWords[Math.floor(Math.random() * loremWords.length)] + ' '; p += s.charAt(0).toUpperCase() + s.slice(1).trim() + '. '; } result += p.trim() + NL + NL; } }
        el.innerHTML = '<pre style="margin:0;white-space:pre-wrap">' + escHtml(result) + '</pre>';
        break;
      case 'sequence':
        const start = parseInt(document.getElementById('seqStart')?.value) || 1;
        const end = parseInt(document.getElementById('seqEnd')?.value) || 100;
        const step = parseInt(document.getElementById('seqStep')?.value) || 1;
        const nums = [];
        for (let i = start; i <= end; i += step) nums.push(i);
        result = nums.join(NL);
        el.innerHTML = '<pre style="margin:0;white-space:pre-wrap">' + escHtml(result) + '</pre>';
        break;
      case 'randomdata':
        const rdType = document.getElementById('rdType')?.value || 'name';
        const rdcnt = parseInt(document.getElementById('rdCount')?.value) || 10;
        result = generateRandomData(rdType, rdcnt);
        el.innerHTML = '<pre style="margin:0;white-space:pre-wrap">' + escHtml(result) + '</pre>';
        break;
    }
    toast('生成完成');
  } catch (e) {
    el.innerHTML = '❌ 错误: ' + escHtml(e.message);
    toast('生成失败','error');
  }
}

function copyGenResult() { copyTextById('genResult'); }

function uuidV1() {
  const now = Date.now();
  return 'xxxxxxxx-xxxx-1xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (now + Math.random() * 16) % 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

function generateRandomData(type, count) {
  const surnames = ['张','王','李','赵','陈','杨','黄','周','吴','徐','孙','马','胡','朱','郭','何','罗','高','林','郑','梁'];
  const names = ['伟','芳','秀英','敏','静','丽','强','磊','洋','勇','艳','杰','娟','涛','明','超','秀兰','霞','平','刚','桂英'];
  const cities = ['北京','上海','广州','深圳','杭州','成都','武汉','南京','西安','重庆','苏州','天津','长沙','郑州','东莞','青岛','合肥','佛山','宁波','昆明'];
  const streets = ['中山路','人民路','建设路','解放路','文化路','和平路','新华路','长江路','黄河路','长城路'];
  const emails = ['@qq.com','@163.com','@gmail.com','@outlook.com','@sina.com','@126.com'];
  let result = '';
  for (let i = 0; i < count; i++) {
    switch (type) {
      case 'name': result += surnames[Math.floor(Math.random()*surnames.length)] + names[Math.floor(Math.random()*names.length)] + (Math.random()>0.5?names[Math.floor(Math.random()*names.length)]:'') + NL; break;
      case 'email': result += Math.random().toString(36).substring(2,8) + emails[Math.floor(Math.random()*emails.length)] + NL; break;
      case 'phone': result += '1' + ['3','5','7','8'][Math.floor(Math.random()*4)] + Math.random().toString().slice(2,11) + NL; break;
      case 'idcard': result += Math.floor(110000+Math.random()*330000) + (1970+Math.floor(Math.random()*40)).toString() + String(Math.floor(Math.random()*12)+1).padStart(2,'0') + String(Math.floor(Math.random()*28)+1).padStart(2,'0') + String(Math.floor(Math.random()*1000)).padStart(3,'0') + NL; break;
      case 'address': result += cities[Math.floor(Math.random()*cities.length)] + '市' + ['朝阳区','海淀区','浦东新区','天河区','西湖区','武侯区'][Math.floor(Math.random()*6)] + streets[Math.floor(Math.random()*streets.length)] + Math.floor(Math.random()*300+1) + '号' + NL; break;
    }
  }
  return result.trim();
}

