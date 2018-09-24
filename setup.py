import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-partitioning',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Add partitioning to django models',
    long_description=README,
    author='Soin Sergey',
    author_email='soins1992@gmail.com',
)