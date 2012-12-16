from pypy.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from pypy.rlib.parsing.tree import RPythonVisitor
import py

from ripe import compiler, ripedir

grammar = py.path.local(ripedir).join("grammar.txt").read("rt")
regexs, rules, ToAST = parse_ebnf(grammar)
_parse = make_parse_function(regexs, rules, eof=True)


BASES = {"BINARY" : 2, "OCTAL" : 8, "DECIMAL" : 10, "HEX" : 16}


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


class Compound(Node):
    def __init__(self, statements=None):
        if statements is None:
            statements = []
        self.statements = statements

    def compile(self, context):
        for statement in self.statements:
            statement.compile(context)


class Expression(Node):
    def __init__(self, expr):
        self.expr = expr

    def compile(self, context):
        self.expr.compile(context)
        context.emit(compiler.DISCARD_TOP)


class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def compile(self, context):
        self.expr.compile(context)
        context.emit(compiler.ASSIGN, context.register_variable(self.name))


class Variable(Node):
    def __init__(self, name):
        self.name = name

    def compile(self, context):
        context.emit(
            compiler.LOAD_VARIABLE, context.register_variable(self.name),
        )


class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def compile(self, context):
        self.left.compile(context)
        self.right.compile(context)
        context.emit(compiler.BINOP[self.op])



class Int(Node):
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        context.emit(
            compiler.LOAD_CONSTANT, context.register_constant(self.value),
        )

    def neg(self):
        return self.__class__(-self.value)


class SingleQString(Node):
    def __init__(self, value):
        self.value = value


class DoubleQString(Node):
    def __init__(self, value):
        self.value = value


class If(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def compile(self, context):
        self.condition.compile(context)
        context.emit(compiler.JUMP_IF_FALSE, 0)
        jmp_pos = len(context.data) - 1
        self.body.compile(context)
        context.data[jmp_pos] = chr(len(context.data))


class Unless(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def compile(self, context):
        self.condition.compile(context)
        context.emit(compiler.JUMP_IF_TRUE, 0)
        jmp_pos = len(context.data) - 1
        self.body.compile(context)
        context.data[jmp_pos] = chr(len(context.data))


class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def compile(self, context):
        start_pos = len(context.data)
        self.condition.compile(context)
        context.emit(compiler.JUMP_IF_FALSE, 0)
        jmp_pos = len(context.data) - 1
        self.body.compile(context)
        context.emit(compiler.JUMP_BACKWARD, start_pos)
        context.data[jmp_pos] = chr(len(context.data))


class Until(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def compile(self, context):
        start_pos = len(context.data)
        self.condition.compile(context)
        context.emit(compiler.JUMP_IF_TRUE, 0)
        jmp_pos = len(context.data) - 1
        self.body.compile(context)
        context.emit(compiler.JUMP_BACKWARD, start_pos)
        context.data[jmp_pos] = chr(len(context.data))


class Puts(Node):
    # XXX
    def __init__(self, expr):
        self.expr = expr

    def compile(self, context):
        self.expr.compile(context)
        context.emit(compiler.PUTS, 0)


class Transformer(RPythonVisitor):
    def dispatch(self, node):
        return getattr(self, "visit_%s" % node.symbol)(node)

    def visit_program(self, node):
        if not node.children:
            return Compound()
        statements, = node.children
        return self.dispatch(statements)

    def visit_statements(self, node):
        return Compound([
            self.dispatch(statement) for statement in node.children
        ])

    def visit_expression_statement(self, node):
        expression, = node.children
        return Expression(self.dispatch(expression))

    def visit_assignment_statement(self, node):
        variable, obj = node.children[0].children[0].children
        variable, = variable.children
        obj, = obj.children
        return Assign(variable.additional_info, self.dispatch(obj))

    def visit_numeric_literal(self, node):
        number = self.dispatch(node.children[-1])
        if len(node.children) == 2:
            sign, _ = node.children
            if sign.additional_info.count("-") % 2:
                return number.neg()
        return number

    def visit_integer_literal(self, node):
        integer, = node.children
        base = integer.symbol.split("_", 1)[0]

        value = integer.additional_info
        value = value[2:] if value.startswith("0") and value != "0" else value

        return Int(int(value, BASES[base]))

    def visit_string_literal(self, node):
        string, = node.children
        value = string.additional_info
        end = len(value) - 1
        assert end > 0
        value = value[1:end]

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
        return BinOp(
            self.dispatch(left), op.additional_info, self.dispatch(right)
        )

    def visit_if_expression(self, node):
        condition, then = node.children
        body, = then.children
        return If(self.dispatch(condition), self.dispatch(body))

    def visit_unless_expression(self, node):
        condition, then = node.children
        body, = then.children
        return Unless(self.dispatch(condition), self.dispatch(body))

    def visit_while_expression(self, node):
        condition, do = node.children
        body, = do.children
        return While(self.dispatch(condition), self.dispatch(body))

    def visit_until_expression(self, node):
        condition, do = node.children
        body, = do.children
        return Until(self.dispatch(condition), self.dispatch(body))

    def visit_puts_statement(self, node):
        # XXX
        return Puts(self.dispatch(node.children[0]))


transformer = Transformer()


def parse(source, transformer=transformer):
    """
    Parse the source code and produce an AST.

    """

    ast = ToAST().transform(_parse(source))
    return transformer.visit_program(ast)
