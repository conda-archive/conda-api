import re
import sys
if 'develop' in sys.argv:
    import setuptools

from distutils.core import setup

kwds = {}
kwds['long_description'] = open('README.rst').read()

# Read version from bitarray/__init__.py
pat = re.compile(r'__version__\s*=\s*(\S+)', re.M)
data = open('conda_api.py').read()
kwds['version'] = eval(pat.search(data).group(1))


setup(
    name = "conda-api",
    author = "Continuum Analytics, Inc.",
    author_email = "ilan@continuum.io",
    license = "BSD",
    description = "light weight conda interface library",
    py_modules = ['conda_api'],
    classifiers = [
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
    ],
    **kwds
)
