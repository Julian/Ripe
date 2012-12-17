from pypy.jit.metainterp.test.support import LLJitMixin
from textwrap import dedent
from unittest import TestCase

from ripe.interpreter import interpret


class TestJit(TestCase, LLJitMixin):
    def test_jit(self):
        codes = [dedent(source) for source in (
        "puts 1",
        """
        n = 0
        while n != 10 do
            n = n + 1
        end
        """,
        )]

        def main(i):
            interpret(codes[i])

        self.meta_interp(main, [1], listops=True)
