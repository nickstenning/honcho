from __future__ import print_function

import argparse
from collections import defaultdict
import logging
import os
import re
import sys

from honcho import __version__
from honcho.procfile import Procfile
from honcho.process import Process, ProcessManager

logging.basicConfig(format='%(levelname)s: %(message)s')
log = logging.getLogger('honcho')

# Optionally make use of colorama to transparantly convert
# ANSI color code's for use on Windows
try:
    import colorama
    colorama.init(autoreset=True)
except ImportError:
    pass

process_manager = ProcessManager()

def make_procfile(filename):
    try:
        with open(filename) as f:
            content = f.read()
    except IOError:
        log.error('Procfile does not exist or is not a file')
        return False

    procfile = Procfile(content)

    if not procfile.commands:
        log.error('No processes defined in Procfile')
        return False

    return procfile

def read_env(args):
    app_root = args.app_root or os.path.dirname(args.procfile)
    try:
        with open(os.path.join(app_root, '.env')) as f:
            content = f.read()
    except IOError:
        content = ''

    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)

            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)

            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))

            os.environ[key] = val

def parse_concurrency(desc):
    result = defaultdict(lambda: 1)
    if desc is None:
        return result
    for item in desc.split(','):
        key, concurrency = item.split('=', 1)
        result[key] = int(concurrency)
    return result

def check(args):
    procfile = make_procfile(args.procfile)

    if not procfile:
        sys.exit(1)

    print('Valid procfile detected ({})'.format(', '.join(procfile.commands.keys())))

def run(args):
    read_env(args)

    cmd = ' '.join(args.command)
    p = Process(cmd, stdout=sys.stdout)
    p.wait()

def start(args):
    read_env(args)
    procfile = make_procfile(args.procfile)

    if not procfile:
        sys.exit(1)

    port = args.port
    concurrency = parse_concurrency(args.concurrency)

    for name, cmd in procfile.commands.iteritems():
        for i in xrange(1, concurrency[name] + 1):
            n = '{name}.{i}'.format(**vars())
            os.environ['PORT'] = str(port)
            process_manager.add_process(n, cmd)
            port += 1
        port += 1000

    process_manager.loop()

def main():
    args = parser.parse_args()
    args.func(args)

parser = argparse.ArgumentParser(description='Manage Procfile-based applications',
                                 version=__version__)

parser.add_argument('-f', '--procfile', help='Default: Procfile', default='Procfile')
parser.add_argument('-d', '--app-root', help='Default: Procfile directory')

subparsers = parser.add_subparsers(help='Commands')
parser_check = subparsers.add_parser('check', help="Validate your application's Procfile")
parser_run = subparsers.add_parser('run', help="Run a command using your application's environment")
parser_start = subparsers.add_parser('start', help="Start the application (or a specific PROCESS)")

parser_check.set_defaults(func=check)

parser_run.add_argument('command', nargs='+', help='Command to run')
parser_run.set_defaults(func=run)

parser_start.add_argument('-p', '--port', help='Default: 5000', type=int, default=5000)
parser_start.add_argument('-c', '--concurrency', help='The number of each process type to run. The value passed in should be in the format "process=num,process=num"')
parser_start.add_argument('process', nargs='?', help='Name of process to start. All processes will be run if omitted.')
parser_start.set_defaults(func=start)

if __name__ == '__main__':
    main()
