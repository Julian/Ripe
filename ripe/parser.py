import py
from pypy.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function

from ripe import ripedir

grammar = py.path.local(ripedir).join("grammar.txt").read("rt")
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


class Program(Node):
    def __init__(self, statements=()):
        self.statements = list(statements)


class Expression(Node):
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


class Bool(Node):
    def __init__(self, value):
        self.value = value


class SingleQString(Node):
    def __init__(self, value):
        self.value = value


class DoubleQString(Node):
    def __init__(self, value):
        self.value = value


class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = list(body)


class Until(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = list(body)


class Transformer(object):
    def visit(self, node):
        return getattr(self, "visit_%s" % node.symbol)(node)

    def visit_program(self, node):
        if not node.children:
            return Program()
        statements, = node.children
        return Program(self.visit(statements))

    def visit_statements(self, node):
        return (self.visit(statement) for statement in node.children)

    def visit_expression_statement(self, node):
        expression, = node.children
        return Expression(self.visit(expression))

    def visit_assignment_statement(self, node):
        variable, obj = node.children[0].children[0].children
        obj, = obj.children
        return Assign(self.visit(variable), self.visit(obj))

    def visit_numeric_literal(self, node):
        number = self.visit(node.children[-1])

        if len(node.children) != 1:
            sign, _ = node.children
            sign = 1 if not sign.additional_info.count("-") % 2 else -1
            number.value *= sign

        return number

    def visit_integer_literal(self, node):
        integer, = node.children
        base = integer.symbol.partition("_")[0]

        value = integer.additional_info
        value = value[2:] if value.startswith("0") and value != "0" else value

        bases = {"BINARY" : 2, "OCTAL" : 8, "DECIMAL" : 10, "HEX" : 16}

        return Int(int(value, bases[base]))

    def visit_signed_number(self, node):
        sign, number_node = node.children
        number = self.visit_unsigned_number(number_node)
        if sign.additional_info == "-":
            number = number * -1
        return number

    def visit_string_literal(self, node):
        string, = node.children
        value = string.additional_info[1:-1]

        if string.symbol == "SINGLE_QUOTED_STRING":
            return SingleQString(value)
        elif string.symbol == "DOUBLE_QUOTED_STRING":
            return DoubleQString(value)
        raise NotImplementedError

    def visit_variable(self, node):
        name, = node.children
        return Variable(name.additional_info)

    def visit_equality_expression(self, node):
        left, op, right = node.children
        return BinOp(self.visit(left), op.additional_info, self.visit(right))

    def visit_while_expression(self, node):
        condition, do = node.children
        body, = do.children
        return While(self.visit(condition), self.visit(body))

    def visit_until_expression(self, node):
        condition, do = node.children
        body, = do.children
        return Until(self.visit(condition), self.visit(body))


transformer = Transformer()


def parse(source, transformer=transformer):
    """
    Parse the source code and produce an AST.

    """

    ast = ToAST().transform(_parse(source))
    return transformer.visit_program(ast)
