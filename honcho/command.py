import argparse
import codecs
import logging
import os
import sys
from collections import defaultdict

from honcho import __version__
from honcho.procfile import Procfile
from honcho.process import Process, ProcessManager
from honcho import compat, environ

logging.basicConfig(format='%(asctime)s [%(process)d] [%(levelname)s] '
                           '%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
log = logging.getLogger(__name__)

PATH = os.path.dirname(__file__)
BASENAME = os.path.basename(os.getcwd())

EXPORT_CHOICES = ['supervisord', 'upstart']

try:
    # Python 3
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)
except AttributeError:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr)


process_manager = ProcessManager()


class CommandError(Exception):
    pass

_parent_parser = argparse.ArgumentParser(
    'honcho',
    description='Manage Procfile-based applications',
    add_help=False)
_parent_parser.add_argument(
    '-e', '--env',
    help='environment file[,file]', default='.env')
_parent_parser.add_argument(
    '-d', '--app-root',
    help='procfile directory', default='.')
_parent_parser.add_argument(
    '-f', '--procfile',
    help='procfile path', default='Procfile')
_parent_parser.add_argument(
    '-v', '--version',
    action='version', version='%(prog)s ' + __version__)

_parser_defaults = {
    'parents': [_parent_parser],
    'formatter_class': argparse.ArgumentDefaultsHelpFormatter,
}

parser = argparse.ArgumentParser(**_parser_defaults)

subparsers = parser.add_subparsers(title='tasks')


def command_check(args):
    procfile = _procfile(_procfile_path(args.app_root, args.procfile))

    log.info('Valid procfile detected ({0})'.format(', '.join(procfile.commands)))

parser_check = subparsers.add_parser(
    'check',
    help="validate a Procfile",
    **_parser_defaults)
parser_check.set_defaults(func=command_check)


def command_export(args):
    if args.log == "/var/log/APP":
        args.log = args.log.replace('APP', args.app)

    if args.user is None:
        if compat.ON_WINDOWS:
            args.user = os.environ.get('USERNAME')
        else:
            args.user = os.environ.get('USER')

    if args.user is None:
        raise CommandError('Could not automatically deduce user: please '
                           'supply the -u/--user option.')

    args.app_root = os.path.abspath(args.app_root)

    procfile_path = _procfile_path(args.app_root, args.procfile)
    procfile = _procfile(procfile_path)
    env = _read_env(procfile_path, args.env)
    concurrency = _parse_concurrency(args.concurrency)

    mod = __import__('.'.join(['honcho', 'export', args.format]),
                     fromlist=['Export'])

    export = mod.Export(procfile, args, env, concurrency)
    export.export()

parser_export = subparsers.add_parser(
    'export',
    help="export a Procfile to another format",
    **_parser_defaults)
parser_export.add_argument(
    '-a', '--app',
    help="alternative app name", default=BASENAME, type=str, metavar='APP')
parser_export.add_argument(
    '-l', '--log',
    help="directory to place process logs in",
    default="/var/log/APP", type=str, metavar='DIR')
parser_export.add_argument('-p', '--port', default=5000, type=int, metavar='N')
parser_export.add_argument(
    '-c', '--concurrency',
    help='number of each process type to run.',
    type=str, metavar='process=num,process=num')
parser_export.add_argument(
    '-u', '--user',
    help="user the application should run as",
    type=str)
parser_export.add_argument(
    '-s', '--shell',
    help="the shell that should run the application",
    default='/bin/sh', type=str)
parser_export.add_argument(
    'location',
    help="folder to export to",
    default=EXPORT_CHOICES[0], type=str, metavar="LOCATION")
parser_export.add_argument(
    'format',
    help="format in which to export",
    default=EXPORT_CHOICES[0], choices=EXPORT_CHOICES,
    type=str, metavar="FORMAT")
parser_export.set_defaults(func=command_export)


def command_help(args):
    argv = ['--help']
    if args.task:
        argv.append(args.task)
    return parser.parse_args(argv[::-1])

