import argparse
import logging
import os
import re
import sys
from collections import defaultdict
try:
    from shlex import quote as shellquote # Python 3
except ImportError:
    from pipes import quote as shellquote

from honcho import __version__
from honcho.procfile import Procfile
from honcho.process import Process, ProcessManager
from honcho import compat

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

PATH = os.path.dirname(__file__)
BASENAME = os.path.basename(os.getcwd())

EXPORT_CHOICES = ['supervisord', 'upstart']

process_manager = ProcessManager()


# option decorator
def option(*args, **kwargs):
    def _decorator(func):
        _option = (args, kwargs)
        if hasattr(func, 'options'):
            func.options.append(_option)
        else:
            func.options = [_option]
        return func
    return _decorator

# arg decorator
arg = option


class Commander(type):
    def __new__(cls, name, bases, attrs):
        subcommands = {}
        commands = attrs.get('commands', [])
        for command in commands:
            func = attrs.get(command, None)
            if func is not None:
                subcommand = {
                    'name': command,
                    'func': func,
                    'options': []
                }
                if hasattr(func, 'options'):
                    subcommand['options'] = func.options
                subcommands[command] = subcommand
        attrs['_subcommands'] = subcommands
        return type.__new__(cls, name, bases, attrs)


class CommandError(Exception):
    pass


