# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import MagicMock

from honcho.test.helpers import TestCase

from honcho.export.base import BaseExport
from honcho.export.base import dashrepl


class TestBaseExport(TestCase):
    def setUp(self):  # noqa
        self.fake_template_env = MagicMock()
        self.export = BaseExport(template_env=self.fake_template_env)

    def test_get_template(self):
        self.export.get_template('foo/bar.tpl')
        self.fake_template_env.get_template.assert_called_with('foo/bar.tpl')


class TestDashrepl(TestCase):
    def test_dashrepl(self):
        self.assertEqual('foo', dashrepl('foo'))
        self.assertEqual('foo-1', dashrepl('foo.1'))
        self.assertEqual('foo-bar-baz', dashrepl('foo.bar.baz'))
        self.assertEqual('foo_bar_baz', dashrepl('foo_bar_baz'))
        self.assertEqual('foo-bar-baz', dashrepl('foo!bar:baz'))
        self.assertEqual('καλημέρα-κόσμε', dashrepl('καλημέρα.κόσμε'))
