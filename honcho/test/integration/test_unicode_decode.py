from ..helpers import TestCase
from ..helpers import get_honcho_output


class TestUnicodeDecode(TestCase):

    def test_unicode_decode_error(self):
        ret, out, err = get_honcho_output(['-f',
                                           'Procfile.unicode_decode', 'start'])
        self.assertEqual(ret, 0)
        self.assertRegexpMatches(out, "normal output")
