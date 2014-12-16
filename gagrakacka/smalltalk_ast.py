
class Node(object):
    pass


class Program(Node):

    def __init__(self, children):
        self.children = children


class Integer(Node):

    def __init__(self, value):
        self.value = value


class String(Node):

    def __init__(self, value):
        self.value = value


class Label(Node):

    def __init__(self, label):
        self.label = label


class Message(Node):

    def __init__(self, receiver, message, args):
        self.receiver, self.message, self.args = receiver, message, args


class Block(Node):

    def __init__(self, args, ast):
        self.args = args
        self.ast = ast


class Assignment(Node):

    def __init__(self, cell, value):
        self.cell, self.value = cell, value


class List(Node):

    def __init__(self, cells):
        self.values = cells


class Symbol(Node):

    def __init__(self, value):
        self.value = value


class MethodDefinition(Node):

    def __init__(self, pattern, code, locals):
        self.pattern, self.code, self.locals = pattern, code, locals


class ClassDefinition(Node):

    def __init__(self, name, is_class, definitions):
        self.name, self.is_class, self.definitions = name, is_class, definitions


class Return(Node):

    def __init__(self, expr):
        self.expr = expr
