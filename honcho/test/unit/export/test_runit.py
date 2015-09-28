import collections

from mock import patch

from honcho.test.helpers import TestCase

from honcho.export.runit import Export

FakeProcess = collections.namedtuple('FakeProcess', 'name env')

FIX_1PROC = [FakeProcess('web.1', {'FOO': 'bar'})]


class TestExportRunit(TestCase):
    def setUp(self):  # noqa
        self.export = Export()

        self.get_template_patcher = patch.object(Export, 'get_template')
        self.get_template = self.get_template_patcher.start()

    def tearDown(self):  # noqa
        self.get_template_patcher.stop()

    def test_render(self):
        out = list(self.export.render(FIX_1PROC, {'app': 'elephant'}))

        run = _files_named('elephant-web-1/run', out)
        log = _files_named('elephant-web-1/log/run', out)
        self.assertEqual(1, len(run))
        self.assertTrue(run[0].executable)
        self.assertEqual(1, len(log))
        self.assertTrue(log[0].executable)

    def test_render_env(self):
        out = list(self.export.render(FIX_1PROC, {'app': 'elephant'}))

        env = _files_named('elephant-web-1/env/FOO', out)
        self.assertEqual(1, len(env))
        self.assertEqual('bar', env[0].content)


def _files_named(name, lst):
    return [f for f in lst if f.name == name]
