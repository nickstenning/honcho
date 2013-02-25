from ..helpers import *


def test_honcho_start_joins_stderr_into_stdout():
    ret, out, err = get_honcho_output(['-f', 'Procfile.output', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'some normal output')
    assert_regexp_matches(out, r'and then write to stderr')
    assert_equal(err, '')


def test_honcho_run_keeps_stderr_and_stdout_separate():
    ret, out, err = get_honcho_output(['run', 'python', 'output.py'])

    assert_equal(ret, 0)
    assert_equal(out.strip(), 'some normal output')
    assert_equal(err.strip(), 'and then write to stderr')
