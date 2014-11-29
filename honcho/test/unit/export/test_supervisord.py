import logging
import os
from collections import defaultdict, namedtuple
from honcho.test.helpers import TestCase
from honcho.test.helpers import get_procfile

from honcho import compat
from honcho.export.supervisord import Export


Options = namedtuple("Options", ("app", "app_root", "format", "log", "port", "user", "shell", "location"))

DEFAULT_OPTIONS = Options(app="app", app_root="/path/to/app", format="supervisord", log="/path/to/log",
                          port=5000, user=os.getlogin(), shell="/usr/local/shell", location="/path/to/export")

DEFAULT_ENV = {}

DEFAULT_CONCURRENCY = defaultdict(lambda: 1)

logger = logging.getLogger(__name__)


def get_render(procfile, options, environment, concurrency):
    export = Export(procfile, options, environment, concurrency)
    return export.render(export.procfile, export.options, export.environment, export.concurrency)


class TestExportSupervisord(TestCase):

    def test_supervisord_export(self):
        procfile = get_procfile("Procfile.simple")
        render = get_render(procfile, DEFAULT_OPTIONS, DEFAULT_ENV, DEFAULT_CONCURRENCY)

        self.assertEqual(1, len(render))
        (fname, contents), = render

        parser = compat.ConfigParser()
        parser.readfp(compat.StringIO(contents))

        section = "program:app-foo"

        self.assertTrue(parser.has_section(section))
        self.assertEqual(DEFAULT_OPTIONS.user, parser.get(section, "user"))
        self.assertEqual("{0} -c 'python simple.py'"
                         .format(DEFAULT_OPTIONS.shell),
                         parser.get(section, "command"))

    def test_supervisord_concurrency(self):
        procfile = get_procfile("Procfile.simple")
        render = get_render(procfile, DEFAULT_OPTIONS, DEFAULT_ENV, {"foo": 4})

        self.assertEqual(1, len(render))
        (fname, contents), = render
        logger.debug('contents =\n%s', contents)

        parser = compat.ConfigParser()
        parser.readfp(compat.StringIO(contents))

        for job_index in compat.xrange(4):
            section = "program:app-foo-{0}".format(job_index)
            self.assertTrue(parser.has_section(section))
            self.assertEqual('PORT="{0}"'
                             .format(DEFAULT_OPTIONS.port + job_index),
                             parser.get(section, "environment"))

        self.assertEqual(
            parser.get("group:app", "programs"),
            ",".join("app-foo-{0}".format(i) for i in compat.xrange(4)))
