#!/usr/bin/python3
# -*- coding:utf-8 -*-

from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
short_description = """a lovable data analysis and algorithmic trading library for cryptocurrencies,
including tools for deploying any strategies including pattern based strategies,
price action strategies, indicator based strategies and also Machine learning based strategies. 
able to run multi strategy instances on a single bot as a webapp and a lot more..."""


plot = ['plotly>=4.0']

ai = ["tensorflow",
      'catboost; platform_machine != "aarch64"',
      'xgboost',
      'tensorboard']

develop = [
    'coveralls',
    'mypy',
    'ruff',
    'pre-commit',
    'pytest',
    'pytest-asyncio',
    'pytest-cov',
    'pytest-mock',
    'pytest-random-order',
    'isort',
    'time-machine',
    'types-cachetools',
    'types-filelock',
    'types-requests',
    'types-tabulate',
    'types-python-dateutil'
]

jupyter = [
    'jupyter',
    'nbstripout',
    'ipykernel',
    'nbconvert',
]

test = [
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'pytest-mock',
        ]

hdf5 = [
    'tables',
    'blosc',
]


all_extra = plot + develop + jupyter + ai

with open(this_directory/"requirements.txt", "r") as reqs:
    base_requirements = reqs.readlines()


setup(
    name='pythoncoin',
    version='v2.0.00',
    packages=['pycoin'],
    license="MIT",
    author='Hadi Fathipour',
    author_email="hadi9628983@gmail.com",
    url='https://github.com/hadif1999/pycoin',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=test, 
    install_requires=base_requirements,
    extras_require={
        "plot":plot,
        "ai":ai,
        "plot":plot,
        "jupyter":jupyter,
        "hdf5":hdf5,
        "all":all_extra},
    python_requires='>=3.10',
    
)
