#!/usr/bin/env python3
from setuptools import setup, find_packages
from os import path


with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='urxvt_tabbed',
    version='1.0.0',
    license='GPLv3',
    description='Tab wrapper for urxt',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/simonzack/urxvt-tabbed',

    author='simonzack',
    author_email='simonzack@gmail.com',

    install_requires=['pygobject', 'python3-xlib', 'pyxdg'],

    packages=find_packages(),
    scripts=['bin/urxvt-tabbed'],

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
    ],
)
