import textwrap
import sys

import pytest

python_bin = sys.executable

script = textwrap.dedent("""
    from __future__ import print_function
    import os
    import sys
    print(os.environ.get("ANIMAL", "elephant"))
    print("error output", file=sys.stderr)
""")

all_honcho_runners = pytest.mark.parametrize('runner', ['entrypoint', 'package'])


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'test.py': script,
}], indirect=True)
def test_start(testenv, runner):
    ret, out, err = testenv.run_honcho(['start'], runner=runner)

    assert ret == 0
    assert 'elephant' in out
    assert 'error output' in out


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    '.env': 'ANIMAL=giraffe',
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'test.py': script,
}], indirect=True)
def test_start_env(testenv, runner):
    ret, out, err = testenv.run_honcho(['start'], runner=runner)

    assert 'giraffe' in out


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    '.env': 'PROCFILE=Procfile.dev',
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'Procfile.dev': 'bar: {0} test_dev.py'.format(python_bin),
    'test.py': script,
    'test_dev.py': textwrap.dedent("""
        from __future__ import print_function
        print("mongoose")
        """)
}], indirect=True)
def test_start_env_procfile(testenv, runner):
    ret, out, err = testenv.run_honcho(['start'], runner=runner)

    assert 'mongoose' in out


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'Procfile.dev': 'bar: {0} test_dev.py'.format(python_bin),
    'test.py': script,
    'test_dev.py': textwrap.dedent("""
        from __future__ import print_function
        print("mongoose")
        """)
}], indirect=True)
def test_start_procfile_after_command(testenv, runner):
    # Regression test for #173: Ensure that -f argument can be provided after
    # command
    ret, out, err = testenv.run_honcho(['start', '-f', 'Procfile.dev'], runner=runner)

    assert 'mongoose' in out


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'Procfile.dev': 'bar: {0} test_dev.py'.format(python_bin),
    'test.py': script,
    'test_dev.py': textwrap.dedent("""
        from __future__ import print_function
        print("mongoose")
        """)
}], indirect=True)
def test_start_procfile_before_command(testenv, runner):
    # Test case for #173: Ensure that -f argument can be provided before command
    ret, out, err = testenv.run_honcho(['-f', 'Procfile.dev', 'start'], runner=runner)

    assert 'mongoose' in out


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'test.py': 'import sys; sys.exit(42)',
}], indirect=True)
def test_start_returncode(testenv, runner):
    ret, out, err = testenv.run_honcho(['start'], runner=runner)

    assert ret == 42
