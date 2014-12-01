from __future__ import print_function

import os
import sys
from pkg_resources import resource_filename

from honcho.command import CommandError

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

    def _mkdir(self, directory):
        if os.path.exists(directory):
            return
        try:
            os.makedirs(directory)
        except OSError as e:
            print(e)
            raise CommandError("Can not create {0}"
                               .format(directory))

    def _write(self, filename, content):
        path = os.path.join(self.options.location, filename)

        try:
            open(path, 'w').write(content)
        except IOError:
            raise CommandError("Can not write to file {0}"
                               .format(path))

    def get_template(self, name, package, directory='data/export/'):
        """Gets a Jinja2 template from specified directory.

        :param name: the name of specified template file.
        :param package: the top-level package for located the template
                        directory.
        :param directory: the template directory which contains the template
                          file.
        :returns: a :class:`jinja2.Template` instance.
        """
        relative_path = os.path.join(directory, self.options.format, name)
        path = resource_filename(package, relative_path)
        try:
            return Template(open(path).read())
        except IOError:
            raise CommandError("Can not find template with name {0}"
                               .format(name))

    def export(self):
        self._mkdir(self.options.location)

        files = self.render(self.procfile,
                            self.options,
                            self.environment,
                            self.concurrency)

        for name, content in files:
            print("[honcho export] writing: %s" % name, file=sys.stderr)
            self._write(name, content)

        return files

    def render(self, procfile, options, environment, concurrency):
        raise NotImplementedError("You must write a render method.")
