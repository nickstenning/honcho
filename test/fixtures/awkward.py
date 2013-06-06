from __future__ import print_function
import sys

if __name__ == '__main__':
    for i in range(10):
        print("Hello with no line break", end='')
        sys.stdout.flush()
