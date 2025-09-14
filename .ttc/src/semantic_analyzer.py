import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tora_ast import *
from errors import SemanticError
from stdlib import get_builtin_constants

class SemanticAnalyzer:
    def __init__(self):
        # 全局符号表
        self.symbol_table = {}
        # 当前作用域符号表
        self.scope_stack = [{}]
        # 内置常量
        self.builtin_constants = get_builtin_constants()
        # 声明内置常量
        for name in self.builtin_constants:
            self.declare_symbol(name, "constant")
        # 内置函数
        from stdlib import get_builtin_functions
        self.builtin_functions = get_builtin_functions()
        # 声明内置函数
        for name in self.builtin_functions:
            self.declare_symbol(name, "function")

    def enter_scope(self):
        """进入新的作用域"""
        self.scope_stack.append({})

    def exit_scope(self):
        """退出当前作用域"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def declare_symbol(self, name, symbol_type):
        """在当前作用域声明符号"""
        current_scope = self.scope_stack[-1]
        if name in current_scope:
            raise SemanticError(f"Symbol '{name}' already declared in current scope")
        current_scope[name] = symbol_type

    def lookup_symbol(self, name):
        """查找符号，从内到外搜索作用域"""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None

    def analyze(self, node):
        """分析AST节点"""
        if isinstance(node, Program):
            return self.analyze_program(node)
        elif isinstance(node, LetStatement):
            return self.analyze_let_statement(node)
        elif isinstance(node, FunctionStatement):
            return self.analyze_function_statement(node)
        elif isinstance(node, IfStatement):
            return self.analyze_if_statement(node)
        elif isinstance(node, WhileStatement):
            return self.analyze_while_statement(node)
        elif isinstance(node, ForStatement):
            return self.analyze_for_statement(node)
        elif isinstance(node, PrintStatement):
            return self.analyze_print_statement(node)
        elif isinstance(node, ExpressionStatement):
            return self.analyze_expression_statement(node)
        elif isinstance(node, BinaryOperation):
            return self.analyze_binary_operation(node)
        elif isinstance(node, FunctionCall):
            return self.analyze_function_call(node)
        elif isinstance(node, Identifier):
            return self.analyze_identifier(node)
        # 其他节点类型不需要特殊处理
        return node

    def analyze_program(self, node):
        """分析程序节点"""
        for statement in node.children:
            self.analyze(statement)
        return node

    def analyze_let_statement(self, node):
        """分析变量声明语句"""
        # 检查变量是否已声明
        if self.lookup_symbol(node.value) is not None:
            # 检查是否在同一作用域中声明
            current_scope = self.scope_stack[-1]
            if node.value in current_scope:
                raise SemanticError(f"Variable '{node.value}' already declared")
        
        # 声明变量
        var_type = "unknown"  # 简化处理，实际应该推断类型
        if node.type_annotation:
            var_type = node.type_annotation
        self.declare_symbol(node.value, var_type)
        
        # 分析表达式
        if node.children:
            self.analyze(node.children[0])
        
        return node

    def analyze_function_statement(self, node):
        """分析函数声明语句"""
        # 检查函数是否已声明
        if self.lookup_symbol(node.value) is not None:
            raise SemanticError(f"Function '{node.value}' already declared")
        
        # 声明函数
        self.declare_symbol(node.value, "function")
        
        # 进入函数作用域
        self.enter_scope()
        
        # 声明参数
        for param_name, param_type in node.parameters:
            self.declare_symbol(param_name, param_type)
        
        # 分析函数体
        if node.body:
            for statement in node.body:
                self.analyze(statement)
        
        # 退出函数作用域
        self.exit_scope()
        
        return node

    def analyze_if_statement(self, node):
        """分析if语句"""
        # 分析条件表达式
        self.analyze(node.condition)
        
        # 分析then_body
        self.analyze(node.then_body)
        
        # 分析else_body（如果存在）
        if node.else_body:
            self.analyze(node.else_body)
        
        return node

    def analyze_while_statement(self, node):
        """分析while语句"""
        # 分析条件表达式
        self.analyze(node.condition)
        
        # 分析循环体
        self.analyze(node.body)
        
        return node

    def analyze_for_statement(self, node):
        """分析for语句"""
        # 声明循环变量
        self.declare_symbol(node.value, "unknown")
        
        # 分析可迭代对象
        self.analyze(node.iterable)
        
        # 分析循环体
        self.analyze(node.body)
        
        return node

    def analyze_print_statement(self, node):
        """分析打印语句"""
        # 分析表达式
        self.analyze(node.expression)
        
        return node

    def analyze_expression_statement(self, node):
        """分析表达式语句"""
        # 分析表达式
        self.analyze(node.expression)
        
        return node

    def analyze_binary_operation(self, node):
        """分析二元操作"""
        # 分析左右操作数
        self.analyze(node.left)
        self.analyze(node.right)
        
        return node

    def analyze_function_call(self, node):
        """分析函数调用"""
        # 检查函数是否存在
        func_type = self.lookup_symbol(node.function)
        if func_type is None:
            raise SemanticError(f"Function '{node.function}' not declared")
        if func_type != "function":
            raise SemanticError(f"'{node.function}' is not a function")
        
        # 分析参数
        for arg in node.arguments:
            self.analyze(arg)
        
        return node

    def analyze_identifier(self, node):
        """分析标识符"""
        # 检查标识符是否已声明
        if self.lookup_symbol(node.value) is None:
            # 检查是否是内置常量
            if node.value in self.builtin_constants:
                return node
            raise SemanticError(f"Variable '{node.value}' not declared")
        
        return node