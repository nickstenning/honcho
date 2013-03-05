import re
from ..helpers import *

import honcho

def test_simple():
    ret, out, err = get_honcho_output(['-f', 'Procfile.simple', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1  \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'foo\.1  \| (....)?process terminated\n')
    assert_regexp_matches(out, r'system \| (....)?sending SIGTERM to all processes\n')

    count = len(re.findall(r'foo\.1  \| (....)?one two three\n', out))
    assert_equal(count, 3)


def test_start_with_arg():
    ret, out, err = get_honcho_output(['-f', 'Procfile.simple', 'start', 'foo'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1  \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'foo\.1  \| (....)?process terminated\n')
    assert_regexp_matches(out, r'system \| (....)?sending SIGTERM to all processes\n')

    count = len(re.findall(r'foo\.1  \| (....)?one two three\n', out))
    assert_equal(count, 3)


def test_start_returncode():
    ret, out, err = get_honcho_output(['-f', 'Procfile.returncode', 'start'])

    assert_true(ret in [123, 42])


def test_start_with_arg_returncode():
    ret, out, err = get_honcho_output(['-f', 'Procfile.returncode', 'start', 'bar'])

    assert_equal(ret, 42)


def test_run_captures_all_arguments():
    if not honcho.ON_POSIX:
        return
    command = ['run', 'env', '-i', 'A=B']
    ret, out, err = get_honcho_output(command)
    assert_equal(ret, 0)
    assert_equal(out.strip(), "A=B")


def test_run_captures_all_arguments_windows():
    # note: this is not the same exact test as on Posix 
    # but this captures the gist of the intention
    if not honcho.ON_WINDOWS:
        return
    command = ['run', 'cmd', '/a', '/e:on', '/c', 'cd', '&', 'set']
    ret, out, err = get_honcho_output(command)
    assert_equal(ret, 0)
    assert_true("honcho" in out)
    assert_true("HOMEDRIVE" in out)
