#!/usr/bin/env python3
"""按住方向键时盯着 `/cmd_vel`，判断"卡顿"到底出在哪一侧。

用法（在机器人上，与 WebUI **同一个终端环境**里跑）：

    python3 ~/ros2fox/src/fox_webui/scripts/watch_cmd_vel.py

> 注：`scripts/` 不随包安装（与 `fake_telemetry.py` 一样），直接从源码目录跑即可。

然后在网页上按住"前进"几秒，看本脚本的输出。

怎么读结果
----------
* **间隙 ≤ 150 ms、零值次数 ≈ 松手次数** → ROS 侧健康，卡顿在浏览器/网络（见下"排查"）。
* **出现 > 300 ms 的间隙（"⚠️ 间隙"）** → 指令真的断了。若同时看到"← 归零"，
  说明是**看门狗清零**（`webui.yaml` 的 `cmd_timeout` 没生效或页面在后台）。
* **完全没有输出** → `/cmd_vel` 一个都没收到：Publisher/订阅不匹配
  （常见原因：`ROS_LOCALHOST_ONLY` 不一致、或 `/cmd_vel` 被 Nav2 抢着发）。

排查顺序（按性价比）
--------------------
1. 确认 Agent 已重启（否则跑的是旧代码，`cmd_timeout` 还是 300 ms）。
2. 浏览器**保持前台**：后台标签页会把 `setInterval` 节流到 ≥1 s → 必卡。
3. 手机/平板：手指在按钮上滑动会触发 `pointerleave`（已在 2026-10-02 用
   pointer capture 修掉）→ 更新前端后重试。
4. 本脚本能给出"是否为 ROS 侧断裂"的确定结论。
"""
from __future__ import annotations

import sys
import time

import rclpy
from geometry_msgs.msg import Twist

TOPIC = '/cmd_vel'
GAP_WARN = 0.30          # 超过这个间隙就报警（秒）
ZERO_EPS = 1e-3


def main(argv=None) -> int:
    rclpy.init(args=argv)
    node = rclpy.create_node('watch_cmd_vel')
    state = {
        'last': None,        # 上一条消息时间
        'last_nonzero': None,
        'n': 0,
        'gaps': 0,
        'zero_after_move': 0,
        'prev_nonzero': False,
        'max_gap': 0.0,
        't0': time.time(),
    }

    def is_zero(m: Twist) -> bool:
        return (abs(m.linear.x) < ZERO_EPS and abs(m.linear.y) < ZERO_EPS
                and abs(m.angular.z) < ZERO_EPS)

    def cb(msg: Twist) -> None:
        now = time.time()
        z = is_zero(msg)
        # ① 消息间隙
        if state['last'] is not None:
            gap = now - state['last']
            if gap > state['max_gap']:
                state['max_gap'] = gap
            if gap > GAP_WARN:
                state['gaps'] += 1
                print(f'⚠️  间隙 {gap*1000:6.0f} ms '
                      f'(vx={msg.linear.x:+.2f} vy={msg.linear.y:+.2f} '
                      f'vth={msg.angular.z:+.2f})', flush=True)
        state['last'] = now
        state['n'] += 1
        # ② 正在走的时候突然归零 → 多半是看门狗清零
        if z and state['prev_nonzero']:
            state['zero_after_move'] += 1
            print('    ← 归零（正在走的时候收到 0）'
                  '  → 大概率是看门狗清零，查 webui.yaml 的 cmd_timeout / 页面是否在后台',
                  flush=True)
        if not z:
            state['last_nonzero'] = now
        state['prev_nonzero'] = not z

    node.create_subscription(Twist, TOPIC, cb, 10)
    print(f'监听 {TOPIC} …  现在去网页上按住"前进" 5 秒，然后松手（Ctrl-C 结束）')
    print(f'判定阈值：消息间隙 > {GAP_WARN*1000:.0f} ms 视为"断了"')
    print('-' * 76, flush=True)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        dur = max(1e-6, time.time() - state['t0'])
        print('-' * 76)
        print(f'共收到 {state["n"]} 条，历时 {dur:.1f} s（平均 {state["n"]/dur:.1f} Hz）')
        print(f'最大间隙 {state["max_gap"]*1000:.0f} ms；超阈值间隙 {state["gaps"]} 次；'
              f'走行中被归零 {state["zero_after_move"]} 次')
        if state['n'] == 0:
            print('❌ 一条都没收到 → 检查 ROS_LOCALHOST_ONLY 是否与其它节点一致、'
                  '以及 /cmd_vel 是否被 Nav2 占用')
        elif state['gaps'] == 0 and state['zero_after_move'] <= 1:
            print('✅ ROS 侧健康（间隙与归零都在正常范围）→ 卡顿更可能在浏览器/网络侧')
        else:
            print('⚠️ ROS 侧确实有断裂 → 结合上面的"归零"提示判断是否为看门狗清零')
        try:
            node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
