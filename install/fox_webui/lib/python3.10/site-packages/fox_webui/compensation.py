"""把页面上调的补偿值写回 harvest_config.yaml —— **保留注释**的行级回写。

为什么不用 `yaml.safe_dump` 回写
--------------------------------
`harvest_config.yaml` 141 行里有 **70 行是中文注释**（还有一大段解释工具偏移
局部坐标系怎么测的说明）。`safe_dump` 只保留数据、注释全丢 —— 那等于把现场
最宝贵的调参笔记抹掉。`ruamel.yaml` 能保注释，但环境里没装，也不想为这一个
功能加依赖。所以这里用**行级数值替换**：只改 `key: 数字` 里的数字，
其余字节（含注释、空行、缩进、行尾注释）原样保留。

为什么一次写两份文件
--------------------
`harvest_node._load_config()` 的查找顺序是 **install/share 优先**（ament 安装产物），
源码路径只是兜底。所以只写 `src/.../harvest_config.yaml` 的话，下次启动读到的
还是旧值 —— 必须两份都写。列表由 `default_paths()` 给出。

安全
----
* 只允许改白名单键（`KEYS`），且做限幅校验；
* 写前把原文件备份成 `<file>.bak`（每次保存覆盖，够用于"改坏了救回来"）；
* 写用「临时文件 + os.replace」原子替换，避免出现半截文件；
* 单进程内用锁串行化（WebUI 里只有 HTTP 线程会调用）。
"""
from __future__ import annotations

import os
import re
import shutil
import threading
import time

import yaml

#: 允许从网页修改的键（本次需求只做抓取点补偿）
KEYS = ('tool_offset_x', 'tool_offset_y', 'tool_offset_z')

#: 单轴限幅（mm）：防止误操作把补偿调成几百毫米后撞机
LIMIT_MM = 200.0

DEFAULT_SRC = '/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml'
DEFAULT_SHARE = ('/home/ubuntu/ros2fox/install/fox_grape_harvest/share/'
                 'fox_grape_harvest/config/harvest_config.yaml')


def default_paths() -> list[str]:
    """要回写的文件列表（源码 + install/share），只返回存在的。"""
    out = []
    for p in (DEFAULT_SRC, DEFAULT_SHARE):
        if os.path.isfile(p):
            out.append(p)
    return out


def _fmt(v: float) -> str:
    """数值 → YAML 文本：整数不写小数点（-80 而不是 -80.0），与文件里原有风格一致。"""
    f = float(v)
    if abs(f - round(f)) < 1e-9:
        return str(int(round(f)))
    return f'{f:g}'


def check_limits(values: dict) -> tuple[bool, str]:
    """限幅校验。"""
    for k, v in values.items():
        if k not in KEYS:
            return False, f'不允许修改的键: {k}（只允许 {", ".join(KEYS)}）'
        try:
            f = float(v)
        except (TypeError, ValueError):
            return False, f'{k} 不是数字: {v!r}'
        if abs(f) > LIMIT_MM:
            return False, f'{k}={f:g} 超出限幅 ±{LIMIT_MM:g} mm'
    return True, ''


def patch_numbers(text: str, values: dict) -> tuple[str, list[str]]:
    """行级替换 `key: 数字`。返回 (新文本, 实际改动的键)。"""
    changed = []
    for key, val in values.items():
        # 匹配： 缩进 + key + ':' + 空白 + 数字 + 其余（行尾注释/空白原样保留）
        # ⚠️ flags 必须在 compile 阶段给：已编译 pattern 的 sub() 不接 flags 参数
        pat = re.compile(rf'^(\s*{re.escape(key)}\s*:\s*)(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)(.*)$',
                         re.M)
        def _sub(m):
            if abs(float(m.group(2)) - float(val)) < 1e-9:
                return m.group(0)                     # 值没变就不动，避免无意义写盘
            changed.append(key)
            return f'{m.group(1)}{_fmt(val)}{m.group(3)}'
        text = pat.sub(_sub, text, count=1)
    return text, changed


class ConfigWriter:
    """带备份 + 原子替换的配置文件回写器。"""

    def __init__(self, paths: list[str] | None = None):
        self.paths = paths if paths is not None else default_paths()
        self._lock = threading.Lock()
        self.last_save: dict = {}

    # ── 读 ──
    def read(self, path: str | None = None) -> dict:
        """读回当前磁盘上的补偿值（读第一份存在的文件即可）。"""
        p = path or (self.paths[0] if self.paths else None)
        if not p or not os.path.isfile(p):
            return {}
        with open(p, 'r', encoding='utf-8') as fp:
            cfg = yaml.safe_load(fp) or {}
        arm = cfg.get('arm') or {}
        return {k: float(arm[k]) for k in KEYS if arm.get(k) is not None}

    # ── 写 ──
    def save(self, values: dict) -> dict:
        """把 values（{key: 数值}）写进所有目标文件。返回结果摘要。"""
        ok, why = check_limits(values)
        if not ok:
            return {'ok': False, 'error': why}

        with self._lock:
            results = []
            any_change = False
            for p in self.paths:
                try:
                    with open(p, 'r', encoding='utf-8') as fp:
                        text = fp.read()
                    new_text, changed = patch_numbers(text, values)
                    if not changed:
                        results.append({'path': p, 'ok': True, 'changed': False,
                                        'detail': '值未变化，跳过'})
                        continue
                    # 备份（原文件 → .bak）
                    try:
                        shutil.copy2(p, p + '.bak')
                    except Exception as exc:
                        results.append({'path': p, 'ok': False,
                                        'detail': f'备份失败，已中止（未写入）: {exc}'})
                        continue
                    # 原子写
                    tmp = f'{p}.tmp{os.getpid()}'
                    with open(tmp, 'w', encoding='utf-8') as fp:
                        fp.write(new_text)
                    os.replace(tmp, p)
                    any_change = True
                    results.append({'path': p, 'ok': True, 'changed': True,
                                    'keys': sorted(set(changed))})
                except Exception as exc:
                    results.append({'path': p, 'ok': False, 'detail': f'{type(exc).__name__}: {exc}'})

            all_ok = all(r.get('ok') for r in results) if results else False
            self.last_save = {'ts': round(time.time(), 3),
                              'ok': all_ok, 'changed': any_change, 'results': results}
            return {'ok': all_ok, 'changed': any_change, 'results': results,
                    'ts': self.last_save['ts'], 'paths': list(self.paths)}
