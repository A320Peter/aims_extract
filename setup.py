#!/usr/bin/python3

from setuptools import setup

setup(
    name="aims_extract",
    version="0.2",
    packages=["aims"],
    python_requires='>=3.6',
    install_requires=['Beautifulsoup4', 'requests', 'python-dateutil'],
    entry_points={
        'console_scripts':
        ['aims = aims.aims:main']}
)
