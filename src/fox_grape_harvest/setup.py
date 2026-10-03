from setuptools import setup
import os
from glob import glob

package_name = 'fox_grape_harvest'

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
        (os.path.join('share', package_name, 'config'), glob('config/*.yml')),
        (os.path.join('share', package_name, 'scripts'),
            ['scripts/test_detection.py', 'scripts/grape_grasp_test.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='zq',
    maintainer_email='msnakes@qq.com',
    description='Grape harvesting package for FOX robot',
    license='AGPL',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'grape_harvest_node = fox_grape_harvest.harvest_node:main',
            'grape_grasp_test.py = fox_grape_harvest.grape_grasp_test:main',
        ],
    },
)
