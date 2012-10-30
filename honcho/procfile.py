try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import re

LINE = re.compile(r'^([A-Za-z0-9_]+):\s*(.+)$')


class Procfile(object):
    def __init__(self, contents):
        self.commands = OrderedDict()

        for line in contents.splitlines():
            m = LINE.match(line)
            if m:
                self.commands[m.group(1)] = m.group(2)
