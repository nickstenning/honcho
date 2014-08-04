from ..helpers import TestCase
from ..helpers import get_honcho_output


class TestAwkward(TestCase):

    def test_awkward(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.awkward', 'start'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'system    \| (....)?awkward\.1 started \(pid=\d+\)\n')
        self.assertRegexpMatches(out, r'awkward\.1 \| (....)?(Hello with no line break){10}\n')
        self.assertRegexpMatches(out, r'system    \| (....)?awkward\.1 stopped \(rc=0\)\n')
