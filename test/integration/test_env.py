from ..helpers import *


def test_env_start():
    ret, out, err = get_honcho_output(['-f', 'Procfile.env', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'animals\.1 \| (....)?I like giraffes')
