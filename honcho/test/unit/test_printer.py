import datetime
from ..helpers import TestCase

from honcho.printer import Printer


class FakeOutput(object):

    def __init__(self):
        self.out = []

    def write(self, data):
        self.out.append(data)

    def last_write(self):
        return self.out[-1]


class FakeEnv(object):
    def now(self):
        return datetime.datetime(2012, 8, 11, 12, 42)


class TestPrinter(TestCase):

    def test_defaults_simple(self):
        out = FakeOutput()
        p = Printer(output=out, env=FakeEnv())
        p.write("monkeys")
        self.assertEqual("12:42:00 unknown | monkeys", out.last_write())

    def test_defaults_multiline(self):
        out = FakeOutput()
        p = Printer(output=out, env=FakeEnv())
        p.write("one\ntwo\nthree")

        expect = "12:42:00 unknown | one\n12:42:00 unknown | two\n12:42:00 unknown | three"
        self.assertEqual(expect, out.last_write())

    def test_name_simple(self):
        out = FakeOutput()
        p = Printer(output=out, name="Robert Louis Stevenson", env=FakeEnv())
        p.write("quiescent")
        self.assertEqual("12:42:00 Robert Louis Stevenson | quiescent",
                         out.last_write())

    def test_length_simple(self):
        out = FakeOutput()
        p = Printer(output=out, name="oop", width=6, env=FakeEnv())
        p.write("narcissist")
        self.assertEqual("12:42:00 oop    | narcissist", out.last_write())

    def test_colour_simple(self):
        out = FakeOutput()
        p = Printer(output=out, name="red", colour="31", env=FakeEnv())
        p.write("conflate")
        self.assertEqual("\033[31m12:42:00 red | \033[0mconflate",
                         out.last_write())
