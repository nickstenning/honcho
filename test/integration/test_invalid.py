from ..helpers import get_honcho_output, assert_equal, assert_regexp_matches


def test_invalid():
    ret, out, err = get_honcho_output(['-f', 'Procfile.invalid', 'start'])

    assert_equal(ret, 1)

    assert_regexp_matches(err, 'No processes defined in Procfile')