parser_help = subparsers.add_parser(
    'help',
    help="describe available tasks or one specific task",
    **_parser_defaults)
parser_help.add_argument('task', help='task to show help for', nargs='?')
parser_help.set_defaults(func=command_help)


def command_run(args):
    procfile_path = _procfile_path(args.app_root, args.procfile)
    os.environ.update(_read_env(procfile_path, args.env))

    if compat.ON_WINDOWS:
        # do not quote on Windows, subprocess will handle it for us
        # using the MSFT quoting rules
        cmd = args.command
    else:
        cmd = ' '.join(compat.shellquote(arg) for arg in args.command)

    p = Process(cmd, stdout=sys.stdout, stderr=sys.stderr)
    p.wait()
    sys.exit(p.returncode)

parser_run = subparsers.add_parser(
    'run',
    help="run a command using your application's environment",
    **_parser_defaults)
parser_run.add_argument(
    'command',
    nargs=argparse.REMAINDER,
    help='command to run')
parser_run.set_defaults(func=command_run)


def command_start(args):
    procfile_path = _procfile_path(args.app_root, args.procfile)
    procfile = _procfile(procfile_path)
    os.environ.update(_read_env(procfile_path, args.env))

    port = int(os.environ.get('PORT', args.port))
    concurrency = _parse_concurrency(args.concurrency)
    quiet = _parse_quiet(args.quiet)

    processes = args.processes

    if len(processes) > 0:
        commands = {}
        for process in processes:
            try:
                commands[process] = procfile.commands[process]
            except KeyError:
                raise CommandError("Process type '{0}' does not exist in Procfile".format(process))
    else:
        commands = procfile.commands

    for name, cmd in compat.iteritems(commands):
        for i in compat.xrange(concurrency[name]):
            n = '{name}.{num}'.format(name=name, num=i + 1)
            os.environ['PORT'] = str(port + i)
            process_manager.add_process(n, cmd, quiet=(name in quiet))
        port += 100

    sys.exit(process_manager.loop())

parser_start = subparsers.add_parser(
    'start',
    help="start the application (or a specific PROCESS)",
    **_parser_defaults)
parser_start.add_argument(
    '-p', '--port',
    help="starting port number",
    type=int, default=5000, metavar='N')
parser_start.add_argument(
    '-c', '--concurrency',
    help='the number of each process type to run.',
    type=str, metavar='process=num,process=num')
parser_start.add_argument(
    '-q', '--quiet',
    help='process names for which to suppress output',
    type=str, metavar='process1,process2,process3')
parser_start.add_argument(
    'processes', nargs='*',
    help='process(es) to start (default: all processes will be run)')
parser_start.set_defaults(func=command_start)


def main(argv=None):
    if argv is not None:
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args()
    try:
        args.func(args)
    except CommandError as e:
        log.error(str(e))
        sys.exit(1)


def _procfile_path(app_root, procfile):
    return os.path.join(app_root, procfile)


def _procfile(filename):
    try:
        with open(filename) as f:
            content = f.read()
    except IOError:
        raise CommandError('Procfile does not exist or is not a file')

    procfile = Procfile(content)

    if not procfile.commands:
        raise CommandError('No processes defined in Procfile')

    return procfile


def _read_env(procfile_path, env):
    app_root = os.path.dirname(procfile_path)
    files = [e.strip() for e in env.split(',')]
    content = []
    for envfile in files:
        try:
            with open(os.path.join(app_root, envfile)) as f:
                content.append(f.read())
        except IOError:
            pass

    return environ.parse('\n'.join(content))


def _parse_concurrency(desc):
    result = defaultdict(lambda: 1)
    if desc is None:
        return result
    for item in desc.split(','):
        key, concurrency = item.split('=', 1)
        result[key] = int(concurrency)
    return result


def _parse_quiet(desc):
    result = []
    if desc is None:
        return result
    result = desc.split(',')
    return result


if __name__ == '__main__':
    main()
