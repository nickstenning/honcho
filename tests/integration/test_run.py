import sys
import textwrap

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
    'test.py': script
}], indirect=True)
def test_run(testenv, runner):
    ret, out, err = testenv.run_honcho(['run', python_bin, 'test.py'], runner=runner)

    assert ret == 0
    assert out == 'elephant\n'
    assert 'error output\n' in err


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    '.env': 'ANIMAL=giraffe',
    'test.py': script,
}], indirect=True)
def test_run_env(testenv, runner):
    ret, out, err = testenv.run_honcho(['run', python_bin, 'test.py'], runner=runner)

    assert ret == 0
    assert out == 'giraffe\n'

@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    '.env.x': 'ANIMAL=giraffe',
    'test.py': script,
}], indirect=True)
def test_run_args_before_command(testenv, runner):
    # Regression test for #122 -- ensure that common args can be given
    # before the subcommand.
    ret, out, err = testenv.run_honcho(['-e', '.env.x', 'run', python_bin, 'test.py'], runner=runner)

    assert ret == 0
    assert out == 'giraffe\n'


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    'test.py': script
}], indirect=True)
def test_run_options_positionals_separator(testenv, runner):
    # Regression test for #159 -- ensure that honcho handles the '--'
    # options/positionals separator correctly.
    ret, out, err = testenv.run_honcho(['run', '--', python_bin, 'test.py'], runner=runner)

    assert ret == 0
    assert out == 'elephant\n'
