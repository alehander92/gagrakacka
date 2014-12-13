from parsimonious import Grammar
import smalltalk_ast

def parse_smalltalk(source):
    parsed = GagrakackaGrammar.parse(source)
    return Converter().convert(parsed)


GagrakackaGrammar = Grammar('''
p = (expression '.'? ws?)*
expression = assignment / message / number / string / label / block / list
pure_expression = number / string / label / block / list
assignable = message / number / string / label / block / list
assignment = label ws? ':=' ws? assignable
number = float / integer
float = ~"[0-9]+"i "." ~"[0-9]+"i
integer = ~"[0-9]+"i
label = ~"[a-zA-Z\-\?]+"i
string = "'" t "'"
t = ~"[^\\']*"i
block = '[' (arg ws?)* '|' ws? (expression '.'? ws?)* ']'
arg = ':' label
ws = ~"[ \\t\\n]+"i
list = '#(' (assignable ws?)* ')'
operator = '>=' / '<=' / '=' / '>' / '<' / '+' / '-' / '*' / '/' / '%' / '^' / '&' / '|' / '#'
message = binary / keyword / unary
binary = pure_expression ws operator ws pure_expression
keyword = pure_expression ws (label ':' ws? pure_expression ws?)+
unary = pure_expression ws label
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
		message = node.children[2].text
		out = smalltalk_ast.Message(receiver, message, [])
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
		ast = smalltalk_ast.Program([self.convert_child(child.children[0].children[0]) for child in node.children[4]])
		out = smalltalk_ast.Block(args, ast)
		return out


	def convert_binary(self, node):
		receiver = self.convert_child(node.children[0].children[0])
		message = node.children[2].text
		args = [self.convert_child(node.children[4].children[0])]
		return smalltalk_ast.Message(receiver, message, args)
