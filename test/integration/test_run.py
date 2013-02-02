from ..helpers import *


def test_run_quoting():
    ret, out, err = get_honcho_output(['run', 'python', '-c', 'print "hello world"'])

    assert_equal(ret, 0)
    assert_equal(out, 'hello world\n')


def test_run_subshell():
    ret, out, err = get_honcho_output(['run', 'echo', '$TEST_ANIMAL'])

    assert_equal(ret, 0)
    assert_equal(out, '$TEST_ANIMAL\n')


def test_run_env():
    ret, out, err = get_honcho_output(['run', 'sh', '-c', 'echo $TEST_ANIMAL'])

    assert_equal(ret, 0)
    assert_equal(out, 'giraffe\n')
