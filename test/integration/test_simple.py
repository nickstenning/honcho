import re
from ..helpers import *


def test_simple():
    ret, out, err = get_honcho_output(['-f', 'Procfile.simple', 'start'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1  \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'foo\.1  \| (....)?process terminated\n')
    assert_regexp_matches(out, r'system \| (....)?sending SIGTERM to all processes\n')

    count = len(re.findall(r'foo\.1  \| (....)?one two three\n', out))
    assert_equal(count, 3)
