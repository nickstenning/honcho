"""
Compatibility layer and utilities, mostly for proper Windows support
"""
import sys

# This works for both 32 and 64 bit Windows
ON_WINDOWS = 'win32' in str(sys.platform).lower()
