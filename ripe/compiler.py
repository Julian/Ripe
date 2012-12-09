bytecodes = [
    "LOAD_CONSTANT",
    "LOAD_VARIABLE",
    "RETURN",
    "ASSIGN",
    "DISCARD_TOP",
    "JUMP_IF_FALSE",
    "JUMP_BACKWARD",
    "BINARY_ADD",
    "BINARY_SUB",
    "BINARY_EQ",
]
for i, bytecode in enumerate(bytecodes):
        globals()[bytecode] = i


BINOP = {"+" : BINARY_ADD, "-" : BINARY_SUB, "==" : BINARY_EQ}


class CompilerContext(object):
    def __init__(self):
        self.data = []
        self.constants = []
        self.names = []
        self.name_indices = {}

    def emit(self, bytecode, arg=0):
        self.data.append((bytecode, arg))

    def register_constant(self, constant):
        self.constants.append(constant)
        return len(self.constants) - 1

    def register_variable(self, name):
        if name in self.name_indices:
            return self.name_indices[name]

        self.names.append(name)
        return self.name_indices.setdefault(name, len(self.names) - 1)

    def create_bytecode(self):
        return ByteCode(self.data, self.constants[:], len(self.names))


class ByteCode(object):
    def __init__(self, code, constants, num_vars):
        self.code = list(code)
        self.constants = constants
        self.num_vars = num_vars

    def dump(self):
        return "\n".join(
            "%s %s" % (bytecodes[code], arg) for code, arg in self.code
        )


def compile_ast(ast_node):
    context = CompilerContext()
    ast_node.compile(context)
    context.emit(RETURN, 0)
    return context.create_bytecode()