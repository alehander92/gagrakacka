from parsimonious import Grammar
import smalltalk_ast


def parse_smalltalk(source):
    parsed = GagrakackaGrammar.parse(source)
    return Converter().convert(parsed)


GagrakackaGrammar = Grammar('''
p = (expression '.'? ws?)*
expression = assignment / extend / message / number / symbol / string / label / block / list / parened / return
pure_expression = number / symbol / string / label / block / list / parened
a_expression = keyword / unary / number / symbol / string / label / block / list / parened
assignable = message / number / symbol / string / label / block / list / parened
assignment = label ws? ':=' ws? assignable
parened = '(' expression ws? ')'
number = float / integer
float = ~"[0-9]+"i "." ~"[0-9]+"i
integer = ~"[0-9]+"i
label = ~"[a-zA-Z\_\?]+"i
symbol = "#" label
string = "'" t "'"
t = ~"[^\\']*"i
block = '[' (arg ws?)* '|'? ws? (expression '.'? ws?)* ']'
arg = ':' label
ws = ~"[ \\t\\n]+"i
list = '#(' (list_element ws?)* ')'
list_element = number / string / list
extend = label (ws 'class')? ws 'extend' ws '[' ws method_definition* ']'
method_definition = pattern ws? method_block ws?
pattern = keyword_pattern / unary_pattern / binary_pattern
keyword_pattern = (label ':' ws? pure_expression ws?)+
return = '^' ws assignable
unary_pattern = ~"[a-zA-Z\_\?]+"i
binary_pattern = operator ws label
method_block = '[' ws? local_definition? ws? (expression '.'? ws?)* ']'
local_definition = '|' ws? (label ws?)* '|'
operator = '>=' / '<=' / '=' / '>' / '<' / '+' / '-' / '*' / '/' / '%' / '^' / '&' / '|' / '#'
message = keyword / unary / binary
binary = pure_expression ws (operator ws a_expression ws?)*
keyword = pure_expression ws (label ':' ws? pure_expression ws?)+
unary = pure_expression (ws label)+
''')


class Converter(object):

    def convert(self, sexp):
        return self.convert_code(sexp.children)

    def convert_code(self, expressions):
        return smalltalk_ast.Program([self.convert_child(expr.children[0]) for expr in expressions])

    def convert_child(self, child):
        return getattr(self, 'convert_' + child.expr_name)(child)

    def convert_expression(self, expr):
        return self.convert_child(expr.children[0])

    def convert_pure_expression(self, pure_expr):
        return self.convert_child(pure_expr.children[0])

    def convert_label(self, label):
        return smalltalk_ast.Label(label.text)

    def convert_integer(self, value):
        return smalltalk_ast.Integer(int(value.text))

    def convert_string(self, value):
        return smalltalk_ast.String(value.text[1:-1])

    def convert_number(self, number):
        return self.convert_child(number.children[0])

    def convert_message(self, message):
        return self.convert_child(message.children[0])

    def convert_unary(self, node):
        receiver = self.convert_child(node.children[0])
        messages = [child.children[1].text for child in node.children[1]]
        out = receiver
        for m in messages:
            out = smalltalk_ast.Message(out, m, [])

        return out

    def convert_keyword(self, node):
        receiver = self.convert_child(node.children[0])
        words = [child.children[0].text for child in node.children[2]]
        message = ':'.join(words) + ':'
        args = [self.convert_child(child.children[3]) for child in node.children[2]]
        end = smalltalk_ast.Message(receiver, message, args)
        return end

    def convert_assignable(self, node):
        return self.convert_child(node.children[0])

    def convert_assignment(self, node):
        cell = self.convert_child(node.children[0])
        value = self.convert_child(node.children[4].children[0])
        return smalltalk_ast.Assignment(cell, value)

    def convert_list(self, node):
        cells = [self.convert_child(child.children[0].children[0]) for child in node.children[1]]
        return smalltalk_ast.List(cells)

    def convert_block(self, node):
        args = [child.children[0].children[1].text for child in node.children[1]]
        ast = smalltalk_ast.Program(
            [self.convert_child(child.children[0].children[0]) for child in node.children[4]])
        out  = smalltalk_ast.Block(args, ast)
        return out

    def convert_binary(self, node):
        receiver = self.convert_child(node.children[0].children[0])
        messages = [child.children[0].text for child in node.children[2].children]
        args = [self.convert_child(child.children[2].children[0])
                for child in node.children[2].children]
        for m, a in zip(messages, args):
            receiver = smalltalk_ast.Message(receiver, m, [a])
        return receiver

    def convert_parened(self, node):
        return self.convert_child(node.children[1])

    def convert_symbol(self, node):
        return smalltalk_ast.Symbol(node.children[1].text)

    def convert_extend(self, node):
        name = node.children[0].text
        is_class = node.children[1].children != []
        definitions = [self.convert_child(child) for child in node.children[7]]
        return smalltalk_ast.ClassDefinition(name, is_class, definitions)

    def convert_local_definition(self, node):
        return [child.text for child in node.children]

    def convert_keyword_pattern(self, node):
        words = [child.children[0].text for child in node.children]
        message = ':'.join(words) + ':'
        args = [child.children[3].text for child in node.children]
        return smalltalk_ast.Message(None, message, args)

    def convert_unary_pattern(self, node):
        return smalltalk_ast.Message(None, node.text, [])

    def convert_binary_pattern(self, node):
        return smalltalk_ast.Message(None, node.children[0].text, [node.children[2].text])

    def convert_method_definition(self, node):
        pattern = self.convert_child(node.children[0].children[0])
        locals, code = self.convert_child(node.children[2])
        return smalltalk_ast.MethodDefinition(pattern, code, locals)

    def convert_method_block(self, node):
        locals = self.convert_local_definition(node.children[2])
        ast = smalltalk_ast.Program([self.convert_child(child.children[0].children[0]) for child in node.children[4]])
        return locals, ast

    def convert_return(self, node):
        return smalltalk_ast.Return(self.convert_child(node.children[2]))

