from os import path
from shutil import rmtree
from tempfile import mkdtemp

from ..helpers import TestCase
from ..helpers import get_honcho_output


class NamedTemporaryDirectory:
    """A temporary directory that cleans up after itself."""

    def __init__(self, suffix='', prefix='tmp', dir=None):
        self.temp_dir = mkdtemp(suffix, prefix, dir)

    def __del__(self):
        self.delete()

    def delete(self):
        if self.temp_dir:
            rmtree(self.temp_dir)
            self.temp_dir = None

    def __enter__(self):
        return self.temp_dir

    def __exit__(self, *args):
        self.delete()


class TestExport(TestCase):
    def test_export_supervisord(self):
        with NamedTemporaryDirectory() as temp_dir:
            ret, out, err = get_honcho_output([
                'export',                  # command
                '-f', 'Procfile.simple',   # Procfile input
                'supervisord',             # output FORMAT
                temp_dir,                  # output LOCATION
            ])

            self.assertEqual(ret, 0)
            self.assertEqual(out, '')
            self.assertEqual(err, '')
            self.assertTrue(path.exists(path.join(temp_dir, 'fixtures.conf')))

    def test_export_upstart(self):
        with NamedTemporaryDirectory() as temp_dir:
            ret, out, err = get_honcho_output([
                'export',                  # command
                '-f', 'Procfile.simple',   # Procfile input
                'upstart',                 # output FORMAT
                temp_dir,                  # output LOCATION
            ])

            self.assertEqual(ret, 0)
            self.assertEqual(out, '')
            self.assertEqual(err, '')
            for filename in ('fixtures.conf',
                             'fixtures-foo.conf',
                             'fixtures-foo-1.conf'):
                self.assertTrue(path.exists(path.join(temp_dir, filename)))
