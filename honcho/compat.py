
'''
Compatibility layer and utilities, mostly for proper Windows support
'''
import sys


# this works for both 32 and 64 bits Windows
ON_WINDOWS = 'win32' in str(sys.platform).lower()
