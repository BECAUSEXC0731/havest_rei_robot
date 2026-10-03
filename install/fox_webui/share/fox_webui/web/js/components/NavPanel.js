/* 导航面板：航点一键前往 / 地图选点前往 / 取消 / 返航 / 设初始位姿
 *
 * 与 MapView 通过 shared.js 里的 UI.picked 共享"地图上选中的点"。
 */
import { ref, computed } from 'vue'
import { UI, cur, api, postJSON } from '../shared.js'

export const NavPanel = {
  name: 'NavPanel',
  setup() {
    const ctrl = computed(() => cur().control || {})
    const nav = computed(() => cur().nav || {})
    const waypoints = computed(() => ctrl.value.waypoints || [])
    const svcReady = computed(() => !!ctrl.value.services?.['navigate_to_pose'])
    const busy = ref(false)
    const msg = ref('')
    const msgOk = ref(true)
    const wpIndex = ref(0)
    const yaw = ref(0)

    async function call(path, body, okText) {
      busy.value = true
      msg.value = ''
      try {
        const r = await postJSON(api(path), body || {})     // 邻居机器 → 自动转发
        msgOk.value = !!(r && r.ok)
        if (msgOk.value) {
          msg.value = r.accepted === false ? ((r.error) || '未接受')
            : (okText || '已发送')
        } else {
          msg.value = (r && r.error) || '操作失败'
        }
      } finally {
        busy.value = false
      }
    }

    const goPicked = () => {
      if (!UI.picked) return
      call('/api/nav/goal', { x: UI.picked[0], y: UI.picked[1], yaw: yaw.value }, '导航目标已发送')
    }
    const setPose = () => {
      if (!UI.picked) return
      call('/api/initial_pose', { x: UI.picked[0], y: UI.picked[1], yaw: yaw.value }, '已设置初始位姿')
    }
    const goWp = () => {
      const w = waypoints.value[wpIndex.value]
      if (!w) return
      call('/api/nav/goal', { x: w.x, y: w.y, yaw: w.yaw }, `前往「${w.desc}」`)
    }
    const cancel = () => call('/api/nav/cancel', {}, '已请求取消导航')
    const goHome = () => call('/api/nav/home', {}, '已发送返航')

    return { UI, nav, waypoints, svcReady, busy, msg, msgOk, wpIndex, yaw,
             goPicked, setPose, goWp, cancel, goHome,
             fmt: (v, d = 2) => (v === null || v === undefined ? '–' : Number(v).toFixed(d)) }
  },
  template: `
  <section class="card">
    <h2>🧭 导航
      <span class="tag" v-if="!svcReady">Nav2 未就绪</span>
      <span class="tag" v-else-if="nav.active">导航中</span>
    </h2>

    <template v-if="UI.picked">
      <div class="kv small"><span>已选点</span>
        <b>{{ fmt(UI.picked[0]) }}, {{ fmt(UI.picked[1]) }} m</b></div>
      <div class="slider-row">
        <span>朝向</span>
        <input type="range" min="-3.14" max="3.14" step="0.05" v-model.number="yaw" />
        <b>{{ (yaw * 57.3).toFixed(0) }}</b><i>°</i>
      </div>
      <div class="row-btns">
        <button class="mini primary" :disabled="busy" @click="goPicked">🚗 前往此处</button>
        <button class="mini" :disabled="busy" @click="setPose">📍 设为初始位姿</button>
        <button class="mini" @click="UI.picked = null">✕ 清除</button>
      </div>
    </template>
    <p class="hint" v-else>在地图上点一下选目标点（可在「设初始位姿」里给定位）</p>

    <div class="divider"></div>
    <div class="sub">航点（来自 harvest_config.yaml）</div>
    <div class="coord-row">
      <select v-model.number="wpIndex" class="grow">
        <option v-for="(w, i) in waypoints" :key="w.id" :value="i">{{ w.desc }}</option>
      </select>
      <button class="mini primary" :disabled="busy || !waypoints.length" @click="goWp">前往</button>
    </div>

    <div class="row-btns">
      <button class="mini" :disabled="busy" @click="cancel">■ 取消导航</button>
      <button class="mini" :disabled="busy" @click="goHome">🏠 返回原点</button>
    </div>

    <p class="hint" v-if="nav.active">
      剩余 {{ fmt(nav.distance_remaining) }} m · 已用 {{ nav.navigation_time_s ?? '–' }} s ·
      恢复 {{ nav.recoveries ?? 0 }} 次
    </p>
    <p class="hint warn-text" v-if="msg && !msgOk">⚠ {{ msg }}</p>
    <p class="hint" v-else-if="msg">✓ {{ msg }}</p>
  </section>
  `
}
