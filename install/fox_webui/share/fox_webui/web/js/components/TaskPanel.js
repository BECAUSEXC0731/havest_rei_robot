/* 采摘任务面板：一键全流程 / 暂停 / 继续 / 停止 + 实时阶段进度
 *
 * 与后端的关系：
 *   POST /api/task/{start|stop|pause|resume|pick_one} → 发 /grape_harvest/command
 *   状态来自 state.task（harvest_node 1Hz 上报的 JSON）
 *
 * 安全：harvest 会动底盘与机械臂 → start/stop 都要二次确认；
 *      检测列表里的"抓一颗"也会走同一个确认（见 VideoPanel → postJSON）。
 */
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { UI, cur, api, postJSON, getJSON } from '../shared.js'

const ST_NAME = { idle: '待命', running: '运行中', paused: '已暂停',
                  done: '已完成', error: '出错', unknown: '未知' }
const ST_CLS = { idle: 'mute', running: 'good', paused: 'warn',
                 done: 'good', error: 'bad', unknown: 'mute' }

export const TaskPanel = {
  name: 'TaskPanel',
  setup() {
    const task = computed(() => cur().task || null)
    const listening = computed(() => !!cur().control?.task_listening)
    const running = computed(() => !!task.value?.running)
    const grasping = computed(() => !!cur().control?.grasping)
    const busy = ref('')
    const msg = ref('')
    const msgOk = ref(true)

    async function send(action, body, label) {
      busy.value = action
      msg.value = ''
      try {
        const r = await postJSON(api(`/api/task/${action}`), body || {})
        msgOk.value = !!(r && r.ok)
        msg.value = msgOk.value ? `${label}已下发` : `${label}失败：${(r && r.error) || '未知错误'}`
      } finally {
        busy.value = ''
      }
    }

    const start = () => {
      if (!confirm('确认开始采摘全流程？\n\n会依次：导航到各葡萄架航点 → 检测 → 抓取 → 放篮。\n'
                   + '请确认现场无人、机械臂周围无障碍，急停按钮在手边。')) return
      send('start', {}, '开始采摘')
    }
    const stop = () => {
      if (!confirm('确认停止？\n\n会在当前动作完成后停下（协作式停止），并让机械臂归位。')) return
      send('stop', {}, '停止')
    }
    const pause = () => send('pause', {}, '暂停')
    const resume = () => send('resume', {}, '继续')

    /* ── 抓取点补偿：改内存立即生效；手动点“保存”才写回 harvest_config.yaml ── */
    // 值的唯一来源是 /api/compensation（挂载 / 每 5s / 每次改动后）——
    // 不要用 SSE 里的 control.compensation：它会让显示和真值对不上。
    const compDirty = ref(false)
    const compBusy = ref('')
    const compMsg = ref('')
    const compOk = ref(true)
    const compInfo = ref(null)          // GET /api/compensation 的完整返回（含 dirty_keys/上次保存）

    // ⚠️ short 是本地字段名(x/y/z)，api 是后端接口认的增量名(dx/dy/dz)，
    //    两者不能混用：后端只认 dx/dy/dz/tool_offset_*，发 {x:10} 会被静默忽略。
    const AXES = [
      { key: 'tool_offset_x', short: 'x', api: 'dx', label: 'X（径向）' },
      { key: 'tool_offset_y', short: 'y', api: 'dy', label: 'Y（侧向）' },
      { key: 'tool_offset_z', short: 'z', api: 'dz', label: 'Z（垂直）' },
    ]
    // ⚠️ 用本地 reactive + v-model：直接 :value="comp[key]" 单向绑定在数字输入框上
    //    实测不刷新（后端值已变、框里还是旧数字）。
    //    值的来源只有一个：refreshComp() —— 挂载时、每 5s、以及**每次改动后**都拉一次，
    //    这样不用猜 SSE/响应结构，改完立即与文件/内存里的权威值对齐。
    const compLocal = reactive({ x: 0, y: 0, z: 0 })

    async function refreshComp() {
      try {
        const j = await getJSON(api('/api/compensation'))
        compInfo.value = j
        if (j && j.value) {
          for (const a of AXES) compLocal[a.short] = j.value[a.key]
        }
        if (j && typeof j.dirty === 'boolean') compDirty.value = j.dirty
      } catch (e) { /* 忽略 */ }
    }
    function _applyResp(r) {
      const vals = (r && r.value && typeof r.value === 'object') ? r.value : null
      if (vals) {
        for (const a of AXES) {
          const nv = vals[a.key]
          if (typeof nv === 'number') compLocal[a.short] = nv
        }
      }
      if (r && r.keys && typeof r.dirty === 'boolean') compInfo.value = r   // 完整补偿信息
      if (r && typeof r.dirty === 'boolean') compDirty.value = r.dirty
    }
    async function bump(a, delta) {
      compBusy.value = a.short
      compMsg.value = ''
      try {
        const r = await postJSON(api('/api/compensation'), { [a.api]: delta })
        compOk.value = !!(r && r.ok)
        _applyResp(r)
        compMsg.value = compOk.value
          ? `${a.api} ${delta > 0 ? '+' : ''}${delta} mm 已生效（未保存）`
          : ((r && r.error) || '修改失败')
      } finally { compBusy.value = '' }
      await refreshComp()          // 以服务端值为准对齐输入框/脏标记
    }
    async function setAxis(a, raw) {
      const v = Number(raw)
      if (!Number.isFinite(v)) return
      compBusy.value = a.short
      compMsg.value = ''
      try {
        // 手输是绝对值 → 必须用完整键 tool_offset_*（dx/dy/dz 是增量语义！）
        const r = await postJSON(api('/api/compensation'), { [a.key]: v })
        compOk.value = !!(r && r.ok)
        _applyResp(r)
        compMsg.value = compOk.value
          ? `${a.api} 设为 ${v} mm 已生效（未保存）`
          : ((r && r.error) || '修改失败')
      } finally { compBusy.value = '' }
      await refreshComp()
    }
    // 写回的两个文件：源码 vs install（否则路径尾部一样，看不出区别）
    const fileLabel = (p) => (p.includes('/src/') ? '源码 src/' + p.split('/src/')[1]
      : p.includes('/install/') ? 'install/' + p.split('/install/')[1] : p)

    const saveComp = async () => {
      compBusy.value = 'save'
      try {
        const r = await postJSON(api('/api/compensation/save'), {})
        compOk.value = !!(r && r.ok)
        if (compOk.value) {
          const files = (r.results || []).filter((x) => x.changed).map((x) => fileLabel(x.path))
          compMsg.value = r.changed
            ? `已写入 ${files.join(' 与 ')}（原文件已备份 .bak）`
              + (r.harvest_reloaded ? '；已通知 harvest 重读配置' : '')
            : '值与文件一致，无需写入'
        } else {
          compMsg.value = (r && r.error)
            || (r.results || []).map((x) => x.detail).filter(Boolean).join('; ') || '保存失败'
        }
        await refreshComp()
      } finally { compBusy.value = '' }
    }
    // 不弹确认框：撤销只丢弃"未保存的内存改动"，不碰文件（写文件要单独点保存）
    const revertComp = async () => {
      compBusy.value = 'revert'
      try {
        const r = await postJSON(api('/api/compensation/revert'), {})
        compOk.value = !!(r && r.ok)
        compMsg.value = compOk.value ? '已撤销，回到配置文件里的值' : ((r && r.error) || '撤销失败')
        await refreshComp()
      } finally { compBusy.value = '' }
    }

    // 切机器 → 重新拉该机的补偿值（补偿是"每台机各自的 harvest_config.yaml"）
    watch(() => UI.robot, () => refreshComp())

    // 补偿面板：挂载时拉一次（限幅/文件路径/上次保存时间），之后低频刷新
    let compTimer = null
    onMounted(() => {
      refreshComp()
      compTimer = setInterval(refreshComp, 5000)
    })
    onBeforeUnmount(() => { if (compTimer) clearInterval(compTimer) })

    return { task, listening, running, grasping, busy, msg, msgOk, start, stop, pause, resume,
             compDirty, compBusy, compMsg, compOk, compInfo, AXES, compLocal,
             bump, setAxis, saveComp, revertComp, refreshComp,
             ST_NAME, ST_CLS }  },
  template: `
  <section class="card">
    <h2>🍇 采摘任务
      <span class="pill" :class="ST_CLS[task?.state || 'idle']">
        {{ ST_NAME[task?.state || 'idle'] }}
      </span>
      <span class="tag" v-if="!listening">harvest 节点未启动</span>
    </h2>

    <div class="kv small"><span>阶段</span><b>{{ task?.stage || '—' }}</b></div>
    <div class="kv small" v-if="task?.waypoints">
      <span>航点</span><b>{{ (task.waypoint ?? 0) + 1 }} / {{ task.waypoints }}</b></div>
    <div class="kv small"><span>检测 / 已摘</span>
      <b>{{ task?.detected ?? 0 }} / {{ task?.picked ?? 0 }}</b></div>
    <div class="kv small" v-if="task?.elapsed_s">
      <span>已用时</span><b>{{ task.elapsed_s.toFixed(0) }} s</b></div>
    <p class="hint" v-if="task?.message">{{ task.message }}</p>
    <p class="hint" v-else-if="!task">尚未收到 /grape_harvest/status（节点未启动或未运行）</p>

    <div class="row-btns">
      <button class="mini primary" :disabled="busy || running || !listening" @click="start">▶ 一键采摘</button>
      <button class="mini" :disabled="busy || !running" @click="pause">⏸ 暂停</button>
      <button class="mini" :disabled="busy || !task?.paused" @click="resume">⏵ 继续</button>
      <button class="mini danger" :disabled="busy || !running" @click="stop">■ 停止</button>
    </div>

    <p class="hint warn-text" v-if="msg && !msgOk">⚠ {{ msg }}</p>
    <p class="hint" v-else-if="msg">✓ {{ msg }}</p>
    <p class="hint">
      单颗抓取：在「视频」面板开启识别后，点检测列表里的 <b>🎯 抓取</b>
      —— 动作与 <span class="mono">grape_grasp_test.py</span> 相同
      （过渡点 → 抓取点 → 夹紧 → 回安全点 → 松开），只依赖 arm + gripper 模块，
      不需要启动 harvest
    </p>
    <p class="hint" v-if="grasping">🤏 正在执行单颗抓取（急停仍可生效）…</p>

    <!-- ── 抓取点补偿（实时）── -->
    <div class="divider"></div>
    <h2>🎯 抓取点补偿（实时）
      <span class="tag" v-if="compDirty">有未保存改动</span>
    </h2>
    <p class="hint" style="margin-top:0">
      抓取点 = 葡萄坐标 + 按朝向旋转过的该偏移（与 <span class="mono">grape_grasp_test.py</span> 同款）。
      改动<b>立即生效</b>，下次点 🎯 抓取 就用新值；满意后点“保存到配置”写入
      <span class="mono">harvest_config.yaml</span>（下次启动自动带上，不用重配）。
    </p>

    <p class="hint" v-if="!compInfo">读取中…（点“刷新”可重试）</p>
    <div v-for="a in AXES" :key="a.key" class="step-row">
      <span class="axis">{{ a.label }}</span>
      <input type="number" step="1" v-model.number="compLocal[a.short]" :disabled="!compInfo"
             @change="setAxis(a, compLocal[a.short])" />
      <button class="mini" :disabled="!compInfo || compBusy === a.short" @click="bump(a, -10)">−10</button>
      <button class="mini" :disabled="!compInfo || compBusy === a.short" @click="bump(a, -1)">−1</button>
      <button class="mini" :disabled="!compInfo || compBusy === a.short" @click="bump(a, 1)">+1</button>
      <button class="mini" :disabled="!compInfo || compBusy === a.short" @click="bump(a, 10)">+10</button>
    </div>

    <div class="row-btns">
      <button class="mini primary" :disabled="compBusy === 'save' || !compDirty"
              @click="saveComp">💾 保存到配置</button>
      <button class="mini" :disabled="compBusy === 'revert' || !compDirty"
              @click="revertComp">↩ 撤销改动</button>
      <button class="mini" @click="refreshComp">刷新</button>
    </div>
    <p class="hint warn-text" v-if="compMsg && !compOk">⚠ {{ compMsg }}</p>
    <p class="hint" v-else-if="compMsg">✓ {{ compMsg }}</p>
    <p class="hint" v-if="compInfo?.last_save?.ts">
      上次保存：{{ new Date(compInfo.last_save.ts * 1000).toLocaleTimeString() }}
      （限幅 ±{{ compInfo.limit_mm }} mm，写回 {{ (compInfo.paths || []).length }} 个文件）
    </p>
  </section>
  `
}
