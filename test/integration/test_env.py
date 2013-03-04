from ..helpers import *
import honcho


def test_env_start():
    procfile = 'Procfile.env' if honcho.ON_POSIX else 'Procfile.envwin'
    ret, out, err = get_honcho_output(['-f', procfile, 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'animals\.1 \| (....)?I like giraffes')


def test_env_run():
    if honcho.ON_POSIX:
        command  = ['run', 'sh', '-c', 'echo $TEST_ANIMAL'] 
    else:
        command = ['run', 'cmd', '/c', 'echo', '%TEST_ANIMAL%']
    ret, out, err = get_honcho_output(command)

    assert_equal(ret, 0)
    assert_equal(out.strip(), 'giraffe')
