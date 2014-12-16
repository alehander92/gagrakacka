class Env(object):

    def __init__(self, parent, vars):
        self.parent, self.vars = parent, vars
        self.root = self if self.parent is None else self.parent.root

    def __setitem__(self, var, value):
        self.vars[var] = value

    def __getitem__(self, var):
        a = self
        while a:
            if var in a.vars:
                return a.vars[var]
            previous, a = a, a.parent
        return previous.vars['Nil']
