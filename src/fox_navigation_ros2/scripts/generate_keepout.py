#!/usr/bin/env python3
"""
generate_keepout.py — 生成 Nav2 keepout（禁行区）掩码地图

配合 Nav2 keepout filter 使用：把禁行区标成致命障碍，全局路径自动绕开。
掩码语义：**黑色像素 = 禁行区（occupied=100）**，白色像素 = 可通行。

推荐用法（手动编辑禁行区配置文件，最直观）:
  1) 编辑 src/fox_navigation_ros2/config/keepout_zones.yaml，
     把每个禁行区（多边形/矩形/圆形）的顶点写进去（世界坐标, 米，与地图同一坐标系）
  2) 运行:
     python3 src/fox_navigation_ros2/scripts/generate_keepout.py \\
         --map maps/test_map.yaml --out maps/keepout \\
         --zones src/fox_navigation_ros2/config/keepout_zones.yaml \\
         --preview
  --preview 会生成 maps/keepout_preview.png：真实地图 + 红色禁行区叠图，方便核对位置。

也可以直接在命令行叠加:
  --rect cx cy w h / --circle cx cy r / --polygon "x1,y1 x2,y2 ..."（可多次）

生成的 <out>.pgm + <out>.yaml 由 nav2 map_server 加载，作为 keepout 掩码。
坐标：x 向右、y 向上；禁行区超出地图范围的部分自动忽略。
"""

import argparse
import os
import sys

import numpy as np
import yaml


def load_map_header(pgm_path: str):
    """读取 PGM 的宽高（P5/P2 二进制，只读头）。"""
    with open(pgm_path, 'rb') as f:
        # 逐 token 读头：magic, width, height, maxval
        tokens = []
        data = f.read(64)
        # PGM 头允许注释行(#)，简单按行解析
        lines = data.decode('ascii', errors='ignore').splitlines()
        nums = []
        magic = None
        for ln in lines:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if magic is None:
                magic = ln
                continue
            nums += ln.split()
            if len(nums) >= 2:
                break
        if magic is None or len(nums) < 2:
            sys.exit(f"无法解析 PGM 头: {pgm_path}")
        w, h = int(nums[0]), int(nums[1])
    return w, h


def world_to_pixel(x, y, ox, oy, res, h):
    """世界坐标(米) → (col, row)。row 0 在顶部（occupancy grid 惯例）。"""
    col = int(np.floor((x - ox) / res))
    row = (h - 1) - int(np.floor((y - oy) / res))
    return col, row


def add_rect(mask, ox, oy, res, cx, cy, w, h, name='矩形'):
    """中心 + 宽高 的矩形禁行区。返回内部像素布尔掩码。"""
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = cy - h / 2.0, cy + h / 2.0
    c0, r0 = world_to_pixel(x0, y0, ox, oy, res, mask.shape[0])
    c1, r1 = world_to_pixel(x1, y1, ox, oy, res, mask.shape[0])
    c0, c1 = sorted((c0, c1))
    r0, r1 = sorted((r0, r1))
    c0, c1 = max(c0, 0), min(c1, mask.shape[1] - 1)
    r0, r1 = max(r0, 0), min(r1, mask.shape[0] - 1)
    inside = np.zeros(mask.shape, dtype=bool)
    inside[r0:r1 + 1, c0:c1 + 1] = True
    mask[inside] = 0
    n = int(inside.sum())
    print(f"  {name}: 矩形 [{cx}, {cy}] {w}x{h} m → {n} 像素")
    return inside


def add_circle(mask, ox, oy, res, cx, cy, r, name='圆形'):
    """圆形禁行区。返回内部像素布尔掩码。"""
    H, W = mask.shape
    rows, cols = np.mgrid[0:H, 0:W]
    # 世界坐标下的网格
    gx = ox + (cols + 0.5) * res
    gy = oy + (H - 0.5 - rows) * res  # row 0 在顶部 → y 最大
    inside = (gx - cx) ** 2 + (gy - cy) ** 2 <= r ** 2
    mask[inside] = 0
    print(f"  {name}: 圆形 [{cx}, {cy}] r={r} m → {int(inside.sum())} 像素")
    return inside


