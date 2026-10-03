/* 共享状态与工具：SSE 连接、格式化、REST 调用、多机（模式 C）机器切换。
   用 Vue 的 reactive 做"一个状态源"，所有组件从它取数据。 */
import { reactive } from 'vue'

export const S = reactive({
  data: {},           // /api/state 快照（含 robots: {名字: 紧凑快照}）
  connected: false,   // SSE 是否连着
  err: '',
  updatedAt: 0,
})

/** 跨组件的 UI 临时状态（如地图上选中的点，供导航面板/地图浮条共用）。 */
export const UI = reactive({
  picked: null,       // [x, y] 地图上选中的世界坐标（米）
  robot: '',          // 当前查看的机器名；空 = 本机（多机 · 模式 C）
  // 当前机器的激光/路径点数：由 MapView（它那条 /api/map_state 里带着）填充，
  // 供状态卡显示 —— 邻居的 scan/plan 不在 SSE 里，只有地图那条路拿得到。
  mapN: { scan: 0, plan: 0 },
})

/* ────────────────────────── 多机（模式 C 对称 HTTP 聚合）──────────────────────────
 *
 * 每台机都跑一个 Agent，并在 `peers` 里列出其他机器；各机之间用 HTTP 互拉状态。
 * 于是**任意一台的 :8080 打开都能看到全部机器**。前端只需记住"当前选的机器"：
 *
 *   cur()      取当前机器的那一份数据（本机 = 快照顶层；邻居 = S.data.robots[name]）
 *   api(path)  拼出接口路径（本机 = 原样；邻居 = /api/to/<名字>+path，由本机 Agent 转发）
 *   videoSrc() 视频地址（本机相对；邻居用它的 base URL 直连，<img> 无跨域限制）
 *
 * 所有面板统一走这三个函数，就不用各自判断机器了（详见 docs/WebUI_技术文档.md §7.4）。
 */

/** 本机名字（来自快照）。 */
export const meName = () => S.data?.robot?.name || ''

/** 当前选中的机器名（空 → 本机）。 */
export const curName = () => UI.robot || meName()

/** 是否正在看本机。 */
export const isMe = () => {
  const me = meName()
  return !UI.robot || UI.robot === me
}

/** 当前机器的那一份数据（本机 = 顶层，向后兼容；邻居 = robots[name]）。 */
export function cur() {
  if (isMe()) return S.data || {}
  return S.data?.robots?.[UI.robot] || {}
}

/** 接口路径：本机原样；邻居 → `/api/to/<名字><path>`（本机 Agent 单跳转发）。 */
export function api(path) {
  return isMe() ? path : '/api/to/' + encodeURIComponent(curName()) + path
}

/** 视频地址：本机相对路径；邻居用它的 base URL 直连（不需要本机反代）。 */
export function videoSrc(src) {
  if (isMe()) return '/video/' + src
  const base = (S.data?.robots?.[UI.robot]?.url || '').replace(/\/+$/, '')
  return base ? base + '/video/' + src : '/video/' + src
}

/** 机器列表（顶栏下拉用）：本机在前、其余按名字。 */
export function robotsList() {
  const rs = S.data?.robots || {}
  const me = meName()
  const names = Object.keys(rs).sort((a, b) => (a === me ? -1 : b === me ? 1 : a.localeCompare(b)))
  return names.map((k) => ({ name: k, ...rs[k], is_me: k === me }))
}

/** 建立 SSE 长连接（10Hz 全量状态），断线自动重连（EventSource 内建）。 */
export function startSSE() {
  const es = new EventSource('/api/stream')
  es.onopen = () => { S.connected = true; S.err = '' }
  es.onmessage = (ev) => {
    try {
      S.data = JSON.parse(ev.data)
      S.updatedAt = Date.now()
      S.connected = true
    } catch (e) { S.err = 'bad payload: ' + e }
  }
  es.onerror = () => { S.connected = false; S.err = 'SSE 断开，重连中…' }
  return es
}

/* ── 格式化 ── */
export const fmt = (v, d = 2) =>
  (v === null || v === undefined || Number.isNaN(v)) ? '–' : Number(v).toFixed(d)

export const fmtList = (arr) =>
  (!arr || !arr.length) ? '–' : arr.join(' / ')

export const clock = (ts) => ts ? new Date(ts * 1000).toLocaleTimeString() : '–'

/* ── 健康着色 ── */
export function healthClass(h) {
  if (!h) return 'mute'
  if (h.online) return 'good'
  return h.count ? 'bad' : 'mute'
}
export function healthText(h) {
  if (!h) return '–'
  if (h.online) return '在线'
  return h.count ? '掉线' : '无数据'
}

/* ── REST ── */
export async function postJSON(path, body = {}) {
  const r = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const t = await r.text()
  try {
    return JSON.parse(t)
  } catch (e) {
    // 不要只报 'bad json'：带上片段，否则界面上一片静默、后端其实已经生效了
    return { ok: false, error: `响应不是 JSON (HTTP ${r.status}): ${t.slice(0, 80)}` }
  }
}
export async function getJSON(path) {
  const r = await fetch(path)
  return await r.json()
}

/* ── 日志级别 ── */
export const LEVEL_NAME = { 10: 'DEBUG', 20: 'INFO', 30: 'WARN', 40: 'ERROR', 50: 'FATAL' }
export const LEVEL_CLASS = { 10: 'lv-d', 20: 'lv-i', 30: 'lv-w', 40: 'lv-e', 50: 'lv-f' }
