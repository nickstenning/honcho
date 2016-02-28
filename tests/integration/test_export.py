import os

import pytest


@pytest.mark.parametrize('testenv', [{
    'Procfile': "web: python web.py"
}], indirect=True)
def test_export_supervisord(testenv):
    ret, out, err = testenv.run_honcho([
        'export',
        'supervisord',
        testenv.path('giraffe'),
        '-a', 'neck',
    ])

    expected = testenv.path('giraffe', 'neck.conf')

    assert ret == 0
    assert os.path.exists(expected)


@pytest.mark.parametrize('testenv', [{
    'Procfile': "web: python web.py"
}], indirect=True)
def test_export_upstart(testenv):
    ret, out, err = testenv.run_honcho([
        'export',
        'upstart',
        testenv.path('elephant'),
        '-a', 'trunk',
    ])

    assert ret == 0
    for filename in ('trunk.conf',
                     'trunk-web.conf',
                     'trunk-web-1.conf'):
        expected = testenv.path('elephant', filename)
        assert os.path.exists(expected)
