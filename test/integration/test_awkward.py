from ..helpers import *

def test_awkward():
    out = get_honcho_output(['-f', 'Procfile.awkward', 'start'])

    assert_regexp_matches(out, r'\d\d:\d\d:\d\d awkward\.1 \| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'\d\d:\d\d:\d\d awkward\.1 \| (....)?(Hello with no line break){10}\n')
    assert_regexp_matches(out, r'\d\d:\d\d:\d\d awkward\.1 \| (....)?process terminated\n')
