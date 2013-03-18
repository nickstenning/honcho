from ..helpers import *
from honcho import compat


def test_env_start():
    procfile = 'Procfile.envwin' if compat.ON_WINDOWS else 'Procfile.env'
    ret, out, err = get_honcho_output(['-f', procfile, 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'animals\.1 \| (....)?I like giraffes')


def test_env_run():
    if compat.ON_WINDOWS:
        command = ['run', 'cmd', '/c', 'echo', '%TEST_ANIMAL%']
    else:
        command  = ['run', 'sh', '-c', 'echo $TEST_ANIMAL'] 
    ret, out, err = get_honcho_output(command)

    assert_equal(ret, 0)
    assert_equal(out, 'giraffe\n')
