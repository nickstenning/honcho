from ..helpers import *
from honcho.process import ON_POSIX


def test_env_start():
    procfile = 'Procfile.env' if ON_POSIX else 'Procfile.envwin'
    ret, out, err = get_honcho_output(['-f', procfile, 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'animals\.1 \| (....)?I like giraffes')


def test_env_run():
    command  = ['run', 'sh', '-c', 'echo $TEST_ANIMAL'] if ON_POSIX else ['run', 'echo', '%TEST_ANIMAL%']
    ret, out, err = get_honcho_output(command)

    assert_equal(ret, 0)
    assert_equal(out.strip(), 'giraffe')
