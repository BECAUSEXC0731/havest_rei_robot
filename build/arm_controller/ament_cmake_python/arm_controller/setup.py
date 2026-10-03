from setuptools import find_packages
from setuptools import setup

setup(
    name='arm_controller',
    version='0.0.1',
    packages=find_packages(
        include=('arm_controller', 'arm_controller.*')),
)
