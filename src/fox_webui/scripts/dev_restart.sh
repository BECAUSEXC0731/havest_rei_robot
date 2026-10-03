#!/usr/bin/env bash
# 开发用一键重启：杀掉旧进程 → 启动 agent + 假数据源 → 自检端口与状态
# 用法：bash src/fox_webui/scripts/dev_restart.sh [--no-fake]
set -u
ROOT=/home/ubuntu/ros2fox
cd "$ROOT" || exit 1

# 1) 清理（用 [] 避免 pkill 匹配到自己）
for p in $(pgrep -f "fox_webui_agent" 2>/dev/null); do kill -9 "$p" 2>/dev/null; done
for p in $(pgrep -f "fake_telemetry" 2>/dev/null); do kill -9 "$p" 2>/dev/null; done
sleep 1

# 2) 组装环境（外部脚本无法用 ~/.zshrc 里的包装函数）
# shellcheck disable=SC1091
source "$ROOT/src/fox_webui/scripts/fox_webui_env.sh"

# 3) 启动 agent
setsid nohup python3 "$ROOT/install/fox_webui/lib/fox_webui/fox_webui_agent" \
    --ros-args -p detect_mode:=sim > /tmp/webui.log 2>&1 < /dev/null &
sleep 5

# 4) 启动假数据源
if [ "${1:-}" != "--no-fake" ]; then
    setsid nohup python3 "$ROOT/src/fox_webui/scripts/fake_telemetry.py" \
        --all --echo-cmd-vel --duration 7200 > /tmp/fake.log 2>&1 < /dev/null &
    sleep 4
fi

# 5) 自检
echo "== ping ==";      curl -s -m 3 http://127.0.0.1:8080/api/ping; echo
echo "== 进程 ==";      pgrep -af "fox_webui_agent|fake_telemetry" | sed 's/ --.*//' 
echo "== 状态摘要 =="
curl -s -m 3 http://127.0.0.1:8080/api/state \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); \
print("pose:", d.get("pose")); print("arm:", d.get("arm")); \
print("gripper:", d.get("gripper")); print("online:", (d.get("robot") or {}).get("online")); \
c=d.get("control") or {}; print("estop:", c.get("estop"), "| nav_active:", c.get("nav_active")); \
print("services:", c.get("services"))'
echo "== 日志尾部 =="; tail -2 /tmp/webui.log
