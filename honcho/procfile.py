import re

LINE = re.compile(r'^([A-Za-z0-9_]+):\s*(.+)$')

class InvalidProcfileError(Exception):
    pass

class Procfile(object):
    def __init__(self, contents):
        self.commands = {}

        for line in contents.splitlines():
            m = LINE.match(line)
            if m:
                self.commands[m.group(1)] = m.group(2)

