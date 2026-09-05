#!/usr/bin/env python3
"""
draw_keepout.py — 交互式在地图上绘制禁行区（GUI，OpenCV）

直接在真实地图图像上点鼠标画多边形/矩形/圆形禁行区，保存为
keepout_zones.yaml（与 generate_keepout.py --zones 兼容），
并自动调用 generate_keepout.py 生成掩码 + 预览图。

用法（在有显示的终端 / VNC 里运行）:
  python3 src/fox_navigation_ros2/scripts/draw_keepout.py \\
      --map   maps/test_map.yaml \\
      --zones src/fox_navigation_ros2/config/keepout_zones.yaml \\
      --out   maps/keepout

鼠标 / 键盘:
  左键点击 : 添加顶点（多边形逐点；矩形/圆形选两点）
  右键点击 : 闭合当前多边形
  z        : 撤销当前形状的上一个点
  u        : 删除最近一个完整形状
  1 / 2 / 3: 切换模式 多边形 / 矩形 / 圆形
  s        : 保存到 yaml + 自动生成掩码和预览图（maps/keepout_preview.png）
  q / Esc  : 退出（不保存）

无界面自检（SSH/无显示时验证链路）:
  python3 src/fox_navigation_ros2/scripts/draw_keepout.py \\
      --map maps/test_map.yaml --zones /tmp/zt.yaml --selftest
"""

import argparse
import os
import subprocess
import sys

import cv2
import numpy as np
import yaml
from PIL import Image

ZOOM = 2          # 显示放大倍数，方便点击
FILL_ALPHA = 0.35  # 已闭合禁行区的填充透明度


def load_map(map_yaml):
    """返回 (img_bgr, res, ox, oy, W, H)。W/H 为原始地图像素尺寸。"""
    mdir = os.path.dirname(os.path.abspath(map_yaml))
    with open(map_yaml) as f:
        m = yaml.safe_load(f)
    ox, oy, _ = m['origin']
    res = float(m['resolution'])
    pgm = os.path.join(mdir, m['image'])
    img = np.array(Image.open(pgm).convert('L'))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    H, W = img.shape
    return img_bgr, res, ox, oy, W, H


def disp_to_world(cx, cy, ox, oy, res, H):
    """显示像素(放大后) → 世界坐标(米)。"""
    col = cx / ZOOM
    row = cy / ZOOM
    wx = ox + (col + 0.5) * res
    wy = oy + (H - 1 - row + 0.5) * res
    return wx, wy


def world_to_disp(wx, wy, ox, oy, res, H):
    """世界坐标(米) → 显示像素(放大后)。"""
    col = (wx - ox) / res - 0.5
    row = (H - 1) - (wy - oy) / res - 0.5
    return int(col * ZOOM), int(row * ZOOM)


def save_zones(shapes, path):
    """把形状列表写为 generate_keepout.py 兼容的 zones yaml。返回写入的 zones 列表。"""
    zones = []
    for i, s in enumerate(shapes, 1):
        if s['type'] == 'polygon':
            zones.append({'name': f'zone_{i}', 'type': 'polygon',
                          'points': [list(p) for p in s['points']]})
        elif s['type'] == 'rect':
            x0, y0 = s['p0']
            x1, y1 = s['p1']
            zones.append({'name': f'zone_{i}', 'type': 'rect',
                          'center': [round((x0 + x1) / 2, 3), round((y0 + y1) / 2, 3)],
                          'size': [round(abs(x1 - x0), 3), round(abs(y1 - y0), 3)]})
        elif s['type'] == 'circle':
            zones.append({'name': f'zone_{i}', 'type': 'circle',
                          'center': list(s['center']), 'radius': s['radius']})
    with open(path, 'w') as f:
        yaml.safe_dump({'zones': zones}, f, default_flow_style=False, sort_keys=False)
    return zones


def run_generate(map_yaml, zones_yaml, out):
    """调用 generate_keepout.py 生成掩码 + 预览图。"""
    gen = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generate_keepout.py')
    r = subprocess.run(
        [sys.executable, gen, '--map', map_yaml, '--out', out,
         '--zones', zones_yaml, '--preview'])
    return r.returncode


