import sys
import textwrap

import pytest

python_bin = sys.executable

script = textwrap.dedent("""
    import os
    import sys
    print(os.environ.get("ANIMAL", "elephant"))
    print("error output", file=sys.stderr)
""")


@pytest.mark.parametrize('testenv', [{
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'test.py': script,
}], indirect=True)
def test_start(testenv):
    ret, out, err = testenv.run_honcho(['start'])

    assert ret == 0
    assert 'elephant' in out
    assert 'error output' in out


@pytest.mark.parametrize('testenv', [{
    '.env': 'ANIMAL=giraffe',
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'test.py': script,
}], indirect=True)
def test_start_env(testenv):
    ret, out, err = testenv.run_honcho(['start'])

    assert 'giraffe' in out


@pytest.mark.parametrize('testenv', [{
    '.env': 'PROCFILE=Procfile.dev',
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'Procfile.dev': 'bar: {0} test_dev.py'.format(python_bin),
    'test.py': script,
    'test_dev.py': textwrap.dedent("""
        print("mongoose")
        """)
}], indirect=True)
def test_start_env_procfile(testenv):
    ret, out, err = testenv.run_honcho(['start'])

    assert 'mongoose' in out


@pytest.mark.parametrize('testenv', [{
    'Procfile': 'foo: {0} test.py'.format(python_bin),
    'test.py': 'import sys; sys.exit(42)',
}], indirect=True)
def test_start_returncode(testenv):
    ret, out, err = testenv.run_honcho(['start'])

    assert ret == 42


draining = textwrap.dedent("""
    import signal
    import sys
    import time

    def drain(signum, frame):
        time.sleep(1)
        print("drained", flush=True)
        sys.exit(0)

    signal.signal(signal.SIGTERM, drain)
    print("ready", flush=True)
    time.sleep(30)
""")


@pytest.mark.skipif(sys.platform == 'win32', reason='relies on POSIX signals')
@pytest.mark.parametrize('testenv', [{
    'Procfile': '\n'.join([
        'quick: {0} -c "import time; time.sleep(1)"'.format(python_bin),
        'slow: {0} draining.py'.format(python_bin),
    ]),
    'draining.py': draining,
}], indirect=True)
@pytest.mark.parametrize(('args', 'drained'), [
    (['start'], True),
    (['start', '--timeout', '0'], False),
])
def test_start_timeout(testenv, args, drained):
    _, out, _ = testenv.run_honcho(args)

    assert 'ready' in out
    assert ('drained' in out) == drained
