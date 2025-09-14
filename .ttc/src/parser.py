import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Token
from tora_ast import *
from errors import SyntaxError

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def current_token(self):
        """获取当前token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek_token(self):
        """查看下一个token"""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def advance(self):
        """移动到下一个token"""
        self.pos += 1

    def expect(self, type_):
        """期望下一个token是指定类型，否则抛出语法错误"""
        token = self.current_token()
        if token and token.type == type_:
            self.advance()
            return token
        else:
            expected = f"Expected {type_}, got {token.type if token else 'EOF'}"
            line = token.line if token else None
            column = token.column if token else None
            raise SyntaxError(expected, line, column)

    def parse_program(self):
        """解析整个程序"""
        statements = []
        while self.current_token() is not None and self.current_token().type != "EOF":
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        """解析语句"""
        token = self.current_token()
        if token is None or token.type == "EOF":
            return None
            
        if token.type == "LET":
            return self.parse_let_statement()
        elif token.type == "FN":
            return self.parse_function_statement()
        elif token.type == "IF":
            return self.parse_if_statement()
        elif token.type == "WHILE":
            return self.parse_while_statement()
        elif token.type == "FOR":
            return self.parse_for_statement()
        elif token.type == "PRINT" or token.type == "PRINTLN":
            return self.parse_print_statement()
        elif token.type == "RETURN":
            return self.parse_return_statement()
        else:
            # 检查是否是赋值语句
            if self.peek_token() and self.peek_token().type == "ASSIGN":
                return self.parse_assignment_statement()
            else:
                # 默认为表达式语句
                expr = self.parse_expression()
                self.expect("SEMICOLON")
                return ExpressionStatement(expr)

    def parse_let_statement(self):
        """解析变量声明语句：let <变量名>[: 类型] = <表达式>;"""
        self.expect("LET")
        identifier = self.expect("IDENTIFIER")
        
        # 可选的类型注解
        type_annotation = None
        if self.current_token() and self.current_token().type == "COLON":
            self.advance()
            type_annotation = self.parse_type()
        
        self.expect("ASSIGN")
        expression = self.parse_expression()
        self.expect("SEMICOLON")
        
        return LetStatement(identifier.value, type_annotation, expression)

    def parse_function_statement(self):
        """解析函数声明语句：fn <函数名>(<参数>)[: 返回类型] { <函数体> }"""
        self.expect("FN")
        name = self.expect("IDENTIFIER")
        
        # 解析参数列表
        self.expect("LPAREN")
        parameters = []
        if self.current_token() and self.current_token().type != "RPAREN":
            parameters.append(self.parse_parameter())
            while self.current_token() and self.current_token().type == "COMMA":
                self.advance()
                parameters.append(self.parse_parameter())
        self.expect("RPAREN")
        
        # 可选的返回类型
        return_type = None
        if self.current_token() and self.current_token().type == "COLON":
            self.advance()
            return_type = self.parse_type()
        
        # 解析函数体
        self.expect("LBRACE")
        body = []
        while self.current_token() and self.current_token().type != "RBRACE":
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        self.expect("RBRACE")
        
        return FunctionStatement(name.value, parameters, return_type, body)

    def parse_parameter(self):
        """解析函数参数"""
        identifier = self.expect("IDENTIFIER")
        return identifier.value

    def parse_type(self):
        """解析类型"""
        # 简单实现，只支持基本类型
        token = self.current_token()
        if token and token.type == "IDENTIFIER":
            self.advance()
            return token.value
        else:
            raise SyntaxError(f"Expected type, got {token.type if token else 'EOF'}", token.line if token else None, token.column if token else None)

    def parse_if_statement(self):
        """解析if语句：if <条件> { <then_body> } [else { <else_body> }]"""
        self.expect("IF")
        self.expect("LPAREN")
        condition = self.parse_expression()
        self.expect("RPAREN")
        
        # 解析then_body
        self.expect("LBRACE")
        then_body = []
        while self.current_token() and self.current_token().type != "RBRACE":
            stmt = self.parse_statement()
            if stmt is not None:
                then_body.append(stmt)
        self.expect("RBRACE")
        
        # 解析可选的else_body
        else_body = None
        if self.current_token() and self.current_token().type == "ELSE":
            self.advance()
            self.expect("LBRACE")
            else_body = []
            while self.current_token() and self.current_token().type != "RBRACE":
                stmt = self.parse_statement()
                if stmt is not None:
                    else_body.append(stmt)
            self.expect("RBRACE")
        
        return IfStatement(condition, Program(then_body), Program(else_body) if else_body else None)

    def parse_while_statement(self):
        """解析while语句：while <条件> { <body> }"""
        self.expect("WHILE")
        # 可选的括号
        if self.current_token() and self.current_token().type == "LPAREN":
            self.advance()
            condition = self.parse_expression()
            self.expect("RPAREN")
        else:
            condition = self.parse_expression()
        
        # 解析body
        self.expect("LBRACE")
        body = []
        while self.current_token() and self.current_token().type != "RBRACE":
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        self.expect("RBRACE")
        
        return WhileStatement(condition, Program(body))

    def parse_for_statement(self):
        """解析for语句：for <变量> in <可迭代对象> { <body> }"""
        self.expect("FOR")
        identifier = self.expect("IDENTIFIER")
        
        # 简化实现，假设in关键字存在
        if self.current_token() and self.current_token().type == "IDENTIFIER" and self.current_token().value == "in":
            self.advance()
        iterable = self.parse_expression()
        
        # 解析body
        self.expect("LBRACE")
        body = []
        while self.current_token() and self.current_token().type != "RBRACE":
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
        self.expect("RBRACE")
        
        return ForStatement(identifier.value, iterable, Program(body))

    def parse_print_statement(self):
        """解析打印语句：print(<表达式>); 或 println(<表达式>);"""
        token = self.current_token()
        newline = token.type == "PRINTLN"
        self.advance()
        self.expect("LPAREN")
        expression = self.parse_expression()
        self.expect("RPAREN")
        self.expect("SEMICOLON")
        
        return PrintStatement(expression, newline)

    def parse_return_statement(self):
        """解析返回语句：return <表达式>;"""
        self.expect("RETURN")
        expression = self.parse_expression()
        self.expect("SEMICOLON")
        return ExpressionStatement(expression)

    def parse_assignment_statement(self):
        """解析赋值语句：<标识符> = <表达式>;"""
        identifier = self.expect("IDENTIFIER")
        self.expect("ASSIGN")
        expression = self.parse_expression()
        self.expect("SEMICOLON")
        return AssignmentStatement(identifier.value, expression)

    def parse_expression(self):
        """解析表达式（简化版，只处理加法和乘法）"""
        return self.parse_relational_expression()

    def parse_relational_expression(self):
        """解析关系表达式"""
        left = self.parse_additive_expression()
        
        while self.current_token() and self.current_token().type in ["EQUALS", "NOT_EQUALS", "LESS_EQUAL", "GREATER_EQUAL", "LESS_THAN", "GREATER_THAN"]:
            operator = self.current_token().type
            self.advance()
            right = self.parse_additive_expression()
            left = BinaryOperation(operator, left, right)
        
        return left

    def parse_additive_expression(self):
        """解析加法表达式"""
        left = self.parse_multiplicative_expression()
        
        while self.current_token() and self.current_token().type in ["PLUS", "MINUS"]:
            operator = self.current_token().type
            self.advance()
            right = self.parse_multiplicative_expression()
            left = BinaryOperation(operator, left, right)
        
        return left

    def parse_multiplicative_expression(self):
        """解析乘法表达式"""
        left = self.parse_primary_expression()
        
        while self.current_token() and self.current_token().type in ["MULTIPLY", "DIVIDE"]:
            operator = self.current_token().type
            self.advance()
            right = self.parse_primary_expression()
            left = BinaryOperation(operator, left, right)
        
        return left

    def parse_primary_expression(self):
        """解析基本表达式"""
        token = self.current_token()
        
        if token is None or token.type == "EOF":
            raise SyntaxError("Unexpected end of input")
        elif token.type == "NUMBER":
            self.advance()
            return NumberLiteral(float(token.value) if '.' in token.value else int(token.value))
        elif token.type == "STRING":
            self.advance()
            # 移除引号
            value = token.value[1:-1]
            return StringLiteral(value)
        elif token.type == "IDENTIFIER":
            # 检查是否是函数调用
            if self.peek_token() and self.peek_token().type == "LPAREN":
                return self.parse_function_call()
            else:
                self.advance()
                return Identifier(token.value)
        elif token.type == "LPAREN":
            self.advance()
            expr = self.parse_expression()
            self.expect("RPAREN")
            return expr
        elif token.type == "LBRACKET":
            return self.parse_list_literal()
        else:
            raise SyntaxError(f"Unexpected token {token.type}", token.line, token.column)

    def parse_function_call(self):
        """解析函数调用：identifier(<参数列表>)"""
        identifier = self.expect("IDENTIFIER")
        self.expect("LPAREN")
        
        arguments = []
        if self.current_token() and self.current_token().type != "RPAREN":
            arguments.append(self.parse_expression())
            while self.current_token() and self.current_token().type == "COMMA":
                self.advance()
                arguments.append(self.parse_expression())
        
        self.expect("RPAREN")
        return FunctionCall(identifier.value, arguments)

    def parse_list_literal(self):
        """解析列表字面量：[<元素列表>]"""
        self.expect("LBRACKET")
        
        elements = []
        if self.current_token() and self.current_token().type != "RBRACKET":
            elements.append(self.parse_expression())
            while self.current_token() and self.current_token().type == "COMMA":
                self.advance()
                elements.append(self.parse_expression())
        
        self.expect("RBRACKET")
        return ListLiteral(elements)