def smalltalk_string(string, env):
    return env['String'].smalltalk_send('new:', [string], env)


def smalltalk_array(array, env):
    return env['Array'].smalltalk_send('new:', [array], env)


def smalltalk_dictionary(dictionary, env):
    return env['Dictionary'].smalltalk_send('new:', [dictionary], env)


def smalltalk_method(method, env):
    if isinstance(method, types.FunctionType):
        return env['BytecodeMethod'].smalltalk_send('lambda:', [method], env)
    else:
        return method


def smalltalk_symbol(symbol, env):
    return env['Symbol'].smalltalk_send('new:', [symbol], env)


def smalltalk_boolean(boolean, env):
    return env['true' if boolean else 'false']


def smalltalk_integer(value, env):
    return env['Integer'].smalltalk_send('new:', [value], env)

