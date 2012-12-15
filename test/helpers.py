import os
import re
from subprocess import Popen, PIPE
from nose.tools import *
from mock import *

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


if not 'assert_regexp_matches' in globals():

    def assert_regexp_matches(text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(text):
            msg = msg or "Regexp didn't match"
            msg = '%s: %r not found in %r' % (msg, expected_regexp.pattern, text)
            raise AssertionError(msg)

if not 'assert_regexp_notmatches' in globals():

    def assert_regexp_notmatches(text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if expected_regexp.search(text):
            msg = msg or "Regexp did match"
            msg = '%s: %r found in %r' % (msg, expected_regexp.pattern, text)
            raise AssertionError(msg)


def get_honcho_output(args):
    os.chdir(FIXTURE_ROOT)
    cmd = ['honcho']
    cmd.extend(args)

    # The below is mostly copy-pasted from subprocess.py's check_output (to
    # support python 2.6)

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    output, error = process.communicate()
    retcode = process.poll()

    return retcode, output, error
