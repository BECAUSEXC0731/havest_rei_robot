"""
深度图 → 3D 坐标转换工具
利用相机内参将 2D 像素 + 深度值转换为相机坐标系下的 3D 点，
再通过手眼标定矩阵转换到机器人基座坐标系。
"""
import math
import numpy as np
import json
import os
try:
    import yaml
except ImportError:
    yaml = None


def load_hand_eye_calibration(calib_path: str) -> np.ndarray:
    """
    加载手眼标定结果中的 4×4 变换矩阵。
    返回: camera → robot_base 的变换矩阵 (4×4)
    """
    if not os.path.exists(calib_path):
        raise FileNotFoundError(f"手眼标定文件不存在: {calib_path}")

    with open(calib_path) as f:
        data = json.load(f)

    T = np.array(data['transform_4x4'], dtype=np.float64)
    print(f"[深度] 加载手眼标定: {calib_path}")
    print(f"[深度] 平均误差: {data.get('avg_error_mm', 'N/A')} mm")
    return T


def pixel_to_camera_3d(u: int, v: int, depth_m: float,
                        camera_matrix: np.ndarray) -> np.ndarray:
    """
    将像素坐标 (u, v) + 深度值 (米) 转为相机坐标系下的 3D 点。
    公式:
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        z = depth
    Args:
        u, v: 像素坐标
        depth_m: 深度值（米）
        camera_matrix: 3×3 相机内参矩阵
    Returns:
        (x, y, z) 相机坐标系下的 3D 点（米）
    """
    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]

    x = (u - cx) * depth_m / fx
    y = (v - cy) * depth_m / fy
    z = depth_m

    return np.array([x, y, z], dtype=np.float64)


def camera_to_robot_3d(point_cam: np.ndarray,
                       T_cam_to_robot: np.ndarray) -> np.ndarray:
    """
    将相机坐标系下的 3D 点转换到机器人基座坐标系。
    Args:
        point_cam: (x, y, z) 相机坐标系（米）
        T_cam_to_robot: 4×4 变换矩阵
    Returns:
        (x, y, z) 机器人坐标系（米）
    """
    p_h = np.array([point_cam[0], point_cam[1], point_cam[2], 1.0])
    p_robot = T_cam_to_robot @ p_h
    return p_robot[:3]


