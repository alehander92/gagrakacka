import parser
from smalltalk_ast import *

def value_init(this, value, env):
    this.value = value
    return this


class Interpreter(object):

    def a_eval(self, node, env):
        print('EVAL %s' % str(type(node).__name__.lower()), node.__dict__)
        return getattr(self, 'a_eval_%s' % str(type(node).__name__.lower()))(node, env)

    def a_eval_program(self, children, env):
        results = [self.a_eval(child, env) for child in children.children]
        return results[-1]

    def a_eval_integer(self, integer, env):
        a = env['Integer']
        return a.smalltalk_send('new:', [integer.value], env)

    def a_eval_string(self, string, env):
        klass = env['String']
        return klass.smalltalk_send('new:', [string.value], env)

    def a_eval_label(self, label, env):
        return env[label.label]

    def a_eval_message(self, message, env):
        receiver = self.a_eval(message.receiver, env)
        args = [self.a_eval(arg, env) for arg in message.args]
        return receiver.smalltalk_send(message.message, args, env)

    def a_eval_block(self, block, env):
        args = block.args
        ast = block.ast
        return env['BlockClosure'].smalltalk_send('new', [], env).smalltalk_send('args:ast:', [args, ast], env)

    def a_eval_assignment(self, assignment, env):
        env[assignment.cell.label] = self.a_eval(assignment.value, env)
        return env[assignment.cell.label]

    def a_eval_list(self, list, env):
        return smalltalk_array([self.a_eval(value, env) for value in list.values], env)

# Gagrakacka

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
                print('MESSAGE %s in %s' % (message, kind.name))
                return kind.handlers[message](self, *(args + [handler_env]))
            else:
                print('WRONG %s %s' % (message, kind.name))
        return self.smalltalk_send('doesNotUnderstand:', [message], env)


class Klass(SObject):

    def __init__(self, name, parent, handlers, env):
        self.name = name
        self.parent = parent
        self.handlers = handlers
        self.klass = env.vars.get('Class')

    def smalltalk_ancestors(self):
        z = self
        ancestors = []
        while z.parent is not None:
            ancestors.append(z.parent)
            z = z.parent
        return ancestors


class Atom(SObject):

    def __init__(self, klass, data):
        self.klass = klass
        self.data = data


class SmalltalkError(Exception):
    pass


class DoesNotUnderstand(SmalltalkError):
    pass


class SmalltalkParserError(SmalltalkError):
    pass

# 'Sofia' printLn

# ->

# Message(
#     String('Sofia'),
#     ['printLn'],
#     [None])


def error(exception):
    raise exception


def display(this, thing):
    print(thing)
    return this


def smalltalk_string(string, env):
    return env['String'].smalltalk_send('new:', [string], env)


def smalltalk_array(array, env):
    return env['Array'].smalltalk_send('new:', [array], env)


def smalltalk_dictionary(dictionary, env):
    return env['Dictionary'].smalltalk_send('new:', [dictionary], env)

def smalltalk_integer(value, env):
    return env['Integer'].smalltalk_send('new:', [value], env)


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

env = Env(None, {})

env.vars['Class'] = Klass('Class', None, {}, env)
env.vars['Object'] = Klass('Object', None, {}, env)
env.vars['Class'].parent = env.vars['Object']
env.vars['Class'].klass = env.vars['Class']
env.vars['String'] = Klass('String', env.vars['Object'], {}, env)
env.vars['Integer'] = Klass('Integer', env.vars['Object'], {}, env)
env.vars['UndefinedObject'] = Klass('UndefinedObject', env.vars['Object'], {}, env)
env.vars['Nil'] = Atom(env.vars['UndefinedObject'], {})
env.vars['Collection'] = Klass('Collection', env.vars['Object'], {}, env)
env.vars['Array'] = Klass('Array', env.vars['Collection'], {}, env)
env.vars['BlockClosure'] = Klass('BlockClosure', env.vars['Object'], {}, env)
env.vars['Dictionary'] = Klass('Dictionary', env.vars['Collection'], {}, env)

