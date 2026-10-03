#!/usr/bin/env python3
"""USB 设备软复位（相当于"拔插一次"），用于 Orbbec 深度传感器卡死。

背景（2026-09-19 实测）
----------------------
Astra Pro Plus 是**两个** USB 设备：
  * 2bc5:0403  "ORBBEC Depth Sensor"（深度/IR，走 OpenNI 私有协议）
  * 2bc5:0501  "Astra Pro HD Camera"（彩色 UVC）
深度初始化失败时 OrbbecSDK 日志（工作区 Log/OrbbecSDK.log.txt）会写：
    [error] OpenNIDevice.cpp:340] Command and sensor firmware not createed!
    [warning] No required type sensor found! sensorType: OB_SENSOR_DEPTH / OB_SENSOR_IR
即"深度固件通道握手失败"。设备本身还在 USB 上（lsusb 看得到），彩色也正常，
但深度要复位一次才好 —— 用 USBDEVFS_RESET ioctl 就能做到，**不需要 sudo**
（本机 udev 规则 99-obsensor-libusb.rules 把设备节点设成了 0666）。

用法
----
    python3 usb_reset.py                 # 复位所有 2bc5:xxxx（Orbbec）设备
    python3 usb_reset.py 2bc5:0403       # 只复位深度传感器
    python3 usb_reset.py --list          # 只列出匹配到的设备
"""
from __future__ import annotations

import argparse
import fcntl
import glob
import os
import sys
import time

USBDEVFS_RESET = ord('U') << 8 | 20


def find_usb_nodes(vid_pid: str | None) -> list[dict]:
    """扫描 /sys/bus/usb/devices，返回匹配的设备（含 busnum/devnum 与节点路径）。"""
    out = []
    for d in glob.glob('/sys/bus/usb/devices/*'):
        try:
            vid = open(os.path.join(d, 'idVendor')).read().strip()
            pid = open(os.path.join(d, 'idProduct')).read().strip()
        except OSError:
            continue
        if vid_pid and f'{vid}:{pid}'.lower() != vid_pid.lower():
            continue
        if not vid_pid and vid != '2bc5':
            continue
        try:
            bus = int(open(os.path.join(d, 'busnum')).read().strip())
            dev = int(open(os.path.join(d, 'devnum')).read().strip())
            prod = open(os.path.join(d, 'product')).read().strip()
        except OSError:
            prod = ''
        out.append({'sys': d, 'vid_pid': f'{vid}:{pid}', 'bus': bus, 'dev': dev,
                    'product': prod, 'node': f'/dev/bus/usb/{bus:03d}/{dev:03d}'})
    return out


def usb_reset(node: str) -> bool:
    try:
        fd = os.open(node, os.O_WRONLY)
    except OSError as exc:
        print(f'  ✗ 打不开 {node}: {exc}（权限不足？需要 udev 规则或 sudo）')
        return False
    try:
        fcntl.ioctl(fd, USBDEVFS_RESET, 0)
        return True
    except OSError as exc:
        print(f'  ✗ 复位失败 {node}: {exc}')
        return False
    finally:
        os.close(fd)


def main() -> int:
    ap = argparse.ArgumentParser(description='USB 设备软复位（默认复位所有 Orbbec 设备）')
    ap.add_argument('vid_pid', nargs='?', default=None,
                    help='形如 2bc5:0403；不填则复位所有 2bc5:xxxx')
    ap.add_argument('--list', action='store_true', help='只列出匹配设备')
    args = ap.parse_args()

    devs = find_usb_nodes(args.vid_pid)
    if not devs:
        print(f'✗ 没找到 {args.vid_pid or "2bc5:xxxx"} 设备')
        return 1
    for d in devs:
        print(f"  {d['vid_pid']}  bus {d['bus']} dev {d['dev']}  {d['product']}  ({d['node']})")
    if args.list:
        return 0

    ok = 0
    for d in devs:
        print(f"复位 {d['vid_pid']} ({d['product']}) …")
        if usb_reset(d['node']):
            print('  ✓ 已发送复位')
            ok += 1
        time.sleep(1.0)
    # 复位后设备会重新枚举（devnum 通常变化），等它稳定
    time.sleep(4.0)
    print('复位后设备列表：')
    for d in find_usb_nodes(args.vid_pid):
        print(f"  {d['vid_pid']}  bus {d['bus']} dev {d['dev']}  {d['product']}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