def get_depth_at_pixel(depth_image: np.ndarray, u: int, v: int,
                       window_size: int = 5, max_search: int = 16,
                       min_depth: float = 0.1, max_depth: float = 2.0) -> float:
    """
    从对齐后的深度图中获取指定像素的深度值（米）。
    只在窗口内取中位数抗噪；若窗口内全是空洞(0/NaN/超范围)，
    则逐步扩大搜索半径，取最近(最小)的有效深度——葡萄表面是最近物体，最可能是它。
    Args:
        depth_image: 深度图 (H, W)，单位：米
        u, v: 像素坐标
        window_size: 采样窗口大小（奇数）
        max_search: 空洞时的最大搜索半径（像素）
        min_depth / max_depth: 有效深度范围（米），排除传感器近零噪声/超远噪声。
            注意：本相机深度实际工作范围约 0.1~0.4m，min_depth 用 0.3 会把
            近距离葡萄(14~40cm)全过滤掉导致“no depth”（2026-08-08 已从 0.3 降到 0.1）
    Returns:
        深度值（米），无效返回 None
    """
    h, w = depth_image.shape[:2]
    if u < 0 or u >= w or v < 0 or v >= h:
        return None

    def _valid_vals(v_start, v_end, u_start, u_end):
        patch = depth_image[v_start:v_end, u_start:u_end]
        return patch[(patch >= min_depth) & (patch <= max_depth) &
                     (~np.isnan(patch)) & (~np.isinf(patch))]

    # 1) 小窗口：中位数滤波抗噪
    half = window_size // 2
    valid = _valid_vals(max(0, v - half), min(h, v + half + 1),
                        max(0, u - half), min(w, u + half + 1))
    if len(valid) > 0:
        return float(np.median(valid))

    # 2) 小窗口全空洞 → 逐步扩大半径，取最近(最小)有效深度
    for r in range(window_size // 2 + 2, max_search + 1, 2):
        valid = _valid_vals(max(0, v - r), min(h, v + r + 1),
                            max(0, u - r), min(w, u + r + 1))
        if len(valid) > 0:
            return float(np.min(valid))

    return None


def depth_to_robot_3d(u: int, v: int, depth_image: np.ndarray,
                       camera_matrix: np.ndarray,
                       T_cam_to_robot: np.ndarray,
                       window_size: int = 5):
    """
    一步完成: 像素 → 深度 → 相机3D → 机器人3D（毫米）。
    Args:
        u, v: 像素坐标
        depth_image: 深度图 (米)
        camera_matrix: 3×3 相机内参
        T_cam_to_robot: 4×4 相机→机器人变换
    Returns:
        (point_robot_mm, depth_m) or (None, None)
        point_robot_mm: (x, y, z) 毫米
        depth_m: 原始深度值（米）
    """
    depth_m = get_depth_at_pixel(depth_image, u, v, window_size)
    if depth_m is None or depth_m <= 0:
        return None, None

    pt_cam = pixel_to_camera_3d(u, v, depth_m, camera_matrix)
    pt_robot = camera_to_robot_3d(pt_cam, T_cam_to_robot)

    # 转换到毫米
    pt_robot_mm = pt_robot * 1000.0
    return pt_robot_mm, depth_m


def depth_to_robot_3d_stable(u: int, v: int, depth_frames,
                              camera_matrix: np.ndarray,
                              T_cam_to_robot: np.ndarray,
                              window_size: int = 5, max_search: int = 16):
    """
    跨帧取稳定深度并转机器人3D（毫米）。
    对最近若干帧在该像素附近的有效深度取中位数，抗葡萄这类深度闪烁。
    Args:
        depth_frames: 最近若干帧的深度图列表（每帧单位：米）
        其余同 depth_to_robot_3d
    Returns:
        (point_robot_mm, depth_m) or (None, None)
    """
    vals = []
    for depth in depth_frames:
        if depth is None:
            continue
        d = get_depth_at_pixel(depth, u, v, window_size, max_search)
        if d is not None and d > 0:
            vals.append(d)
    if not vals:
        return None, None
    depth_m = float(np.median(vals))

    pt_cam = pixel_to_camera_3d(u, v, depth_m, camera_matrix)
    pt_robot = camera_to_robot_3d(pt_cam, T_cam_to_robot)
    pt_robot_mm = pt_robot * 1000.0
    return pt_robot_mm, depth_m


# ═══════════════════════ 手动深度对齐 (D2C) ═══════════════════════
# Astra Pro 驱动自带 D2C 对齐崩溃(固件参数NaN)，改用手动对齐：
# 用标定好的 彩色↔IR 外参 T_color_to_ir，把 RGB 像素映射到 IR/深度系取深度。

def load_d2c_config(extrinsic_path: str, ir_info_path: str):
    """
    加载手动对齐配置：返回 (K_ir, T_color_to_ir)，文件缺失/解析失败返回 None。
        extrinsic_path: calib_result/color_ir_extrinsic.json (含 T_color_to_ir_4x4)
        ir_info_path:   calib_data/ir/ir_camera_info.yaml (IR 内参，即深度内参)
    """
    if yaml is None or not os.path.exists(extrinsic_path) or not os.path.exists(ir_info_path):
        return None
    try:
        with open(ir_info_path) as f:
            d = yaml.safe_load(f)
        K_ir = np.array(d['camera_matrix']['data'], dtype=np.float64).reshape(3, 3)
        with open(extrinsic_path) as f:
            e = json.load(f)
        T = np.array(e['T_color_to_ir_4x4'], dtype=np.float64).reshape(4, 4)
        return K_ir, T
    except Exception:
        return None


def color_pixel_to_camera_3d(u: int, v: int, depth_image: np.ndarray,
                             K_color: np.ndarray, K_ir: np.ndarray,
                             T_color_to_ir: np.ndarray,
                             window_size: int = 5, max_search: int = 16,
                             max_iter: int = 4):
    """
    手动 D2C：RGB 像素 (u,v) → 彩色系 3D 点（米）。
    沿彩色射线迭代：点变换到 IR/深度系 → 取该像素深度 → 变换回彩色系，2~4 次收敛。
    取不到有效深度返回 None。
    """
    fx_c, fy_c = K_color[0, 0], K_color[1, 1]
    cx_c, cy_c = K_color[0, 2], K_color[1, 2]
    fx_i, fy_i = K_ir[0, 0], K_ir[1, 1]
    cx_i, cy_i = K_ir[0, 2], K_ir[1, 2]
    R = T_color_to_ir[:3, :3]
    t = T_color_to_ir[:3, 3]
    Rt = R.T

    dir_c = np.array([(u - cx_c) / fx_c, (v - cy_c) / fy_c, 1.0])
    d = 0.5
    last_pt = None
    for _ in range(max_iter):
        P_c = d * dir_c
        P_i = R @ P_c + t
        if P_i[2] <= 0:
            break
        u_i = int(round(fx_i * P_i[0] / P_i[2] + cx_i))
        v_i = int(round(fy_i * P_i[1] / P_i[2] + cy_i))
        d_i = get_depth_at_pixel(depth_image, u_i, v_i, window_size, max_search)
        if d_i is None or d_i <= 0:
            break
        P_i_actual = np.array([(u_i - cx_i) / fx_i * d_i,
                               (v_i - cy_i) / fy_i * d_i,
                               d_i])
        P_c_actual = Rt @ (P_i_actual - t)
        if P_c_actual[2] <= 0:
            break
        last_pt = P_c_actual
        if abs(P_c_actual[2] - d) < 0.003:   # 收敛阈值 3mm
            break
        d = P_c_actual[2]
    return last_pt


def depth_to_robot_3d_d2c_stable(u: int, v: int, depth_frames,
                                 K_color: np.ndarray, K_ir: np.ndarray,
                                 T_color_to_ir: np.ndarray,
                                 T_cam_to_robot: np.ndarray,
                                 window_size: int = 5, max_search: int = 16):
    """
    手动 D2C + 多帧中值：RGB 像素 → 彩色系3D → 机器人3D（毫米）。
    Args:
        depth_frames: 最近若干帧深度图列表（米，IR/深度系，未对齐）
    Returns:
        (point_robot_mm, depth_m) or (None, None)
    """
    pts = []
    for depth in depth_frames:
        if depth is None:
            continue
        pt = color_pixel_to_camera_3d(u, v, depth, K_color, K_ir,
                                      T_color_to_ir, window_size, max_search)
        if pt is not None:
            pts.append(pt)
    if not pts:
        return None, None
    pt_med = np.median(np.array(pts), axis=0)
    pt_robot = camera_to_robot_3d(pt_med, T_cam_to_robot)
    return pt_robot * 1000.0, float(pt_med[2])


def depth_to_robot_3d_nearest_in_box(bbox, depth_frames,
                                     K_color: np.ndarray, K_ir: np.ndarray,
                                     T_color_to_ir: np.ndarray,
                                     T_cam_to_robot: np.ndarray,
                                     step: int = 6, window_size: int = 5,
                                     max_search: int = 16, max_iter: int = 4):
    """
    手动 D2C：在检测框内找最近(最小深度)的有效 3D 点，转机器人坐标(毫米)。

    适用于深色/稀疏深度的葡萄：中心像素常无深度，但框内总有若干有效点；
    葡萄是前景物体，框内最近点即其前表面，比中心单点稳健得多。

    Args:
        bbox: [x1, y1, x2, y2]（彩色图像素）
        depth_frames: 最近若干帧深度图列表（米，IR/深度系，未对齐）
        step: 框内采样步长（像素），越大越快、越粗糙
    Returns:
        (point_robot_mm, depth_m) or (None, None)
    """
    x1, y1, x2, y2 = map(int, bbox)
    if x2 <= x1 or y2 <= y1:
        return None, None

    best_z = None
    best_pt = None
    for depth in depth_frames:
        if depth is None:
            continue
        h, w = depth.shape[:2]
        for v in range(max(0, y1), min(h, y2), step):
            for u in range(max(0, x1), min(w, x2), step):
                pt = color_pixel_to_camera_3d(u, v, depth, K_color, K_ir,
                                              T_color_to_ir, window_size,
                                              max_search, max_iter)
                if pt is not None and pt[2] > 0:
                    if best_z is None or pt[2] < best_z:
                        best_z = pt[2]
                        best_pt = pt

    if best_pt is None:
        return None, None
    pt_robot = camera_to_robot_3d(best_pt, T_cam_to_robot)
    return pt_robot * 1000.0, float(best_z)


# ═══════════════════════ 抓取可行性判定（可抓性） ═══════════════════════
# 判定只负责"坐标是否落在可达域内"(工作空间盒 + 可选半径约束/自适应裕度)，
# 不参与任何 3D 坐标计算 → 调整判定容度不会影响定位/抓取精度。

GRASP = 0         # 完全可达
MARGINAL = 1      # 临界可达（在容差带内，可微调/兜底）
UNREACHABLE = 2   # 不可达

DEFAULT_GRASP_CHECK = {
    'margin_xy_mm': 10.0,        # XY 向内安全裕度（越大越保守）
    'margin_z_mm': 10.0,         # Z 向内安全裕度
    'marginal_mm': 0.0,          # 盒外 ≤ 该值的"临界可达"容差带；0=关闭
    'margin_scale_per_m': 0.0,   # 自适应裕度：每远 1m 额外增加的 mm；0=关闭
    'radius_min_mm': 0.0,        # 水平半径 hypot(x,y) 下限；0=关闭
    'radius_max_mm': 0.0,        # 水平半径 hypot(x,y) 上限；0=关闭
}


def load_grasp_check(cfg: dict) -> dict:
    """从 harvest_config.yaml 的 arm.grasp_check 读取判定参数（缺失用默认）。"""
    gc = dict(DEFAULT_GRASP_CHECK)
    raw = ((cfg or {}).get('arm', {}) or {}).get('grasp_check', {}) or {}
    for k in DEFAULT_GRASP_CHECK:
        v = raw.get(k)
        if v is not None:
            gc[k] = float(v)
    return gc


def classify_reach(x: float, y: float, z: float, ws: dict, gc: dict):
    """工作空间可抓性分级（单位 mm）。

    Returns:
        (level, code): level 0=GRASP / 1=MARGINAL / 2=UNREACHABLE
    Args:
        ws: {'x_min','x_max','y_min','y_max','z_min','z_max'} (mm)
        gc: load_grasp_check() 的字典

    规则:
      轴内缩 margin 后仍在盒内          → 该轴 0
      超出内缩盒但 ≤ marginal_mm 容差带 → 该轴 1
      超出更多                          → 该轴 2
    可选水平半径约束用于剔除"盒角落"的假可达。
    """
    mag = gc['margin_scale_per_m'] * (math.hypot(x, y) / 1000.0)
    mxy = gc['margin_xy_mm'] + mag
    mz = gc['margin_z_mm'] + mag
    band = abs(gc['marginal_mm'])

    def axis_level(v, lo, hi, m):
        if lo + m <= v <= hi - m:
            return 0
        if lo + m - band <= v <= hi - m + band:
            return 1
        return 2

    levels = {
        'X': axis_level(x, ws['x_min'], ws['x_max'], mxy),
        'Y': axis_level(y, ws['y_min'], ws['y_max'], mxy),
        'Z': axis_level(z, ws['z_min'], ws['z_max'], mz),
    }

    r = math.hypot(x, y)
    if gc['radius_max_mm'] > 0:
        if r > gc['radius_max_mm'] + band:
            levels['R'] = 2
        elif r > gc['radius_max_mm']:
            levels['R'] = 1
    if gc['radius_min_mm'] > 0:
        if r < gc['radius_min_mm'] - band:
            levels['R'] = 2
        elif r < gc['radius_min_mm'] and levels.get('R', 0) < 1:
            levels['R'] = 1

    level = max(levels.values())
    if level == 0:
        return GRASP, 'GRASP'
    bad = ''.join(k for k, lv in levels.items() if lv == level)
    return level, ('MARGINAL:' + bad if level == 1 else 'NO:' + bad)


def clamp_to_workspace(x: float, y: float, z: float, ws: dict,
                       gc: dict | None = None,
                       inward_mm: float = 0.0):
    """把不可达坐标夹到工作空间内**最近的可达点**（兜底抓取用，2026-09-28）。

    规则：
      · 各轴超出 [lo, hi] → 夹到边界，再按 ``inward_mm`` 向内收
        （避免正好压在边界上被机械臂/驱动判不可达）
      · 若配了 ``radius_max_mm`` / ``radius_min_mm``（水平半径约束）→ 把水平分量
        (x, y) 按比例缩/放到该半径边界

    Args:
        x, y, z: 机器人系坐标 (mm)
        ws: {'x_min','x_max','y_min','y_max','z_min','z_max'}
        gc: load_grasp_check() 的字典（可为 None = 不管半径约束）
        inward_mm: 夹到边界后再向内收的距离 (mm)
    Returns:
        (x2, y2, z2, moved_mm) —— 夹取后的点，以及相对原点移动了多少 mm
        （moved_mm 越小说明该目标离可达域越近）
    """
    inward = max(0.0, float(inward_mm))

    def _clamp(v, lo, hi):
        lo2, hi2 = lo + inward, hi - inward
        if lo2 > hi2:                      # 区间比 inward 还窄 → 取中点
            lo2 = hi2 = (lo + hi) / 2.0
        return min(max(v, lo2), hi2)

    x2 = _clamp(x, ws['x_min'], ws['x_max'])
    y2 = _clamp(y, ws['y_min'], ws['y_max'])
    z2 = _clamp(z, ws['z_min'], ws['z_max'])

    if gc:
        r = math.hypot(x2, y2)
        r_max = float(gc.get('radius_max_mm', 0.0) or 0.0)
        r_min = float(gc.get('radius_min_mm', 0.0) or 0.0)
        if r_max > 0 and r > max(0.0, r_max - inward) and r > 1e-6:
            s = max(0.0, r_max - inward) / r
            x2, y2 = x2 * s, y2 * s
        elif r_min > 0 and r < (r_min + inward) and r > 1e-6:
            s = (r_min + inward) / r
            x2, y2 = x2 * s, y2 * s

    moved = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2 + (z2 - z) ** 2)
    return x2, y2, z2, moved
