from __future__ import print_function
import random
import sys

words = [word.strip() for word in open('/usr/share/dict/words')]

if __name__ == '__main__':
    while True:
        print(' '.join(random.choice(words) for _ in range(3)))
        sys.stdout.flush()
        # time.sleep(0.1)
