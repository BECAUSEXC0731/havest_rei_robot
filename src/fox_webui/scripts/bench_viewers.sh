#!/usr/bin/env bash
# 测量“观看者数量 → agent CPU”的关系（用于验证按需订阅与共享编码是否真的省 CPU）
cd /home/ubuntu/ros2fox || exit 1
pid=$(pgrep -f fox_webui_agent | head -1)
sample() { top -b -n 2 -d 3 -p "$pid" | grep -a python3 | tail -1 | awk '{print "   CPU="$9"%  RSS="$6"KB"}'; }
vw() { curl -s -m 3 http://127.0.0.1:8080/api/health \
        | python3 -c 'import json,sys;print("   viewers",json.load(sys.stdin).get("video_viewers"))'; }

echo "[0 观看者]"; vw; sample

pids=()
for i in 1 2 3; do
    curl -s -o /dev/null "http://127.0.0.1:8080/video/color" &
    pids+=($!)
    sleep 2
    echo "[$i 观看者]"; vw; sample
done

echo "[全部断开后 2s]"
for p in "${pids[@]}"; do kill "$p" 2>/dev/null; done
sleep 3; vw
