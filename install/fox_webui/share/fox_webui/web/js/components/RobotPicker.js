/* 顶栏"机器下拉"（多机 · 模式 C）。
 *
 * 只在超过 1 台时显示。切换写入 shared.js 的 UI.robot，
 * 之后所有面板自动改看该机的数据、控制也发到该机（见 shared.js 的 cur()/api()）。
 *
 * 邻居离线的处理：后端不会把掉线的机器从列表里删掉（还能看"最后一次已知状态"），
 * 所以这里只标灰，不做删除，避免用户切到一半机器消失。
 *
 * ⚠️ 两个状态分开看（后端 state.py 的 reachable / online）：
 *   `reachable` = 能不能连上那台的 Agent（HTTP）→ 决定"能不能切过去看"
 *   `online`    = 那台的机器人数据在不在跑（有 /odom）→ 决定绿灯
 * 混用会出现"本机显示离线、邻居显示在线"的误导（实测踩过）。
 */
import { computed, watch } from 'vue'
import { UI, curName, robotsList } from '../shared.js'

export const RobotPicker = {
  name: 'RobotPicker',
  setup() {
    const list = computed(() => robotsList())
    const multi = computed(() => list.value.length > 1)
    const active = computed(() => list.value.find((r) => r.name === curName()) || {})

    // 选中的机器不在列表里了（改名 / 邻居被移出 peers）→ 回落到本机
    watch(list, (l) => {
      if (UI.robot && !l.some((r) => r.name === UI.robot)) UI.robot = ''
    })

    const pick = (e) => { UI.robot = e.target.value || '' }

    // 后缀：不可达 → 红色；可达但没数据 → 提示"无底盘数据"
    function suffix(r) {
      if (r.reachable === false) {
        return `（不可达${r.age == null ? '' : ' ' + r.age.toFixed(0) + 's'}）`
      }
      return r.online ? '' : ' · 无底盘数据'
    }
    const dotCls = (r) => (!r.reachable ? 'dot bad' : (r.online ? 'dot ok' : 'dot warn'))

    return { UI, list, multi, active, pick, suffix, dotCls, curName }
  },
  template: `
  <span class="robot-picker" v-if="multi">
    <span class="muted">机器</span>
    <select :value="UI.robot" @change="pick"
            :title="active.reachable === false ? (active.err || '不可达') : '可达'">
      <option v-for="r in list" :key="r.name" :value="r.is_me ? '' : r.name">
        {{ r.is_me ? '★ ' : '' }}{{ r.name }}{{ suffix(r) }}
      </option>
    </select>
    <span :class="dotCls(active)"></span>
  </span>
  `
}
