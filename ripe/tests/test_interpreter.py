from StringIO import StringIO
from textwrap import dedent
from unittest import TestCase
import sys

from ripe.interpreter import interpret


class TestInterpreter(TestCase):
    def setUp(self):
        self.stdout = sys.stdout = StringIO()
        self.addCleanup(lambda : setattr(sys, "stdout", sys.__stdout__))

    def interpret(self, source):
        return interpret(dedent(source))

    def test_interpret(self):
        interpret("1 + 2")

    def test_puts(self):
        # XXX: This eventually should be a method on Kernel but this will allow
        #      us to proceed for a while. When it does, all the tests that rely
        #      on this should still function equivalently, but this test might
        #      want to be moved elsewhere.
        self.interpret("puts 1")
        self.assertEqual(self.stdout.getvalue(), "1\n")

    def test_assign(self):
        self.interpret("""
        i = 12
        puts i
        """)
        self.assertEqual(self.stdout.getvalue(), "12\n")

    def test_eq(self):
        self.interpret("puts 1 == 1")
        self.assertEqual(self.stdout.getvalue(), "true\n")

    def test_neq(self):
        self.interpret("puts 5 != 5")
        self.assertEqual(self.stdout.getvalue(), "false\n")

    def test_while(self):
        self.interpret("""
        i = 0
        while i != 4
            puts i
            i = i + 1
        end
        """)
        self.assertEqual(self.stdout.getvalue(), "0\n1\n2\n3\n")
