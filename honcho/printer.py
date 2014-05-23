from datetime import datetime
import sys


class Printer(object):

    def __init__(self, output=sys.stdout, name='unknown', colour=None, width=0):
        self.output = output
        self.name = name
        self.colour = colour
        self.width = width

        self._write_prefix = True

    def write(self, *args, **kwargs):
        new_args = []
        for arg in args:
            lines = arg.split('\n')
            new_lines = []
            for line in lines:
                # now this is really uggly but I cant seem to find a way to 
                # properly encode/decode/wtf in py3
                if sys.version_info[0] > 2:
                    safe_line = line
                else:
                    safe_line = line.encode('utf-8')
                new_lines.append(
                    self._prefix() + safe_line if safe_line else safe_line)
            new_args.append('\n'.join(new_lines))
        try:
            self.output.write(*new_args, **kwargs)
        except UnicodeEncodeError:
            self.output.write('Problem encoding message', **kwargs)

    def _prefix(self):
        time = datetime.now().strftime('%H:%M:%S')
        name = self.name.ljust(self.width)
        prefix = '{time} {name} | '.format(time=time, name=name)
        if self.colour:
            return _colour_string(self.colour, prefix)
        else:
            return prefix


def _ansi(code):
    return '\033[{0}m'.format(code)


def _colour_string(colour, s):
    return '{0}{1}{2}'.format(_ansi(colour), s, _ansi(0))
