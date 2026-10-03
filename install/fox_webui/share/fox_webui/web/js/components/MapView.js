/* 地图视图：Canvas 画底图 + 机器人位姿 + 激光点 + 全局路径。
 *
 * 坐标换算（务必按此，否则机器人会上下镜像）：
 *     px = (x - origin_x) / resolution * scale
 *     py = canvas.height - (y - origin_y) / resolution * scale
 * PGM 第 0 行对应 y 最大处，所以 y 要翻转。
 */
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { UI, api, fmt } from '../shared.js'

export const MapView = {
  name: 'MapView',
  setup() {
    const canvasEl = ref(null)
    const meta = ref(null)
    const err = ref('')
    const cursor = ref(null)
    const clickPt = ref(null)
    // ⚠️ 地图只关心"当前这台机器"的 pose / scan / plan。
    //   邻居的 scan/plan **不在** SSE 里（后端紧凑版故意剔除，避免 10Hz 推大 payload），
    //   所以这里按机器单独拉 /api/state（本机直连、邻居走 /api/to/ 转发）。
    const state = ref({})
    let img = null
    let scale = 1
    let raf = null
    let lastDraw = 0
    let timer = null

    async function load() {
      try {
        err.value = ''
        const r = await fetch(api('/api/map'))
        const m = await r.json()
        if (!m.ok) { err.value = m.error || '地图不可用'; return }
        meta.value = m
        const im = new Image()
        im.src = api('/api/map.png') + '?t=' + Date.now()
        await im.decode()
        img = im
        resize()
        draw()
      } catch (e) {
        err.value = '地图加载失败: ' + e
      }
    }

    async function pullState() {
      try {
        // 用专用的轻量端点：只带 pose/scan/plan，不拖 health/modules/control 回来
        // （邻居那条路还要经 /api/to/ 转发，越轻越好）
        const r = await fetch(api('/api/map_state'))
        const s = await r.json()
        state.value = s
        // 把点数分享给状态卡：邻居的 scan/plan 不在 SSE 里，只有这里拿得到
        UI.mapN = { scan: s.scan?.n ?? 0, plan: s.plan?.n ?? 0 }
      } catch (e) { /* 忽略：保留上一帧 */ }
    }

    function resize() {
      const cv = canvasEl.value
      if (!cv || !meta.value) return
      const wrapW = Math.max(240, cv.parentElement.clientWidth - 2)
      const maxH = Math.min(560, Math.max(300, window.innerHeight * 0.56))
      const W = meta.value.width
      const H = meta.value.height
      scale = Math.min(wrapW / W, maxH / H)
      cv.width = Math.round(W * scale)
      cv.height = Math.round(H * scale)
      cv.style.width = cv.width + 'px'
      cv.style.height = cv.height + 'px'
    }

    function toPx(x, y) {
      const cv = canvasEl.value
      const m = meta.value
      return [
        (x - m.origin[0]) / m.resolution * scale,
        cv.height - (y - m.origin[1]) / m.resolution * scale,
      ]
    }

    function toWorld(px, py) {
      const cv = canvasEl.value
      const m = meta.value
      return [
        m.origin[0] + (px / scale) * m.resolution,
        m.origin[1] + ((cv.height - py) / scale) * m.resolution,
      ]
    }

    function draw() {
      const cv = canvasEl.value
      if (!cv || !img) return
      const ctx = cv.getContext('2d')
      ctx.clearRect(0, 0, cv.width, cv.height)
      ctx.imageSmoothingEnabled = false
      ctx.drawImage(img, 0, 0, cv.width, cv.height)

      const st = state.value || {}

      // 激光点
      const scan = st.scan?.points
      if (scan && scan.length) {
        ctx.fillStyle = 'rgba(255,90,90,0.9)'
        for (let i = 0; i < scan.length; i++) {
          const [px, py] = toPx(scan[i][0], scan[i][1])
          ctx.fillRect(px - 1, py - 1, 2, 2)
        }
      }

      // 全局路径
      const plan = st.plan?.points
      if (plan && plan.length > 1) {
        ctx.strokeStyle = '#2ecc71'
        ctx.lineWidth = 2
        ctx.beginPath()
        for (let i = 0; i < plan.length; i++) {
          const [px, py] = toPx(plan[i][0], plan[i][1])
          i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)
        }
        ctx.stroke()
      }

      // 点击选点
      if (clickPt.value) {
        const [px, py] = toPx(clickPt.value[0], clickPt.value[1])
        ctx.strokeStyle = '#ffd33d'
        ctx.lineWidth = 2
        ctx.beginPath(); ctx.arc(px, py, 7, 0, Math.PI * 2); ctx.stroke()
        ctx.beginPath(); ctx.moveTo(px - 11, py); ctx.lineTo(px + 11, py)
        ctx.moveTo(px, py - 11); ctx.lineTo(px, py + 11); ctx.stroke()
      }

      // 机器人（箭头方向 = 朝向）
      if (st.pose) {
        const [px, py] = toPx(st.pose.x, st.pose.y)
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(-(st.pose.yaw || 0))       // canvas y 向下 → 取负还原 CCW
        ctx.fillStyle = '#4ea1ff'
        ctx.strokeStyle = '#ffffff'
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(12, 0); ctx.lineTo(-8, 8); ctx.lineTo(-3, 0); ctx.lineTo(-8, -8)
        ctx.closePath()
        ctx.fill(); ctx.stroke()
        ctx.restore()
      }
    }

    function loop(t) {
      if (t - lastDraw > 200) {         // 5Hz 重绘足够，省 CPU
        lastDraw = t
        draw()
      }
      raf = requestAnimationFrame(loop)
    }

    function onMove(e) {
      const cv = canvasEl.value
      const r = cv.getBoundingClientRect()
      cursor.value = toWorld(e.clientX - r.left, e.clientY - r.top)
    }
    function onClick(e) {
      const cv = canvasEl.value
      const r = cv.getBoundingClientRect()
      const w = toWorld(e.clientX - r.left, e.clientY - r.top)
      clickPt.value = w
      UI.picked = w                 // 与导航面板共享
      console.log('[map] clicked world coords (m):', w)
    }

    /* ── 地图浮条上的快捷动作 ── */
    const actionMsg = ref('')
    async function post(path, body) {
      actionMsg.value = ''
      try {
        const r = await fetch(api(path), {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body || {}),
        })
        const j = await r.json().catch(() => ({}))
        actionMsg.value = j.ok ? '✓ 已发送' : ('⚠ ' + (j.error || j.detail || '失败'))
      } catch (err) {
        actionMsg.value = '⚠ ' + err
      }
    }
    const goHere = () => post('/api/nav/goal', { x: clickPt.value[0], y: clickPt.value[1], yaw: 0 })
    const setPoseHere = () => post('/api/initial_pose', { x: clickPt.value[0], y: clickPt.value[1], yaw: 0 })
    const clearPick = () => { clickPt.value = null; UI.picked = null; actionMsg.value = '' }
    function onResize() { resize(); draw() }

    onMounted(() => {
      load()
      pullState()
      timer = setInterval(pullState, 500)      // 2Hz：地图够用，且带上 scan/plan
      window.addEventListener('resize', onResize)
      raf = requestAnimationFrame(loop)
    })
    // 切机器 → 换底图、清掉上一台机选的点和提示（不同机器地图/坐标系可能不同）
    watch(() => UI.robot, () => {
      clickPt.value = null
      UI.picked = null
      actionMsg.value = ''
      UI.mapN = { scan: 0, plan: 0 }
      load()
      pullState()
    })
    onBeforeUnmount(() => {
      window.removeEventListener('resize', onResize)
      if (timer) clearInterval(timer)
      if (raf) cancelAnimationFrame(raf)
    })

    return { canvasEl, meta, err, cursor, clickPt, onMove, onClick, fmt,
             goHere, setPoseHere, clearPick, actionMsg }
  },
  template: `
  <section class="card span-2">
    <h2>🗺️ 地图
      <span class="tag" v-if="meta">{{ meta.width }}×{{ meta.height }} @ {{ meta.resolution }} m/px</span>
      <span class="tag" v-else>加载中…</span>
    </h2>
    <div class="map-wrap">
      <canvas ref="canvasEl" @mousemove="onMove" @mouseleave="cursor = null" @click="onClick"></canvas>
      <div class="map-overlay" v-if="cursor">({{ fmt(cursor[0], 2) }}, {{ fmt(cursor[1], 2) }}) m</div>
      <div class="map-actions" v-if="clickPt">
        <span class="mono">({{ fmt(clickPt[0], 2) }}, {{ fmt(clickPt[1], 2) }})</span>
        <button class="mini primary" @click="goHere">🚗 前往</button>
        <button class="mini" @click="setPoseHere">📍 设初始位姿</button>
        <button class="mini" @click="clearPick">✕</button>
        <span class="hint" v-if="actionMsg">{{ actionMsg }}</span>
      </div>
    </div>
    <p class="hint" v-if="err">⚠ {{ err }}</p>
    <p class="hint" v-else>
      <span class="dot-legend" style="background:#ff5a5a"></span>激光
      <span class="dot-legend" style="background:#2ecc71"></span>全局路径
      <span class="dot-legend" style="background:#4ea1ff"></span>机器人
      · 点击地图选目标点
    </p>
  </section>
  `
}
