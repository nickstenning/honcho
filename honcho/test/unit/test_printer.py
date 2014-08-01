import datetime
from ..helpers import TestCase
from mock import MagicMock, patch

from honcho.printer import Printer


class TestPrinter(TestCase):
    def setUp(self):  # noqa
        self.out = MagicMock()

        self._dt_patch = patch('honcho.printer.datetime')
        self._dt = self._dt_patch.start()
        self._dt.now.return_value = datetime.datetime(2012, 8, 11, 12, 42)

    def tearDown(self):  # noqa
        self._dt_patch.stop()

    def test_defaults_simple(self):
        self.p = Printer(output=self.out)
        self.p.write("monkeys")
        self.out.write.assert_called_once_with("12:42:00 unknown | monkeys")

    def test_defaults_multiline(self):
        self.p = Printer(output=self.out)
        self.p.write("one\ntwo\nthree")

        expect = "12:42:00 unknown | one\n12:42:00 unknown | two\n12:42:00 unknown | three"
        self.out.write.assert_called_once_with(expect)

    def test_name_simple(self):
        self.p = Printer(output=self.out, name="Robert Louis Stevenson")
        self.p.write("quiescent")
        self.out.write.assert_called_once_with("12:42:00 Robert Louis Stevenson | quiescent")

    def test_length_simple(self):
        self.p = Printer(output=self.out, name="oop", width=6)
        self.p.write("narcissist")
        self.out.write.assert_called_once_with("12:42:00 oop    | narcissist")

    def test_colour_simple(self):
        self.p = Printer(output=self.out, name="red", colour="31")
        self.p.write("conflate")
        self.out.write.assert_called_once_with("\033[31m12:42:00 red | \033[0mconflate")
