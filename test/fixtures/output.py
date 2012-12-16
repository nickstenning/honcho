import sys


if __name__ == '__main__':
    sys.stdout.write('some normal output\n')
    sys.stdout.flush()
    sys.stderr.write('and then write to stderr\n')
    sys.stderr.flush()
