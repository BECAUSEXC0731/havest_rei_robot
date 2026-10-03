/* 日志面板：/rosout 增量拉取 + 级别过滤 + 自动滚屏 */
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { UI, api, getJSON, LEVEL_NAME, LEVEL_CLASS } from '../shared.js'

export const LogPanel = {
  name: 'LogPanel',
  setup() {
    const lines = ref([])
    const minLevel = ref(20)
    const auto = ref(true)
    const boxEl = ref(null)
    const paused = ref(false)
    let lastId = 0
    let timer = null

    async function poll() {
      if (paused.value) return
      try {
        const j = await getJSON(api(`/api/logs?since=${lastId}&limit=300`))
        if (j.logs && j.logs.length) {
          lastId = j.logs[j.logs.length - 1].id
          lines.value.push(...j.logs)
          if (lines.value.length > 800) lines.value = lines.value.slice(-600)
          if (auto.value) {
            await nextTick()
            if (boxEl.value) boxEl.value.scrollTop = boxEl.value.scrollHeight
          }
        }
      } catch (e) { /* ignore */ }
    }

    function clear() { lines.value = []; }
    function reset() { lines.value = []; lastId = 0; poll() }

    // 切机器 → 清屏重新拉（不同机器的 id 序列互相独立）
    watch(() => UI.robot, () => reset())

    onMounted(() => { poll(); timer = setInterval(poll, 1000) })
    onBeforeUnmount(() => { if (timer) clearInterval(timer) })

    return { lines, minLevel, auto, boxEl, paused, clear, reset, LEVEL_NAME, LEVEL_CLASS }
  },
  template: `
  <section class="card span-all">
    <h2>📜 日志（/rosout）
      <select v-model.number="minLevel">
        <option :value="10">全部</option>
        <option :value="20">INFO+</option>
        <option :value="30">WARN+</option>
        <option :value="40">ERROR+</option>
      </select>
      <label class="chk"><input type="checkbox" v-model="auto"> 自动滚屏</label>
      <label class="chk"><input type="checkbox" v-model="paused"> 暂停</label>
      <button class="mini" @click="reset">刷新</button>
      <button class="mini" @click="clear">清空</button>
    </h2>
    <div class="logs" ref="boxEl">
      <div v-for="l in lines" :key="l.id"
           class="log-line" :class="LEVEL_CLASS[l.level]" v-show="l.level >= minLevel">
        <span class="mono t">{{ new Date(l.t * 1000).toLocaleTimeString() }}</span>
        <span class="mono lv">{{ LEVEL_NAME[l.level] || l.level }}</span>
        <span class="mono nm">{{ l.name }}</span>
        <span class="msg">{{ l.msg }}</span>
      </div>
    </div>
  </section>
  `
}
