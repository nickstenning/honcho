from setuptools import setup, find_packages

setup(
    name = 'honcho',
    version = '0.0.3',
    packages = find_packages(),

    install_requires = [],

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
