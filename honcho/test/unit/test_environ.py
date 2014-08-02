import textwrap
from ..helpers import TestCase

from honcho import environ

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


class TestEnviron(TestCase):
    def test_environ_parse(self):
        for content, commands in FIXTURES:
            content = textwrap.dedent(content)
            result = environ.parse(content)
            self.assertEqual(result, commands)
