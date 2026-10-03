/* 机械臂 + 夹爪控制面板（含状态显示）
 *
 * 安全：
 *  - 工作空间越界由后端拦截，这里只做输入提示；
 *  - 「解锁电机」「设零点」属于危险动作 → 弹确认框 + 传 confirm=true。
 */
import { ref, computed } from 'vue'
import { cur, api, postJSON } from '../shared.js'

export const ArmPanel = {
  name: 'ArmPanel',
  setup() {
    const arm = computed(() => cur().arm || null)
    const grip = computed(() => cur().gripper || null)
    const ws = computed(() => cur().control?.workspace || {})
    const svc = computed(() => cur().control?.services || {})
    const busy = ref(false)
    const msg = ref('')
    const msgOk = ref(true)

    const form = ref({ x: 200, y: 0, z: 130 })
    const lastSync = ref(0)

    // 位置输入框跟随实际值（用户没在编辑时）
    function syncFromRobot(retry = 0) {
      if (arm.value) {
        form.value = { x: Math.round(arm.value.x), y: Math.round(arm.value.y),
                       z: Math.round(arm.value.z) }
      } else if (retry < 10) {
        lastSync.value = window.setTimeout(() => syncFromRobot(retry + 1), 1000)
      }
    }
    syncFromRobot()

    async function call(path, body, okText) {
      busy.value = true
      msg.value = ''
      try {
        // api() 会在"看着邻居机器"时把请求转给那台机的 Agent（模式 C）
        const r = await postJSON(api(path), body || {})
        msgOk.value = !!(r && r.ok)
        msg.value = msgOk.value ? (okText || '已完成') : ((r && r.error) || '操作失败')
      } finally {
        busy.value = false
      }
    }

    const goto = () => call('/api/arm/goto', { x: +form.value.x, y: +form.value.y, z: +form.value.z }, '已发送绝对移动')
    const home = () => call('/api/arm/home', {}, '已回安全位')
    const jog = (dx, dy, dz) => call('/api/arm/relative', { dx, dy, dz }, '已发送微调')
    const unlock = () => {
      if (!confirm('⚠️ 解锁电机：机械臂将失去保持力，可能因重力下垂。\n确认执行？')) return
      call('/api/arm/unlock', { confirm: true }, '已解锁（可手动扳动）')
    }
    const setZero = () => {
      if (!confirm('⚠️ 设零点：会把机械臂【当前位姿】记录为零点，\n之后所有绝对坐标都会因此偏移。\n确认执行？')) return
      call('/api/arm/set_zero', { confirm: true }, '已设零点')
    }
    const gripClose = () => call('/api/gripper', { close: true }, '已发送：抓紧')
    const gripOpen = () => call('/api/gripper', { close: false }, '已发送：松开')

    const gripName = computed(() => {
      const r = grip.value?.ratio
      if (r === undefined || r === null) return '–'
      return r > 0.75 ? '松开（张开）' : r < 0.25 ? '抓紧（闭合）' : '中间位置'
    })

    return { arm, grip, ws, svc, form, busy, msg, msgOk,
             goto, home, jog, unlock, setZero, gripClose, gripOpen, gripName,
             fmt: (v, d = 1) => (v === null || v === undefined ? '–' : Number(v).toFixed(d)) }
  },
  template: `
  <section class="card">
    <h2>🦾 机械臂
      <span class="tag" v-if="!svc['goto_position']">服务未就绪</span>
    </h2>

    <div class="kv small"><span>当前位置</span>
      <b>{{ fmt(arm?.x) }} / {{ fmt(arm?.y) }} / {{ fmt(arm?.z) }} mm</b>
    </div>
    <div class="kv small"><span>姿态</span>
      <b>R {{ fmt(arm?.roll, 1) }} / P {{ fmt(arm?.pitch, 1) }} / Y {{ fmt(arm?.yaw, 1) }} °</b>
    </div>

    <div class="coord-row">
      <label>X<input type="number" v-model.number="form.x" /></label>
      <label>Y<input type="number" v-model.number="form.y" /></label>
      <label>Z<input type="number" v-model.number="form.z" /></label>
      <button class="mini primary" :disabled="busy" @click="goto">前往</button>
    </div>

    <div class="sub">微调（mm）</div>
    <div class="row-btns">
      <button class="mini" :disabled="busy" @click="jog(-10,0,0)">X −10</button>
      <button class="mini" :disabled="busy" @click="jog(10,0,0)">X +10</button>
      <button class="mini" :disabled="busy" @click="jog(0,-10,0)">Y −10</button>
      <button class="mini" :disabled="busy" @click="jog(0,10,0)">Y +10</button>
      <button class="mini" :disabled="busy" @click="jog(0,0,-10)">Z −10</button>
      <button class="mini" :disabled="busy" @click="jog(0,0,10)">Z +10</button>
    </div>

    <div class="row-btns">
      <button class="mini" :disabled="busy" @click="home">🏠 回安全位</button>
      <button class="mini danger" :disabled="busy" @click="unlock">⚠ 解锁电机</button>
      <button class="mini danger" :disabled="busy" @click="setZero">⚠ 设零点</button>
    </div>
    <p class="hint">工作空间 X[{{ ws.x_min }}~{{ ws.x_max }}] Y[{{ ws.y_min }}~{{ ws.y_max }}]
      Z[{{ ws.z_min }}~{{ ws.z_max }}]（越界会被拒绝）</p>

    <!-- ── 夹爪 ── -->
    <div class="divider"></div>
    <h2>🤏 夹爪</h2>
    <div class="kv"><span>状态</span><b>{{ gripName }}</b></div>
    <div class="bar"><div class="bar-fill grip"
      :style="{width: ((grip?.ratio ?? 0) * 100).toFixed(0) + '%'}"></div></div>
    <div class="kv small"><span>脉宽</span><b>{{ grip?.pulse ?? '–' }}</b></div>
    <div class="row-btns">
      <button class="mini primary" :disabled="busy" @click="gripClose">✅ 抓紧</button>
      <button class="mini" :disabled="busy" @click="gripOpen">✖ 松开</button>
    </div>
    <p class="hint">2000 = 抓紧（闭合） / 500 = 松开（张开）· 动作约 1.5s</p>
    <p class="hint" v-if="msg" :class="msgOk ? '' : 'warn-text'">{{ msgOk ? '✓ ' : '⚠ ' }}{{ msg }}</p>
  </section>
  `
}
