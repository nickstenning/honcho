"""
Compatibility layer and utilities, mostly for proper Windows support
"""
import ctypes
import sys
import time
from datetime import datetime, timedelta


# This works for both 32 and 64 bit Windows
ON_WINDOWS = 'win32' in str(sys.platform).lower()


def graceful_kill_windows(proc, timeout=2000):
    """
    gracefully kill a windows process, with a timeout
    
    send a ctrl-c event while disabling our own
    ctrl event handler to prevent killing ourselves and then
    re-enable our own ctrl handler and free the child console
    after a small delay
    """
    def wait():
        end = datetime.now() + timedelta(milliseconds=timeout)
        while proc.poll() is None:
            if datetime.now() >= end:
                break
            time.sleep(0.01)

    if ctypes.windll.kernel32.AttachConsole(proc.pid):
        ctypes.windll.kernel32.SetConsoleCtrlHandler(None, True)
        ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, 0)
        wait()
        ctypes.windll.kernel32.FreeConsole()
        ctypes.windll.kernel32.SetConsoleCtrlHandler(None, False)
    else:
        wait()