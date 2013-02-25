from ..helpers import *
import os
from honcho.process import ON_POSIX


def test_proctype_increment():
    procfile = 'Procfile.ports' if ON_POSIX else 'Procfile.portswin'
    ret, out, err = get_honcho_output(['-f', procfile, 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'web\.1    \| (....)?PORT=5000')
    assert_regexp_matches(out, r'worker\.1 \| (....)?PORT=5100')
    assert_regexp_matches(out, r'redis\.1  \| (....)?PORT=5200')
    assert_regexp_matches(out, r'es\.1     \| (....)?PORT=5300')


def test_concurrency_increment():
    ret, out, err = get_honcho_output(['-f', 'Procfile.ports', 'start', '-c', 'web=2,worker=3'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'web\.1    \| (....)?PORT=5000')
    assert_regexp_matches(out, r'web\.2    \| (....)?PORT=5001')
    assert_regexp_matches(out, r'worker\.1 \| (....)?PORT=5100')
    assert_regexp_matches(out, r'worker\.2 \| (....)?PORT=5101')
    assert_regexp_matches(out, r'worker\.3 \| (....)?PORT=5102')
    assert_regexp_matches(out, r'redis\.1  \| (....)?PORT=5200')
    assert_regexp_matches(out, r'es\.1     \| (....)?PORT=5300')


def test_get_port_from_dot_env():

    ret, out, err = get_honcho_output(['-f', 'Procfile.ports', '-e', '.env_port', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'web\.1    \| (....)?PORT=8000')


def test_get_port_from_env():
    os.environ['PORT'] = '3000'

    ret, out, err = get_honcho_output(['-f', 'Procfile.ports', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'web\.1    \| (....)?PORT=3000')
