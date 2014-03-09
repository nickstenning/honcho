from ..helpers import get_honcho_output, assert_regexp_matches, assert_equal


def test_awkward():
    ret, out, err = get_honcho_output(['-f', 'Procfile.awkward', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'awkward\.1 \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'awkward\.1 \| (....)?(Hello with no line break){10}\n')
    assert_regexp_matches(out, r'awkward\.1 \| (....)?process terminated\n')
