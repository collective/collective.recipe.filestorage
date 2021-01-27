# -*- coding: utf-8 -*-
"""
Doctest runner for 'collective.recipe.filestorage'.
"""
__docformat__ = 'restructuredtext'

import os
import re
import unittest
import zc.buildout.tests
import zc.buildout.testing
import subprocess

from zope.testing import doctest, renormalizing

optionflags =  (doctest.ELLIPSIS |
#                doctest.REPORT_NDIFF |
                doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE)
                
current_dir = os.path.abspath(os.path.dirname(__file__))
recipe_location = current_dir
zope2_location = os.path.join(current_dir, 'zope2')

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    # Install any other recipes that should be available in the tests
    zc.buildout.testing.install('plone.recipe.zope2instance', test)
    zc.buildout.testing.install('zc.recipe.egg', test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('collective.recipe.filestorage', test)
    
    # Add a base.cfg we can extend
    version = os.environ.get('PLONE_VERSION', '5.1')
    zc.buildout.testing.write('base.cfg', '''
[buildout]
extends = http://dist.plone.org/release/{version}-latest/versions.cfg
find-links =
    https://dist.plone.org/release/{version}-latest/
    https://dist.plone.org/thirdparty/
'''.format(version=version))

def run_buildout(*args):
    (out,err) = subprocess.Popen([os.path.join('bin', 'buildout')]+list(args),
                                 stdout=subprocess.PIPE,stderr=subprocess.STDOUT
    ).communicate()
    if out is None:
        return ''
    else:
        return out

def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'doctests.rst',
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # ignore warnings in output
                        (re.compile('^.*?Warning.*?\n\s*?\n', re.I | re.S), ''),
                        (re.compile('^.*?zip_safe.*?$', re.M), ''),
                        (re.compile('^.*?module references __path__.*?$', re.M), ''),
                        (re.compile('^\s*\n', re.S), ''),
                        zc.buildout.testing.normalize_path,
                        ]),
                globs = globals()
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
