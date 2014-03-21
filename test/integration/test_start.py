import re
from ..helpers import (get_honcho_output, assert_equal, assert_regexp_matches,
                       assert_true, assert_regexp_fails)

from honcho import compat


def test_start_simple():
    ret, out, err = get_honcho_output(['-f', 'Procfile.simple', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1  \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'foo\.1  \| (....)?process terminated\n')
    assert_regexp_matches(out, r'system \| (....)?sending SIGTERM to all processes\n')

    count = len(re.findall(r'foo\.1  \| (....)?(normal|error) output\n', out))
    assert_equal(count, 2)


def test_start_with_arg():
    ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', 'foo'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1  \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'foo\.1  \| (....)?process terminated\n')
    assert_regexp_matches(out, r'system \| (....)?sending SIGTERM to all processes\n')

    count = len(re.findall(r'foo\.1  \| (....)?(normal|error) output\n', out))
    assert_equal(count, 2)


def test_start_with_multiple_args():
    ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', 'foo', 'bar'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1  \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'foo\.1  \| (....)?process terminated\n')
    assert_regexp_matches(out, r'bar\.1  \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'foo\.1  \| (....)?process terminated\n')
    assert_regexp_matches(out, r'system \| (....)?sending SIGTERM to all processes\n')

    count = len(re.findall(r'foo\.1  \| (....)?(normal|error) output\n', out))
    assert_equal(count, 2)
    count = len(re.findall(r'bar\.1  \| (....)?(normal|error) output\n', out))
    assert_equal(count, 2)
    count = len(re.findall(r'baz\.1  \| (....)?(normal|error) output\n', out))
    assert_equal(count, 0)


def test_start_returncode():
    procfile = 'Procfile.returncodewin' if compat.ON_WINDOWS else 'Procfile.returncode'
    ret, out, err = get_honcho_output(['-f', procfile, 'start'])

    assert_true(ret in [123, 42])


def test_start_with_arg_returncode():
    procfile = 'Procfile.returncodewin' if compat.ON_WINDOWS else 'Procfile.returncode'
    ret, out, err = get_honcho_output(['-f', procfile, 'start', 'bar'])

    assert_equal(ret, 42)


def test_start_joins_stderr_into_stdout():
    ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'normal output')
    assert_regexp_matches(out, r'error output')
    assert_equal(err, '')


def test_start_quiet_simple():
    ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', '-qbaz'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1 *\| (....)?normal output')
    assert_regexp_matches(out, r'foo\.1 *\| (....)?error output')
    assert_regexp_matches(out, r'bar\.1 *\| (....)?normal output')
    assert_regexp_matches(out, r'bar\.1 *\| (....)?error output')
    assert_regexp_fails(out, r'baz\.1 \(quiet\) *\| (....)?normal output')
    assert_regexp_fails(out, r'baz\.1 \(quiet\) *\| (....)?error output')

    assert_regexp_matches(out, r'baz\.1 \(quiet\) *\| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'baz\.1 \(quiet\) *\| (....)?process terminated\n')

    assert_equal(err, '')


def test_start_quiet_multi():
    ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start', '-qbaz,bar'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1 *\| (....)?normal output')
    assert_regexp_matches(out, r'foo\.1 *\| (....)?error output')
    assert_regexp_fails(out, r'bar\.1 \(quiet\) *\| (....)?normal output')
    assert_regexp_fails(out, r'bar\.1 \(quiet\) *\| (....)?error output')
    assert_regexp_fails(out, r'baz\.1 \(quiet\) *\| (....)?normal output')
    assert_regexp_fails(out, r'baz\.1  \(quiet\)*\| (....)?error output')

    assert_regexp_matches(out, r'bar\.1 \(quiet\) *\| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'bar\.1 \(quiet\) *\| (....)?process terminated\n')
    assert_regexp_matches(out, r'baz\.1 \(quiet\) *\| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'baz\.1 \(quiet\) *\| (....)?process terminated\n')

    assert_equal(err, '')

def test_check_race_condition():
    '''
    check for proper output at least 10 times
    '''
    for i in range(10):
        ret, out, err = get_honcho_output(['-f', 'Procfile.default', 'start'])

        assert_equal(ret, 0)

        err_msg = "Regexp didn't match on iteration #{0}".format(i)

        assert_regexp_matches(out, r'foo\.1 *\| (....)?normal output', err_msg)
        assert_regexp_matches(out, r'foo\.1 *\| (....)?error output', err_msg)
        assert_regexp_matches(out, r'bar\.1 *\| (....)?normal output', err_msg)
        assert_regexp_matches(out, r'bar\.1 *\| (....)?error output', err_msg)
        assert_regexp_matches(out, r'baz\.1 *\| (....)?normal output', err_msg)
        assert_regexp_matches(out, r'baz\.1 *\| (....)?error output', err_msg)

        assert_regexp_matches(out, r'foo\.1 *\| (....)?started with pid \d+\n', err_msg)
        assert_regexp_matches(out, r'foo\.1 *\| (....)?process terminated\n', err_msg)
        assert_regexp_matches(out, r'bar\.1 *\| (....)?started with pid \d+\n', err_msg)
        assert_regexp_matches(out, r'bar\.1 *\| (....)?process terminated\n', err_msg)
        assert_regexp_matches(out, r'baz\.1 *\| (....)?started with pid \d+\n', err_msg)
        assert_regexp_matches(out, r'baz\.1 *\| (....)?process terminated\n', err_msg)
