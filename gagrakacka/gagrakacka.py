import os
import parser
from smalltalk_atom_converters import *
from env import Env
from errors import SmalltalkError, MessageArgCountError, DoesNotUnderstand
from sobjects import Metaclass, Klass, Atom
from interpreter import Interpreter

def error(exception):
    raise exception


def display(this, thing):
    print(thing)
    return this


env = Env(None, {})

env.vars['Behavior'] = Klass('Behavior', None, {}, env)
env.vars['ClassDescription'] = Klass('ClassDescription', env.vars['Behavior'], {}, env)
env.vars['Metaclass'] = Klass('Metaclass', env.vars['ClassDescription'], {}, env)
env.vars['Class'] = Klass('Class', env.vars['ClassDescription'], {}, env)
env.vars['Object'] = Klass('Object', None, {}, env)
env.vars['Behavior'].parent = env.vars['Object']
env.vars['Behavior'].klass.parent = env.vars['Object'].klass
env.vars['Object'].klass.parent = env.vars['Class']
for k in ['Metaclass', 'ClassDescription', 'Behavior', 'Object', 'Class']:
    env.vars[k].klass.klass = env.vars['Metaclass']
env.vars['String'] = Klass('String', env.vars['Object'], {}, env)
env.vars['Number'] = Klass('Number', env.vars['Object'], {}, env)
env.vars['Integer'] = Klass('Integer', env.vars['Number'], {}, env)
env.vars['UndefinedObject'] = Klass('UndefinedObject', env.vars['Object'], {}, env)
env.vars['Nil'] = Atom(env.vars['UndefinedObject'], {})
env.vars['Collection'] = Klass('Collection', env.vars['Object'], {}, env)
env.vars['Array'] = Klass('Array', env.vars['Collection'], {}, env)
env.vars['BlockClosure'] = Klass('BlockClosure', env.vars['Object'], {}, env)
env.vars['GagrakackaMethod'] = Klass('GagrakackaMethod', env.vars['Object'], {}, env)
env.vars['Dictionary'] = Klass('Dictionary', env.vars['Collection'], {}, env)
env.vars['Symbol'] = Klass('Symbol', env.vars['Object'], {}, env)
env.vars['BytecodeMethod'] = Klass('BytecodeMethod', env.vars['Object'], {}, env)

env.vars['Object'].handlers = {
    'printNl': lambda this, env: display(this, this.smalltalk_send('asString', [], env).value),

    'asString': lambda this, env: smalltalk_string('a %s' % this.klass.name, env),

    'messages': lambda this, env: smalltalk_array([smalltalk_string(key, env) for key in this.klass.handlers.keys()], env),

    'doesNotUnderstand:': lambda this, message, env:
        error(DoesNotUnderstand('%s does not und %s' %
                                (this.smalltalk_send('asString', [], env).value, message))),

    'class': lambda this, _: this.klass,

    'slots': lambda this, _: smalltalk_dictionary({smalltalk_string(key): value for key, value in this.data}, env),

    'init': lambda this, _: this,

    'init:': lambda this, value, env: this,
}


def subclass(this, symbol, env):
    return Klass(symbol.value, this, {}, env)

env.vars['ClassDescription'].handlers = {
    'methodDictionary': lambda this, env: smalltalk_dictionary({smalltalk_symbol(k, env): smalltalk_method(v, env) for k, v in this.handlers.items()}, env),
    'superclass': lambda this, env: this.parent or env['nil'],
    'ancestors': lambda this, env: smalltalk_array(this.smalltalk_ancestors(), env),
    'subclass:': subclass
}

env.vars['Class'].handlers = {
    'new': lambda this, env: Atom(this, {}).smalltalk_send('init', [], env),
    'new:': lambda this, value, env: Atom(this, {}).smalltalk_send('init:', [value], env),
    'asString': lambda this, env: smalltalk_string(this.name, env),
}

env.vars['Metaclass'].handlers = {
    'asString': lambda this, env: smalltalk_string('%s class' % this.name, env)
}

def value_init(default):
    def _inner(this, *value_and_env):
        if len(value_and_env) == 1:
            if default == list:
                this.value = []
            elif default == dict:
                this.value = [[], []]
            else:
                this.value = default
        else:
            this.value = value_and_env[0]
        return this
    return _inner



# Gagrakacka

# 'Sofia' printLn

# ->

# Message(
#     String('Sofia'),
#     ['printLn'],
#     [None])



env.vars['String'].handlers = {
    'asString': lambda this, env: smalltalk_string("'%s'" % this.value, env),
    'length': lambda this, env: smalltalk_integer(len(this.value), env),
    'init:': value_init(''),
    'init': value_init(''),
    '=': lambda this, other, env: smalltalk_boolean(this.value == other.value, env)
}

