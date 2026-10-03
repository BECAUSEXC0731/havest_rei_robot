from setuptools import setup
import os
from glob import glob

package_name = 'fox_webui'


def web_data_files():
    """把 web/ 目录（含 lib/ 等子目录）按原结构装到 share/<pkg>/web/。

    setuptools 的 data_files 会把同一 entry 下的文件"拍平"到目标目录，
    所以这里逐个目录建 entry，保证 web/lib/vue.esm-browser.prod.js 之类
    的路径在 install 空间里依然正确（前端 importmap 依赖这些路径）。
    """
    entries = []
    for root, _dirs, files in os.walk('web'):
        if not files:
            continue
        entries.append((
            os.path.join('share', package_name, root),
            [os.path.join(root, f) for f in files],
        ))
    return entries

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.json5')),
    ] + web_data_files(),
    # web 静态资源逐个目录安装，保留 lib/ 等子目录结构
    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='zq',
    maintainer_email='msnakes@qq.com',
    description='FOX grape harvest robot WebUI',
    license='AGPL',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fox_webui_agent = fox_webui.agent_node:main',
        ],
    },
)

# 注意: web/ 目录由 scripts/install_web.sh 或 colcon 之后手工同步到 share/fox_webui/web
#      （setuptools 的 data_files 对目录支持不稳定，这里用 post 安装脚本保持可控）
