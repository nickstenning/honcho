from ..helpers import *


def test_proctype_increment():
    ret, out, err = get_honcho_output(['-f', 'Procfile.ports', 'start'])

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
