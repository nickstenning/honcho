from honcho import colour

from ..helpers import *


def test_colours():
    assert_equal(colour.red, '31')
    assert_equal(colour.intense_red, '31;1')
    assert_equal(colour.cyan, '36')
    assert_equal(colour.intense_cyan, '36;1')


def test_get_colours():
    gen = colour.get_colours()

    expect = ['cyan', 'yellow', 'green', 'magenta', 'red', 'blue']
    expect = [getattr(colour, x) for x in expect]
    actual = [gen.next() for _ in xrange(6)]

    assert_equal(expect, actual)
