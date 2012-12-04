from unittest import TestCase

from ruby.parser import CompoundStatement, Statement, Int, BinOp, Name, parse


class TestInteger(TestCase):
    def test_zero(self):
        source = "0"
        self.assertEqual(
            parse(source),
            CompoundStatement([Statement(Int(0))])
        )

    def test_one(self):
        source = "1"
        self.assertEqual(
            parse(source),
            CompoundStatement([Statement(Int(1))])
        )

    def test_a_lot(self):
        source = "123454321"
        self.assertEqual(
            parse(source),
            CompoundStatement([Statement(Int(123454321))])
        )

    def test_dec(self):
        source = "0d12"
        self.assertEqual(
            parse(source),
            CompoundStatement([Statement(Int(12))])
        )

    def test_bin(self):
        source = "0b101"
        self.assertEqual(
            parse(source),
            CompoundStatement([Statement(Int(0b101))])
        )

    def test_oct(self):
        source = "0o127"
        self.assertEqual(
            parse(source),
            CompoundStatement([Statement(Int(0o127))])
        )

    def test_hex(self):
        source = "0x1af"
        self.assertEqual(
            parse(source),
            CompoundStatement([Statement(Int(0x1af))])
        )
