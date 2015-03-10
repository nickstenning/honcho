# coding=utf-8

import textwrap
from ..helpers import TestCase

from honcho import environ
from honcho import compat

ENVFILE_FIXTURES = [
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
    [
        # Quotation mark surrounded
        r"""
        MYVAR='"surrounded"'
        """,
        {'MYVAR': '"surrounded"'}
    ],
    [
        # Escaped quotation mark surrounded
        r"""
        MYVAR=\"escaped\"
        """,
        {'MYVAR': '"escaped"'}
    ],
    [
        # At-sign in value
        r"""
        MYVAR=user@domain.com
        """,
        {'MYVAR': 'user@domain.com'}
    ],
    [
        # Much punctuation in value
        r"""
        MYVAR=~pun|u@|0n$=
        """,
        {'MYVAR': '~pun|u@|0n$='}
    ],
    [
        # Unicode values
        r"""
        MYVAR=⋃ñᴉ—☪ó∂ǝ
        """,
        {'MYVAR': '⋃ñᴉ—☪ó∂ǝ'}
    ],
    [
        # Unicode keys
        r"""
        ṀẎṾẠṚ=value
        """,
        {}
    ],
    [
        # Quoted space in value
        r"""
        MYVAR='sp ace'
        """,
        {'MYVAR': 'sp ace'}
    ],
    [
        # Escaped characters in value
        r"""
        TABS='foo\tbar'
        NEWLINES='foo\nbar'
        VTAB='foo\vbar'
        DOLLAR='foo\$bar'
        """,
        {'TABS': 'foo\tbar',
         'NEWLINES': 'foo\nbar',
         'VTAB': 'foo\vbar',
         'DOLLAR': 'foo\\$bar'}
    ],
]

PROCFILE_FIXTURES = [
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


class TestEnviron(TestCase):
    def test_environ_parse(self):
        for content, commands in ENVFILE_FIXTURES:
            content = textwrap.dedent(content)
            result = environ.parse(content)
            self.assertEqual(result, commands)


class TestProcfileParse(TestCase):

    def test_parse_procfiles(self):
        for content, processes in PROCFILE_FIXTURES:
            content = textwrap.dedent(content)
            p = environ.parse_procfile(content)
            self.assertEqual(p.processes, processes)

    def test_procfile_ordered(self):
        content = textwrap.dedent("""
        one: onecommand
        two: twocommand
        three: twocommand
        four: fourcommand
        """)

        p = environ.parse_procfile(content)
        order = [k for k in p.processes]
        self.assertEqual(['one', 'two', 'three', 'four'], order)


class TestProcfile(TestCase):

    def test_init(self):
        p = environ.Procfile()
        self.assertEqual(0, len(p.processes))

    def test_add_process(self):
        p = environ.Procfile()
        p.add_process('foo', 'echo 123')
        self.assertEqual('echo 123', p.processes['foo'])

    def test_add_process_ensures_unique_name(self):
        p = environ.Procfile()
        p.add_process('foo', 'echo 123')
        self.assertRaises(AssertionError, p.add_process, 'foo', 'echo 123')


def ep(*args, **kwargs):
    return environ.expand_processes(compat.OrderedDict(args), **kwargs)


class TestExpandProcesses(TestCase):

    def test_name(self):
        p = ep(("foo", "some command"))
        self.assertEqual(1, len(p))
        self.assertEqual("foo.1", p[0].name)

    def test_name_multiple(self):
        p = ep(("foo", "some command"), ("bar", "another command"))
        self.assertEqual(2, len(p))
        self.assertEqual("foo.1", p[0].name)
        self.assertEqual("bar.1", p[1].name)

    def test_name_concurrency(self):
        p = ep(("foo", "some command"), concurrency={"foo": 3})
        self.assertEqual(3, len(p))
        self.assertEqual("foo.1", p[0].name)
        self.assertEqual("foo.2", p[1].name)
        self.assertEqual("foo.3", p[2].name)

    def test_name_concurrency_multiple(self):
        p = ep(("foo", "some command"), ("bar", "another command"),
               concurrency={"foo": 3, "bar": 2})
        self.assertEqual(5, len(p))
        self.assertEqual("foo.1", p[0].name)
        self.assertEqual("foo.2", p[1].name)
        self.assertEqual("foo.3", p[2].name)
        self.assertEqual("bar.1", p[3].name)
        self.assertEqual("bar.2", p[4].name)

    def test_command(self):
        p = ep(("foo", "some command"))
        self.assertEqual("some command", p[0].cmd)

    def test_port_not_defaulted(self):
        p = ep(("foo", "some command"))
        self.assertEqual({}, p[0].env)

    def test_port(self):
        p = ep(("foo", "some command"), port=8000)
        self.assertEqual({"PORT": "8000"}, p[0].env)

    def test_port_multiple(self):
        p = ep(("foo", "some command"),
               ("bar", "another command"),
               port=8000)
        self.assertEqual({"PORT": "8000"}, p[0].env)
        self.assertEqual({"PORT": "8100"}, p[1].env)

    def test_port_from_env(self):
        p = ep(("foo", "some command"),
               ("bar", "another command"),
               env={"PORT": 8000})
        self.assertEqual({"PORT": "8000"}, p[0].env)
        self.assertEqual({"PORT": "8100"}, p[1].env)

    def test_port_from_env_coerced_to_number(self):
        p = ep(("foo", "some command"), env={"PORT": "5000"})
        self.assertEqual({"PORT": "5000"}, p[0].env)

    def test_port_from_env_overrides(self):
        p = ep(("foo", "some command"), env={"PORT": 5000}, port=8000)
        self.assertEqual({"PORT": "5000"}, p[0].env)

    def test_port_concurrency(self):
        p = ep(("foo", "some command"),
               ("bar", "another command"),
               concurrency={"foo": 3, "bar": 2},
               port=4000)
        self.assertEqual({"PORT": "4000"}, p[0].env)
        self.assertEqual({"PORT": "4001"}, p[1].env)
        self.assertEqual({"PORT": "4002"}, p[2].env)
        self.assertEqual({"PORT": "4100"}, p[3].env)
        self.assertEqual({"PORT": "4101"}, p[4].env)

    def test_quiet(self):
        p = ep(("foo", "some command"), quiet=["foo", "bar"])
        self.assertEqual(True, p[0].quiet)

    def test_quiet_multiple(self):
        p = ep(("foo", "some command"),
               ("bar", "another command"),
               quiet=["foo"])
        self.assertEqual(True, p[0].quiet)
        self.assertEqual(False, p[1].quiet)

    def test_env(self):
        p = ep(("foo", "some command"),
               env={"ANIMAL": "giraffe", "DEBUG": "false"})
        self.assertEqual("giraffe", p[0].env["ANIMAL"])
        self.assertEqual("false", p[0].env["DEBUG"])

    def test_env_multiple(self):
        p = ep(("foo", "some command"),
               ("bar", "another command"),
               env={"ANIMAL": "giraffe", "DEBUG": "false"})
        self.assertEqual("giraffe", p[0].env["ANIMAL"])
        self.assertEqual("false", p[0].env["DEBUG"])
        self.assertEqual("giraffe", p[1].env["ANIMAL"])
        self.assertEqual("false", p[1].env["DEBUG"])
