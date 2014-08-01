from ..helpers import TestCase

from honcho import colour, compat


class TestColour(TestCase):
    def test_colours(self):
        self.assertEqual(colour.red, '31')
        self.assertEqual(colour.intense_red, '31;1')
        self.assertEqual(colour.cyan, '36')
        self.assertEqual(colour.intense_cyan, '36;1')

    def test_get_colours(self):
        gen = colour.get_colours()

        expect = ['cyan', 'yellow', 'green', 'magenta', 'red', 'blue']
        expect = [getattr(colour, x) for x in expect]
        actual = [next(gen) for _ in compat.xrange(6)]

        self.assertEqual(expect, actual)
