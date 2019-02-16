from os.path import dirname, join, abspath
from setuptools import find_packages, setup

ROOT_DIR = dirname(abspath(__file__))

setup(
    packages=find_packages(where=join(ROOT_DIR, 'src/smesco/')),
    package_dir={'smesco': 'src/smesco/'},
    include_package_data=True,
    scripts=['src/smesco/manage.py']
)
