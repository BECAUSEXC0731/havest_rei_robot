"""等待工具：让"长流程"既能跑在被 spin 的节点上，又不依赖嵌套 spin。

为什么需要它（实测数据，见 scripts/nested_spin_probe.py）
------------------------------------------------------
原实现把整条采摘流程跑在 timer/命令回调里，等待用 ``rclpy.spin_once(node)`` /
``spin_until_future_complete(node, fut)``。实测结果：

    在一个回调内部做 10 次 ``spin_once(0.9)`` 期间外部发 3 条消息 →
    **只有 1 条被处理**（其余一直躺在 DDS 队列里）。

后果非常严重：流程跑起来之后，**外部发的 stop/pause/急停根本收不到** ——
想让它停只能杀进程。根因是同一个节点被同一个 executor 重入 spin，
rclpy 的 ``_cb_iter`` 生成器状态被破坏，回调被静默丢弃。

正确做法（本模块提供）：
* 主线程用 ``MultiThreadedExecutor`` 一直 spin（回调永远有人处理）；
* 长流程放到 **worker 线程**；
* worker 里等 future 不再自己 spin，而是 ``add_done_callback + Event.wait``，
  由主线程的 executor 去兑现 future；
* 需要"推进一下"的地方（等里程计、控制循环）改成 sleep，让主线程去 spin。

调用方在启动 worker 线程前调用 ``set_external_spin(True)`` 即可切换；
不设置时保持旧行为（自己 spin），所以 ``grape_grasp_test.py`` 等单线程脚本不受影响。
"""
from __future__ import annotations

import threading
import time

import rclpy

_EXTERNAL_SPIN = False


def set_external_spin(enabled: bool) -> None:
    """外部（主线程）已在 spin → worker 里的等待改为 Event.wait，不再自己 spin。"""
    global _EXTERNAL_SPIN
    _EXTERNAL_SPIN = bool(enabled)


def external_spin() -> bool:
    return _EXTERNAL_SPIN


def wait_future(node, future, timeout: float) -> bool:
    """等一个 rclpy future，返回是否在超时前完成。"""
    if future.done():
        return True
    if not _EXTERNAL_SPIN:
        # 旧行为：自己 spin（单线程脚本用）
        rclpy.spin_until_future_complete(node, future, timeout_sec=timeout)
        return future.done()

    done = threading.Event()

    def _on_done(_f):
        done.set()

    try:
        future.add_done_callback(_on_done)
    except Exception:
        pass
    done.wait(timeout)
    return future.done()


def pump(node, dt: float = 0.05) -> None:
    """在长流程里"推进一下"：外部 spin 模式下只是睡一会儿（回调由别的线程处理）。"""
    if _EXTERNAL_SPIN:
        time.sleep(max(0.0, float(dt)))
        return
    try:
        rclpy.spin_once(node, timeout_sec=dt)
    except Exception:
        pass


def wait_until(predicate, timeout: float, node=None, step: float = 0.05) -> bool:
    """轮询等待条件成立（期间用 pump 推进）。"""
    end = time.time() + float(timeout)
    while time.time() < end:
        if predicate():
            return True
        pump(node, step)
    return bool(predicate())
