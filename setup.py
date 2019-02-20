#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'appdirs>=1.4.3',
    'click>=6.7',
    'prompt-toolkit>=1.0.15,<2.0',
    'pygments>=2.2.0',
    'pymssql>=2.1.3',
    'sqlalchemy>=1.2.5',
    'tabulate>=0.8.2',
    ]

setup(
    author="Simon Bowly",
    author_email='simon.bowly@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Command line interface to Microsoft SQL servers.",
    entry_points={
        'console_scripts': [
            'mscli=mscli:cli',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='mscli',
    name='mscli',
    packages=find_packages(include=['mscli']),
    url='https://github.com/simonbowly/mscli',
    version='0.1.0',
    zip_safe=False,
)
