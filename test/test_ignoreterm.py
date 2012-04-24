import signal
import sys
import time

def handler(signum, frame):
    print "Received SIGTERM"
    sys.stdout.flush()

signal.signal(signal.SIGTERM, handler)

if __name__ == '__main__':
    while True:
        print "Still here"
        sys.stdout.flush()
        time.sleep(1)
