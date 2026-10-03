#!/usr/bin/env bash
# 组装 fox_webui 的运行环境（bash / zsh 均可 source）
#
# 为什么需要它：
#   本机 ~/.zshrc 把 ros2/colcon 包装成了 zsh 函数（内部 source local_setup.zsh）。
#   这在交互式终端好用，但**无法用于** setsid/nohup/systemd 这类"脱离会话"的启动方式
#   （外部程序不能执行 shell 函数），而手动 `source /opt/ros/humble/setup.zsh`
#   在本环境下会卡死。因此这里直接把 workspace 各包的路径拼好。
#
# 用法：
#   source scripts/fox_webui_env.sh
#   setsid nohup python3 install/fox_webui/lib/fox_webui/fox_webui_agent --ros-args -p port:=8080 \
#       > /tmp/webui.log 2>&1 < /dev/null &

FOX_WS="${FOX_WS:-$HOME/ros2fox}"

# PYTHONPATH：各包安装出来的 python 包目录
#   ⚠️ 两种布局都要加（本项目混用 ament_python 与 ament_cmake）：
#   * ament_python  → install/<pkg>/lib/python3.10/site-packages
#   * ament_cmake   → install/<pkg>/local/lib/python3.10/dist-packages   ← 消息包(arm_controller/rei_robot_base)在这里
_p=""
for d in "$FOX_WS"/install/*/lib/python3.10/site-packages \
         "$FOX_WS"/install/*/local/lib/python3.10/dist-packages; do
    [ -d "$d" ] && _p="${_p}${_p:+:}$d"
done
[ -n "$_p" ] && export PYTHONPATH="${_p}${PYTHONPATH:+:$PYTHONPATH}"

# LD_LIBRARY_PATH：各包的本地库（消息包的类型支持 .so 依赖它）
_l=""
for d in "$FOX_WS"/install/*/lib "$FOX_WS"/install/*/local/lib; do
    [ -d "$d" ] && _l="${_l}${_l:+:}$d"
done
[ -n "$_l" ] && export LD_LIBRARY_PATH="${_l}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# AMENT_PREFIX_PATH：ament 索引查找（get_package_share_directory 等）
_a=""
for d in "$FOX_WS"/install/*; do
    [ -d "$d/share/ament_index/resource_index/packages" ] && _a="${_a}${_a:+:}$d"
done
[ -n "$_a" ] && export AMENT_PREFIX_PATH="${_a}${AMENT_PREFIX_PATH:+:$AMENT_PREFIX_PATH}"

# 底盘型号（rei_robot_base 依赖）
export REI_ROBOT="${REI_ROBOT:-fox_three}"

# 便捷函数：后台常驻启动 Agent
#   fox_webui_start [额外 ros-args ...]
fox_webui_start() {
    local log="${FOX_WEBUI_LOG:-/tmp/webui.log}"
    setsid nohup python3 "$FOX_WS/install/fox_webui/lib/fox_webui/fox_webui_agent" "$@" \
        > "$log" 2>&1 < /dev/null &
    echo "fox_webui_agent 已在后台启动 (log: $log)"
}
