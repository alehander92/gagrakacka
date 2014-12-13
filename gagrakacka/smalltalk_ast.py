
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
