from ..helpers import TestCase
from ..helpers import get_honcho_output


class TestInvalid(TestCase):

    def test_invalid(self):
        ret, out, err = get_honcho_output(['-f', 'Procfile.invalid', 'start'])

        self.assertEqual(ret, 1)

        self.assertRegexpMatches(err, 'No processes defined in Procfile')
