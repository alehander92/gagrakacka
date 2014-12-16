class Env(object):

    def __init__(self, parent, vars):
        self.parent, self.vars = parent, vars

    def __setitem__(self, var, value):
        self.vars[var] = value

    def __getitem__(self, var):
        a = self
        while a:
            if var in a.vars:
                return a.vars[var]
            previous, a = a, a.parent
        return previous.vars['Nil']

