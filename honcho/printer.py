from collections import namedtuple
import sys

from .compat import ON_WINDOWS

Message = namedtuple("Message", "type data time name colour")


class Printer(object):
    """
    Printer is where Honcho's user-visible output is defined. A Printer
    instance receives typed messages and prints them to its output (usually
    STDOUT) in the Honcho format.
    """

    def __init__(self,
                 output=sys.stdout,
                 time_format="%H:%M:%S",
                 width=0):
        self.output = output
        self.time_format = time_format
        self.width = width

    def write(self, message):
        if message.type != 'line':
            raise RuntimeError('Printer can only process messages of type "line"')

        name = message.name if message.name is not None else ""
        name = name.ljust(self.width)
        if name:
            name += " "

        # When encountering data that cannot be interpreted as UTF-8 encoded
        # Unicode, Printer will replace the unrecognisable bytes with the
        # Unicode replacement character (U+FFFD).
        if isinstance(message.data, bytes):
            string = message.data.decode("utf-8", "replace")
        else:
            string = message.data

        for line in string.splitlines():
            time_formatted = message.time.strftime(self.time_format)
            prefix = '{time} {name}| '.format(time=time_formatted, name=name)
            if message.colour:
                prefix = _colour_string(message.colour, prefix)
            self.output.write(prefix + line + "\n")


def _ansi(code):
    return '\033[{0}m'.format(code)


def _colour_string(colour, s):
    return '{0}{1}{2}'.format(_ansi(colour), s, _ansi(0))


if ON_WINDOWS:
    # The colorama package provides transparent support for ANSI colour codes
    # on Win32 platforms. We try and import and configure that, but fall back
    # to no colour if we fail.
    try:
        import colorama
    except ImportError:
        def _colour_string(colour, s):  # noqa
            return s
    else:
        colorama.init()
