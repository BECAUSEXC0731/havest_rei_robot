/* FOX WebUI 前端入口（Vue3 ESM 免构建）
 *
 * 为什么不用打包器：现场机器人常无外网，npm 依赖与构建产物都会成为负担；
 * Vue3 提供 esm-browser 版本 + importmap 即可直接用，改完刷新页面就生效。
 */
import { createApp } from 'vue'
import { S, UI, startSSE } from './shared.js'
import { StatusPanels, HealthPanel } from './components/StatusPanels.js'
import { MapView } from './components/MapView.js'
import { VideoPanel } from './components/VideoPanel.js'
import { LogPanel } from './components/LogPanel.js'
import { ManualControl, EstopBar } from './components/ManualControl.js'
import { ArmPanel } from './components/ArmPanel.js'
import { NavPanel } from './components/NavPanel.js'
import { ModulePanel } from './components/ModulePanel.js'
import { TaskPanel } from './components/TaskPanel.js'
import { RobotPicker } from './components/RobotPicker.js'

const Root = {
  components: { StatusPanels, HealthPanel, MapView, VideoPanel, LogPanel,
                ManualControl, EstopBar, ArmPanel, NavPanel, ModulePanel, TaskPanel,
                RobotPicker },
  setup() {
    startSSE()
    return { S, UI }
  },
  computed: {
    robotTitle() {
      // 多机：标题显示"本机 → 正在看的机器"，避免误操作到别的车
      const me = this.S.data?.robot?.name || 'fox'
      const cur = this.UI.robot
      return cur && cur !== me ? `${me} → ${cur}` : me
    },
    online() {
      // "机器人在跑"（有底盘数据）——本机看顶层，邻居看它的快照
      if (this.UI.robot) return !!this.S.data?.robots?.[this.UI.robot]?.online
      return !!this.S.data?.robot?.online
    },
    reachable() {
      // "能不能连上 Agent"（模式 C）：本机恒为真；邻居看 HTTP 可达性
      if (!this.UI.robot) return true
      return this.S.data?.robots?.[this.UI.robot]?.reachable !== false
    },
    updated() {
      const ts = this.S.data?.ts
      return ts ? new Date(ts * 1000).toLocaleTimeString() : '–'
    },
  },
  template: `
  <header class="topbar">
    <div class="brand">🍇 <b>FOX WebUI</b><span class="robot">{{ robotTitle }}</span></div>
    <div class="right">
      <RobotPicker />
      <span class="dot" :class="!reachable ? 'bad' : (online ? 'ok' : 'warn')"></span>
      <span class="muted">{{ !reachable ? '邻居不可达' : (online ? '在线' : '无底盘数据') }}</span>
      <span class="muted" v-if="!S.connected">⚠ {{ S.err || 'SSE 断开' }}</span>
      <span class="muted">{{ updated }}</span>
      <EstopBar />
    </div>
  </header>

  <main class="grid">
    <MapView />
    <NavPanel />
    <VideoPanel />
    <TaskPanel />
    <ModulePanel />
    <ArmPanel />
    <ManualControl />
    <StatusPanels />
    <HealthPanel />
    <LogPanel />
  </main>

  <footer class="footer muted">
    S4 · 多机（模式 C 对称 HTTP）· 手动驾驶 / 机械臂 / 夹爪 / 航点 / 一键采摘 ·
    文档见 docs/WebUI_技术文档.md §7.4
  </footer>
  `
}

createApp(Root).mount('#app')
