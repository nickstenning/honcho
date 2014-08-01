from ..helpers import TestCase
from ..helpers import get_honcho_output


class TestMulti(TestCase):

    def test_multi_check(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.multi', 'check'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(err, 'Valid procfile detected')
        self.assertRegexpMatches(err, r'\bfoo\b')
        self.assertRegexpMatches(err, r'\bbar\b')
        self.assertRegexpMatches(err, r'\bbaz\b')
