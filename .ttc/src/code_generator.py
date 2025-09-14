import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tora_ast import *
from stdlib import generate_stdlib_code, get_builtin_functions, get_builtin_constants

class CodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.builtin_functions = get_builtin_functions()
        self.builtin_constants = get_builtin_constants()

    def indent(self):
        """增加缩进"""
        self.indent_level += 1

    def dedent(self):
        """减少缩进"""
        self.indent_level -= 1

    def get_indent(self):
        """获取当前缩进字符串"""
        return "    " * self.indent_level

    def generate(self, node):
        """生成代码"""
        if isinstance(node, Program):
            return self.generate_program(node)
        elif isinstance(node, LetStatement):
            return self.generate_let_statement(node)
        elif isinstance(node, FunctionStatement):
            return self.generate_function_statement(node)
        elif isinstance(node, IfStatement):
            return self.generate_if_statement(node)
        elif isinstance(node, WhileStatement):
            return self.generate_while_statement(node)
        elif isinstance(node, ForStatement):
            return self.generate_for_statement(node)
        elif isinstance(node, PrintStatement):
            return self.generate_print_statement(node)
        elif isinstance(node, ExpressionStatement):
            return self.generate_expression_statement(node)
        elif isinstance(node, AssignmentStatement):
            return self.generate_assignment_statement(node)
        elif isinstance(node, BinaryOperation):
            return self.generate_binary_operation(node)
        elif isinstance(node, FunctionCall):
            return self.generate_function_call(node)
        elif isinstance(node, Identifier):
            return self.generate_identifier(node)
        elif isinstance(node, NumberLiteral):
            return self.generate_number_literal(node)
        elif isinstance(node, StringLiteral):
            return self.generate_string_literal(node)
        elif isinstance(node, ListLiteral):
            return self.generate_list_literal(node)
        else:
            raise ValueError(f"Unknown node type: {type(node)}")

    def generate_program(self, node):
        """生成程序代码"""
        code = []
        
        # 添加标准库代码
        stdlib_code = generate_stdlib_code()
        if stdlib_code:
            code.append(stdlib_code)
        
        # 添加空行以提高可读性
        code.append("")
        
        for statement in node.children:
            generated = self.generate(statement)
            if generated:
                code.append(generated)
        return "\n".join(code)

    def generate_let_statement(self, node):
        """生成变量声明语句"""
        indent = self.get_indent()
        if node.children:
            expr_code = self.generate(node.children[0])
            return f"{indent}{node.value} = {expr_code}"
        else:
            return f"{indent}{node.value} = None"

    def generate_function_statement(self, node):
        """生成函数声明语句"""
        indent = self.get_indent()
        code = [f"{indent}def {node.value}("]
        
        # 添加参数
        params = [param[0] for param in node.parameters]
        code[0] += ", ".join(params) + "):"
        
        # 生成函数体
        self.indent()
        if node.body:
            for statement in node.body:
                code.append(self.generate(statement))
        else:
            code.append(f"{self.get_indent()}pass")
        self.dedent()
        
        return "\n".join(code)

    def generate_if_statement(self, node):
        """生成if语句"""
        indent = self.get_indent()
        code = []
        
        # 生成if条件
        condition_code = self.generate(node.condition)
        code.append(f"{indent}if {condition_code}:")
        
        # 生成then_body
        self.indent()
        if node.then_body.children:
            for statement in node.then_body.children:
                code.append(self.generate(statement))
        else:
            code.append(f"{self.get_indent()}pass")
        self.dedent()
        
        # 生成else_body（如果存在）
        if node.else_body and node.else_body.children:
            code.append(f"{indent}else:")
            self.indent()
            for statement in node.else_body.children:
                code.append(self.generate(statement))
            self.dedent()
        
        return "\n".join(code)

    def generate_while_statement(self, node):
        """生成while语句"""
        indent = self.get_indent()
        code = []
        
        # 生成while条件
        condition_code = self.generate(node.condition)
        code.append(f"{indent}while {condition_code}:")
        
        # 生成循环体
        self.indent()
        if node.body.children:
            for statement in node.body.children:
                code.append(self.generate(statement))
        else:
            code.append(f"{self.get_indent()}pass")
        self.dedent()
        
        return "\n".join(code)

    def generate_for_statement(self, node):
        """生成for语句"""
        indent = self.get_indent()
        code = []
        
        # 生成for语句（简化为for-in循环）
        iterable_code = self.generate(node.iterable)
        code.append(f"{indent}for {node.value} in {iterable_code}:")
        
        # 生成循环体
        self.indent()
        if node.body.children:
            for statement in node.body.children:
                code.append(self.generate(statement))
        else:
            code.append(f"{self.get_indent()}pass")
        self.dedent()
        
        return "\n".join(code)

    def generate_print_statement(self, node):
        """生成打印语句"""
        indent = self.get_indent()
        expr_code = self.generate(node.expression)
        if node.newline:
            return f"{indent}print({expr_code})"
        else:
            return f"{indent}print({expr_code}, end='')"

    def generate_expression_statement(self, node):
        """生成表达式语句"""
        indent = self.get_indent()
        expr_code = self.generate(node.expression)
        return f"{indent}{expr_code}"

    def generate_assignment_statement(self, node):
        """生成赋值语句"""
        indent = self.get_indent()
        expr_code = self.generate(node.expression)
        return f"{indent}{node.identifier} = {expr_code}"

    def generate_binary_operation(self, node):
        """生成二元操作"""
        left_code = self.generate(node.left)
        right_code = self.generate(node.right)
        
        # 映射操作符
        op_map = {
            "PLUS": "+",
            "MINUS": "-",
            "MULTIPLY": "*",
            "DIVIDE": "/",
            "EQUALS": "==",
            "NOT_EQUALS": "!=",
            "LESS_EQUAL": "<=",
            "GREATER_EQUAL": ">=",
            "LESS_THAN": "<",
            "GREATER_THAN": ">"
        }
        
        op = op_map.get(node.operator, node.operator)
        
        # 特殊处理字符串连接
        if node.operator == "PLUS":
            # 检查是否是数字加法
            left_node = node.left
            right_node = node.right
            # 如果两个操作数都是数字或标识符（可能是数字变量），则使用普通加法
            if ((isinstance(left_node, NumberLiteral) or isinstance(left_node, Identifier)) and
                (isinstance(right_node, NumberLiteral) or isinstance(right_node, Identifier))):
                return f"({left_code} {op} {right_code})"
            
            # 否则使用字符串连接
            # 检查是否已经包含str()调用
            if left_code.startswith("str(") and left_code.endswith(")"):
                left_wrapped = left_code
            else:
                left_wrapped = f"str({left_code})"
            
            if right_code.startswith("str(") and right_code.endswith(")"):
                right_wrapped = right_code
            else:
                right_wrapped = f"str({right_code})"
            
            return f"{left_wrapped} + {right_wrapped}"
        
        return f"({left_code} {op} {right_code})"

    def generate_function_call(self, node):
        """生成函数调用"""
        args_code = []
        for arg in node.arguments:
            args_code.append(self.generate(arg))
        args_str = ", ".join(args_code)
        
        # 检查是否是内置函数
        if node.function in self.builtin_functions:
            # 对于内置函数，直接使用映射的Python函数
            python_function = self.builtin_functions[node.function]
            # 特殊处理print和println
            if node.function in ["print", "println"]:
                if node.function == "print":
                    return f"print({args_str}, end='')"
                else:
                    return f"print({args_str})"
            # 特殊处理push函数（Python中是append）
            elif node.function == "push":
                if len(node.arguments) == 2:
                    list_expr = self.generate(node.arguments[0])
                    item_expr = self.generate(node.arguments[1])
                    return f"{list_expr}.append({item_expr})"
                else:
                    raise ValueError("push function requires exactly 2 arguments")
            else:
                # 特殊处理lambda函数调用
                if python_function.startswith("lambda"):
                    # 对于lambda函数，直接调用
                    return f"({python_function})({args_str})"
                else:
                    # 特殊处理random模块的函数
                    if python_function.startswith("random_module."):
                        return f"{python_function[len('random_module.'):]}({args_str})"
                    else:
                        return f"{python_function}({args_str})"
        else:
            # 用户定义的函数
            return f"{node.function}({args_str})"

    def generate_identifier(self, node):
        """生成标识符"""
        # 检查是否是内置常量
        if node.value in self.builtin_constants:
            return self.builtin_constants[node.value]
        return node.value

    def generate_number_literal(self, node):
        """生成数字字面量"""
        return str(node.value)

    def generate_string_literal(self, node):
        """生成字符串字面量"""
        # 使用repr来正确处理转义字符
        return repr(node.value)

    def generate_list_literal(self, node):
        """生成列表字面量"""
        elements_code = []
        for element in node.elements:
            element_code = self.generate(element)
            # 特殊处理布尔常量
            if element_code == "true":
                element_code = "True"
            elif element_code == "false":
                element_code = "False"
            elements_code.append(element_code)
        elements_str = ", ".join(elements_code)
        return f"[{elements_str}]"