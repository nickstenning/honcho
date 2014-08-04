from __future__ import unicode_literals

import datetime
from ..helpers import TestCase

from honcho.printer import Printer, Message


def fake_message(data, **kwargs):
    defaults = {
        'type': 'line',
        'data': data,
        'time': datetime.datetime(2012, 8, 11, 12, 42),
        'name': None,
        'colour': None,
    }
    defaults.update(kwargs)
    return Message(**defaults)


class FakeOutput(object):

    def __init__(self):
        self.out = []

    def write(self, data):
        self.out.append(data)

    def string(self):
        return "".join(self.out)


class TestPrinter(TestCase):

    def test_write(self):
        out = FakeOutput()
        p = Printer(output=out)
        p.write(fake_message("monkeys\n"))
        self.assertEqual("12:42:00 | monkeys\n", out.string())

    def test_write_wrong_type(self):
        out = FakeOutput()
        p = Printer(output=out)
        self.assertRaises(RuntimeError, p.write, fake_message("monkeys\n", type="error"))

    def test_write_invalid_utf8(self):
        out = FakeOutput()
        p = Printer(output=out)
        p.write(fake_message(b"\xfe\xff\n"))
        self.assertEqual("12:42:00 | \ufffd\ufffd\n", out.string())

    def test_write_no_newline(self):
        out = FakeOutput()
        p = Printer(output=out)
        p.write(fake_message("monkeys"))
        self.assertEqual("12:42:00 | monkeys\n", out.string())

    def test_write_multiline(self):
        out = FakeOutput()
        p = Printer(output=out)
        p.write(fake_message("one\ntwo\nthree\n"))
        expect = "12:42:00 | one\n12:42:00 | two\n12:42:00 | three\n"
        self.assertEqual(expect, out.string())

    def test_write_with_name(self):
        out = FakeOutput()
        p = Printer(output=out)
        p.write(fake_message("quiescent\n", name="Robert Louis Stevenson"))
        self.assertEqual("12:42:00 Robert Louis Stevenson | quiescent\n",
                         out.string())

    def test_write_with_set_width(self):
        out = FakeOutput()
        p = Printer(output=out, width=6)
        p.write(fake_message("giraffe\n"))
        self.assertEqual("12:42:00        | giraffe\n", out.string())

    def test_write_with_name_and_set_width(self):
        out = FakeOutput()
        p = Printer(output=out, width=6)
        p.write(fake_message("narcissist\n", name="oop"))
        self.assertEqual("12:42:00 oop    | narcissist\n", out.string())

    def test_write_with_colour(self):
        out = FakeOutput()
        p = Printer(output=out)
        p.write(fake_message("conflate\n", name="foo", colour="31"))
        self.assertEqual("\033[31m12:42:00 foo | \033[0mconflate\n",
                         out.string())
