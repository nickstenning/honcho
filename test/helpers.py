import os
import re
from honcho.procfile import Procfile
from subprocess import Popen, PIPE
from nose.tools import assert_equal, assert_true  # noqa
from mock import patch, MagicMock, call  # noqa

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')

try:
    from nose.tools import assert_regexp_matches
except ImportError:

    def assert_regexp_matches(text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regexp, str):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(text):
            msg = msg or "Regexp didn't match"
            msg = '%s: %r not found in %r' % (msg, expected_regexp.pattern, text)
            raise AssertionError(msg)


def assert_regexp_fails(text, failed_regexp, msg=None):
    """Fail the test if the text matches the regular expression."""
    if isinstance(failed_regexp, str):
        failed_regexp = re.compile(failed_regexp)
    if failed_regexp.search(text):
        msg = msg or "Regexp matched"
        msg = '%s: %r found in %r' % (msg, failed_regexp.pattern, text)
        raise AssertionError(msg)


def get_honcho_output(args, input=None):
    os.chdir(FIXTURE_ROOT)
    cmd = ['honcho']
    cmd.extend(args)

    # The below is mostly copy-pasted from subprocess.py's check_output (to
    # support python 2.6)

    process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = process.communicate(input)
    retcode = process.returncode

    return retcode, output, error


def get_procfile(name):
    with open(os.path.join(FIXTURE_ROOT, name)) as f:
        return Procfile(f.read())
