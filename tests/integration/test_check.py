import textwrap

import pytest

all_honcho_runners = pytest.mark.parametrize('runner', ['entrypoint', 'package'])


@all_honcho_runners
@pytest.mark.parametrize('testenv', [{
    'Procfile': textwrap.dedent("""
        foo: python web.py
        bar: ruby worker.rb
        baz: node socket.js
    """)
}], indirect=True)
def test_check(testenv, runner):
    ret, out, err = testenv.run_honcho(['check'], runner=runner)

    assert ret == 0
    assert 'Valid procfile detected' in err
    assert 'foo, bar, baz' in err
