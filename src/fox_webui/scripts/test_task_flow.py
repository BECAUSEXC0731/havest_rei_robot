#!/usr/bin/env python3
"""T3.6/T3.7 无硬件冒烟测试：发命令 → 轮询 /api/task → 检查协作式停止。

用法: python3 src/fox_webui/scripts/test_task_flow.py [base_url]
"""
import json
import sys
import time
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8080'


def post(path, body=None):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body or {}).encode(),
        headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)


def brief(t):
    if not t:
        return 'None'
    return (f"state={t.get('state')} stage={t.get('stage')} "
            f"running={t.get('running')} paused={t.get('paused')} "
            f"wp={t.get('waypoint')}/{t.get('waypoints')} "
            f"picked={t.get('picked')} msg={t.get('message')}")


def watch(seconds, step=2.0, label=''):
    end = time.time() + seconds
    last = None
    while time.time() < end:
        t = get('/api/task').get('task')
        cur = brief(t)
        if cur != last:
            print(f"  [{time.strftime('%H:%M:%S')}] {cur}", flush=True)
            last = cur
        time.sleep(step)
    return last


print('== 1) 起始状态 ==')
print(' ', brief(get('/api/task').get('task')))

print('== 2) 发 start ==')
print(' ', post('/api/task/start'))
print('   观察 16s：')
watch(16)

print('== 3) 中途发 stop（验证协作式停止）==')
print(' ', post('/api/task/stop'))
watch(12)

print('== 4) pause / resume 往返 ==')
print('  start:', post('/api/task/start'))
time.sleep(3)
print('  pause:', post('/api/task/pause'))
time.sleep(2)
print(' ', brief(get('/api/task').get('task')))
print('  resume:', post('/api/task/resume'))
time.sleep(2)
print(' ', brief(get('/api/task').get('task')))
print('  stop:', post('/api/task/stop'))

print('== 5) pick_one（带坐标，验证目标选择链路）==')
print(' ', post('/api/task/pick_one', {'x': 231.9, 'y': 178.3, 'z': 95.8}))
watch(14)

print('== 6) 非法动作 ==')
try:
    post('/api/task/boom')
except Exception as exc:
    print('  ->', exc)
