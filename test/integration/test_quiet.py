from ..helpers import *


def test_single_quiet():
    ret, out, err = get_honcho_output(['-f', 'Procfile.quiet', 'start', '-qbaz'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1 *\| (....)?some normal output')
    assert_regexp_matches(out, r'foo\.1 *\| (....)?and then write to stderr')
    assert_regexp_matches(out, r'bar\.1 *\| (....)?some normal output')
    assert_regexp_matches(out, r'bar\.1 *\| (....)?and then write to stderr')
    assert_regexp_fails(out, r'baz\.1 \(quiet\) *\| (....)?some normal output')
    assert_regexp_fails(out, r'baz\.1 \(quiet\) *\| (....)?and then write to stderr')

    assert_regexp_matches(out, r'baz\.1 \(quiet\) *\| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'baz\.1 \(quiet\) *\| (....)?process terminated\n')

    assert_equal(err, '')

def test_multi_quiet():
    ret, out, err = get_honcho_output(['-f', 'Procfile.quiet', 'start', '-qbaz,bar'])

    assert_equal(ret, 0)

    assert_regexp_matches(out, r'foo\.1 *\| (....)?some normal output')
    assert_regexp_matches(out, r'foo\.1 *\| (....)?and then write to stderr')
    assert_regexp_fails(out, r'bar\.1 \(quiet\) *\| (....)?some normal output')
    assert_regexp_fails(out, r'bar\.1 \(quiet\) *\| (....)?and then write to stderr')
    assert_regexp_fails(out, r'baz\.1 \(quiet\) *\| (....)?some normal output')
    assert_regexp_fails(out, r'baz\.1  \(quiet\)*\| (....)?and then write to stderr')

    assert_regexp_matches(out, r'bar\.1 \(quiet\) *\| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'bar\.1 \(quiet\) *\| (....)?process terminated\n')
    assert_regexp_matches(out, r'baz\.1 \(quiet\) *\| (....)?started with pid \d+\n')
    assert_regexp_matches(out, r'baz\.1 \(quiet\) *\| (....)?process terminated\n')

    assert_equal(err, '')