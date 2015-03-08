from __future__ import print_function

import os
import re
import sys

from honcho.compat import shellquote

try:
    import jinja2
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
    # Override this in subclasses -- e.g.: `supervisord`, `upstart`, etc.
    default_template_dir = ''

    def __init__(self, template_dir=None, template_env=None):
        if template_env:
            self._template_env = template_env
        else:
            self._template_env = self._get_template_env(template_dir)

    def _get_template_env(self, template_dir):
        loader = self._get_loader(template_dir)
        return _default_template_env(loader)

    def _get_loader(self, template_dir):
        if template_dir:
            return jinja2.FileSystemLoader([template_dir])
        else:
            return jinja2.PackageLoader(
                package_name=__name__,
                package_path=self._get_package_path())

    def _get_package_path(self):
        return os.path.join('templates', self.default_template_dir)

    def get_template(self, path):
        """
        Retrieve the template at the specified path. Returns an instance of
        :py:class:`Jinja2.Template` by default, but may be overridden by
        subclasses.
        """
        return self._template_env.get_template(path)

    def render(self, processes, context):
        raise NotImplementedError("You must implement a render method.")


def dashrepl(value):
    """
    Replace any non-word characters with a dash.
    """
    patt = re.compile(r'\W', re.UNICODE)
    return re.sub(patt, '-', value)


def _default_template_env(loader):
    env = jinja2.Environment(loader=loader)
    env.filters['shellquote'] = shellquote
    env.filters['dashrepl'] = dashrepl
    return env
