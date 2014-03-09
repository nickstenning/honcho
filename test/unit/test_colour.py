from honcho import colour, compat

from ..helpers import assert_equal


def test_colours():
    assert_equal(colour.red, '31')
    assert_equal(colour.intense_red, '31;1')
    assert_equal(colour.cyan, '36')
    assert_equal(colour.intense_cyan, '36;1')


def test_get_colours():
    gen = colour.get_colours()

    expect = ['cyan', 'yellow', 'green', 'magenta', 'red', 'blue']
    expect = [getattr(colour, x) for x in expect]
    actual = [next(gen) for _ in compat.xrange(6)]

    assert_equal(expect, actual)
