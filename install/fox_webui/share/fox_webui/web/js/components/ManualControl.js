/* 手动控制：方向按键 + 速度滑块 + 键盘 WASD/QE + 停止。
 *
 * 安全设计（与后端看门狗配合）：
 *  - 按住时以 10Hz 续期 POST /api/cmd_vel；抬手/失焦/关页面 → 立刻发一次零速；
 *  - 即使前端没发成功，后端 300ms 未收到续期也会自动归零；
 *  - 急停锁存时后端会拒绝指令，前端显示为禁用态。
 */
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { cur, api, postJSON } from '../shared.js'

const DIRS = [
  { k: 'fl', label: '↖', v: [1, 1, 0] },
  { k: 'f', label: '↑', v: [1, 0, 0] },
  { k: 'fr', label: '↗', v: [1, -1, 0] },
  { k: 'l', label: '←', v: [0, 1, 0] },
  { k: 'stop', label: '■', v: [0, 0, 0] },
  { k: 'r', label: '→', v: [0, -1, 0] },
  { k: 'bl', label: '↙', v: [-1, 1, 0] },
  { k: 'b', label: '↓', v: [-1, 0, 0] },
  { k: 'br', label: '↘', v: [-1, -1, 0] },
]

const KEYMAP = {
  w: [1, 0, 0], s: [-1, 0, 0], a: [0, 1, 0], d: [0, -1, 0],
  q: [0, 0, 1], e: [0, 0, -1],
  ArrowUp: [1, 0, 0], ArrowDown: [-1, 0, 0],
  ArrowLeft: [0, 1, 0], ArrowRight: [0, -1, 0],
}

