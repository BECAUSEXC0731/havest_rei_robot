/* 状态卡片组 + 话题健康表 */
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { cur, api, getJSON, fmt, fmtList, healthClass, healthText, UI } from '../shared.js'

export const StatusPanels = {
  name: 'StatusPanels',
  setup() {
    const d = computed(() => cur())
    const pose = computed(() => d.value.pose)
    const twist = computed(() => d.value.twist || {})
    const cmd = computed(() => d.value.cmd_vel || {})
    const batt = computed(() => d.value.battery)
    const battPct = computed(() => {
      const v = batt.value?.voltage
      if (!v) return 0
      return Math.max(0, Math.min(100, ((v - 18) / (25.2 - 18)) * 100))
    })
    const battCls = computed(() => {
      const v = batt.value?.voltage || 0
      return v < 20 ? 'danger' : v < 22 ? 'warn' : 'good'
    })
    const chassis = computed(() => d.value.chassis)
    // 本机：SSE 顶层有 scan/plan；邻居：SSE 里没有（紧凑版剔除了），
    // 回退用 MapView 从 /api/map_state 拿到的点数（同一台机器，数据一致）
    const scanN = computed(() => d.value.scan?.n ?? UI.mapN?.scan ?? 0)
    const planN = computed(() => d.value.plan?.n ?? UI.mapN?.plan ?? 0)
    return { pose, twist, cmd, batt, battPct, battCls, chassis, scanN, planN, fmt, fmtList }
  },
  template: `
  <section class="card">
    <h2>📍 地图定位 <span class="tag">{{ pose ? (pose.src === 'tf' ? 'TF map→base_footprint' : '/lidar_loc_pose') : '无定位' }}</span></h2>
    <div class="kv"><span>X</span><b>{{ fmt(pose?.x, 3) }}</b><i>m</i></div>
    <div class="kv"><span>Y</span><b>{{ fmt(pose?.y, 3) }}</b><i>m</i></div>
    <div class="kv"><span>朝向</span><b>{{ fmt(pose?.yaw_deg, 1) }}</b><i>°</i></div>
    <p class="hint" v-if="!pose">⚠ 尚未定位：请在 RViz 用 2D Pose Estimate 给一次初始位姿</p>
    <p class="hint" v-else>激光点 {{ scanN }} · 路径点 {{ planN }}</p>
  </section>

  <section class="card">
    <h2>🚗 底盘速度</h2>
    <div class="sub">实测（/odom）</div>
    <div class="kv"><span>vx</span><b>{{ fmt(twist.vx) }}</b><i>m/s</i></div>
    <div class="kv"><span>vy</span><b>{{ fmt(twist.vy) }}</b><i>m/s</i></div>
    <div class="kv"><span>vth</span><b>{{ fmt(twist.vth) }}</b><i>rad/s</i></div>
    <div class="sub">指令（/cmd_vel）</div>
    <div class="kv"><span>vx</span><b>{{ fmt(cmd.vx) }}</b><i>m/s</i></div>
    <div class="kv"><span>vth</span><b>{{ fmt(cmd.vth) }}</b><i>rad/s</i></div>
  </section>

  <section class="card">
    <h2>🔋 电池</h2>
    <div class="kv big"><span>电压</span><b>{{ fmt(batt?.voltage, 2) }}</b><i>V</i></div>
    <div class="bar"><div class="bar-fill" :class="battCls" :style="{width: battPct.toFixed(0) + '%'}"></div></div>
    <p class="hint">阈值参考：≥23V 正常 / &lt;22V 注意 / &lt;20V 需充电</p>
  </section>

  <section class="card">
    <h2>⚙️ 底盘状态</h2>
    <div class="kv"><span>电机转速</span><b>{{ fmtList(chassis?.motor_speed) }}</b></div>
    <div class="kv"><span>碰撞</span><b>{{ fmtList(chassis?.crash) }}</b></div>
    <div class="kv"><span>跌落</span><b>{{ fmtList(chassis?.cliff) }}</b></div>
    <div class="kv"><span>烟雾</span><b>{{ chassis?.smoke ?? '–' }}</b></div>
    <div class="kv"><span>超声波</span><b>{{ fmtList(chassis?.ultrasound) }}</b></div>
  </section>
  `
}

export const HealthPanel = {
  name: 'HealthPanel',
  setup() {
    // 健康表走"按机器取"的接口：本机 = /api/health；邻居 = /api/to/<名字>/api/health。
    // （SSE 里的 robots 是紧凑版，故意不含 health —— 避免 10Hz 推大 payload）
    const health = ref({})
    const viewers = computed(() => cur().detector || {})
    let timer = null

    async function pull() {
      try {
        const j = await getJSON(api('/api/health'))
        health.value = j.topics || {}
      } catch (e) { /* 网络抖动忽略 */ }
    }
    onMounted(() => { pull(); timer = setInterval(pull, 1000) })
    onBeforeUnmount(() => { if (timer) clearInterval(timer) })

    const rows = computed(() =>
      Object.keys(health.value).sort().map((k) => ({ topic: k, h: health.value[k] })))
    return { rows, viewers, healthClass, healthText, fmt }
  },
  template: `
  <section class="card span-2">
    <h2>🩺 话题健康
      <span class="tag" v-if="viewers.active">识别: {{ viewers.mode }} · {{ viewers.detections }} 个目标</span>
    </h2>
    <div class="health-wrap">
      <table class="health">
        <thead><tr><th>话题</th><th>状态</th><th>频率</th><th>延迟</th></tr></thead>
        <tbody>
          <tr v-for="r in rows" :key="r.topic">
            <td class="mono">{{ r.topic }}</td>
            <td><span class="pill" :class="healthClass(r.h)">{{ healthText(r.h) }}</span></td>
            <td>{{ r.h.static ? (r.h.count ? '静态/锁存' : '–') : (r.h.online ? fmt(r.h.hz, 1) + ' Hz' : '–') }}</td>
            <td>{{ r.h.age === null ? '–' : fmt(r.h.age, 1) + ' s' }}</td>
          </tr>
          <tr v-if="!rows.length"><td colspan="4" class="muted">等待数据…</td></tr>
        </tbody>
      </table>
    </div>
  </section>
  `
}
