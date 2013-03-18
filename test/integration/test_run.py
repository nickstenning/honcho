import sys
from ..helpers import *


def test_run_quoting():
    # 'python' is not always in the path on all test os
    # in particular on Windows, this is not the case    
    python = sys.executable
    ret, out, err = get_honcho_output(['run', python, '-c', 
                                       'print "hello world"' ])

    assert_equal(ret, 0)
    assert_equal(out, 'hello world\n')
