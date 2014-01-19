#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
	name='urxvt_tabbed',
	version='0.1.0',
	license='GPLv3',
	description='Tab wrapper for urxt',
	url='https://github.com/simonzack/urxvt-tabbed',

	author='simonzack',
	author_email='simonzack@gmail.com',

	install_requires = ['pygobject', 'python3-xlib'],

	packages=find_packages(),
	scripts=['bin/urxvt-tabbed'],

	classifiers = [
		'Development Status :: 3 - Alpha',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 3',
		'Topic :: Terminals :: Terminal Emulators/X Terminals',
	],
)
