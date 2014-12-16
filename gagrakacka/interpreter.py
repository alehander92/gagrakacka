from smalltalk_atom_converters import smalltalk_integer, smalltalk_string, smalltalk_symbol, smalltalk_array
from smalltalk_ast import Return

class Interpreter(object):

    def a_eval(self, node, env):
        # print('EVAL %s' % str(type(node).__name__.lower()), node.__dict__)
        return getattr(self, 'a_eval_%s' % str(type(node).__name__.lower()))(node, env)

    def a_eval_program(self, children, env):
        result = None
        for child in children.children:
            result = self.a_eval(child, env)
            if isinstance(child, Return):
                return result
        return result or env['Nil']

    def a_eval_integer(self, integer, env):
        if 0 <= integer.value < 257:
            return env.root.vars['__integerCache'][integer.value]
        else:
            return smalltalk_integer(integer.value, env)

    def a_eval_string(self, string, env):
        return smalltalk_string(string.value, env)

    def a_eval_label(self, label, env):
        return env[label.label]

    def a_eval_message(self, message, env):
        receiver = self.a_eval(message.receiver, env)
        args = [self.a_eval(arg, env) for arg in message.args]
        return receiver.smalltalk_send(message.message, args, env)

    def a_eval_block(self, block, env):
        args = block.args
        ast = block.ast
        return env['BlockClosure'].smalltalk_send('args:ast:', [args, ast], env)

    def a_eval_assignment(self, assignment, env):
        env[assignment.cell.label] = self.a_eval(assignment.value, env)
        return env[assignment.cell.label]

    def a_eval_symbol(self, symbol, env):
        return smalltalk_symbol(symbol.value, env)

    def a_eval_classdefinition(self, class_definition, env):
        if not class_definition.is_class:
            klass = env[class_definition.name]
        else:
            klass = env[class_definition.name].klass
        for definition in class_definition.definitions:
            klass.handlers[
                definition.pattern.message] = self.a_eval_methoddefinition(definition, env)
        return klass

    def a_eval_methoddefinition(self, method_definition, env):
        args = method_definition.pattern.args
        return env['GagrakackaMethod'].smalltalk_send('args:locals:ast:', [args, method_definition.locals, method_definition.code], env)

    def a_eval_return(self, return_statement, env):
        return self.a_eval(return_statement.expr, env)

    def a_eval_list(self, list, env):
        return smalltalk_array([self.a_eval(value, env) for value in list.values], env)
