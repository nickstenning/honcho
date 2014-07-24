"""
Compatibility layer and utilities, mostly for proper Windows and Python 3
support.
"""
import sys

# Wrap stdout and stderr, to fix UnicodeEncodeError when environment
# variables PYTHONUNBUFFERED=true
import codecs
import locale
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr)

# This works for both 32 and 64 bit Windows
ON_WINDOWS = 'win32' in str(sys.platform).lower()

# Python 3 hasn't iteritems, we should use items instead
try:
    {}.iteritems
except AttributeError:
    iteritems = lambda data: data.items()
else:
    iteritems = lambda data: data.iteritems()

# Python 3 hasn't xrange, we should use range instead
try:
    xrange = xrange
except NameError:
    xrange = range

# Python 3 does not have StringIO, we should use the io module instead
try:
    from StringIO import StringIO  # noqa
except ImportError:
    from io import StringIO  # noqa

# Python 3 renamed ConfigParser to configparser
try:
    from ConfigParser import ConfigParser  # noqa
except ImportError:
    from configparser import ConfigParser  # noqa

# Python 3 exposed quote as public API in the shlex module
try:
    from pipes import quote as shellquote  # noqa
except ImportError:
    from shlex import quote as shellquote  # noqa
