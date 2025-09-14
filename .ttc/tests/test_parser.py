import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from lexer import lexer
from parser import Parser
from tora_ast import *

class TestParser(unittest.TestCase):
    def test_parse_let_statement(self):
        """Test parsing let statements"""
        code = "let x = 42;"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, LetStatement)
        self.assertEqual(stmt.identifier.value, "x")
        self.assertIsInstance(stmt.expression, NumberLiteral)
        self.assertEqual(stmt.expression.value, 42)
    
    def test_parse_function_call(self):
        """Test parsing function calls"""
        code = "print(\"Hello\");"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, ExpressionStatement)
        self.assertIsInstance(stmt.expression, FunctionCall)
        self.assertEqual(stmt.expression.function_name.value, "print")
        self.assertEqual(len(stmt.expression.arguments), 1)
        self.assertIsInstance(stmt.expression.arguments[0], StringLiteral)
    
    def test_parse_binary_expression(self):
        """Test parsing binary expressions"""
        code = "let x = 1 + 2 * 3;"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, LetStatement)
        self.assertIsInstance(stmt.expression, BinaryOperation)
        # Check operator precedence: * should be evaluated before +
        self.assertEqual(stmt.expression.operator, "+")
        self.assertIsInstance(stmt.expression.left, NumberLiteral)
        self.assertEqual(stmt.expression.left.value, 1)
        self.assertIsInstance(stmt.expression.right, BinaryOperation)
        self.assertEqual(stmt.expression.right.operator, "*")
    
    def test_parse_list_literal(self):
        """Test parsing list literals"""
        code = "let arr = [1, 2, 3];"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, LetStatement)
        self.assertIsInstance(stmt.expression, ListLiteral)
        self.assertEqual(len(stmt.expression.elements), 3)
        for i, element in enumerate(stmt.expression.elements):
            self.assertIsInstance(element, NumberLiteral)
            self.assertEqual(element.value, i + 1)
    
    def test_parse_assignment_statement(self):
        """Test parsing assignment statements"""
        code = "x = 10;"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AssignmentStatement)
        self.assertEqual(stmt.identifier.value, "x")
        self.assertIsInstance(stmt.expression, NumberLiteral)
        self.assertEqual(stmt.expression.value, 10)
    
    def test_parse_while_loop(self):
        """Test parsing while loops"""
        code = "while x < 10 { x = x + 1; }"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, WhileStatement)
        self.assertIsInstance(stmt.condition, BinaryOperation)
        self.assertEqual(stmt.condition.operator, "<")
        self.assertEqual(len(stmt.body.statements), 1)
        self.assertIsInstance(stmt.body.statements[0], AssignmentStatement)

if __name__ == '__main__':
    unittest.main()