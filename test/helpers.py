import os
import subprocess
from nose.tools import *
from mock import *

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')

def get_honcho_output(args):
    os.chdir(FIXTURE_ROOT)
    cmd = ['honcho']
    cmd.extend(args)
    return subprocess.check_output(cmd)
