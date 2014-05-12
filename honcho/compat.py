"""
Compatibility layer and utilities, mostly for proper Windows and Python 3
support.
"""
import sys

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


# Python 3 doesn't understand __metaclass__ magic
def with_metaclass(meta, *bases):
    """Create a base class with metaclass."""
    return meta('NewBase', bases, {})

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
