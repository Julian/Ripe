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


class Assign(Node):
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj


class Variable(Node):
    def __init__(self, name):
        self.name = name


class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


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
    def _gather_statements(self, star):
        while len(star.children) == 2:
            child, star = star.children
            yield self.visit_statement(child)
        yield self.visit_statement(star.children[0])

    def visit_program(self, node):
        # XXX: Some statements and then EOF, not sure why I can't remove the
        #      EOF and just get a list of statements with >statements*<
        if len(node.children) < 2:
            statements = []
        else:
            statements = self._gather_statements(node.children[0])

        return CompoundStatement(statements)

    def visit_statement(self, node):
        chnode, = node.children
        if chnode.symbol == "expression":
            expr = self.visit_expression(chnode)
        elif chnode.symbol == "assignment_statement":
            expr = self.visit_assign(chnode)
        return Statement(expr)

    def visit_expression(self, node):
        chnode, = node.children
        return getattr(self, "visit_%s" % chnode.symbol)(chnode)

    def visit_assign(self, node):
        assignment = node.children[0].children[0]
        # XXX: Why doesn't this work with ["="] in the grammar?
        name, _, obj = assignment.children
        # XXX: Why doesn't the variable get substituted by the identifier?
        name, obj = name.children[0].additional_info, obj.children[0]
        return Assign(Variable(name), self.visit_expression(obj))

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

    def visit_equality_expression(self, node):
        left, op, right = node.children
        op = op.children[0].additional_info
        return BinOp(
            self.visit_literal(left), op, self.visit_expression(right)
        )


transformer = Transformer()


def parse(source, transformer=transformer):
    """
    Parse the source code and produce an AST.

    """

    return transformer.visit_program(_parse(source))
