class ASTNode:
    """
    抽象语法树（AST）节点基类。
    每个节点包含类型、值和子节点。
    """
    def __init__(self, type_, value=None, children=None):
        self.type = type_
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        return f"ASTNode({self.type}, {self.value}, {self.children})"

# 表达式节点
class Expression(ASTNode):
    pass

# 语句节点
class Statement(ASTNode):
    pass

# 程序节点
class Program(ASTNode):
    def __init__(self, statements=None):
        super().__init__("PROGRAM", None, statements)

# 变量声明节点
class LetStatement(Statement):
    def __init__(self, identifier, type_annotation=None, expression=None):
        children = [expression] if expression else []
        super().__init__("LET", identifier, children)
        self.type_annotation = type_annotation

# 函数声明节点
class FunctionStatement(Statement):
    def __init__(self, name, parameters, return_type=None, body=None):
        children = parameters + (body if body else [])
        super().__init__("FN", name, children)
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

# if语句节点
class IfStatement(Statement):
    def __init__(self, condition, then_body, else_body=None):
        children = [condition, then_body]
        if else_body:
            children.append(else_body)
        super().__init__("IF", None, children)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

# while循环节点
class WhileStatement(Statement):
    def __init__(self, condition, body):
        super().__init__("WHILE", None, [condition, body])
        self.condition = condition
        self.body = body

# for循环节点
class ForStatement(Statement):
    def __init__(self, identifier, iterable, body):
        super().__init__("FOR", identifier, [iterable, body])
        self.iterable = iterable
        self.body = body

# 表达式语句节点
class ExpressionStatement(Statement):
    def __init__(self, expression):
        super().__init__("EXPRESSION_STATEMENT", None, [expression])
        self.expression = expression

# 赋值语句节点
class AssignmentStatement(Statement):
    def __init__(self, identifier, expression):
        super().__init__("ASSIGNMENT", identifier, [expression])
        self.identifier = identifier
        self.expression = expression

# 标识符节点
class Identifier(Expression):
    def __init__(self, value):
        super().__init__("IDENTIFIER", value)

# 数字字面量节点
class NumberLiteral(Expression):
    def __init__(self, value):
        super().__init__("NUMBER", value)

# 字符串字面量节点
class StringLiteral(Expression):
    def __init__(self, value):
        super().__init__("STRING", value)

# 二元操作节点
class BinaryOperation(Expression):
    def __init__(self, operator, left, right):
        super().__init__("BINARY_OPERATION", operator, [left, right])
        self.operator = operator
        self.left = left
        self.right = right

# 函数调用节点
class FunctionCall(Expression):
    def __init__(self, function, arguments):
        super().__init__("FUNCTION_CALL", function, arguments)
        self.function = function
        self.arguments = arguments

# 列表字面量节点
class ListLiteral(Expression):
    def __init__(self, elements):
        super().__init__("LIST_LITERAL", None, elements)
        self.elements = elements

# 打印语句节点
class PrintStatement(Statement):
    def __init__(self, expression, newline=True):
        super().__init__("PRINT" if not newline else "PRINTLN", None, [expression])
        self.expression = expression
        self.newline = newline