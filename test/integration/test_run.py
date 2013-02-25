from ..helpers import *


def test_run_quoting():
    ret, out, err = get_honcho_output(['run', 'python', '-c',
                                       'print "hello world"'])

    assert_equal(ret, 0)
    assert_equal(out, 'hello world\n')
