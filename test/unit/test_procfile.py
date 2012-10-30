import textwrap

from honcho.procfile import Procfile
from ..helpers import *

FIXTURES = [
    [
        # Simple
        """
        web: command
        """,
        {'web': 'command'}
    ],
    [
        # Simple 2
        """
        foo: python foo.py
        bar: python bar.py
        """,
        {'foo': 'python foo.py', 'bar': 'python bar.py'}
    ],
    [
        # No newline at EOF
        """
        web: command""",
        {'web': 'command'}
    ],
    [
        # Comments
        """
        #commented: command
        """,
        {}
    ],
    [
        # Invalid characters
        """
        -foo: command
        """,
        {}
    ],
    [
        # Shell metacharacters
        """
        web: sh -c "echo $FOOBAR" >/dev/null 2>&1
        """,
        {'web': 'sh -c "echo $FOOBAR" >/dev/null 2>&1'}
    ],
]


def test_procfiles():
    for content, commands in FIXTURES:
        content = textwrap.dedent(content)
        procfile = Procfile(content)
        assert_equal(procfile.commands, commands)


def test_procfile_ordered():
    content = textwrap.dedent("""
    one: onecommand
    two: twocommand
    three: twocommand
    four: fourcommand
    """)

    procfile = Procfile(content)

    order = [k for k in procfile.commands]
    assert_equal(['one', 'two', 'three', 'four'], order)
