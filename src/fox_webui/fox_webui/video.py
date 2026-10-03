"""按需 MJPEG 视频流（彩色 / 深度伪彩 / 识别叠加）。

设计要点（见 docs/WebUI_技术文档.md §5.3）
----------------------------------------
* **引用计数**：没有观看者时不订阅、不解码、不编码 —— 这是 Jetson 上的硬要求
  （640x480@30Hz 的图像反序列化 + JPEG 编码足够把 CPU 吃满，进而拖慢导航）。
* 每个观看者一个独立**异步**生成器；最后一个观看者离开时立即退订。
* 名额满时踢掉最旧的连接（而不是拒绝新连接）：浏览器刷新不会断开旧 MJPEG 请求，
  纯计数会被孤儿占满，导致“刷新几次后视频永久 503”（实测踩过，见 _Viewer 注释）。
* 同一帧的 JPEG 编码在多个观看者间共享，观看者数量增加不会线性增加 CPU。
* 深度图单位是 **厘米(16UC1)** —— 本相机实测定论，转米是 /100，**不是 /1000**。

对外接口
--------
    broker = VideoBroker(node, store, detector=None)
    StreamingResponse(broker.stream('color'), media_type=MJPEG_CT)
"""
from __future__ import annotations

import asyncio
import threading
import time

import cv2
import numpy as np

from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image

MJPEG_CT = 'multipart/x-mixed-replace; boundary=frame'

# 深度伪彩显示范围（米）
DEPTH_NEAR = 0.2
DEPTH_FAR = 2.5


