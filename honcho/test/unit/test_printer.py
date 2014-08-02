import datetime
from ..helpers import TestCase

from honcho.printer import Printer


class FakeOutput(object):

    def __init__(self):
        self.out = []

    def write(self, data):
        self.out.append(data)

    def string(self):
        return "".join(self.out)


class FakeEnv(object):
    def now(self):
        return datetime.datetime(2012, 8, 11, 12, 42)


class TestPrinter(TestCase):

    def test_write(self):
        out = FakeOutput()
        p = Printer(output=out, env=FakeEnv())
        p.write("monkeys\n")
        self.assertEqual("12:42:00 | monkeys\n", out.string())

    def test_write_no_newline(self):
        out = FakeOutput()
        p = Printer(output=out, env=FakeEnv())
        p.write("monkeys")
        self.assertEqual("12:42:00 | monkeys\n", out.string())

    def test_write_multiline(self):
        out = FakeOutput()
        p = Printer(output=out, env=FakeEnv())
        p.write("one\ntwo\nthree\n")

        expect = "12:42:00 | one\n12:42:00 | two\n12:42:00 | three\n"
        self.assertEqual(expect, out.string())

    def test_write_with_name(self):
        out = FakeOutput()
        p = Printer(output=out, env=FakeEnv())
        p.write("quiescent\n", name="Robert Louis Stevenson")
        self.assertEqual("12:42:00 Robert Louis Stevenson | quiescent\n",
                         out.string())

    def test_write_with_set_width(self):
        out = FakeOutput()
        p = Printer(output=out, width=6, env=FakeEnv())
        p.write("giraffe\n")
        self.assertEqual("12:42:00        | giraffe\n", out.string())

    def test_write_with_name_and_set_width(self):
        out = FakeOutput()
        p = Printer(output=out, width=6, env=FakeEnv())
        p.write("narcissist\n", name="oop")
        self.assertEqual("12:42:00 oop    | narcissist\n", out.string())

    def test_write_with_colour(self):
        out = FakeOutput()
        p = Printer(output=out, env=FakeEnv())
        p.write("conflate\n", name="foo", colour="31")
        self.assertEqual("\033[31m12:42:00 foo | \033[0mconflate\n",
                         out.string())
