from pypy.rlib import jit

from ripe import compiler
from ripe.compiler import compile_ast
from ripe.objects import W_Integer, boolean, w_true, w_false, w_nil
from ripe.parser import parse


driver = jit.JitDriver(
    greens=["pc", "code", "bc"], reds=["frame"], virtualizables=["frame"],
)


class Frame(object):

    _virtualizable2_ = ['value_stack[*]', 'value_stack_pos', 'vars[*]']

    def __init__(self, bc):
        self = jit.hint(self, fresh_virtualizable=True, access_directly=True)
        self.value_stack = [None] * 3  # safe estimate!
        self.vars = [None] * bc.num_vars
        self.value_stack_pos = 0

    def push(self, v):
        pos = jit.hint(self.value_stack_pos, promote=True)
        assert pos >= 0
        self.value_stack[pos] = v
        self.value_stack_pos = pos + 1

    def pop(self):
        pos = jit.hint(self.value_stack_pos, promote=True)
        new_pos = pos - 1
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
        driver.jit_merge_point(pc=pc, code=code, bc=bc, frame=frame)
        c = ord(code[pc])
        arg = ord(code[pc + 1])
        pc += 2
        if c == compiler.LOAD_CONSTANT:
            frame.push(W_Integer(bc.constants[arg]))
        elif c == compiler.DISCARD_TOP:
            frame.pop()
        elif c == compiler.RETURN:
            return
        elif c == compiler.BINARY_ADD:
            right, left = frame.pop(), frame.pop()
            w_res = left.add(right)
            frame.push(w_res)
        elif c == compiler.BINARY_EQ:
            right, left = frame.pop(), frame.pop()
            w_res = boolean(left.eq(right))
            frame.push(w_res)
        elif c == compiler.BINARY_NEQ:
            right, left = frame.pop(), frame.pop()
            w_res = boolean(not left.eq(right))
            frame.push(w_res)
        elif c == compiler.JUMP_BACKWARD:
            pc = arg
        elif c == compiler.JUMP_IF_FALSE:
            if frame.pop() == w_false:
                frame.push(w_nil)  # XXX: Does this belong here?
                pc = arg
        elif c == compiler.PUTS:
            # XXX
            print frame.pop().inspect()
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
