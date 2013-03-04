import sys

__version__ = '0.4.0devwin'

ON_POSIX = 'posix' in sys.builtin_module_names
# this works for both 32 and 64 bits Windows
ON_WINDOWS = 'win32' in str(sys.platform).lower()
