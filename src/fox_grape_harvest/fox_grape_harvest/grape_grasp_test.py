"""grape_grasp_test 的 console_scripts 入口包装。

独立脚本 scripts/grape_grasp_test.py 不位于包目录内，无法直接作为
console_scripts 的 module:main 目标，因此这里通过 importlib 在运行时
加载已安装的脚本副本并暴露其 main()，从而支持：

    ros2 run fox_grape_harvest grape_grasp_test.py
"""
import importlib.util
import os
import sys

from ament_index_python.packages import get_package_share_directory

_SCRIPT_NAME = 'grape_grasp_test_script'


def _load_script_main():
    script = os.path.join(
        get_package_share_directory('fox_grape_harvest'),
        'scripts', 'grape_grasp_test.py')
    if not os.path.isfile(script):
        raise FileNotFoundError(
            f'未找到已安装的脚本: {script}，请先 colcon build fox_grape_harvest')
    spec = importlib.util.spec_from_file_location(_SCRIPT_NAME, script)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_SCRIPT_NAME] = mod
    spec.loader.exec_module(mod)
    return mod.main


main = _load_script_main()
