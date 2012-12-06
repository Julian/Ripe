import py
from pypy.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function

from ruby import rubydir

grammar = py.path.local(rubydir).join("grammar.txt").read("rt")
regexs, rules, ToAST = parse_ebnf(grammar)
_parse = make_parse_function(regexs, rules, eof=True)


class Node(object):
    """
    An AST node.

    """

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.__dict__ == other.__dict__
        )

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        contents = ("%s=%r" % (k, v) for k, v in self.__dict__.iteritems())
        return "<%s %s>" % (self.__class__.__name__, ", ".join(contents))


class CompoundStatement(Node):
    def __init__(self, statements):
        self.statements = list(statements)


class Statement(Node):
    def __init__(self, expr):
        self.expr = expr


class Name(Node):
    pass


class Int(Node):
    def __init__(self, value):
        self.value = value


class SingleQString(Node):
    def __init__(self, value):
        self.value = value


class DoubleQString(Node):
    def __init__(self, value):
        self.value = value


class Transformer(object):
    def visit_program(self, node):
        statements = node.children[0].children
        return CompoundStatement(self.visit_statement(s) for s in statements)

    def visit_statement(self, node):
        return Statement(self.visit_expression(node.children[0]))

    def visit_expression(self, node):
        return self.visit_literal(node.children[0])

    def visit_literal(self, node):
        chnode = node.children[0]
        if chnode.symbol == "numeric_literal":
            return Int(self.visit_numeric_literal(chnode))
        elif chnode.symbol == "string_literal":
            return self.visit_string_literal(chnode)

    def visit_numeric_literal(self, node):
        chnode = node.children[0]
        if chnode.symbol == "signed_number":
            return self.visit_signed_number(chnode)
        return self.visit_unsigned_number(chnode)

    def visit_signed_number(self, node):
        sign, number_node = node.children
        number = self.visit_unsigned_number(number_node)
        if sign.additional_info == "-":
            number = number * -1
        return number

    def visit_unsigned_number(self, node):
        chnode = node.children[0].children[0]
        value = chnode.additional_info

        if value.startswith(("0b", "0B", "0d", "0D")):
            value = value[2:]

        if chnode.symbol == "BINARY_INTEGER_LITERAL":
            base = 2
        elif chnode.symbol == "OCTAL_INTEGER_LITERAL":
            base = 8
        elif chnode.symbol == "DECIMAL_INTEGER_LITERAL":
            base = 10
        elif chnode.symbol == "HEX_INTEGER_LITERAL":
            base = 16
        else:
            raise ValueError

        return int(value, base)

    def visit_string_literal(self, node):
        chnode = node.children[0]
        value = chnode.additional_info[1:-1]

        if chnode.symbol == "SINGLE_QUOTED_STRING":
            return SingleQString(value)
        return DoubleQString(value)


transformer = Transformer()


def parse(source, transformer=transformer):
    """
    Parse the source code and produce an AST.

    """

    return transformer.visit_program(_parse(source))
