# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import Mock
from mock import patch

from honcho.test.helpers import TestCase

from honcho.export.base import BaseExport
from honcho.export.base import dashrepl


class GiraffeExport(BaseExport):
    def get_template_loader(self):
        return 'longneck'


class TestBaseExport(TestCase):
    @patch('jinja2.Environment')
    def test_env_default(self, env_mock):
        GiraffeExport()
        env_mock.assert_called_with(loader='longneck')

    @patch('jinja2.Environment')
    @patch('jinja2.FileSystemLoader')
    def test_env_template_dir(self, loader_mock, env_mock):
        BaseExport(template_dir='foo/bar')
        loader_mock.assert_called_with(['foo/bar'])
        env_mock.assert_called_with(loader=loader_mock.return_value)

    def test_get_template(self):
        fake_env = Mock()
        export = BaseExport(template_env=fake_env)
        export.get_template('foo/bar.tpl')
        fake_env.get_template.assert_called_with('foo/bar.tpl')


class TestDashrepl(TestCase):
    def test_dashrepl(self):
        self.assertEqual('foo', dashrepl('foo'))
        self.assertEqual('foo-1', dashrepl('foo.1'))
        self.assertEqual('foo-bar-baz', dashrepl('foo.bar.baz'))
        self.assertEqual('foo_bar_baz', dashrepl('foo_bar_baz'))
        self.assertEqual('foo-bar-baz', dashrepl('foo!bar:baz'))
        self.assertEqual('καλημέρα-κόσμε', dashrepl('καλημέρα.κόσμε'))
