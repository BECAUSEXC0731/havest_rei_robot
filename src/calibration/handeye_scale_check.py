#!/usr/bin/env python3
"""
手眼标定 尺度自检（离线诊断）

用已保存的 hand_eye_result.json 里的标定点对 (robot_mm, rvec, tvec)，
拟合带尺度 s 的 p_local 模型:
    robot_pos = s * (R @ (R_board @ p_local + t_board)) + t

判断：
  |s-1| < 8%  → 相机内参/棋盘格边长与机械臂毫米一致，问题在采集噪声（棋盘格太斜/太小）
  s 明显偏离 1 → 存在尺度失配（fx 或 square_size 与实物不符）：
      若棋盘格 29mm 可靠 → 实际 fx ≈ s * fx_used
      若内参可靠        → 实际棋盘格 ≈ s * 29mm
"""
import json
import os
import numpy as np
import cv2
import yaml
from scipy.optimize import least_squares

ROOT = '/home/ubuntu/ros2fox'
COLOR_INFO = os.path.join(ROOT, 'calib_data', 'color', 'color_camera_info.yaml')
RESULT = os.path.join(ROOT, 'calib_result', 'hand_eye_result.json')

BOARD_SIZE = (4, 6)
SQUARE = 0.029  # 实测 29mm


def main():
    with open(RESULT) as f:
        data = json.load(f)
    pairs = data['calib_pairs']
    print(f"加载 {len(pairs)} 个标定点对: {RESULT}")

    if not pairs or 'rvec' not in pairs[0]:
        print("[错误] 保存的标定点对没有棋盘格位姿（rvec/tvec），无法自检")
        return

    r_pts = np.array([[p['robot_mm'][0]/1000, p['robot_mm'][1]/1000,
                       p['robot_mm'][2]/1000] for p in pairs], dtype=np.float64)
    poses = [(np.array(p['rvec'], np.float64), np.array(p['tvec'], np.float64))
             for p in pairs]

    objp = np.zeros((BOARD_SIZE[0]*BOARD_SIZE[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:BOARD_SIZE[0], 0:BOARD_SIZE[1]].T.reshape(-1, 2)
    objp *= SQUARE
    board_center = np.array([(BOARD_SIZE[0]-1)/2*SQUARE,
                             (BOARD_SIZE[1]-1)/2*SQUARE, 0.0])

    def board_center_cam(rv, tv):
        R, _ = cv2.Rodrigues(np.array(rv, np.float64))
        return R @ board_center + np.array(tv, np.float64).flatten()

    centers = np.array([board_center_cam(rv, tv) for rv, tv in poses])

    # 初值：中心点刚性拟合
    rc, cc = r_pts.mean(0), centers.mean(0)
    H = (r_pts - rc).T @ (centers - cc) + np.eye(3)*1e-9
    U, _, Vt = np.linalg.svd(H)
    R0 = Vt.T @ U.T
    if np.linalg.det(R0) < 0:
        Vt[-1, :] *= -1
        R0 = Vt.T @ U.T
    rv0, _ = cv2.Rodrigues(R0)
    t0 = rc - R0 @ cc

    def residuals(p):
        R_, _ = cv2.Rodrigues(np.array(p[:3]))
        t_ = p[3:6]; p_local = p[6:9]; s = p[9]
        errs = []
        for rp, (rv_b, tv_b) in zip(r_pts, poses):
            Rb, _ = cv2.Rodrigues(np.array(rv_b, np.float64))
            tcp = Rb @ p_local + np.array(tv_b, np.float64).flatten()
            pred = s * (R_ @ tcp) + t_
            errs.extend((pred - rp) * 1000)
        return errs

    best = None
    for p0 in (np.zeros(3), np.array([0.12, 0, 0]), np.array([-0.12, 0, 0]),
               np.array([0, 0.12, 0]), np.array([0, -0.12, 0]),
               np.array([0, 0, 0.12]), np.array([0, 0, -0.12])):
        res = least_squares(residuals, np.r_[rv0.flatten(), t0, p0, 1.0],
                            method='lm', max_nfev=3000)
        if best is None or np.sum(np.square(res.fun)) < np.sum(np.square(best.fun)):
            best = res
    if best is None:
        print("[错误] 拟合失败")
        return

    s = float(best.x[9])
    p_local = best.x[6:9]
    errs = np.array([np.linalg.norm(best.fun[i*3:(i+1)*3])
                     for i in range(len(r_pts))])

    # 读 fx_used
    with open(COLOR_INFO) as f:
        d = yaml.safe_load(f)
    fx_used = d['camera_matrix']['data'][0]

    print("\n" + "=" * 60)
    print("  手眼标定尺度自检结果")
    print("=" * 60)
    print(f"  拟合尺度 s = {s:.3f}")
    print(f"  p_local (mm) = [{p_local[0]*1000:.0f}, {p_local[1]*1000:.0f}, {p_local[2]*1000:.0f}]")
    print(f"  平均误差 = {errs.mean():.1f} mm, 最大 = {errs.max():.1f} mm")
    print(f"  当前 fx = {fx_used:.2f}")
    if abs(s - 1.0) > 0.08:
        print("\n  [警告] 尺度失配!")
        print(f"    若棋盘格 29mm 可靠 → 实际 fx ≈ {s*fx_used:.1f} (当前 {fx_used:.1f})")
        print(f"    若 fx 可靠          → 实际棋盘格 ≈ {s*SQUARE*1000:.1f} mm (当前 29)")
        print("  → 需修正内参或边长后重标；若是 fx 问题，建议重采彩色内参（加大角度/远近多样性）")
    else:
        print("\n  [OK] 尺度自检通过")
        if errs.mean() > 5.0:
            print("  → 误差大不是尺度问题，而是采集噪声：棋盘格太小/太斜/roll 变化大，")
            print("    建议把棋盘格贴得更正对相机、减小到端偏移或缩短距离后重采")
    print("=" * 60)


if __name__ == '__main__':
    main()
