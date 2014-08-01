from __future__ import print_function
import sys
import time


if __name__ == '__main__':
    sys.stdout.write('normal output\n')
    sys.stdout.flush()
    sys.stderr.write('error output\n')
    sys.stderr.flush()
    time.sleep(0.1)
