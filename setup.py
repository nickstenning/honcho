import sys
from setuptools import setup, find_packages

from honcho import __version__

requirements = ['jinja2==2.6']

if sys.version_info[:2] < (2, 7):
    requirements.append('argparse')
    requirements.append('ordereddict')

setup(
    name='honcho',
    version=__version__,
    packages=find_packages(exclude=['test*']),
    include_package_data=True,

    # metadata for upload to PyPI
    author='Nick Stenning',
    author_email='nick@whiteink.com',
    url='https://github.com/nickstenning/honcho',
    description='Honcho: a python clone of Foreman. For managing Procfile-based applications.',
    license='MIT',
    keywords='sysadmin process procfile',

    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'honcho=honcho.command:main'
        ]
    }
)
