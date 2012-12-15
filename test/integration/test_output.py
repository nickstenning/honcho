from ..helpers import *


def test_honcho_start_joins_stderr_into_stdout():
    ret, out, err = get_honcho_output(['-f', 'Procfile.output', 'start'])

    assert_equal(ret, 0)

    assert_in('some normal output', out)
    assert_in('and then write to stderr', out)
    assert_equal(err, '')


def test_honcho_run_joins_stderr_into_stdout():
    ret, out, err = get_honcho_output(['run', 'python', 'output.py'])

    assert_equal(ret, 0)
    assert_equal(out, 'some normal output\nand then write to stderr\n')
    assert_equal(err, '')
