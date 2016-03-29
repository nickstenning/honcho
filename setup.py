import codecs
import os
import re
from setuptools import find_packages
from setuptools import setup

###############################################################################

NAME = 'honcho'
AUTHOR = 'Nick Stenning'
AUTHOR_EMAIL = 'nick@whiteink.com'
DESCRIPTION = 'Honcho: a Python clone of Foreman. For managing Procfile-based applications.'
LICENSE = 'MIT'
KEYWORDS = 'sysadmin process procfile'
URL = 'https://github.com/nickstenning/honcho'
CLASSIFIERS = [
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]
INSTALL_REQUIRES = []
EXTRAS_REQUIRE = {
    ':python_version=="2.6"': ['argparse', 'ordereddict'],
    ':sys_platform=="win32"': ['colorama'],
    'export': ['jinja2>=2.7,<2.8'],
}
ENTRY_POINTS = {
    'console_scripts': [
        'honcho=honcho.command:main'
    ],
    'honcho_exporters': [
        'runit=honcho.export.runit:Export',
        'supervisord=honcho.export.supervisord:Export',
        'upstart=honcho.export.upstart:Export',
    ],
}


###############################################################################

HERE = os.path.dirname(__file__)


def read(*path):
    with codecs.open(os.path.join(HERE, *path), encoding='utf-8') as fp:
        return fp.read()

LONG_DESCRIPTION = read('README.rst')
VERSION = re.search(
    r'^__version__ = [\'"]([^\'"]*)[\'"]',
    read('honcho/__init__.py')
).group(1)

if __name__ == "__main__":
    setup(name=NAME,
          version=VERSION,
          packages=find_packages(),
          author=AUTHOR,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          license=LICENSE,
          keywords=KEYWORDS,
          url=URL,
          classifiers=CLASSIFIERS,
          install_requires=INSTALL_REQUIRES,
          extras_require=EXTRAS_REQUIRE,
          entry_points=ENTRY_POINTS,
          include_package_data=True)
