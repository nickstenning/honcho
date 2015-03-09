import os
from setuptools import setup, find_packages

from honcho import __version__

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
    classifiers=[
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
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[],
    extras_require={
        ':python_version=="2.6"': ['argparse', 'ordereddict'],
        ':sys_platform=="win32"': ['colorama'],
        'export:python_version in "3.0,3.1,3.2"': ['jinja2>=2.6,<2.7'],
        'export:python_version not in "3.0,3.1,3.2"': ['jinja2>=2.7,<2.8'],
    },
    entry_points={
        'console_scripts': [
            'honcho=honcho.command:main'
        ],
        'honcho_exporters': [
            'upstart=honcho.export.upstart:Export',
            'supervisord=honcho.export.supervisord:Export',
        ],
    }
)