def point_in_polygon(px, py, poly):
    """射线法判断点是否在多边形内（无依赖）。"""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and \
           (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def add_polygon(mask, ox, oy, res, poly, name='多边形'):
    """多边形禁行区。poly = [(x1,y1), (x2,y2), ...]（世界坐标, 米）。返回内部像素布尔掩码。"""
    if len(poly) < 3:
        sys.exit(f"{name}: 多边形至少需要 3 个顶点")
    H, W = mask.shape
    rows, cols = np.mgrid[0:H, 0:W]
    gx = ox + (cols + 0.5) * res
    gy = oy + (H - 0.5 - rows) * res
    inside = np.zeros((H, W), dtype=bool)
    # 逐像素射线法（地图不大时可接受）
    for r in range(H):
        for c in range(W):
            if point_in_polygon(gx[r, c], gy[r, c], poly):
                inside[r, c] = True
    mask[inside] = 0
    print(f"  {name}: 多边形 {len(poly)} 顶点 → {int(inside.sum())} 像素")
    return inside


def write_pgm(path, arr):
    with open(path, 'wb') as f:
        f.write(f"P5\n{arr.shape[1]} {arr.shape[0]}\n255\n".encode('ascii'))
        f.write(arr.tobytes())


def main():
    ap = argparse.ArgumentParser(description='生成 Nav2 keepout 禁行区掩码地图')
    ap.add_argument('--map', required=True, help='真实地图 yaml（取 origin/resolution/尺寸）')
    ap.add_argument('--out', default='keepout', help='输出前缀（生成 <out>.pgm + <out>.yaml），默认 keepout')
    ap.add_argument('--zones', action='append', metavar='YAML',
                    help='从 YAML 配置文件读取禁行区（推荐，手动编辑多边形/矩形/圆形）')
    ap.add_argument('--rect', nargs=4, type=float, action='append', metavar=('CX', 'CY', 'W', 'H'),
                    help='矩形禁行区: 中心x 中心y 宽 高（可多次）')
    ap.add_argument('--circle', nargs=3, type=float, action='append', metavar=('CX', 'CY', 'R'),
                    help='圆形禁行区: 圆心x 圆心y 半径（可多次）')
    ap.add_argument('--polygon', action='append', metavar='STR',
                    help='多边形禁行区: "x1,y1 x2,y2 ..."（可多次）')
    ap.add_argument('--preview', action='store_true',
                    help='生成预览 PNG（<out>_preview.png，真实地图+红色禁行区叠图）')
    args = ap.parse_args()

    # 读真实地图 yaml
    map_dir = os.path.dirname(os.path.abspath(args.map))
    with open(args.map, 'r') as f:
        m = yaml.safe_load(f)
    ox, oy, otheta = m['origin']
    res = float(m['resolution'])
    pgm = os.path.join(map_dir, m['image'])
    W, H = load_map_header(pgm)
    print(f"真实地图: {pgm} {W}x{H} @ {res} m/px, origin=({ox},{oy})")

    # 全白 = 可通行；禁行区画黑
    mask = np.full((H, W), 255, dtype=np.uint8)
    inside_total = np.zeros((H, W), dtype=bool)
    n_zone = 0

    # 1) 配置文件里的禁行区（手动编辑的主要方式）
    if args.zones:
        for zf in args.zones:
            with open(zf, 'r') as f:
                zones = yaml.safe_load(f) or {}
            print(f"读取禁行区配置: {zf}")
            for z in zones.get('zones', []):
                name = z.get('name', 'zone')
                typ = z.get('type', 'polygon')
                try:
                    if typ == 'polygon':
                        poly = [tuple(p) for p in z['points']]
                        inside_total |= add_polygon(mask, ox, oy, res, poly, name)
                    elif typ == 'rect':
                        cx, cy = z['center']
                        w, h = z['size']
                        inside_total |= add_rect(mask, ox, oy, res, cx, cy, w, h, name)
                    elif typ == 'circle':
                        cx, cy = z['center']
                        inside_total |= add_circle(mask, ox, oy, res, cx, cy, z['radius'], name)
                    else:
                        print(f"  ⚠️ {name}: 未知类型 '{typ}'（支持 polygon/rect/circle），跳过")
                        continue
                except (KeyError, TypeError, ValueError) as e:
                    print(f"  ⚠️ {name}: 配置解析失败 ({e})，跳过")
                    continue
                n_zone += 1

    # 2) 命令行直接叠加
    if args.rect:
        for r in args.rect:
            inside_total |= add_rect(mask, ox, oy, res, *r)
            n_zone += 1
    if args.circle:
        for c in args.circle:
            inside_total |= add_circle(mask, ox, oy, res, *c)
            n_zone += 1
    if args.polygon:
        for p in args.polygon:
            poly = []
            for tok in p.replace(';', ' ').split():
                sx, sy = tok.split(',')
                poly.append((float(sx), float(sy)))
            inside_total |= add_polygon(mask, ox, oy, res, poly)
            n_zone += 1

    if n_zone == 0:
        print("⚠️ 未指定任何禁行区（--zones 或 --rect/--circle/--polygon），生成的是全白(无禁行)掩码 —— 系统可启动但无禁行效果")

    # 输出 PGM + YAML
    out_pgm = args.out if args.out.endswith('.pgm') else args.out + '.pgm'
    out_yaml = args.out if args.out.endswith('.yaml') else args.out + '.yaml'
    write_pgm(out_pgm, mask)
    yaml_doc = {
        'image': os.path.basename(out_pgm),
        'mode': m.get('mode', 'trinary'),
        'resolution': res,
        'origin': [ox, oy, otheta],
        'negate': m.get('negate', 0),
        'occupied_thresh': m.get('occupied_thresh', 0.65),
        'free_thresh': m.get('free_thresh', 0.25),
    }
    with open(out_yaml, 'w') as f:
        yaml.safe_dump(yaml_doc, f, default_flow_style=False, sort_keys=False)

    black = int((mask == 0).sum())
    print(f"\n生成完成: {out_pgm} + {out_yaml}")
    print(f"  禁行像素: {black} / {mask.size} ({100.0 * black / mask.size:.2f}%)")

    # 预览图：真实地图 + 红色禁行区
    if args.preview:
        try:
            from PIL import Image
            img = Image.open(pgm).convert('RGB')
            px = img.load()
            for r in range(H):
                for c in range(W):
                    if inside_total[r, c]:
                        px[c, r] = (255, 0, 0)
            prev = os.path.splitext(out_pgm)[0] + '_preview.png'
            img.save(prev)
            print(f"  预览图: {prev}（红色=禁行区）")
        except Exception as e:
            print(f"  ⚠️ 预览生成失败: {e}")


if __name__ == '__main__':
    main()
