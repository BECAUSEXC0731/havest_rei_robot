from setuptools import find_packages
from setuptools import setup

setup(
    name='rei_robot_base',
    version='0.1.0',
    packages=find_packages(
        include=('rei_robot_base', 'rei_robot_base.*')),
)
