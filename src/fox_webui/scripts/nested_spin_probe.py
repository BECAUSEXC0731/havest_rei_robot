#!/usr/bin/env python3
"""最小实验：在 timer 回调里做「嵌套 spin」时，订阅的消息会不会被处理？

背景：harvest_node 的整条采摘流程跑在 timer/命令回调里，内部用
`rclpy.spin_once(self)` / `spin_until_future_complete(self, ...)` 等待。
实测发现流程运行期间发的 /grape_harvest/command **完全没被处理** →
必须搞清楚是"嵌套 spin 不工作"还是别的原因，再决定改法。

用法：
    python3 nested_spin_probe.py                 # 只跑 A：嵌套 spin_once
    python3 nested_spin_probe.py --mode futures  # 跑 B：线程池 + future 回调
"""
import sys
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String


class Probe(Node):
    def __init__(self, mode: str):
        super().__init__('nested_spin_probe')
        self.mode = mode
        self.got = []
        self.done = False
        self.create_subscription(String, '/probe_cmd', self._cb, 10)
        self.create_timer(2.0, self._block_once)

    def _cb(self, msg):
        self.got.append((time.time(), msg.data))
        self.get_logger().info(f'✅ 收到命令: {msg.data}')

    # ── A：模拟现有代码：在回调里嵌套 spin ──
    def _block_once(self):
        if self.done:
            return
        self.done = True
        self.get_logger().info('▶ A: 进入"长任务"，接下来 10s 每秒调一次 spin_once(0.9)')
        for i in range(10):
            rclpy.spin_once(self, timeout_sec=0.9)
            self.get_logger().info(f'  A: 第 {i+1} 秒，已收到 {len(self.got)} 条')
        self.get_logger().info(f'■ A 结束，共收到 {len(self.got)} 条: {[g[1] for g in self.got]}')


class ProbeB(Node):
    """B：主线程 spin（MultiThreadedExecutor），长任务在 worker 线程里跑，
    等待用「future + done 回调 + Event.wait」，因此不需要自己 spin。"""

    def __init__(self):
        super().__init__('nested_spin_probe_b')
        self.got = []
        self.create_subscription(String, '/probe_cmd', self._cb, 10)
        self.create_timer(2.0, self._start_once)
        self.started = False

    def _cb(self, msg):
        self.got.append((time.time(), msg.data))
        self.get_logger().info(f'✅ B 收到命令: {msg.data}')

    def _start_once(self):
        if self.started:
            return
        self.started = True
        threading.Thread(target=self._work, daemon=True).start()

    def _work(self):
        self.get_logger().info('▶ B: worker 线程开始长任务（10s，用 Event.wait 等待）')

        # 关键：用 done 回调 + Event.wait 代替 spin_until_future_complete
        def _run_call(name, seconds):
            event = threading.Event()
            # 这里用 timer 模拟一次"服务调用"：完成时通过 future 通知
            fut_holder = {}

            def _later():
                fut_holder['ev'].set()
            t = threading.Timer(seconds, _later)
            fut_holder['ev'] = event
            t.start()
            self.get_logger().info(f'  B: 等 {name} 完成…')
            event.wait(timeout=seconds + 5.0)

        _run_call('模拟服务调用', 2.0)
        for i in range(4):
            time.sleep(1.0)
            self.get_logger().info(f'  B: 已收到 {len(self.got)} 条')
        self.get_logger().info(f'■ B 结束，共收到 {len(self.got)} 条: {[g[1] for g in self.got]}')


def main():
    mode = 'spin'
    if '--mode' in sys.argv:
        mode = sys.argv[sys.argv.index('--mode') + 1]
    rclpy.init()
    if mode == 'futures':
        node = ProbeB()
        ex = MultiThreadedExecutor(num_threads=2)
        ex.add_node(node)
        ex.spin()
    else:
        node = Probe(mode)
        rclpy.spin(node)


if __name__ == '__main__':
    main()