class Honcho(compat.with_metaclass(Commander, object)):
    "Manage Procfile-based applications"

    name = 'honcho'
    version = __version__
    epilog = ''
    formatter_class = argparse.ArgumentDefaultsHelpFormatter

    subparser_title = 'tasks'
    subparser_help = ''
    subparser_formatter_class = formatter_class

    default = ['--help']
    commands = ['start', 'check', 'help', 'run', 'export']
    common = [
        option('-e', '--env', help='Environment file[,file]', default='.env'),
        option('-d', '--app-root', help='Procfile directory', default='.'),
        option('-f', '--procfile', help='Procfile path', default='Procfile'),
    ]

    def add_common(self, parser):
        "add all common options and arguments to the main parser"
        common_group = parser.add_argument_group('common arguments')
        for option in self.common:
            options = option(lambda: None).options
            if options:
                args, kwargs = options[0]
                common_group.add_argument(*args, **kwargs)

    def parse(self, argv=None):
        # the main parser
        parser = argparse.ArgumentParser(
            prog=self.name,
            formatter_class=self.formatter_class,
            description=self.__doc__,
            epilog=self.epilog,
        )
        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s ' + self.version)
        self.add_common(parser)

        # then add the subparsers
        subparsers = parser.add_subparsers(
            title=self.subparser_title,
            help=self.subparser_help)

        for name, subcommand in sorted(self._subcommands.items()):
            subparser = subparsers.add_parser(subcommand['name'],
                                              help=subcommand['func'].__doc__,
                                              formatter_class=self.subparser_formatter_class)
            self.add_common(subparser)
            for args, kwargs in subcommand['options']:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=subcommand['func'])

        if not argv:
            argv = sys.argv[1:]
        if not argv:
            argv = self.default

        options = parser.parse_args(argv)

        try:
            options.func(self, options)
        except CommandError as e:
            log.error(str(e))
            sys.exit(1)

    @arg('task', help='Task to show help for', nargs='?')
    def help(self, options):
        "Describe available tasks or one specific task"
        argv = ['--help']
        if options.task:
            argv.append(options.task)
        return self.parse(argv[::-1])

    def check(self, options):
        "Validate your application's Procfile"
        procfile = self.make_procfile(options.procfile)

        log.info('Valid procfile detected ({0})'.format(', '.join(procfile.commands)))

    @arg('command', nargs=argparse.REMAINDER, help='Command to run')
    def run(self, options):
        "Run a command using your application's environment"
        self.set_env(self.read_env(options))

        if compat.ON_WINDOWS:
            # do not quote on Windows, subprocess will handle it for us
            # using the MSFT quoting rules
            cmd = options.command
        else:
            cmd = ' '.join(shellquote(arg) for arg in options.command)

        p = Process(cmd, stdout=sys.stdout, stderr=sys.stderr)
        p.wait()
        sys.exit(p.returncode)

    @option('-p', '--port', type=int, default=5000, metavar='N')
    @option('-c', '--concurrency', help='The number of each process type to run.', type=str, metavar='process=num,process=num')
    @option('-q', '--quiet', help='Any processes that you want to quiet ouput of.', type=str, metavar='process1,process2,process3')
    @arg('processes', nargs='*', help='Process(es) to start. All processes will be run if omitted.')
    def start(self, options):
        "Start the application (or a specific PROCESS)"
        self.set_env(self.read_env(options))
        procfile = self.make_procfile(options.procfile)

        port = int(os.environ.get('PORT', options.port))
        concurrency = self.parse_concurrency(options.concurrency)
        quiet = self.parse_quiet(options.quiet)


        processes = options.processes

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

    @option('-a', '--app',
            help="Alternative app name", default=BASENAME, type=str, metavar='APP')
    @option('-l', '--log',
            help="Specify the directory to place process logs in",
            default="/var/log/APP", type=str, metavar='DIR')
    @option('-p', '--port', default=5000, type=int, metavar='N')
    @option('-c', '--concurrency',
            help='The number of each process type to run.',
            type=str, metavar='process=num,process=num')
    @option('-u', '--user',
            help="Specify the user the application should run as",
            type=str)
    @option('-s', '--shell',
            help="Specify the shell that should run the application",
            default='/bin/sh', type=str)
    @arg('location',
         help="Folder to export to",
         default=EXPORT_CHOICES[0], type=str, metavar="LOCATION")
    @arg('format',
         help="What format to export to",
         default=EXPORT_CHOICES[0], choices=EXPORT_CHOICES, type=str, metavar="FORMAT")
    def export(self, options):
        "Export the application to another process management format"
        if options.log == "/var/log/APP":
            options.log = options.log.replace('APP', options.app)

        if options.user is None:
            if compat.ON_WINDOWS:
                options.user = os.environ.get('USERNAME')
            else:
                options.user = os.environ.get('USER')

        if options.user is None:
            raise CommandError('Could not automatically deduce user: please '
                               'supply the -u/--user option.')

        options.app_root = os.path.abspath(options.app_root)

        procfile = self.make_procfile(options.procfile)
        env = self.read_env(options)
        concurrency = self.parse_concurrency(options.concurrency)

        mod = __import__('.'.join(['honcho', 'export', options.format]),
                         fromlist=['Export'])

        export = mod.Export(procfile, options, env, concurrency)
        export.export()

    def make_procfile(self, filename):
        try:
            with open(filename) as f:
                content = f.read()
        except IOError:
            raise CommandError('Procfile does not exist or is not a file')

        procfile = Procfile(content)

        if not procfile.commands:
            raise CommandError('No processes defined in Procfile')

        return procfile

    def read_env(self, args):
        app_root = args.app_root or os.path.dirname(args.procfile)
        files = [env.strip() for env in args.env.split(',')]
        content = []
        for envfile in files:
            try:
                with open(os.path.join(app_root, envfile)) as f:
                    content.append(f.read())
            except IOError:
                pass

        return self.parse_env('\n'.join(content))

    def parse_env(self, content):
        values = {}
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

                values[key] = val
        return values

    def set_env(self, values):
        os.environ.update(values)

    def parse_concurrency(self, desc):
        result = defaultdict(lambda: 1)
        if desc is None:
            return result
        for item in desc.split(','):
            key, concurrency = item.split('=', 1)
            result[key] = int(concurrency)
        return result

    def parse_quiet(self, desc):
        result = []
        if desc is None:
            return result
        result = desc.split(',')
        return result



def main():
    app = Honcho()
    app.parse()

if __name__ == '__main__':
    main()
