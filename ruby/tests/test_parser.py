from textwrap import dedent
from unittest import TestCase

from pypy.rlib.parsing.parsing import ParseError
from pypy.rlib.parsing.deterministic import LexerError

from ruby import parser
from ruby.parser import (
    Assign,
    CompoundStatement,
    DoubleQString,
    Int,
    Variable,
    SingleQString,
    Statement,
)


class ParserTestMixin(object):
    def assertParses(self, source, *statement_nodes):
        try:
            parsed = parser.parse(source)
        except ParseError as e:
            self.fail(e.nice_error_message(__file__, source))
        except LexerError as e:
            self.fail(e.nice_error_message(__file__))

        self.assertEqual(
            parser.parse(source),
            CompoundStatement(Statement(node) for node in statement_nodes)
        )


class TestEmpty(TestCase):
    def test_empty_program(self):
        self.assertEqual(parser.parse(""), CompoundStatement([]))


class TestInteger(TestCase, ParserTestMixin):
    def test_zero(self):
        self.assertParses("0", Int(0))

    def test_one(self):
        self.assertParses("1", Int(1))

    def test_a_lot(self):
        self.assertParses("123454321", Int(123454321))

    def test_positive(self):
        self.assertParses("+13", Int(13))

    def test_negative(self):
        self.assertParses("-13", Int(-13))

    def test_dec(self):
        self.assertParses("0d12", Int(12))

    def test_bin(self):
        self.assertParses("0b101", Int(0b101))

    def test_oct(self):
        self.assertParses("0o127", Int(0o127))

    def test_hex(self):
        self.assertParses("0x1af", Int(0x1af))

    def test_multiple_integers(self):
        source = dedent("""
        12
        0B10111
        0O172
        """)
        self.assertParses(source, Int(12), Int(0b10111), Int(0o172))


class TestString(TestCase, ParserTestMixin):
    def test_empty_single(self):
        self.assertParses("''", SingleQString(""))

    def test_foo_single(self):
        self.assertParses("'foo'", SingleQString("foo"))

    def test_empty_double(self):
        self.assertParses('""', DoubleQString(""))

    def test_foo_double(self):
        self.assertParses('"foo"', DoubleQString("foo"))


class TestAssignment(TestCase, ParserTestMixin):
    def test_single_assignment(self):
        self.assertParses("x = 12", Assign(Variable("x"), Int(12)))

    def test_a_bunch_of_single_assignments(self):
        source = dedent("""
        x = 12
        y = 'foo'
        """)
        self.assertParses(
            source,
            Assign(Variable("x"), Int(12)),
            Assign(Variable("y"), SingleQString("foo"))
        )
