class W_Object(object):
    pass


class W_Integer(W_Object):
    def __init__(self, value):
        self.value = value

    def add(self, other):
        if not isinstance(other, W_Integer):
            raise TypeError
        return W_Integer(self.value + other.value)

    def eq(self, other):
        if not isinstance(other, W_Integer):
            raise TypeError
        return self.value == other.value

    def inspect(self):
        # XXX
        return str(self.value)


class W_TrueClass(W_Object):
    def inspect(self):
        return "true"


class W_FalseClass(W_Object):
    def inspect(self):
        return "false"


w_true, w_false = W_TrueClass(), W_FalseClass()


def boolean(value):
    if value:
        return w_true
    return w_false
