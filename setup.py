#!/usr/bin/env python

from setuptools import setup


URL_BASE = 'https://github.com/astropy/astropy-tools/'


setup(
    name='astropy-tools',
    version='0.0.0.dev0',
    author='The Astropy Developers',
    author_email='astropy.team@gmail.com',
    url=URL_BASE,
    download_url=URL_BASE + 'archive/master.zip',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
        'Topic :: Utilities'
    ],
    py_modules=[
        'gitastropyplots',
        'gh_issuereport',
        'issue2pr',
        'suggest_backports',
        'astropy_grep_affiliated'
    ],
    entry_points={
        'console_scripts': [
            'gh_issuereport = gh_issuereport:main',
            'issue2pr = issue2pr:main',
            'suggest_backports = suggest_backports:main',
            'astropy_grep_affiliated = astropy_grep_affiliated:main'
        ]
    },
    install_requires=['requests']
)