class FrameSlot:
    """最新帧槽位（生产者=ROS 回调线程，消费者=异步 MJPEG 生成器）。

    消费者用**非阻塞** latest() 轮询 + asyncio.sleep 控节，而不是条件变量阻塞等待：
    阻塞式等待会把生成器所在线程卡住，而 Starlette 无法中断阻塞中的同步生成器，
    客户端断开后线程就永久泄漏（实测会把进程线程池耗尽 → 整个后端卡死）。
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._frame = None
        self._seq = 0

    def set(self, frame) -> None:
        with self._lock:
            self._frame = frame
            self._seq += 1

    def latest(self):
        """非阻塞取当前帧：返回 (frame, seq)。"""
        with self._lock:
            return self._frame, self._seq


class _SourceState:
    __slots__ = ('subs', 'refs', 'slot', 'last_conv', 'last_pull', 'subscribed',
                 'enc_lock', 'enc_jpg', 'enc_seq')

    def __init__(self):
        self.subs = []
        self.refs = 0
        self.slot = FrameSlot()
        self.last_conv = 0.0      # 上次 cv_bridge 转换时间（用于丢帧降频）
        self.last_pull = 0.0      # 上次被观看者取帧的时间（看门狗用）
        self.subscribed = False   # 是否已真正建立订阅（只由 executor 线程改写）
        # 编码缓存：同一帧（seq 相同）只编码一次，多个观看者复用（省 Jetson CPU）
        self.enc_lock = threading.Lock()
        self.enc_jpg = None
        self.enc_seq = -1


class _Viewer:
    """一个观看者（一个 MJPEG 连接）句柄。

    为什么用句柄而不是纯计数：
    浏览器**刷新**页面时，旧的 MJPEG 请求不会被主动断开（实测），旧生成器会一直
    取帧写入已无人读取的 socket —— 纯计数很快被孤儿占满，之后新页面只能收到 503，
    反复刷新几次视频就永远不可用了。所以这里保留句柄，名额满时踢掉**最老的**那个。
    """

    __slots__ = ('name', 'stop', 'since', 'last_pull')

    def __init__(self, name: str):
        self.name = name
        self.stop = False        # 置真后生成器下一轮循环就退出并归还名额
        self.since = time.time()
        self.last_pull = time.time()


class VideoBroker:
    """三路视频源的管理器（带引用计数的按需订阅）。"""

    SOURCES = ('color', 'depth', 'detect')

    def __init__(self, node, store, detector=None,
                 fps: float = 10.0, quality: int = 70, max_viewers: int = 3,
                 color_topic: str = '/camera/color/image_raw',
                 depth_topic: str = '/camera/depth/image_raw'):
        self.node = node
        self.store = store
        self.detector = detector
        self.fps = float(fps)
        self.quality = int(quality)
        self.max_viewers = int(max_viewers)
        self.color_topic = color_topic
        self.depth_topic = depth_topic

        self.bridge = CvBridge()
        self._lock = threading.Lock()
        self._states: dict[str, _SourceState] = {}
        self.viewers: dict[str, int] = {s: 0 for s in self.SOURCES}
        self._viewers: dict[str, list] = {s: [] for s in self.SOURCES}
        self._last_depth_info = ''
        # 丢帧降频：MJPEG 只需 fps，源可能是 30Hz —— **必须在 cv_bridge 之前丢弃**，
        # 否则每帧都做一次 921KB 的转换，GIL 被占满，整个后端（含 /api/*）都会卡死（实测）。
        self.min_interval = 1.0 / max(self.fps, 1.0)

        # ⚠️⚠️ **rclpy 实体只能在 executor 线程里创建/销毁**：
        #    看门狗线程或 asyncio 线程直接 destroy_subscription 会与正在 spin 的
        #    executor 死锁（实测：浏览器关页后事件循环卡死，accept 队列积压 20 个连接）。
        #    所以：任意线程只改 refs 计数，真正的订/退订由这个 2Hz timer 在
        #    executor 线程里按“期望状态”幂等地同步。
        self._sync_timer = node.create_timer(0.5, self._sync_subscriptions)

        self._watchdog = threading.Thread(target=self._watch_loop,
                                         name='video-watchdog', daemon=True)
        self._watchdog.start()

    # ────────────── 订阅生命周期 ──────────────

    # ───────────── 订阅生命周期（只在 executor 线程执行）─────────────

    def _sync_subscriptions(self) -> None:
        """按“期望状态”幂等地建立/拆除订阅。**必须在 executor 线程执行**。

        期望状态 = refs > 0；实际状态 = st.subscribed（以及 detector.active）。
        幂等写法可以天然处理"刚连上又断开"这类竞态（不会出现订了又退错乱）。
        """
        with self._lock:
            items = list(self._states.items())
        for name, st in items:
            want = st.refs > 0
            if want and not st.subscribed:
                self._do_subscribe(name, st)
            elif not want and st.subscribed:
                self._do_unsubscribe(name, st)

        # 识别器的生命周期同样只能在这里启停（它自己也会 create/destroy 订阅）
        if self.detector is not None:
            det = self.detector
            if det.want_active and not det.active:
                det.start_now()
            elif not det.want_active and det.active:
                det.stop_now()

    def _do_subscribe(self, name: str, st: _SourceState) -> None:
        if st.subscribed:
            return
        if name == 'color':
            st.subs.append(self.node.create_subscription(
                Image, self.color_topic, self._make_color_cb(st), qos_profile_sensor_data))
        elif name == 'depth':
            st.subs.append(self.node.create_subscription(
                Image, self.depth_topic, self._make_depth_cb(st), qos_profile_sensor_data))
        elif name == 'detect':
            # 识别叠加的画面由 PreviewDetector 产出；这里只是“订阅”它的输出槽
            # ⚠️ 必须传 st.slot（FrameSlot），不能传 _SourceState 本身
            if self.detector is not None:
                self.detector.acquire(st.slot)
        st.subscribed = True
        self.node.get_logger().info(f'[video] 开始订阅源: {name}')

    def _do_unsubscribe(self, name: str, st: _SourceState) -> None:
        if not st.subscribed:
            return
        if name == 'detect':
            if self.detector is not None:
                self.detector.release(st.slot)
        else:
            for sub in st.subs:
                self.node.destroy_subscription(sub)
            st.subs = []
        st.subscribed = False
        self.node.get_logger().info(f'[video] 停止订阅源: {name}')

    def _acquire(self, name: str) -> _Viewer:
        """占用一个观看者名额（任意线程可调；**不碰 rclpy 实体**）。

        名额满时**不报错**，而是踢掉最老的观看者（通常是浏览器刷新后残留的孤儿），
        保证“刚打开/刚刷新”的页面一定能看到画面。
        """
        with self._lock:
            st = self._states.setdefault(name, _SourceState())
            lst = self._viewers.setdefault(name, [])
            while len(lst) >= self.max_viewers:
                oldest = min(lst, key=lambda v: v.since)
                oldest.stop = True
                lst.remove(oldest)            # 立即腾出名额（对方下一轮循环会退出）
                self.node.get_logger().warn(
                    f'[video] {name} 观看者已达上限 {self.max_viewers}，'
                    f'踢掉最旧连接（存活 {time.time() - oldest.since:.0f}s）')
            v = _Viewer(name)
            lst.append(v)
            st.refs = len(lst)
            self.viewers[name] = st.refs
            return v

    def _release(self, v: _Viewer) -> None:
        """归还名额（任意线程可调；**不碰 rclpy 实体**）。"""
        with self._lock:
            lst = self._viewers.get(v.name)
            st = self._states.get(v.name)
            if lst is None or st is None:
                return
            if v in lst:
                lst.remove(v)
            st.refs = len(lst)
            self.viewers[v.name] = st.refs

    def _watch_loop(self) -> None:
        """看门狗：回收“已断开但生成器没被关闭”的观看者。

        现实情况：浏览器关标签页/网络断了，Starlette 并不总能 close 掉异步生成器，
        结果订阅与编码循环永远不退 —— 必须在机器人上防止这种泄漏
        （实测验过：curl 中途断开后 viewers 会残留）。
        """
        while True:
            time.sleep(2.0)
            now = time.time()
            with self._lock:
                stale = [v for lst in self._viewers.values() for v in lst
                         if now - v.last_pull > 5.0]
            for v in stale:
                self.node.get_logger().warn(f'[video] 回收失联观看者: {v.name}')
                self._release(v)

    # ────────────── 图像回调 ──────────────

    def _make_color_cb(self, st: _SourceState):
        def _cb(msg: Image):
            self.store.tick('/camera/color/image_raw')
            now = time.time()
            if now - st.last_conv < self.min_interval:      # 丢帧（不转换，省 GIL）
                return
            st.last_conv = now
            try:
                img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            except Exception as exc:
                self.node.get_logger().warn(f'[video] 彩色转换失败: {exc}')
                return
            st.slot.set(img)
        return _cb

    def _make_depth_cb(self, st: _SourceState):
        def _cb(msg: Image):
            self.store.tick('/camera/depth/image_raw')
            now = time.time()
            if now - st.last_conv < self.min_interval:      # 丢帧
                return
            st.last_conv = now
            try:
                raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            except Exception as exc:
                self.node.get_logger().warn(f'[video] 深度转换失败: {exc}')
                return
            st.slot.set(raw)
        return _cb

    # ────────────── 渲染 ──────────────

    def render_depth(self, raw) -> np.ndarray:
        """深度 → 伪彩（含单位换算与中心距离标注）。

        ⚠️ 本相机 16UC1 单位是厘米：/100 得米。若改成 /1000 会出现
        "最远只有 40cm" 的经典假象（项目踩过，见 AGENTS.md）。
        """
        if raw.dtype == np.uint16:
            d = raw.astype(np.float32) / 100.0          # cm → m
        elif raw.dtype == np.float32:
            d = raw.copy()                              # 已经是米
        else:
            d = raw.astype(np.float32) / 100.0

        valid = (d > 0.05) & (d < 12.0)
        dn = np.clip(d, DEPTH_NEAR, DEPTH_FAR)
        norm = ((dn - DEPTH_NEAR) / (DEPTH_FAR - DEPTH_NEAR) * 255.0).astype(np.uint8)
        color = cv2.applyColorMap(norm, cv2.COLORMAP_TURBO)
        color[~valid] = (0, 0, 0)

        h, w = color.shape[:2]
        cy, cx = h // 2, w // 2
        center = float(d[cy, cx]) if valid[cy, cx] else 0.0
        self._last_depth_info = f'center={center:.2f}m  range={DEPTH_NEAR}-{DEPTH_FAR}m'
        cv2.putText(color, f'{center:.2f} m (center)', (8, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(color, 'depth: cm/100 -> m', (8, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.circle(color, (cx, cy), 5, (255, 255, 255), 1, cv2.LINE_AA)
        return color

    @staticmethod
    def _nosignal(name: str) -> np.ndarray:
        img = np.full((480, 640, 3), 18, np.uint8)
        text = f'{name}: no signal'
        cv2.putText(img, text, (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (120, 120, 120), 2, cv2.LINE_AA)
        return img

    def _encode(self, frame) -> bytes:
        ok, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.quality])
        return buf.tobytes() if ok else b''

    # ────────────── MJPEG 流 ──────────────

    def _render_jpg(self, name: str, st: _SourceState, frame, seq: int) -> bytes:
        """转换（深度伪彩）+ JPEG 编码，带同源同帧缓存。**在线程里调用**。

        多个观看者看同一源时只编码一次：3 个观看者不会变成 3 倍 CPU。
        """
        with st.enc_lock:
            if st.enc_jpg is not None and st.enc_seq == seq:
                return st.enc_jpg
        if name == 'depth' and frame is not None and getattr(frame, 'ndim', 0) == 2:
            frame = self.render_depth(frame)
        jpg = self._encode(frame)
        with st.enc_lock:
            if jpg:
                st.enc_jpg, st.enc_seq = jpg, seq
        return jpg

    def stream(self, name: str):
        """返回**异步** MJPEG 生成器。

        ⚠️ 名额在调用时就占用（而不是首次迭代），否则超出上限只能靠 500 报错，
           拿不到可读的信息。名额满时踢掉最旧的连接，**不会拒绝新页面**。
        ⚠️ 必须用异步生成器：同步生成器会被 Starlette 丢进线程池，而一个永不结束的
           流会**永久占用一个池线程**；客户端断开时无法中断 → 线程泄漏 → 池耗尽 →
           连 /api/ping 都没人处理（实测踩过）。

        关于“浏览器刷新”：Starlette 1.6.0 在 ASGI 2.4 下走 `await stream_response(send)`
        分支（不做 listen_for_disconnect），而浏览器刷新时旧 MJPEG 请求不会主动断开、
        socket 也不会报 OSError，所以旧生成器会继续跑。**不要自己调
        request.is_disconnected()**（其内部用已取消的 CancelScope await receive，可能
        把 Cancelled 抛进生成器/与 Starlette 抢同一个 receive 通道，实测引起页面卡住）；
        本项目改用“名额满就踢最旧”的确定性策略。
        """
        if name not in self.SOURCES:
            raise RuntimeError(f'未知视频源: {name}')
        v = self._acquire(name)           # 名额满了会踢掉最旧的观看者
        st = self._states[name]
        return self._stream_impl(name, st, v)

    async def _stream_impl(self, name: str, st: _SourceState, v: _Viewer):
        period = 1.0 / max(self.fps, 1.0)
        last_seq = -1
        idle_since = time.time()
        try:
            while True:
                if v.stop:               # 名额被更“新”的观看者抢占 → 优雅退出
                    self.node.get_logger().info(f'[video] 观看者被替换，关闭旧流: {name}')
                    return
                v.last_pull = time.time()
                frame, seq = st.slot.latest()
                if frame is None or seq == last_seq:
                    # 没有新帧：短暂等待；持续 1s 无新帧就回一张“无信号”帧
                    await asyncio.sleep(period)
                    if time.time() - idle_since <= 1.0:
                        continue
                    frame, seq = self._nosignal(name), -2
                else:
                    last_seq = seq
                    idle_since = time.time()

                # 深度伪彩 + JPEG 编码都放线程（不阻塞事件循环），同帧只编码一次
                jpg = await asyncio.to_thread(self._render_jpg, name, st, frame, seq)
                if jpg:
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n'
                           b'Content-Length: ' + str(len(jpg)).encode() + b'\r\n\r\n'
                           + jpg + b'\r\n')
                await asyncio.sleep(period)
        finally:
            self._release(v)
