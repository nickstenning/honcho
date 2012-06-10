from setuptools import setup, find_packages

from honcho import __version__

setup(
    name = 'honcho',
    version = __version__,
    packages = find_packages(),

    # metadata for upload to PyPI
    author = 'Nick Stenning',
    author_email = 'nick@whiteink.com',
    url = 'https://github.com/nickstenning/honcho',
    description = 'Honcho - manage Procfile-based applications',
    license = 'MIT',
    keywords = 'sysadmin process procfile',

    entry_points = {
        'console_scripts': [
            'honcho = honcho.command:main'
        ]
    }
)
