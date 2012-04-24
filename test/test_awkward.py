from __future__ import print_function
import sys
import time

if __name__ == '__main__':
    for i in xrange(10):
        print("Hello with no line break", end='')
        sys.stdout.flush()
        time.sleep(1)


