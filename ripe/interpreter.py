from ripe import compiler
from ripe.compiler import compile_ast
from ripe.parser import parse


class Frame(object):
    def __init__(self, bc):
        self.value_stack = [0] * 100  # safe estimate!
        self.vars = [0] * bc.num_vars
        self.value_stack_pos = 0

    def push(self, v):
        self.value_stack[self.value_stack_pos] = v
        self.value_stack_pos += 1

    def pop(self):
        new_pos = self.value_stack_pos - 1
        assert new_pos >= 0
        v = self.value_stack[new_pos]
        self.value_stack_pos = new_pos
        return v


def add(left, right):
    return left + right


def execute(frame, bc):
    code = bc.code
    pc = 0
    while True:
        c = ord(code[pc])
        arg = ord(code[pc + 1])
        pc += 2
        if c == compiler.LOAD_CONSTANT:
            frame.push(bc.constants[arg])
        elif c == compiler.DISCARD_TOP:
            frame.pop()
        elif c == compiler.RETURN:
            return
        elif c == compiler.BINARY_ADD:
            right = frame.pop()
            left = frame.pop()
            frame.push(add(left, right))
        elif c == compiler.BINARY_NEQ:
            left, right = frame.pop(), frame.pop()
            frame.push(left != right)
        elif c == compiler.JUMP_BACKWARD:
            pc = arg
        elif c == compiler.JUMP_IF_FALSE:
            if not frame.pop():
                pc = arg
        elif c == compiler.PUTS:
            # XXX
            print frame.pop()
        elif c == compiler.ASSIGN:
            frame.vars[arg] = frame.pop()
        elif c == compiler.LOAD_VARIABLE:
            frame.push(frame.vars[arg])
        else:
            assert False, compiler.bytecodes[c]


def interpret(source):
    bc = compile_ast(parse(source))
    frame = Frame(bc)
    execute(frame, bc)
    return frame
