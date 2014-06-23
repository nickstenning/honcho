import textwrap

from honcho import environ
from ..helpers import assert_equal

FIXTURES = [
    [
        """
        FOO=bar
        """,
        {'FOO': 'bar'}
    ],
    [
        """
        FOO=bar
        BAZ=qux
        """,
        {'FOO': 'bar', 'BAZ': 'qux'}
    ],
    [
        # No newline at EOF
        """
        FOO=bar""",
        {'FOO': 'bar'}
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
        -foo=command
        """,
        {}
    ],
    [
        # Single quoted
        """
        MYVAR='hello"world'
        """,
        {'MYVAR': 'hello"world'}
    ],
    [
        # Double quoted
        """
        MYVAR="hello'world"
        """,
        {'MYVAR': "hello'world"}
    ],
]


def test_environ_parse():
    for content, commands in FIXTURES:
        content = textwrap.dedent(content)
        result = environ.parse(content)
        yield assert_equal, result, commands
