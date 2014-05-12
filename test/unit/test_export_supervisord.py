import os
from collections import defaultdict, namedtuple

from honcho import compat
from honcho.export.supervisord import Export

from ..helpers import get_procfile, assert_equal

from nose.tools import assert_true


Options = namedtuple("Options", ("app", "app_root", "format", "log", "port", "user", "shell", "location"))

DEFAULT_OPTIONS = Options(app="app", app_root="/path/to/app", format="supervisord", log="/path/to/log",
                          port=5000, user=os.getlogin(), shell="/bin/sh", location="/path/to/export")

DEFAULT_ENV = {}

DEFAULT_CONCURRENCY = defaultdict(lambda: 1)


def get_render(procfile, options, environment, concurrency):
    export = Export(procfile, options, environment, concurrency)
    return export.render(export.procfile, export.options, export.environment, export.concurrency)


def test_supervisord_export():
    procfile = get_procfile("Procfile.simple")
    render = get_render(procfile, DEFAULT_OPTIONS, DEFAULT_ENV, DEFAULT_CONCURRENCY)

    assert_equal(1, len(render))
    (fname, contents), = render

    parser = compat.ConfigParser()
    parser.readfp(compat.StringIO(contents))

    section = "program:app-foo"

    assert_true(parser.has_section(section))
    assert_equal(DEFAULT_OPTIONS.user, parser.get(section, "user"))


def test_supervisord_concurrency():
    procfile = get_procfile("Procfile.simple")
    render = get_render(procfile, DEFAULT_OPTIONS, DEFAULT_ENV, {"foo": 4})

    assert_equal(1, len(render))
    (fname, contents), = render

    parser = compat.ConfigParser()
    parser.readfp(compat.StringIO(contents))

    for job_index in compat.xrange(4):
        section = "program:app-foo-{0}".format(job_index)
        assert_true(parser.has_section(section))
        assert_equal('PORT="{0}"'.format(DEFAULT_OPTIONS.port + job_index),
                     parser.get(section, "environment"))

    assert_equal(parser.get("group:app", "programs"),
                 ",".join("app-foo-{0}".format(i) for i in compat.xrange(4)))
