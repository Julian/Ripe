from StringIO import StringIO
from textwrap import dedent
from unittest import TestCase
import sys

from ripe.interpreter import interpret


class TestInterpreter(TestCase):
    def test_interpret(self):
        interpret("1 + 2")

    def test_puts(self):
        # XXX: This eventually should be a method on Kernel but this will allow
        #      us to proceed for a while
        stdout = sys.stdout = StringIO()
        self.addCleanup(lambda : setattr(sys, "stdout", sys.__stdout__))

        interpret("puts 1")
        self.assertEqual(stdout.getvalue(), "1\n")
