from __future__ import print_function
import os
import pwd
import sys
from honcho.command import CommandError, PATH

try:
    from jinja2 import Template
except ImportError:
    print("honcho's 'export' command requires the jinja2 package,\n"
          "which you don't appear to have installed.\n"
          "\n"
          "To fix this, install honcho with the 'export' extra selected:\n"
          "\n"
          "    pip install honcho[export]\n",
          file=sys.stderr)
    sys.exit(1)


class BaseExport(object):
    def __init__(self, procfile, options, environment, concurrency):
        self.procfile = procfile
        self.options = options
        self.environment = environment
        self.concurrency = concurrency

        try:
            user_entry = pwd.getpwnam(options.user)
        except KeyError:
            raise CommandError("No such user available: {0}"
                               .format(options.user))

        self.uid = user_entry.pw_uid
        self.gid = user_entry.pw_gid

    def _mkdir(self, directory):
        if os.path.exists(directory):
            return
        try:
            os.makedirs(directory)
        except OSError as e:
            print(e)
            raise CommandError("Can not create {0}"
                               .format(directory))

    def _chown(self, filename):
        try:
            os.chown(filename, self.uid, self.gid)
        except OSError:
            raise CommandError("Can not chown {0} to {1}"
                               .format(self.options.log,
                                       self.options.user))

    def _write(self, filename, content):
        path = os.path.join(self.options.location, filename)

        try:
            open(path, 'w').write(content)
        except IOError:
            raise CommandError("Can not write to file {0}"
                               .format(path))

    def get_template(self, name):
        path = os.path.join(PATH, 'data/export/', self.options.format, name)

        try:
            return Template(open(path).read())
        except IOError:
            raise CommandError("Can not find template with name {0}"
                               .format(name))

    def export(self):
        self._mkdir(self.options.location)
        self._mkdir(self.options.log)
        self._chown(self.options.log)

        files = self.render(self.procfile,
                            self.options,
                            self.environment,
                            self.concurrency)

        for name, content in files:
            self._write(name, content)

        return files

    def render(self, procfile, options, environment, concurrency):
        raise NotImplementedError("You must write a render method.")