env.vars['Object'].handlers = {
    'printNl': lambda this, env: display(this, this.smalltalk_send('asString', [], env).value),

    'asString': lambda this, env: smalltalk_string(repr(this), env),

    'messages': lambda this, env: smalltalk_array([smalltalk_string(key, env) for key in this.klass.handlers.keys()], env),

    'ancestors': lambda this, env: smalltalk_array(this.klass.smalltalk_ancestors(), env),

    'doesNotUnderstand:': lambda this, message, env:
        error(DoesNotUnderstand('%s does not und %s' %
                                (this.smalltalk_send('asString', [], env).value, message))),

    'class': lambda this, _ : this.klass,

    'slots': lambda this, _: smalltalk_dictionary({smalltalk_string(key) : value for key, value in this.data}, env),

    'init': lambda this, _: this,

    'init:': lambda this, value, env: this
}

env.vars['Class'].handlers = {
    'new': lambda this, env: Atom(this, {}).smalltalk_send('init', [], env),
    'new:': lambda this, value, env: Atom(this, {}).smalltalk_send('init:', [value], env),
    'asString': lambda this, env: smalltalk_string(this.name, env),
}

env.vars['String'].handlers = {
    'asString': lambda this, env: smalltalk_string("'%s'" % this.value, env),
    'length': lambda this, env: smalltalk_integer(len(this.value), env),
    'init:': value_init
}

env.vars['Integer'].handlers = {
    'asString': lambda this, env: smalltalk_string(str(this.value), env),
    'init:': value_init,
    '-': lambda this, other, env: smalltalk_integer(this.value - other.value, env),
    '+': lambda this, other, env: smalltalk_integer(this.value + other.value, env),
    '*': lambda this, other, env: smalltalk_integer(this.value * other.value, env),
    '/': lambda this, other, env: smalltalk_integer(this.value / other.value, env)
}

env.vars['UndefinedObject'].handlers = {
    'asString': lambda _, env: smalltalk_string('nil', env)
}

def collection_at_put(this, key, cell, _):
    this.value[key.value] = cell
    return this

env.vars['Collection'].handlers = {
    'init:': value_init,
    'at:': lambda this, index, _: this.value[index.value],
    'at:put:': collection_at_put
}

env.vars['Array'].handlers = {
    'asString' : lambda this, env: smalltalk_string('#(%s)' % ' '.join([value.smalltalk_send('asString', [], env).value for value in this.value]), env)
}


def block_closure_value(this, *values_and_env):
    values, env = values_and_env[:-1], values_and_env[-1]  # what is wrong with you python
    if len(this.args) != len(values):
        raise SmalltalkError('wrong number of arguments: expected %d got %d' %
                             (len(this.args), len(values)))

    vars = {arg: value for arg, value in zip(this.args, values)}
    handler_env = Env(env, vars)
    return Interpreter().a_eval(this.ast, handler_env)

def init_block(this, args, ast, _):
    this.args = args
    this.ast = ast
    return this

env.vars['BlockClosure'].handlers = {
    'argumentsCount': lambda this, env: smalltalk_integer(len(this.args), env),
    'args': lambda this, env: smalltalk_array([smalltalk_string(arg, env) for arg in this.args]),
    'value': block_closure_value,
    'value:': block_closure_value,
    'value:value:': block_closure_value,
    'value:value:value:': block_closure_value,
    'valueWithArguments:': lambda this, args, env: block_closure_value(this, *(args + [env])),
    'args:ast:' : init_block,
    'asString' : lambda this, env: smalltalk_string('^block^', env)
}

env.vars['Dictionary'].handlers = {
    'keys' : lambda this, env: smalltalk_array(this.value.keys(), env),
    'values' : lambda this, env: smalltalk_array(this.value.values(), env),
    'asString' : lambda this, env: smalltalk_string('{\n%s\n}' % '\n'.join(
                ['%s: %s' % (key.smalltalk_send('asString', env), value.smalltalk_send('asString', env)) for key, value in this.value.items()]), env)
}


# Interpreter().a_eval(Message(
#     String('Sofia'),
#     'printLn',
#     []), env)

# Interpreter().a_eval(Message(
#     Message(Block(['x'], Label('x')), 'value:', [Integer(-4)]),
#     'printLn',
#     []), env)

def shell():
    z = ''
    a = Interpreter()
    while z != 'quit':
        z = raw_input('> ').strip()
        if z != 'quit':
            ast = parser.parse_smalltalk(z)
            try:
                print(a.a_eval(ast, env).smalltalk_send('asString', [], env).value)
            except SmalltalkError, ex:
                print('error: %s' % str(ex))

shell()
