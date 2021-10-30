import pytest

from honcho import command


# All of the following groups of commands should parse to the same result
@pytest.mark.parametrize('commands', [
    # Regression test for #173
    [
        ['start', '-f', 'Procfile'],
        ['-f', 'Procfile', 'start'],
    ],
    # Regression tests for #223
    [
        ['start', '--no-prefix'],
        ['--no-prefix', 'start'],
    ],
    [
        ['start', '--no-colour'],
        ['--no-colour', 'start'],
    ],
    [
        ['start', '--no-prefix', '--no-colour'],
        ['--no-colour', 'start', '--no-prefix'],
        ['--no-prefix', 'start', '--no-colour'],
        ['--no-prefix','--no-colour', 'start'],
    ]
])
def test_command_equivalence(commands):
    if len(commands) < 2:
        pytest.fail("Must supply at least two commands")

    reference_args = commands.pop(0)
    reference_result = command.parser.parse_args(reference_args)

    for args in commands:
        result = command.parser.parse_args(args)
        assert result == reference_result
