from textwrap import dedent
from unittest import TestCase

from pypy.rlib.parsing.parsing import ParseError
from pypy.rlib.parsing.deterministic import LexerError

from ripe import parser
from ripe.parser import (
    Assign,
    BinOp,
    Compound,
    DoubleQString,
    Expression,
    If,
    Int,
    Method,
    Unless,
    Until,
    Variable,
    While,
    SingleQString,
)


class ParserTestMixin(object):
    def surround(self, node):
        return node

    def assertParses(self, source, *statement_nodes):
        try:
            parsed = parser.parse(source)
        except ParseError as e:
            self.fail(e.nice_error_message(__file__, source))
        except LexerError as e:
            self.fail(e.nice_error_message(__file__))

        self.assertEqual(
            parser.parse(source),
            Compound([self.surround(value) for value in statement_nodes])
        )


class TestEmpty(TestCase, ParserTestMixin):
    def test_empty_program(self):
        self.assertParses("")


class TestComment(TestCase, ParserTestMixin):
    def test_full_line(self):
        self.assertParses("# foo bar\n")

    def test_mid_line(self):
        self.assertParses(
            "a = 1  # foo bar\n", Assign("a", Int(1)),
        )


class TestInteger(TestCase, ParserTestMixin):

    surround = Expression

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
        00172
        """)
        self.assertParses(source, Int(12), Int(0b10111), Int(0o172))


class TestString(TestCase, ParserTestMixin):

    surround = Expression

    def test_empty_single(self):
        self.assertParses("''", SingleQString(""))

    def test_foo_single(self):
        self.assertParses("'foo'", SingleQString("foo"))

    def test_empty_double(self):
        self.assertParses('""', DoubleQString(""))

    def test_foo_double(self):
        self.assertParses('"foo"', DoubleQString("foo"))


class TestPseudoVariables(TestCase, ParserTestMixin):

    # TODO: Right now these aren't special. Maybe they will be.
    surround = Expression

    def test_true(self):
        self.assertParses("true", Variable("true"))

    def test_false(self):
        self.assertParses("false", Variable("false"))

    def test_nil(self):
        self.assertParses("nil", Variable("nil"))

    def test_self(self):
        self.assertParses("self", Variable("self"))


class TestAssign(TestCase, ParserTestMixin):
    def test_single_assignment(self):
        self.assertParses("x = 12", Assign("x", Int(12)))

    def test_a_bunch_of_single_assignments(self):
        source = dedent("""
        x = 12
        y = 'foo'
        """)
        self.assertParses(
            source,
            Assign("x", Int(12)),
            Assign("y", SingleQString("foo"))
        )


class TestBinOp(TestCase, ParserTestMixin):

    surround = Expression

    def test_add_ints(self):
        self.assertParses("2 + 6", BinOp(Int(2), "+", Int(6)))

    def test_subtract_ints(self):
        self.assertParses("1 - 0b101", BinOp(Int(1), "-", Int(0b101)))

    def test_add_int_and_var(self):
        self.assertParses("foo + 1", BinOp(Variable("foo"), "+", Int(1)))

    def test_subtract_int_and_var(self):
        self.assertParses("1 - foo", BinOp(Int(1), "-", Variable("foo")))


class TestConditional(TestCase, ParserTestMixin):

    surround = Expression

    def test_if(self):
        source = dedent("""
        if 1
            i = 2
        end
        """)

        self.assertParses(
            source, If(Int(1), Compound([Assign("i", Int(2))]))
        )

    def test_unless(self):
        source = dedent("""
        unless 1
            i = 2
        end
        """)

        self.assertParses(
            source, Unless(Int(1), Compound([Assign("i", Int(2))]))
        )


class TestLoops(TestCase, ParserTestMixin):

    surround = Expression

    def test_while(self):
        source = dedent("""
        while 1 do
            i = 2
        end
        """)

        self.assertParses(
            source, While(Int(1), Compound([Assign("i", Int(2))]))
        )

    def test_until(self):
        source = dedent("""
        until 1 do
            i = 2
        end
        """)

        self.assertParses(
            source, Until(Int(1), Compound([Assign("i", Int(2))]))
        )


class TestMethodDefinition(TestCase, ParserTestMixin):

    surround = Expression

    # def test_empty_def(self):
    #     source = dedent("""
    #     def foo
    #     end
    #     """)

    #     self.assertParses(source, Method("foo", [], Compound()))

    def test_def_with_single_arg(self):
        source = dedent("""
        def foo x
            1
        end
        """)

        self.assertParses(
            source,
            Method("foo", ["x"], Compound([Expression(Int(1))]))
        )

    def test_def_with_multiple_args(self):
        source = dedent("""
        def foo x, y
            1
        end
        """)

        self.assertParses(
            source,
            Method("foo", ["x", "y"], Compound([Expression(Int(1))]))
        )

    def test_def_with_parens(self):
        source = dedent("""
        def foo(x, y)
            1
        end
        """)

        self.assertParses(
            source,
            Method("foo", ["x", "y"], Compound([Expression(Int(1))]))
        )

    def test_no_args(self):
        source = dedent("""
        def foo
            a = 12
        end
        """)

        self.assertParses(
            source,
            Method("foo", [], Compound([Assign("a", Int(12))]))
        )

    def test_def_with_empty_parens(self):
        source = dedent("""
        def foo()
            1
        end
        """)

        self.assertParses(
            source,
            Method("foo", [], Compound([Expression(Int(1))]))
        )
