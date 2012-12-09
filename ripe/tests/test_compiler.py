from textwrap import dedent
from unittest import TestCase

from ripe.parser import parse
from ripe.compiler import compile_ast


class CompilerTestMixin(object):
    def assertCompiles(self, source, expected):
        bytecode = compile_ast(parse(source))
        self.assertEqual(
            [line.strip() for line in dedent(expected).splitlines() if line],
            bytecode.dump().splitlines()
        )


class TestCompiler(TestCase, CompilerTestMixin):
    def test_basic(self):
        self.assertCompiles(
            "1",
            """
            LOAD_CONSTANT 0
            DISCARD_TOP 0
            RETURN 0
            """
        )

    def test_add(self):
        self.assertCompiles(
            "a + 1",
            """
            LOAD_VARIABLE 0
            LOAD_CONSTANT 0
            BINARY_ADD 0
            DISCARD_TOP 0
            RETURN 0
            """
        )

    def test_sub(self):
        self.assertCompiles(
            "a - 1",
            """
            LOAD_VARIABLE 0
            LOAD_CONSTANT 0
            BINARY_SUB 0
            DISCARD_TOP 0
            RETURN 0
            """
        )

    def test_assign(self):
        self.assertCompiles(
            "a = 1",
            """
            LOAD_CONSTANT 0
            ASSIGN 0
            RETURN 0
            """
        )
