from __future__ import print_function

import os
import sys
from pkg_resources import resource_stream

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

    def get_template(self, filename):
        """Gets a Jinja2 template from specified directory.

        :param name: the name of specified template file.
        :param package: the top-level package for located the template
                        directory.
        :param directory: the template directory which contains the template
                          file.
        :returns: a :class:`jinja2.Template` instance.
        """
        relative_path = os.path.join('templates', filename)
        fp = resource_stream(__package__, relative_path)
        try:
            return Template(fp.read())
        except IOError:
            raise CommandError("Can not find template with name {0}"
                               .format(name))

    def export(self):
        _mkdir(self.options.location)

        files = self.render(self.procfile,
                            self.options,
                            self.environment,
                            self.concurrency)

        for name, content in files:
            _write_file(os.path.join(self.options.location, name), content)

        return files

    def render(self, procfile, options, environment, concurrency):
        raise NotImplementedError("You must write a render method.")


def _mkdir(path):
    if os.path.exists(path):
        return
    try:
        os.makedirs(path)
    except OSError as e:
        print(e)
        raise CommandError("Can not create {0}"
                           .format(directory))


def _write_file(filename, content):
    try:
        with open(filename, 'w') as fp:
            fp.write(content)
    except IOError:
        raise CommandError("Can not write to file {0}"
                           .format(path))