env.vars['Symbol'].handlers = {
    'asString': lambda this, env: smalltalk_string('#%s' % this.value, env),
    'init:': value_init(''),
    'init': value_init(''),
    '=': lambda this, other, env: smalltalk_boolean(this.value == other.value, env)
}

env.vars['Integer'].handlers = {
    'asString': lambda this, env: smalltalk_string(str(this.value), env),
    'init:': value_init(0),
    'init': value_init(0),
    '-': lambda this, other, env: smalltalk_integer(this.value - other.value, env),
    '+': lambda this, other, env: smalltalk_integer(this.value + other.value, env),
    '*': lambda this, other, env: smalltalk_integer(this.value * other.value, env),
    '/': lambda this, other, env: smalltalk_integer(this.value / other.value, env),
    '=': lambda this, other, env: smalltalk_boolean(this.value == other.value, env)
}

env.vars['UndefinedObject'].handlers = {
    'asString': lambda _, env: smalltalk_string('nil', env)
}


def collection_at_put(this, key, cell, _):
    this.value[key.value] = cell
    return this

env.vars['Collection'].handlers = {
    'at:': lambda this, index, _: this.value[index.value],
    'at:put:': collection_at_put
}

def array_each(this, a_block, env):
    for v in this.value:
        a_block.smalltalk_send('value:', [v], env)

    return this

def array_push(this, element, env):
    this.value.append(element)
    return this

env.vars['Array'].handlers = {
    'init:': value_init(list),
    'init': value_init(list),
    'asString': lambda this, env: smalltalk_string('#(%s)' % ' '.join([value.smalltalk_send('asString', [], env).value for value in this.value]), env),
    'each:': array_each,
    'push:': array_push
}


def block_closure_value(this, *values_and_env):
    values, env = values_and_env[:-1], values_and_env[-1]  # what is wrong with you python
    if len(this.args) != len(values):
        raise MessageArgCountError('Wrong number of arguments: expected %d got %d' %
                                   (len(this.args), len(values)))

    vars = {arg: value for arg, value in zip(this.args, values)}
    handler_env = Env(env, vars)
    return Interpreter().a_eval(this.ast, handler_env)


def init_block(this, args, ast, env):
    this = this.smalltalk_send('new', [], env)
    this.args = args
    this.ast = ast
    return this

env.vars['BlockClosure'].klass.handlers = {
    'args:ast:': init_block,
}

env.vars['BlockClosure'].handlers = {
    'argumentsCount': lambda this, env: smalltalk_integer(len(this.args), env),
    'args': lambda this, env: smalltalk_array([smalltalk_string(arg, env) for arg in this.args]),
    'value': block_closure_value,
    'value:': block_closure_value,
    'value:value:': block_closure_value,
    'value:value:value:': block_closure_value,
    'valueWithArguments:': lambda this, args, env: block_closure_value(this, *(args + [env])),
    'asString': lambda this, env: smalltalk_string('^block^', env)
}

def gagrakacka_method_new(this, args, locals, ast, env):
    this = this.smalltalk_send('new', [], env)
    this.args, this.locals, this.ast = args, locals, ast
    return this

env.vars['GagrakackaMethod'].klass.handlers = {
    'args:locals:ast:': gagrakacka_method_new
}


def bytecode_method_init(this, method, env):
    this = this.smalltalk_send('new', [], env)
    this.data['method'] = method
    return this

env.vars['BytecodeMethod'].klass.handlers = {
    'lambda:': bytecode_method_init
}

env.vars['BytecodeMethod'].handlers = {
    'method': lambda this, env: this.data['method']
}


def init_from_dict(this, dict, env):
    this.value = [dict.keys(), dict.values()]
    return this


env.vars['Dictionary'].handlers = {
    'init': value_init(dict),
    'init:': init_from_dict,
    'keys': lambda this, env: smalltalk_array(this.value[0], env),
    'values': lambda this, env: smalltalk_array(this.value[1], env),
    'asString': lambda this, env: smalltalk_string('{\n%s\n}' % '\n'.join(
        ['%s: %s' % (key.smalltalk_send('asString', [], env).value, value.smalltalk_send('asString', [], env).value) for key, value in zip(this.value[0], this.value[1])]), env)

}


def load_file(filename, env):
    with open(filename, 'r') as f:
        source = f.read()
    ast = parser.parse_smalltalk(source)
    return Interpreter().a_eval(ast, env)


def shell():
    z = ''
    a = Interpreter()
    while z != 'quit':
        z = raw_input('> ').strip()
        if z != 'quit':
            shell_expr(a, z)


def shell_expr(a, expr):
    ast = parser.parse_smalltalk(expr)
    try:
        print(a.a_eval(ast, env).smalltalk_send('asString', [], env).value)
    except SmalltalkError, ex:
        print('error: %s' % str(ex))

load_file(os.path.join(os.path.abspath('.'), 'stl/boolean.st'), env)
load_file(os.path.join(os.path.abspath('.'), 'stl/array.st'), env)
shell()
