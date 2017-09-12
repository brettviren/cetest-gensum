#!/usr/bin/env python
'''
This is for the Python utility programs called by waf/wscript
'''

from setuptools import setup, find_packages

packages = find_packages()
print (packages)

setup(name = 'cege',
      version = '0.0',
      packages = packages,
      entry_points = dict(
          console_scripts = [
              'cege = cege.main:main',
          ],
      ),
)
