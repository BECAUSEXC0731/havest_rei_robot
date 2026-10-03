/* 模块启停面板（白名单）：每个模块一行 —— 状态灯 / 启停按钮 / 就绪频率 / 日志
 *
 * 安全：
 *  - 前端**只发模块名**，命令永远来自后端 config/modules.yaml；
 *  - confirm=true 的模块（底盘/机械臂，上电可能动）点击时二次确认；
 *  - 依赖未满足时后端会拒绝并返回缺失列表，这里直接显示。
 */
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { UI, api, getJSON, postJSON } from '../shared.js'

const STATE_NAME = { stopped: '已停止', starting: '启动中', running: '运行中',
                     stopping: '停止中', failed: '异常', external: '外部实例' }
const STATE_CLS = { stopped: 'mute', starting: 'warn', running: 'good',
                    stopping: 'warn', failed: 'bad', external: 'warn' }

export const ModulePanel = {
  name: 'ModulePanel',
  setup() {
    // 模块状态由本面板自己按 1Hz 拉（`api('/api/modules')`），不依赖 SSE。
    // 好处：① 邻居的模块表不在 SSE 里（紧凑版剔除了）；② 接口/状态卡统一只走一条路。
    const mods = ref({})
    const order = ref([])
    const busy = ref('')
    const msg = ref('')
    const msgOk = ref(true)
    const openLog = ref('')
    const logLines = ref([])
    let timer = null

    const rows = computed(() => {
      const names = order.value.length ? order.value : Object.keys(mods.value)
      return names.filter((n) => mods.value[n]).map((n) => ({ n, m: mods.value[n] }))
    })

    async function refreshList() {
      try {
        const r = await getJSON(api('/api/modules'))
        if (r && r.modules) mods.value = r.modules      // 全量：状态/频率/错误都在里面
        if (r && r.order) order.value = r.order
      } catch (e) { /* 忽略 */ }
    }

    async function act(name, action, label) {
      busy.value = name
      msg.value = ''
      try {
        const r = await postJSON(api(`/api/modules/${name}/${action}`), {})
        msgOk.value = !!(r && r.ok)
        msg.value = msgOk.value
          ? `${label} ${name}：${r.message || '已发送'}`
          : `${name} ${label}失败：${(r && r.error) || '未知错误'}`
      } finally {
        busy.value = ''
        await refreshList()        // 立刻刷新一次，不必等下个 1Hz 轮询
      }
    }

    function start(name, needConfirm) {
      if (needConfirm && !confirm(`确认启动「${name}」？\n\n该模块会启动硬件（底盘/机械臂），\n现场请确认周围无人、不会突然动作。`)) return
      act(name, 'start', '启动')
    }
    const stop = (name) => act(name, 'stop', '停止')

    async function showLog(name) {
      openLog.value = openLog.value === name ? '' : name
      if (openLog.value) await pullLog()
    }
    async function pullLog() {
      if (!openLog.value) return
      try {
        const r = await getJSON(api(`/api/modules/${openLog.value}/log?limit=120`))
        logLines.value = (r.logs || []).map((x) => x.line)
      } catch (e) { /* 忽略 */ }
    }

    // 切机器 → 关掉展开的日志（那是上一台机的输出）
    watch(() => UI.robot, () => { openLog.value = ''; logLines.value = [] })

    onMounted(async () => {
      await refreshList()
      timer = setInterval(() => { refreshList(); pullLog() }, 1000)
    })
    onBeforeUnmount(() => { if (timer) clearInterval(timer) })

    return { rows, busy, msg, msgOk, openLog, logLines, start, stop, showLog,
             STATE_NAME, STATE_CLS, fmt: (v, d = 1) => (v ? Number(v).toFixed(d) : '–') }
  },
  template: `
  <section class="card span-2">
    <h2>🧩 模块启停
      <span class="tag">白名单模式 · 命令来自 config/modules.yaml</span>
    </h2>

    <div class="mod-list">
      <div v-for="r in rows" :key="r.n" class="mod-row">
        <span class="pill" :class="STATE_CLS[r.m.state]">{{ STATE_NAME[r.m.state] || r.m.state }}</span>
        <b class="mod-name">{{ r.m.desc || r.n }}</b>
        <span class="mono dim">{{ r.n }}</span>
        <span class="mod-hz">
          <template v-if="r.m.ready_topic">{{ r.m.ready_topic }}
            <template v-if="r.m.hz"> · {{ fmt(r.m.hz) }} Hz</template>
          </template>
        </span>
        <span class="spacer"></span>
        <button class="mini" :disabled="busy === r.n || r.m.state === 'running' || r.m.state === 'starting'"
                @click="start(r.n, r.m.confirm)">▶ 启动</button>
        <button class="mini danger" :disabled="busy === r.n || r.m.state === 'stopped'"
                @click="stop(r.n)">■ 停止</button>
        <button class="mini" @click="showLog(r.n)">{{ openLog === r.n ? '收起日志' : '日志' }}</button>
      </div>
      <p class="hint warn-text" v-for="r in rows.filter((x) => x.m.state === 'external')"
         :key="'ext' + r.n">
        ⚠ {{ r.n }}：{{ r.m.error }} —— 点“停止”可清掉它们（不清就再启动会出现重复实例）
      </p>
      <p class="hint" v-if="!rows.length">等待 /api/modules…（若一直为空，检查 Agent 启动日志里“模块启停”一行）</p>
    </div>

    <p class="hint warn-text" v-if="msg && !msgOk">⚠ {{ msg }}</p>
    <p class="hint" v-else-if="msg">✓ {{ msg }}</p>
    <template v-for="r in rows" :key="'e' + r.n">
      <p class="hint warn-text" v-if="r.m.missing && r.m.missing.length">
        {{ r.n }} 依赖未启动：{{ r.m.missing.join('、') }}
      </p>
    </template>

    <div v-if="openLog" class="mod-log">
      <div class="sub">{{ openLog }} 输出（最近 120 行）</div>
      <pre class="logs mod-logs">{{ logLines.length ? logLines.join('\\n') : '（暂无输出）' }}</pre>
    </div>
  </section>
  `
}