def run_gui(img, res, ox, oy, W, H, args):
    """打开 OpenCV 交互窗口，在地图上绘制禁行区。需要 DISPLAY（VNC/桌面）。"""
    disp = cv2.resize(img, (W * ZOOM, H * ZOOM), interpolation=cv2.INTER_NEAREST)
    canvas = disp.copy()

    shapes = []           # 已闭合形状
    cur = []              # 当前绘制点（世界坐标米）
    cur_type = 'polygon'  # polygon / rect / circle
    cur_first = None      # 矩形/圆的第一点
    last_mouse = (0.0, 0.0)

    win = 'Draw Keepout Zones'
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    def redraw():
        canvas[:] = disp
        for s in shapes:
            overlay = canvas.copy()
            if s['type'] == 'polygon':
                pts = np.array(
                    [world_to_disp(x, y, ox, oy, res, H) for x, y in s['points']],
                    np.int32).reshape(-1, 1, 2)
                cv2.fillPoly(overlay, [pts], (0, 0, 255))
            elif s['type'] == 'rect':
                px0, py0 = world_to_disp(*s['p0'], ox, oy, res, H)
                px1, py1 = world_to_disp(*s['p1'], ox, oy, res, H)
                cv2.rectangle(overlay, (min(px0, px1), min(py0, py1)),
                              (max(px0, px1), max(py0, py1)), (0, 0, 255), -1)
            elif s['type'] == 'circle':
                cx, cy = world_to_disp(*s['center'], ox, oy, res, H)
                r = int(s['radius'] / res * ZOOM)
                cv2.circle(overlay, (cx, cy), r, (0, 0, 255), -1)
            canvas[:] = cv2.addWeighted(overlay, FILL_ALPHA, canvas, 1 - FILL_ALPHA, 0)
        # 当前未闭合形状
        if cur_type == 'polygon' and len(cur) >= 2:
            pts = np.array([world_to_disp(x, y, ox, oy, res, H) for x, y in cur], np.int32)
            cv2.polylines(canvas, [pts], False, (0, 255, 255), 2)
        if cur_type == 'rect' and cur_first is not None:
            px0, py0 = world_to_disp(*cur_first, ox, oy, res, H)
            px1, py1 = world_to_disp(*last_mouse, ox, oy, res, H)
            cv2.rectangle(canvas, (px0, py0), (px1, py1), (0, 255, 255), 1)
        for i, (x, y) in enumerate(cur):
            px, py = world_to_disp(x, y, ox, oy, res, H)
            cv2.circle(canvas, (px, py), 5, (0, 255, 0), -1)
            cv2.putText(canvas, str(i + 1), (px + 6, py - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        if cur_type == 'polygon' and cur_first is not None and not cur:
            px, py = world_to_disp(*cur_first, ox, oy, res, H)
            cv2.circle(canvas, (px, py), 5, (0, 255, 0), -1)

    def on_mouse(event, x, y, flags, param):
        nonlocal cur, cur_first, last_mouse
        if x < 0 or y < 0 or x >= W * ZOOM or y >= H * ZOOM:
            return
        wx, wy = disp_to_world(x, y, ox, oy, res, H)
        last_mouse = (wx, wy)
        if event == cv2.EVENT_LBUTTONDOWN:
            if cur_type == 'polygon':
                cur.append((round(wx, 3), round(wy, 3)))
                redraw()
            elif cur_type in ('rect', 'circle'):
                if cur_first is None:
                    cur_first = (round(wx, 3), round(wy, 3))
                else:
                    if cur_type == 'rect':
                        shapes.append({'type': 'rect', 'p0': cur_first,
                                       'p1': (round(wx, 3), round(wy, 3))})
                    else:
                        r = ((wx - cur_first[0]) ** 2 + (wy - cur_first[1]) ** 2) ** 0.5
                        shapes.append({'type': 'circle', 'center': cur_first,
                                       'radius': round(r, 3)})
                    cur_first = None
                    redraw()
        elif event == cv2.EVENT_RBUTTONDOWN:
            if cur_type == 'polygon' and len(cur) >= 3:
                shapes.append({'type': 'polygon', 'points': list(cur)})
                cur = []
                redraw()

    cv2.setMouseCallback(win, on_mouse)
    redraw()

    print('= 交互绘制禁行区 =')
    print('左键=加顶点  右键=闭合多边形  z=撤销上一点  u=删最近形状')
    print('1/2/3=多边形/矩形/圆形  s=保存并生成掩码  q=退出')
    print(f'地图 {W}x{H} @ {res} m/px, origin=({ox},{oy})')

    while True:
        cv2.imshow(win, canvas)
        cv2.setWindowTitle(
            win,
            f"DrawKeepout | mode:{cur_type} zones:{len(shapes)} "
            f"| mouse:({last_mouse[0]:.2f},{last_mouse[1]:.2f}) m")
        k = cv2.waitKey(20) & 0xFF
        if k in (ord('q'), 27):
            break
        elif k == ord('z'):
            if cur:
                cur.pop()
            elif cur_first is not None:
                cur_first = None
            redraw()
        elif k == ord('u'):
            if shapes:
                shapes.pop()
                redraw()
        elif k == ord('1'):
            cur_type, cur, cur_first = 'polygon', [], None
            print('[模式] 多边形'); redraw()
        elif k == ord('2'):
            cur_type, cur, cur_first = 'rect', [], None
            print('[模式] 矩形'); redraw()
        elif k == ord('3'):
            cur_type, cur, cur_first = 'circle', [], None
            print('[模式] 圆形'); redraw()
        elif k == ord('s'):
            if cur_type == 'polygon' and len(cur) >= 3:
                shapes.append({'type': 'polygon', 'points': list(cur)})
                cur = []
            if not shapes:
                print('[保存] 还没有任何禁行区，先在地图上画一些')
                continue
            save_zones(shapes, args.zones)
            print(f"[保存] {len(shapes)} 个禁行区 → {args.zones}")
            code = run_generate(args.map, args.zones, args.out)
            print(f"[完成] 掩码与预览图已生成（generate 退出码 {code}）")
            break

    cv2.destroyAllWindows()


def main():
    ap = argparse.ArgumentParser(description='交互式在地图上绘制禁行区')
    ap.add_argument('--map', required=True, help='真实地图 yaml')
    ap.add_argument('--zones', default='keepout_zones.yaml', help='保存禁行区的 yaml 路径')
    ap.add_argument('--out', default='keepout', help='掩码输出前缀（交给 generate_keepout.py）')
    ap.add_argument('--selftest', action='store_true',
                    help='无界面自检：模拟绘制并保存，验证坐标→yaml→generate 链路')
    args = ap.parse_args()

    img, res, ox, oy, W, H = load_map(args.map)

    # ---- 无界面自检 ----
    if args.selftest:
        shapes = [
            {'type': 'polygon', 'points': [[ox + 1.0, oy + 1.0],
                                            [ox + 2.0, oy + 1.0],
                                            [ox + 1.5, oy + 2.0]]},
            {'type': 'circle', 'center': [ox + 3.0, oy + 2.0], 'radius': 0.5},
        ]
        save_zones(shapes, args.zones)
        print(f"[selftest] 已写入 {args.zones}")
        code = run_generate(args.map, args.zones, '/tmp/keepout_selftest')
        print(f"[selftest] generate_keepout.py 退出码 {code}")
        sys.exit(0 if code == 0 else 1)

    try:
        run_gui(img, res, ox, oy, W, H, args)
    except cv2.error as e:
        sys.exit(
            "无法打开图形窗口（当前无 DISPLAY，OpenCV GTK 初始化失败）。\n"
            "请在 VNC / 桌面终端里运行本脚本（与 rviz2 相同的显示环境）。\n"
            f"  错误: {e}")


if __name__ == '__main__':
    main()
