import re
from ..helpers import *


def test_simple():
    out = get_honcho_output(['start'])

    assert_regexp_matches(out, r'\d\d:\d\d:\d\d foo\.1  \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'\d\d:\d\d:\d\d foo\.1  \| (....)?process terminated\n')
    assert_regexp_matches(out, r'\d\d:\d\d:\d\d system \| (....)?sending SIGTERM to all processes\n')

    count = len(re.findall(r'\d\d:\d\d:\d\d foo\.1  \| (....)?one two three\n', out))
    assert_equal(count, 3)
