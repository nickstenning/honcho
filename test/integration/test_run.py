import sys
from ..helpers import get_honcho_output, assert_equal, assert_true

from honcho import compat


def test_run_quoting():
    # 'python' is not always in the path on all test os
    # in particular on Windows, this is not the case
    python = sys.executable
    ret, out, err = get_honcho_output(['run', python, '-c',
                                       'print("hello world")'])

    assert_equal(ret, 0)
    assert_equal(out, 'hello world\n')


def test_run_captures_all_arguments():
    if compat.ON_WINDOWS:
        return
    command = ['run', 'env', '-i', 'A=B']
    ret, out, err = get_honcho_output(command)
    assert_equal(ret, 0)
    assert_equal(out.strip(), "A=B")


def test_run_captures_all_arguments_windows():
    # note: this is not the same exact test as on Posix
    # but this captures the gist of the intention
    if not compat.ON_WINDOWS:
        return
    command = ['run', 'cmd', '/a', '/e:on', '/c', 'cd', '&', 'set']
    ret, out, err = get_honcho_output(command)
    assert_equal(ret, 0)
    assert_true("honcho" in out)
    assert_true("HOMEDRIVE" in out)


def test_run_keeps_stderr_and_stdout_separate():
    ret, out, err = get_honcho_output(['run', 'python', 'simple.py'])

    assert_equal(ret, 0)
    assert_equal(out, 'normal output\n')
    assert_equal(err, 'error output\n')
