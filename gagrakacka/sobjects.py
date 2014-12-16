import types
from env import Env
from errors import MessageArgCountError
from interpreter import Interpreter

class SObject(object):

    def smalltalk_send(self, message, args, env):
        ancestors = [self.klass] + self.klass.smalltalk_ancestors()

        for kind in ancestors:
            if message in kind.handlers:
                if message.endswith(':'):
                    words = message.split(':')
                    vars = {k: v for k, v in zip(words, args)}
                    vars['self'] = self
                else:
                    vars = {}
                handler_env = Env(env, vars)
                # print('MESSAGE %s in %s %s' %
                #      (message, kind.name, 'class' if isinstance(kind, Metaclass) else ''))
                if isinstance(kind.handlers[message], types.FunctionType):
                    return kind.handlers[message](self, *(args + [handler_env]))
                else:
                    return self.h_send(kind.handlers[message], args, handler_env)
            else:
                pass # print('WRONG %s %s' % (message, kind.name))
        return self.smalltalk_send('doesNotUnderstand:', [message], env)

    def h_send(self, handler, a, env):
        if len(handler.args) != len(a):
            raise MessageArgCountError('Wrong number of args')
        vars = {k: v for k, v in zip(handler.args, a)}
        vars['self'] = self
        handler_env = Env(env, vars)
        return Interpreter().a_eval(handler.ast, handler_env)


class KlassDescription(SObject):

    def __init__(self, name, parent, handlers, env):
        self.name = name
        self.parent = parent
        self.handlers = handlers

    def smalltalk_ancestors(self):
        z = self
        ancestors = []
        while z.parent is not None:
            ancestors.append(z.parent)
            z = z.parent
        return ancestors

class Klass(KlassDescription):

    def __init__(self, name, parent, handlers, env):
        super(Klass, self).__init__(name, parent, handlers, env)
        parent_metaclass = self.parent.klass if parent is not None else None
        self.klass = Metaclass(name, parent_metaclass, {}, env)


class Metaclass(KlassDescription):

    def __init__(self, name, parent, handlers, env):
        super(Metaclass, self).__init__(name, parent, handlers, env)
        self.klass = env.vars.get('Metaclass')


class Atom(SObject):

    def __init__(self, klass, data):
        self.klass = klass
        self.data = data

