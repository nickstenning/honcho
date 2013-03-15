
'''
Compatibility layer and utilities, mostly for proper Windows support
'''
import sys


ON_POSIX = 'posix' in sys.builtin_module_names
# this works for both 32 and 64 bits Windows
ON_WINDOWS = 'win32' in str(sys.platform).lower()
