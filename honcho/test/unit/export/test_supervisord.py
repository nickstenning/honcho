from mock import MagicMock
from mock import patch

from honcho.test.helpers import TestCase

from honcho.export.supervisord import Export


class TestExportCustomTemplate(TestCase):
    def test_render_custom_template_dir(self):
        template_dir = 'supervisord_custom_template.d'
        export_custom_template_dir = Export(template_dir=template_dir)
        export_custom_template_dir._template_env.get_template = MagicMock()
        p1 = object()

        out = list(export_custom_template_dir.render(p1, {'app': 'elephant'}))
        self.assertEqual(len(out), 1)

        get_template = export_custom_template_dir._template_env.get_template
        self.assertEqual(get_template.call_count, 1)
        get_template.assert_any_call('supervisord.conf')


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

        self.assertEqual('elephant.conf', results[0][0])