export const ManualControl = {
  name: 'ManualControl',
  setup() {
    const speed = ref(0.15)             // 线速度上限（m/s）
    const rot = ref(0.3)                // 角速度上限（rad/s）
    const pressed = ref(new Set())      // 按下的方向键
    const keys = ref(new Set())         // 按下的键盘
    const msg = ref('')
    let timer = null
    let wasActive = false

    const estopLocked = computed(() => !!cur().control?.estop)
    const navActive = computed(() => !!cur().control?.nav_active)
    const blocked = computed(() => estopLocked.value || navActive.value)

    function vec() {
      let vx = 0, vy = 0, vth = 0
      for (const k of keys.value) {
        const v = KEYMAP[k]; if (!v) continue
        vx += v[0]; vy += v[1]; vth += v[2]
      }
      for (const k of pressed.value) {
        const d = DIRS.find((x) => x.k === k)
        if (!d) continue
        vx += d.v[0]; vy += d.v[1]; vth += d.v[2]
      }
      const n = Math.max(1, Math.hypot(vx, vy))
      return {
        vx: (vx / n) * speed.value,
        vy: (vy / n) * speed.value,
        vth: Math.max(-1, Math.min(1, vth)) * rot.value,
      }
    }

    async function tick() {
      const path = api('/api/cmd_vel')      // 看着邻居机器时 → 自动转发给那台机
      if (blocked.value) {
        if (wasActive) { await postJSON(path, { vx: 0, vy: 0, vth: 0 }); wasActive = false }
        return
      }
      const v = vec()
      const moving = v.vx || v.vy || v.vth
      if (moving) {
        wasActive = true
        const r = await postJSON(path, v)
        if (r && r.ok === false) msg.value = r.error || ''
      } else if (wasActive) {
        wasActive = false
        await postJSON(path, { vx: 0, vy: 0, vth: 0 })   // 松手立即停
      }
    }

    function down(k) { const s = new Set(pressed.value); s.add(k); pressed.value = s }
    function up(k) { const s = new Set(pressed.value); s.delete(k); pressed.value = s }
    function keyDown(k) { const s = new Set(keys.value); s.add(k); keys.value = s }
    function keyUp(k) { const s = new Set(keys.value); s.delete(k); keys.value = s }
    function clearAll() { pressed.value = new Set(); keys.value = new Set() }

    /**
     * 按住开始（方向键/QE 都用它）。
     *
     * ⚠️ 触摸屏上的真实 bug（2026-10-02 修）：
     *   原实现在按钮上挂了 `@pointerleave="up()"` —— 手机/平板上手指**稍微滑动一点**
     *   就会离开按钮区域触发 pointerleave → 指令被清掉，松开后又接上，
     *   表现就是“按住过程中会卡一下”。鼠标上很难发现（指针很稳）。
     *   改用 **pointer capture**：按下时把这一路的 move/up 全锁在该按钮上，
     *   手指滑出也不断，只靠 pointerup/pointercancel 结束。
     */
    function press(k, ev) {
      const el = ev && ev.currentTarget
      try { if (el && el.setPointerCapture) el.setPointerCapture(ev.pointerId) }
      catch (e) { /* 旧浏览器不支持：退回原行为 */ }
      down(k)
    }
    function pressKey(k, ev) {
      const el = ev && ev.currentTarget
      try { if (el && el.setPointerCapture) el.setPointerCapture(ev.pointerId) }
      catch (e) { /* 忽略 */ }
      keyDown(k)
    }

    function onKeyDown(e) {
      const k = e.key.length === 1 ? e.key.toLowerCase() : e.key
      if (k === ' ') { clearAll(); e.preventDefault(); return }
      if (KEYMAP[k]) {
        const s = new Set(keys.value); s.add(k); keys.value = s
        e.preventDefault()
      }
    }
    function onKeyUp(e) {
      const k = e.key.length === 1 ? e.key.toLowerCase() : e.key
      if (KEYMAP[k]) { const s = new Set(keys.value); s.delete(k); keys.value = s }
    }
    function onBlur() { clearAll() }
    // 兜底：任何地方的“手抬起”都清空（防止 pointer capture 失败导致卡在“一直走”）
    function onGlobalUp() { clearAll() }

    async function estopHit() { await postJSON(api('/api/estop'), {}); clearAll() }
    async function estopRelease() { await postJSON(api('/api/estop'), { release: true }) }

    onMounted(() => {
      timer = setInterval(tick, 100)
      window.addEventListener('keydown', onKeyDown)
      window.addEventListener('keyup', onKeyUp)
      window.addEventListener('blur', onBlur)
      window.addEventListener('pointerup', onGlobalUp)
      window.addEventListener('pointercancel', onGlobalUp)
    })
    onBeforeUnmount(() => {
      if (timer) clearInterval(timer)
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
      window.removeEventListener('blur', onBlur)
      window.removeEventListener('pointerup', onGlobalUp)
      window.removeEventListener('pointercancel', onGlobalUp)
      postJSON(api('/api/cmd_vel'), { vx: 0, vy: 0, vth: 0 })
    })

    return { DIRS, speed, rot, pressed, keys, down, up, press, pressKey, keyDown, keyUp, clearAll,
             estopHit, estopRelease, estopLocked, blocked, navActive, msg,
             manual: computed(() => cur().control?.manual || {}) }
  },
  template: `
  <section class="card">
    <h2>🕹️ 手动控制
      <span class="tag" v-if="blocked">{{ estopLocked ? '急停锁定' : '导航中已禁用' }}</span>
    </h2>

    <div class="slider-row">
      <span>线速度</span>
      <input type="range" min="0.05" max="0.3" step="0.05" v-model.number="speed" />
      <b>{{ speed.toFixed(2) }}</b><i>m/s</i>
    </div>
    <div class="slider-row">
      <span>角速度</span>
      <input type="range" min="0.1" max="0.5" step="0.1" v-model.number="rot" />
      <b>{{ rot.toFixed(2) }}</b><i>rad/s</i>
    </div>

    <div class="dpad" :class="{ disabled: blocked }">
      <button v-for="d in DIRS" :key="d.k"
              class="dbtn" :class="{ stop: d.k === 'stop', on: pressed.has(d.k) }"
              :disabled="blocked"
              @pointerdown.prevent="press(d.k, $event)"
              @pointerup.prevent="up(d.k)"
              @pointercancel="up(d.k)">{{ d.label }}</button>
    </div>

    <div class="row-btns">
      <button class="mini" :disabled="blocked"
              @pointerdown.prevent="pressKey('q', $event)" @pointerup.prevent="keyUp('q')"
              @pointercancel="keyUp('q')">⟲ 左转 (Q)</button>
      <button class="mini" :disabled="blocked"
              @pointerdown.prevent="pressKey('e', $event)" @pointerup.prevent="keyUp('e')"
              @pointercancel="keyUp('e')">⟳ 右转 (E)</button>
      <button class="mini" @click="clearAll">■ 停止</button>
    </div>

    <p class="hint">键盘：W/S 前后 · A/D 左右平移 · Q/E 旋转 · 空格 立即停<br>
      松手或断网会在 0.3s 内自动归零（后端看门狗）</p>
    <p class="hint" v-if="msg">⚠ {{ msg }}</p>
    <p class="hint" v-if="manual.active">
      当前指令：vx {{ (manual.vx ?? 0).toFixed(2) }} · vy {{ (manual.vy ?? 0).toFixed(2) }} ·
      vth {{ (manual.vth ?? 0).toFixed(2) }}
    </p>
    <p class="hint warn-text" v-if="manual.reason === 'timeout'">
      ⚠ 速度指令续期超时 → 看门狗已自动归零（表现为"车一顿一顿/按住好几秒才动"）。
      通常是网络或浏览器卡顿；阈值见 <span class="mono">webui.yaml</span> 的
      <span class="mono">cmd_timeout</span>
    </p>
  </section>
  `
}

export const EstopBar = {
  name: 'EstopBar',
  setup() {
    const locked = computed(() => !!cur().control?.estop)
    const reason = computed(() => cur().estop?.reason || '')
    async function hit() {
      if (locked.value) { await postJSON(api('/api/estop'), { release: true }) }
      else if (confirm('确认急停？\n\n将立即：发零速 → 取消导航目标 → 锁定手动控制')) {
        await postJSON(api('/api/estop'), { reason: 'webui' })
      }
    }
    return { locked, reason, hit }
  },
  template: `
    <button class="estop" :class="{ active: locked }" @click="hit">
      {{ locked ? '🔓 解除急停' : '🚨 急停' }}
    </button>
  `
}
