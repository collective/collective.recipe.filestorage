# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.filestorage
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '0.7dev'

long_description = (
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('README.rst')
        + '\n' +
        'Change history\n'
        '**************\n'
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Contributors\n'
        '************\n'
        + '\n' +
        read('CONTRIBUTORS.txt')
)
entry_point = 'collective.recipe.filestorage:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'manuel']

setup(name='collective.recipe.filestorage',
      version=version,
      description="This recipe aids the creation and management of multiple Zope 2 filestorages.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Buildout',
          'Framework :: Zope5',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: Zope Public License',
      ],
      keywords='buildout zope zeo zodb mountpoint filestorage',
      author='David Glick',
      author_email='david.glick@plone.org',
      url='https://github.com/collective/collective.recipe.filestorage',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'plone.recipe.zope2instance',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      test_suite='collective.recipe.filestorage.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
