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
    files = [env.strip() for env in args.env.split(',')]
    for envfile in files:
        try:
            with open(os.path.join(app_root, envfile)) as f:
                content = f.read()
            set_env(content)
        except IOError:
            pass


def set_env(content):
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


class MetaVarHidingHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar

        else:
            parts = []

            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                for option_string in action.option_strings:
                    parts.append(option_string)

            return ', '.join(parts)


class MainparserHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, MetaVarHidingHelpFormatter):
    pass


class SubparserHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, MetaVarHidingHelpFormatter):
    def is_subparsers_action(self, action):
        return isinstance(action, argparse._SubParsersAction)

    def _add_item(self, func, args):
        if (func == self._format_action and
                args and self.is_subparsers_action(args[0])):
            return
        self._current_section.items.append((func, args))

    def _metavar_formatter(self, action, default_metavar):
        if action.metavar is not None:
            result = action.metavar
        elif action.choices is not None:
            if self.is_subparsers_action(action):
                result = ""
            else:
                choice_strs = [str(choice) for choice in action.choices]
                result = '{%s}' % ','.join(choice_strs)
        else:
            result = default_metavar

        def format(tuple_size):
            if isinstance(result, tuple):
                return result
            else:
                return (result, ) * tuple_size
        return format

parser = argparse.ArgumentParser(version=__version__,
    description='Manage Procfile-based applications',
    formatter_class=MainparserHelpFormatter)

group = parser.add_argument_group('common arguments')
group.add_argument('-f', '--procfile', help='Procfile path', default='Procfile')
group.add_argument('-d', '--app-root', help='Procfile directory', default='.')
group.add_argument('-e', '--env', help='Environment file[,file]', default='.env')

subparsers = parser.add_subparsers(title='tasks')
subparams = {
    'parents': [parser],
    'add_help': False,
    'formatter_class': SubparserHelpFormatter,
}
parser_check = subparsers.add_parser('check', help="Validate your application's Procfile", **subparams)
parser_run = subparsers.add_parser('run', help="Run command using your environment", **subparams)
parser_start = subparsers.add_parser('start', help="Start the application (or PROCESS)", **subparams)

parser_check.set_defaults(func=check)

parser_run.add_argument('command', nargs='+', help='Command to run')
parser_run.set_defaults(func=run)

parser_start.add_argument('-p', '--port', help='Default: 5000', type=int, default=5000)
parser_start.add_argument('-c', '--concurrency', help='The number of each process type to run. The value passed in should be in the format "process=num,process=num"')
parser_start.add_argument('process', nargs='?', help='Name of process to start. All processes will be run if omitted.')
parser_start.set_defaults(func=start)

if __name__ == '__main__':
    main()
