/* 视频面板：彩色 / 深度伪彩 / 识别叠加 三源切换 + 检测结果列表。
 *
 * "按需订阅"体现在这里：<img src="/video/..."> 一挂上就建立 MJPEG 连接，
 * 切换源/关闭页面时浏览器断开连接，后端引用计数归零 → 立刻退订、停止编码。
 * 可用 /api/health 的 video_viewers 验证（无观看者时应全为 0）。
 */
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { UI, cur, api, videoSrc, postJSON, getJSON, fmt } from '../shared.js'

const REACH_NAME = { 0: '可抓', 1: '临界', 2: '不可达' }
const REACH_CLS = { 0: 'good', 1: 'warn', 2: 'bad' }

export const VideoPanel = {
  name: 'VideoPanel',
  setup() {
    const src = ref('color')
    const boot = ref(Date.now())
    const dets = ref([])
    const detEnabled = ref(false)
    const busy = ref(false)
    let timer = null

    // 切机器时重置视频地址（邻居 → 直连对方的 :8080/video/…；见 shared.js videoSrc）
    const url = computed(() => videoSrc(src.value) + '?t=' + boot.value)
    const det = computed(() => cur().detector || {})

    function setSrc(v) { src.value = v; boot.value = Date.now() }

    watch(() => UI.robot, () => { boot.value = Date.now(); dets.value = []; pollDets() })

    async function toggleDet() {
      busy.value = true
      const r = await postJSON(api('/api/detector'), { enable: !detEnabled.value })
      if (r && r.status) detEnabled.value = !!r.status.active
      busy.value = false
    }

    async function pollDets() {
      // ⚠️ 每次轮询都以服务端状态为准（不能只在"本页点过开启"时才拉）：
      //    否则页面刷新后、或从另一台设备开启识别时，本页的检测列表永远不出现，
      //    「🎯 抓取」按钮就够不着了（实测踩过）。
      try {
        const j = await getJSON(api('/api/detections'))
        detEnabled.value = !!j.enabled
        const want = detEnabled.value || src.value === 'detect'
        dets.value = want ? (j.detections || []) : []
      } catch (e) { /* 网络抖动忽略 */ }
    }

    watch(src, () => { if (src.value === 'detect') detEnabled.value = true })

    /* ── 单颗抓取：把检测框的机器人系坐标发给 harvest_node ── */
    const pickBusy = ref(null)
    const pickMsg = ref('')
    const pickOk = ref(true)

    async function pickOne(d) {
      const pos = d.robot_mm
      if (!pos) { pickMsg.value = '该目标没有有效 3D 坐标（深度无效）'; pickOk.value = false; return }
      if (!confirm(`抓取这一颗？\n\n机器人系坐标 (${pos.map((v) => v.toFixed(0)).join(', ')}) mm\n`
                   + '动作序列（与 grape_grasp_test 相同）：\n'
                   + '  过渡点 → 抓取点 → 夹紧 → 回安全点 → 松开\n'
                   + '需要 arm 与 gripper 模块已启动；请确认机械臂周围无障碍。')) return
      pickBusy.value = d.id
      pickMsg.value = '抓取中…（过渡点 → 抓取点 → 夹紧 → 回安全点 → 松开）'
      try {
        const r = await postJSON(api('/api/task/pick_one'), { x: pos[0], y: pos[1], z: pos[2] })
        pickOk.value = !!(r && r.ok)
        if (pickOk.value) {
          const steps = (r.steps || []).map((s) => s.name).join(' → ')
          pickMsg.value = `${r.message || '完成'}｜${steps}`
        } else {
          const bad = (r && r.steps || []).filter((s) => !s.ok)
            .map((s) => `${s.name}(${s.detail})`).join('; ')
          pickMsg.value = ((r && r.error) || '抓取失败') + (bad ? `｜失败步骤: ${bad}` : '')
        }
      } catch (err) {
        pickOk.value = false
        pickMsg.value = '请求异常：' + err
      } finally {
        pickBusy.value = null
      }
    }

    onMounted(() => { timer = setInterval(pollDets, 500) })
    onBeforeUnmount(() => { if (timer) clearInterval(timer); detEnabled.value = false })

    return { src, url, setSrc, dets, detEnabled, det, toggleDet, busy,
             REACH_NAME, REACH_CLS, fmt, pickOne, pickBusy, pickMsg, pickOk }
  },
  template: `
  <section class="card">
    <h2>🎥 视频
      <select :value="src" @change="setSrc($event.target.value)">
        <option value="color">彩色</option>
        <option value="depth">深度（伪彩）</option>
        <option value="detect">识别叠加</option>
      </select>
      <button class="mini" :disabled="busy" @click="toggleDet">
        {{ detEnabled ? '关闭识别' : '开启识别' }}
      </button>
    </h2>
    <div class="video-wrap">
      <img :src="url" alt="camera stream" />
    </div>
    <div class="kv small"><span>识别状态</span>
      <b>{{ det.active ? '运行中' : '未启用' }} · {{ det.mode || '-' }} · {{ det.detections ?? 0 }} 目标</b>
    </div>
    <p class="hint" v-if="det.error">⚠ {{ det.error }}</p>
    <p class="hint" v-if="!det.active">
      点"开启识别"（或在上面选"识别叠加"）才会启动 3Hz 检测 —— 平时不占用 CPU/GPU。
    </p>

    <template v-if="dets.length">
      <div class="sub">检测结果（{{ dets.length }}）</div>
      <ul class="dets">
        <li v-for="d in dets" :key="d.id">
          <span class="pill" :class="REACH_CLS[d.reach]">{{ REACH_NAME[d.reach] }}</span>
          <span class="mono">X{{ d.robot_mm ? fmt(d.robot_mm[0], 0) : '–' }}
            Y{{ d.robot_mm ? fmt(d.robot_mm[1], 0) : '–' }}
            Z{{ d.robot_mm ? fmt(d.robot_mm[2], 0) : '–' }} mm</span>
          <span class="muted">深度 {{ fmt(d.depth_m, 2) }} m · 置信 {{ fmt(d.conf, 2) }}</span>
          <button class="mini" :disabled="pickBusy === d.id || d.reach === 2"
                  :title="d.reach === 2 ? '超出工作空间，需先移动底盘' : '抓这一颗'"
                  @click="pickOne(d)">🎯 抓取</button>
        </li>
      </ul>
      <p class="hint warn-text" v-if="pickMsg && !pickOk">⚠ {{ pickMsg }}</p>
      <p class="hint" v-else-if="pickMsg">✓ {{ pickMsg }}</p>
    </template>
  </section>
  `
}
