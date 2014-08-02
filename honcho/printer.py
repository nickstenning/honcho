import sys

from honcho.environ import Env


class Printer(object):
    def __init__(self, output=sys.stdout, width=0, env=None):
        self._env = env if env is not None else Env()
        self.output = output
        self.width = width

    def write(self, string, name="", colour=None):
        time = self._env.now().strftime('%H:%M:%S')

        name = name.ljust(self.width)
        if name:
            name += " "

        for line in string.splitlines():
            prefix = '{time} {name}| '.format(time=time, name=name)
            if colour:
                prefix = _colour_string(colour, prefix)
            self.output.write(prefix + line + "\n")


def _ansi(code):
    return '\033[{0}m'.format(code)


def _colour_string(colour, s):
    return '{0}{1}{2}'.format(_ansi(colour), s, _ansi(0))
