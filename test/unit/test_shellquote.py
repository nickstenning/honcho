from ..helpers import *


def test_shell_quoting():
    from honcho.command import shellquote
    data = [
        ('', "''"),
        ('-', '-'),
        ('asdf', 'asdf'),
        ('as df', 'as\\ df'),
        ('as\ndf', 'as\\ndf'),
    ]

    for in_value, out_value in data:
        assert_equal(shellquote(in_value), out_value)
