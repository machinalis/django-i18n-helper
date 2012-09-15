#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('README.md') as readme:
    __doc__ = readme.read()

from distutils.core import setup

setup(
    name='django-i18n-helper',
    version='0.1.1',
    description=u'A internationalization helper that highlights translated strings',
    long_description=__doc__,
    author = u'Santiago Gabriel Romero',
    author_email = 'sromero@machinalis.com',
    url='https://github.com/machinalis/django-i18n-helper',
    packages=['i18n_helper'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
