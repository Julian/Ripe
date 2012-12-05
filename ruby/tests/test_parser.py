from unittest import TestCase

from ruby import parser
from ruby.parser import CompoundStatement, Statement, Int, Name


class ParserTestMixin(object):
    def assertParses(self, source, *statement_nodes):
        self.assertEqual(
            parser.parse(source),
            CompoundStatement(Statement(node) for node in statement_nodes)
        )


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
