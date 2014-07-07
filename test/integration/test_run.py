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


def test_run_dereferences_process_from_procfile():
    ret, out, err = get_honcho_output(['-f', 'Procfile.simple', 'run', 'foo'])

    assert_equal(ret, 0)
    assert_equal(out, 'normal output\n')
    assert_equal(err, 'error output\n')


def test_run_works_with_a_one_word_command_and_no_procfile():
    ret, out, err = get_honcho_output(['run', 'python'])

    assert_equal(ret, 0)
    assert_equal(out, '')
    assert_equal(err, '')


def test_run_falls_back_to_shell_command():
    ret, out, err = get_honcho_output(['-f', 'Procfile.simple', 'run', 'python', 'simple.py'])

    assert_equal(ret, 0)
    assert_equal(out, 'normal output\n')
    assert_equal(err, 'error output\n')


def test_pdb_works_with_run_process():
    ret, out, err = get_honcho_output(['-f', 'Procfile.pdb', 'run', 'foo'], input='quit')

    assert_equal(ret, 1)
    assert out.startswith('normal output\n')
    assert '(Pdb)' in out
    assert 'BdbQuit' in err


def test_pdb_works_with_run_command_for_that_matter():
    ret, out, err = get_honcho_output(['run', 'python', 'with_pdb.py'], input='quit')

    assert_equal(ret, 1)
    assert out.startswith('normal output\n')
    assert '(Pdb)' in out
    assert 'BdbQuit' in err
