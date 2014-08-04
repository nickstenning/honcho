import re
from ..helpers import TestCase
from ..helpers import get_honcho_output

from honcho import compat


class TestStart(TestCase):

    def test_start_simple(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.simple', 'start'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'system \| (....)?foo\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?foo\.1 stopped \(rc=0\)\n')

        count = len(re.findall(r'foo\.1  \| (....)?(normal|error) output\n', out))
        self.assertEqual(count, 2)

    def test_start_with_arg(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', 'foo'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'system \| (....)?foo\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?foo\.1 stopped \(rc=0\)\n')

        count = len(re.findall(r'foo\.1  \| (....)?(normal|error) output\n', out))
        self.assertEqual(count, 2)

    def test_start_with_multiple_args(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', 'foo', 'bar'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'system \| (....)?foo\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?foo\.1 stopped \(rc=.+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?bar\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?bar\.1 stopped \(rc=.+\)\n')

        count = len(re.findall(r'foo\.1  \| (....)?(normal|error) output\n', out))
        self.assertEqual(count, 2)
        count = len(re.findall(r'bar\.1  \| (....)?(normal|error) output\n', out))
        self.assertEqual(count, 2)
        count = len(re.findall(r'baz\.1  \| (....)?(normal|error) output\n', out))
        self.assertEqual(count, 0)

    def test_start_returncode(self):
        procfile = 'Procfile.returncodewin' if compat.ON_WINDOWS else 'Procfile.returncode'
        ret, out, err = get_honcho_output(['-f', procfile, 'start'])

        self.assertTrue(ret in [123, 42])

    def test_start_with_arg_returncode(self):
        procfile = 'Procfile.returncodewin' if compat.ON_WINDOWS else 'Procfile.returncode'
        ret, out, err = get_honcho_output(['-f', procfile, 'start', 'bar'])

        self.assertEqual(ret, 42)

    def test_start_joins_stderr_into_stdout(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'normal output')
        self.assertRegexpMatches(out, r'error output')
        self.assertEqual(err, '')

    def test_start_quiet_simple(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', '-qbaz'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'foo\.1 *\| (....)?normal output')
        self.assertRegexpMatches(out, r'foo\.1 *\| (....)?error output')
        self.assertRegexpMatches(out, r'bar\.1 *\| (....)?normal output')
        self.assertRegexpMatches(out, r'bar\.1 *\| (....)?error output')
        self.assertNotRegexpMatches(out, r'baz\.1 *\| (....)?normal output')
        self.assertNotRegexpMatches(out, r'baz\.1 *\| (....)?error output')

        self.assertRegexpMatches(out, r'system \| (....)?baz\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?baz\.1 stopped \(rc=.+\)\n')

        self.assertEqual(err, '')

    def test_start_quiet_multi(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', '-qbaz,bar'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'foo\.1 *\| (....)?normal output')
        self.assertRegexpMatches(out, r'foo\.1 *\| (....)?error output')
        self.assertNotRegexpMatches(out, r'bar\.1 *\| (....)?normal output')
        self.assertNotRegexpMatches(out, r'bar\.1 *\| (....)?error output')
        self.assertNotRegexpMatches(out, r'baz\.1 *\| (....)?normal output')
        self.assertNotRegexpMatches(out, r'baz\.1 *\| (....)?error output')

        self.assertRegexpMatches(out, r'system \| (....)?bar\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?bar\.1 stopped \(rc=.+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?baz\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?baz\.1 stopped \(rc=.+\)\n')

        self.assertEqual(err, '')

    def test_start_quiet_all(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', '-qfoo,baz,bar'])

        self.assertEqual(ret, 0)

        self.assertNotRegexpMatches(out, r'normal output')
        self.assertNotRegexpMatches(out, r'error output')

        self.assertRegexpMatches(out, r'system \| (....)?foo\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?foo\.1 stopped \(rc=.+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?bar\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?bar\.1 stopped \(rc=.+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?baz\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'system \| (....)?baz\.1 stopped \(rc=.+\)\n')

        self.assertEqual(err, '')
