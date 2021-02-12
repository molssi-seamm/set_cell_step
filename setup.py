#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""set_cell_step
A SEAMM plug-in for setting the periodic (unit) cell.
"""
import sys
from setuptools import setup, find_packages
import versioneer

# from https://github.com/pytest-dev/pytest-runner#conditional-requirement
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements_install.txt') as fd:
    requirements = fd.read()

setup(
    name='set_cell_step',
    author="Paul Saxe",
    author_email='psaxe@molssi.org',
    description=__doc__.splitlines()[1],
    long_description=readme + '\n\n' + history,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license="BSD-3-Clause",
    url='https://github.com/molssi-seamm/set_cell_step',
    packages=find_packages(include=['set_cell_step']),
    include_package_data=True,
    setup_requires=[] + pytest_runner,
    install_requires=requirements,
    test_suite='tests',
    platforms=['Linux',
               'Mac OS-X',
               'Unix',
               'Windows'],
    zip_safe=True,

    keywords=['SEAMM', 'plug-in', 'flowchart', 'unitcell', 'crystal',
              'atomistic'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
        'org.molssi.seamm': [
            'Set Cell = set_cell_step:SetCellStep',
        ],
        'org.molssi.seamm.tk': [
            'Set Cell = set_cell_step:SetCellStep',
        ],
    }
)
