/* FOX WebUI · S1 只读状态面板
   无框架、无构建：SSE 收状态 → 直接更新 DOM。 */

const $ = (id) => document.getElementById(id);

const LEVEL_NAME = { 10: 'DEBUG', 20: 'INFO', 30: 'WARN', 40: 'ERROR', 50: 'FATAL' };
const LEVEL_CLASS = { 10: 'lv-d', 20: 'lv-i', 30: 'lv-w', 40: 'lv-e', 50: 'lv-f' };

let lastLogId = 0;

/* ────────── 工具 ────────── */
function fmt(v, digits = 2) {
  if (v === null || v === undefined || Number.isNaN(v)) return '–';
  return Number(v).toFixed(digits);
}
function setText(id, txt) {
  const el = $(id);
  if (el && el.textContent !== String(txt)) el.textContent = txt;
}
function listText(arr) {
  if (!arr || !arr.length) return '–';
  return Array.isArray(arr) ? arr.join(' / ') : String(arr);
}

/* ────────── 状态渲染 ────────── */
function render(s) {
  // 顶部
  setText('robotName', (s.robot && s.robot.name) || 'fox');
  const online = s.robot && s.robot.online;
  $('connDot').classList.toggle('ok', !!online);
  $('connDot').classList.toggle('bad', !online);
  setText('connText', online ? '机器人在线' : '机器人离线/无底盘数据');
  if (s.ts) setText('lastUpdate', new Date(s.ts * 1000).toLocaleTimeString());

  // 定位
  if (s.pose) {
    setText('poseX', fmt(s.pose.x, 3));
    setText('poseY', fmt(s.pose.y, 3));
    setText('poseYaw', fmt(s.pose.yaw_deg, 1));
    setText('poseSrc', s.pose.src === 'tf' ? 'TF map→base_footprint' : '/lidar_loc_pose');
    setText('poseHint', '');
  } else {
    setText('poseSrc', '无定位');
    setText('poseHint', '⚠ 尚未定位：请在 RViz 用 2D Pose Estimate 给一次初始位姿（lidar_loc 与 AMCL 相同要求）');
  }

  // 速度
  const t = s.twist || {};
  setText('odomVx', fmt(t.vx)); setText('odomVy', fmt(t.vy)); setText('odomVth', fmt(t.vth));
  const c = s.cmd_vel || {};
  setText('cmdVx', fmt(c.vx)); setText('cmdVth', fmt(c.vth));

  // 电池
  if (s.battery) {
    const v = s.battery.voltage;
    setText('battV', fmt(v, 2));
    setText('battState', s.battery.charging ? '充电中 ⚡' : '放电中');
    const pct = Math.max(0, Math.min(100, ((v - 18) / (25.2 - 18)) * 100));
    const bar = $('battBar');
    bar.style.width = pct.toFixed(0) + '%';
    bar.className = 'bar-fill ' + (v < 20 ? 'danger' : v < 22 ? 'warn' : 'good');
  }

  // 机械臂
  if (s.arm) {
    setText('armX', fmt(s.arm.x, 1));
    setText('armY', fmt(s.arm.y, 1));
    setText('armZ', fmt(s.arm.z, 1));
    setText('armRoll', fmt(s.arm.roll, 1));
    setText('armPitch', fmt(s.arm.pitch, 1));
    setText('armYaw', fmt(s.arm.yaw, 1));
  }

  // 夹爪
  if (s.gripper) {
    const r = s.gripper.ratio;
    const name = r > 0.75 ? '松开（张开）' : r < 0.25 ? '抓紧（闭合）' : '中间位置';
    setText('gripState', name);
    setText('gripRatio', Math.round(r * 100));
    setText('gripPulse', s.gripper.pulse);
    $('gripBar').style.width = (r * 100).toFixed(0) + '%';
  } else {
    setText('gripState', '无数据（/gripper/state 未发布）');
  }

  // 底盘状态
  if (s.chassis) {
    setText('motors', listText(s.chassis.motor_speed));
    setText('crash', listText(s.chassis.crash));
    setText('cliff', listText(s.chassis.cliff));
    setText('smoke', s.chassis.smoke);
    setText('ultra', listText(s.chassis.ultrasound));
  }

  renderHealth(s.health || {});
}

function renderHealth(health) {
  const keys = Object.keys(health).sort();
  if (!keys.length) return;
  const rows = keys.map((k) => {
    const h = health[k];
    const state = h.online
      ? '<span class="pill good">在线</span>'
      : (h.count ? '<span class="pill bad">掉线</span>' : '<span class="pill mute">无数据</span>');
    const hz = h.static
      ? (h.count ? '静态/锁存' : '–')
      : (h.online ? fmt(h.hz, 1) + ' Hz' : '–');
    const age = h.age === null ? '–' : fmt(h.age, 1) + ' s';
    return `<tr><td class="mono">${k}</td><td>${state}</td><td>${hz}</td><td>${age}</td></tr>`;
  }).join('');
  const body = $('healthBody');
  if (body.dataset.sig !== keys.join(',')) {          // 只在集合变化时重建表格
    body.dataset.sig = keys.join(',');
    body.innerHTML = rows;
  } else {
    body.innerHTML = rows;                            // 频率/延迟需要持续更新
  }
}

/* ────────── 日志 ────────── */
function levelOk(level) {
  return level >= parseInt($('logLevel').value, 10);
}
function appendLogs(entries) {
  const box = $('logs');
  let added = 0;
  for (const e of entries) {
    if (!levelOk(e.level)) continue;
    const div = document.createElement('div');
    div.className = 'log-line ' + (LEVEL_CLASS[e.level] || '');
    const ts = new Date(e.t * 1000).toLocaleTimeString();
    div.innerHTML = `<span class="mono t">${ts}</span>` +
                    `<span class="mono lv">${LEVEL_NAME[e.level] || e.level}</span>` +
                    `<span class="mono nm">${e.name}</span> ` +
                    `<span class="msg"></span>`;
    div.querySelector('.msg').textContent = e.msg;
    box.appendChild(div);
    added++;
  }
  if (added) {
    while (box.childElementCount > 500) box.removeChild(box.firstChild);
    if ($('logAuto').checked) box.scrollTop = box.scrollHeight;
  }
}
async function pollLogs() {
  try {
    const r = await fetch(`/api/logs?since=${lastLogId}&limit=300`);
    const j = await r.json();
    if (j.logs && j.logs.length) {
      lastLogId = j.logs[j.logs.length - 1].id;
      appendLogs(j.logs);
    }
  } catch (e) { /* 网络抖动忽略 */ }
}

/* ────────── SSE 连接 ────────── */
let es = null;
function connect() {
  es = new EventSource('/api/stream');
  es.onopen = () => { $('connDot').classList.remove('bad'); };
  es.onmessage = (ev) => {
    try { render(JSON.parse(ev.data)); } catch (e) { console.warn('bad payload', e); }
  };
  es.onerror = () => {
    $('connDot').classList.remove('ok');
    $('connDot').classList.add('bad');
    setText('connText', '后端连接中断，重连中…');
    // EventSource 会自行重连；这里无需手动处理
  };
}

/* ────────── 启动 ────────── */
connect();
setInterval(pollLogs, 1000);
pollLogs();

$('logLevel').addEventListener('change', () => { $('logs').innerHTML = ''; lastLogId = 0; pollLogs(); });
$('logClear').addEventListener('click', () => { $('logs').innerHTML = ''; });
