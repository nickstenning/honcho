from setuptools import setup, find_packages

setup(
    name = 'honcho',
    version = '0.0.1',
    packages = find_packages(),

    install_requires = [],

    # metadata for upload to PyPI
    author = 'Nick Stenning (Open Knowledge Foundation)',
    description = 'Honcho - manage Procfile-based applications',
    license = 'MIT',
    keywords = 'sysadmin process procfile',

    entry_points = {
        'console_scripts': [
            'honcho = honcho.command:main'
        ]
    }
)
