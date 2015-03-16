from mock import MagicMock
from mock import patch

from honcho.test.helpers import TestCase

from honcho.export.supervisord import Export


class TestExportSupervisord(TestCase):
    def setUp(self):  # noqa
        self.export = Export()

    @patch.object(Export, 'get_template')
    def test_render_adds_processes_to_context(self, fake_get_template):
        p1, p2 = object(), object()

        self.export.render([p1, p2], {'app': 'elephant'})

        fake_get_template.return_value.render.assert_called_with(
            {'app': 'elephant',
             'processes': [p1, p2]})

    def test_render_uses_app_name_as_filename(self):
        self.export.get_template = MagicMock()

        results = self.export.render([], {'app': 'elephant'})

        self.assertEqual('elephant.conf', results[0].name)
