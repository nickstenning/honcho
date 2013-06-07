"""
Compatibility layer and utilities, mostly for proper Windows and Python 3
support.
"""
import sys

# This works for both 32 and 64 bit Windows
ON_WINDOWS = 'win32' in str(sys.platform).lower()

# Check Python version
IS_PY3 = sys.version_info[0] == 3

# Python 3 hasn't iteritems, we should use items instead
iteritems = lambda data: data.items() if IS_PY3 else data.iteritems()

# Python 3 hasn't next method, we should use builtin function instead
next = lambda gen: next(gen) if IS_PY3 else gen.next()

# Python 3 hasn't xrange, we should use range instead
xrange = range if IS_PY3 else xrange

# Python 3 doesn't understand __metaclass__ magic
def with_metaclass(meta, *bases):
    """Create a base class with metaclass."""
    return meta('NewBase', bases, {})
