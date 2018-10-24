import sys
import subprocess
import re

import pytest


@pytest.mark.skipif(sys.version_info < (2, 7), reason="check_output not available")
def test_runpy_invoke():
    """
    Ensure honcho can also be invoked using runpy (python -m)
    """
    cmd = [sys.executable, '-m', 'honcho', 'version']
    output = subprocess.check_output(cmd, universal_newlines=True)
    assert re.match(r'honcho \d\.\d\.\d.*\n', output)
