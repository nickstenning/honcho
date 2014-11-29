import collections

from mock import MagicMock
from mock import call
from mock import patch

from honcho.test.helpers import TestCase

from honcho.export.upstart import Export

FakeProcess = collections.namedtuple('FakeProcess', 'name')

FIX_1PROC = [FakeProcess('web.1')]
FIX_NPROC = [FakeProcess('web.1'),
             FakeProcess('worker.1'),
             FakeProcess('worker.2')]


class TestExportUpstart(TestCase):
    def setUp(self):  # noqa
        self.export = Export()

        self.master = MagicMock()
        self.process_master = MagicMock()
        self.process = MagicMock()

        def _get_template(name):
            if name.endswith('process_master.conf'):
                return self.process_master
            elif name.endswith('process.conf'):
                return self.process
            elif name.endswith('master.conf'):
                return self.master
            else:
                raise RuntimeError("tests don't know about that template")

        self.get_template_patcher = patch.object(Export, 'get_template')
        self.get_template = self.get_template_patcher.start()
        self.get_template.side_effect = _get_template

    def tearDown(self):  # noqa
        self.get_template_patcher.stop()

    def test_render_master(self):
        out = self.export.render(FIX_1PROC, {'app': 'elephant'})

        self.assertIn(('elephant.conf', self.master.render.return_value),
                      out)

        self.master.render.assert_called_once_with({'app': 'elephant'})

    def test_render_process_master(self):
        out = self.export.render(FIX_1PROC, {'app': 'elephant'})

        self.assertIn(('elephant-web.conf',
                       self.process_master.render.return_value),
                      out)

        expected = {'app': 'elephant',
                    'group_name': 'elephant-web'}
        self.process_master.render.assert_called_once_with(expected)

    def test_render_process(self):
        out = self.export.render(FIX_1PROC, {'app': 'elephant'})

        self.assertIn(('elephant-web-1.conf',
                       self.process.render.return_value),
                      out)

        expected = {'app': 'elephant',
                    'group_name': 'elephant-web',
                    'process': FIX_1PROC[0]}
        self.process.render.assert_called_once_with(expected)

    def test_render_multiple_process_groups(self):
        out = self.export.render(FIX_NPROC, {'app': 'elephant'})

        self.assertIn(('elephant-web.conf',
                       self.process_master.render.return_value),
                      out)
        self.assertIn(('elephant-worker.conf',
                       self.process_master.render.return_value),
                      out)

        expected = [call({'app': 'elephant',
                          'group_name': 'elephant-web'}),
                    call({'app': 'elephant',
                          'group_name': 'elephant-worker'})]
        self.assertEqual(expected, self.process_master.render.call_args_list)

    def test_render_multiple_processes(self):
        out = self.export.render(FIX_NPROC, {'app': 'elephant'})

        self.assertIn(('elephant-web-1.conf',
                       self.process.render.return_value),
                      out)
        self.assertIn(('elephant-worker-1.conf',
                       self.process.render.return_value),
                      out)
        self.assertIn(('elephant-worker-2.conf',
                       self.process.render.return_value),
                      out)

        expected = [call({'app': 'elephant',
                          'group_name': 'elephant-web',
                          'process': FIX_NPROC[0]}),
                    call({'app': 'elephant',
                          'group_name': 'elephant-worker',
                          'process': FIX_NPROC[1]}),
                    call({'app': 'elephant',
                          'group_name': 'elephant-worker',
                          'process': FIX_NPROC[2]})]
        self.assertEqual(expected, self.process.render.call_args_list)
