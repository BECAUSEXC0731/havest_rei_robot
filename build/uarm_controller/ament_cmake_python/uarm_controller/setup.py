from setuptools import find_packages
from setuptools import setup

setup(
    name='uarm_controller',
    version='0.1.0',
    packages=find_packages(
        include=('uarm_controller', 'uarm_controller.*')),
)
