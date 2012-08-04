import argparse
import logging
import os
import re
import sys
from collections import defaultdict

from honcho import __version__
from honcho.procfile import Procfile
from honcho.process import Process, ProcessManager

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

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


class Honcho(object):
    "Manage Procfile-based applications"
    __metaclass__ = Commander

    name = 'honcho'
    version = __version__
    epilog = ''
    formatter_class = argparse.ArgumentDefaultsHelpFormatter

    subparser_title = 'tasks'
    subparser_help = ''
    subparser_formatter_class = formatter_class

    default = ['--help']
    commands = ['start', 'check', 'help', 'run']
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
            if e.message:
                log.error(e.message)
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

    @arg('command', nargs='+', help='Command to run')
    def run(self, options):
        "Run a command using your application's environment"
        self.read_env(options)

        cmd = ' '.join(options.command)
        p = Process(cmd, stdout=sys.stdout)
        p.wait()

    @option('-p', '--port', type=int, default=5000, metavar='N')
    @option('-c', '--concurrency', help='The number of each process type to run.', type=str, metavar='process=num,process=num')
    @arg('process', nargs='?', help='Name of process to start. All processes will be run if omitted.')
    def start(self, options):
        "Start the application (or a specific PROCESS)"
        self.read_env(options)
        procfile = self.make_procfile(options.procfile)

        port = options.port
        concurrency = self.parse_concurrency(options.concurrency)

        if options.process is not None:
            try:
                commands = {options.process: procfile.commands[options.process]}
            except KeyError:
                raise CommandError("Process type '{0}' does not exist in Procfile".format(options.process))
        else:
            commands = procfile.commands

        for name, cmd in commands.iteritems():
            for i in xrange(1, concurrency[name] + 1):
                n = '{name}.{i}'.format(**vars())
                os.environ['PORT'] = str(port)
                process_manager.add_process(n, cmd)
                port += 1
            port += 1000

        process_manager.loop()

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
        for envfile in files:
            try:
                with open(os.path.join(app_root, envfile)) as f:
                    content = f.read()
                self.set_env(content)
            except IOError:
                pass

    def set_env(self, content):
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

    def parse_concurrency(self, desc):
        result = defaultdict(lambda: 1)
        if desc is None:
            return result
        for item in desc.split(','):
            key, concurrency = item.split('=', 1)
            result[key] = int(concurrency)
        return result


def main():
    app = Honcho()
    app.parse()

if __name__ == '__main__':
    main()
