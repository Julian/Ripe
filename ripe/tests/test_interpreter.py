from textwrap import dedent
from unittest import TestCase

from ripe.interpreter import interpret


class TestInterpreter(TestCase):
    def test_interpret(self):
        interpret("1 + 2")
