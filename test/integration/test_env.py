from ..helpers import *


def test_env_start():
    ret, out, err = get_honcho_output(['-f', 'Procfile.env', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'animals\.1 \| (....)?I like giraffes')


def test_env_run():
    ret, out, err = get_honcho_output(['run', 'echo', '$TEST_ANIMAL'])

    assert_equal(ret, 0)
    assert_equal(out, 'giraffe\n')
