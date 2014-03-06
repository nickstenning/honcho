from ..helpers import get_honcho_output, assert_equal, assert_regexp_matches


def test_multi_check():
    ret, out, err = get_honcho_output(['-f', 'Procfile.multi', 'check'])

    assert_equal(ret, 0)

    assert_regexp_matches(err, 'Valid procfile detected')
    assert_regexp_matches(err, r'\bfoo\b')
    assert_regexp_matches(err, r'\bbar\b')
    assert_regexp_matches(err, r'\bbaz\b')
