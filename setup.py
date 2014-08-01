import os
import sys
from setuptools import setup, find_packages

from honcho import __version__

requirements = []
export_requirements = []

if sys.version_info[:2] < (2, 7):
    requirements.append('argparse')
    requirements.append('ordereddict')

if (3, 0) <= sys.version_info[:2] < (3, 3):
    export_requirements = ['jinja2>=2.6,<2.7']
else:
    export_requirements = ['jinja2>=2.7,<2.8']

HERE = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(HERE, 'README.rst')).read()
except:
    long_description = None

setup(
    name='honcho',
    version=__version__,
    packages=find_packages(exclude=['honcho.test*']),
    include_package_data=True,

    # metadata for upload to PyPI
    author='Nick Stenning',
    author_email='nick@whiteink.com',
    url='https://github.com/nickstenning/honcho',
    description='Honcho: a python clone of Foreman. For managing Procfile-based applications.',
    long_description=long_description,
    license='MIT',
    keywords='sysadmin process procfile',

    install_requires=requirements,
    extras_require={
        'export': export_requirements,
    },
    entry_points={
        'console_scripts': [
            'honcho=honcho.command:main'
        ]
    }
)
