#!/usr/bin/env python3

import re
import pypandoc
from setuptools import setup, find_packages

with open('README.md') as file:
	long_description = pypandoc.convert(file.read(), 'rst', format='md')
	#pandoc bug workaround
	long_description = re.sub(r'(:alt:\s*(.+)\s*\r?\n)\s*\r?\n\s*\2', r'\1', long_description)
	print(long_description)

setup(
	name='urxvt_tabbed',
	version='0.1.0',
	license='GPLv3',
	description='Tab wrapper for urxt',
	long_description=long_description,
	url='https://github.com/simonzack/urxvt-tabbed',

	author='simonzack',
	author_email='simonzack@gmail.com',

	install_requires = ['pygobject', 'python3-xlib'],

	packages=find_packages(),
	scripts=['bin/urxvt-tabbed'],

	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 3',
		'Topic :: Terminals :: Terminal Emulators/X Terminals',
	],
)
