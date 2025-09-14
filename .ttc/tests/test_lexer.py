import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from lexer import lexer, TOKEN_TYPES

class TestLexer(unittest.TestCase):
    def test_basic_tokens(self):
        """Test basic token recognition"""
        code = "let x = 42;"
        tokens = list(lexer(code))
        
        # Check that we have the expected tokens
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0].type, 'LET')
        self.assertEqual(tokens[1].type, 'IDENTIFIER')
        self.assertEqual(tokens[1].value, 'x')
        self.assertEqual(tokens[2].type, 'EQUALS')
        self.assertEqual(tokens[3].type, 'NUMBER')
        self.assertEqual(tokens[3].value, '42')
        self.assertEqual(tokens[4].type, 'SEMICOLON')
    
    def test_string_literals(self):
        """Test string literal tokenization"""
        code = '"Hello, World!"'
        tokens = list(lexer(code))
        
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, 'STRING')
        self.assertEqual(tokens[0].value, '"Hello, World!"')
    
    def test_operators(self):
        """Test operator tokenization"""
        code = "+ - * / = == != < > <= >="
        tokens = list(lexer(code))
        
        expected_types = ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'EQUALS', 
                         'EQUALITY', 'INEQUALITY', 'LESS_THAN', 'GREATER_THAN',
                         'LESS_EQUAL', 'GREATER_EQUAL']
        
        self.assertEqual(len(tokens), 11)
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_keywords(self):
        """Test keyword recognition"""
        code = "let fn if else while for"
        tokens = list(lexer(code))
        
        expected_types = ['LET', 'FN', 'IF', 'ELSE', 'WHILE', 'FOR']
        
        self.assertEqual(len(tokens), 6)
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_identifiers(self):
        """Test identifier recognition"""
        code = "variableName functionName _privateVar"
        tokens = list(lexer(code))
        
        self.assertEqual(len(tokens), 3)
        for token in tokens:
            self.assertEqual(token.type, 'IDENTIFIER')
    
    def test_numbers(self):
        """Test number recognition"""
        code = "42 3.14 -10"
        tokens = list(lexer(code))
        
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].type, 'NUMBER')
        self.assertEqual(tokens[0].value, '42')
        self.assertEqual(tokens[1].type, 'NUMBER')
        self.assertEqual(tokens[1].value, '3.14')
        self.assertEqual(tokens[2].type, 'NUMBER')
        self.assertEqual(tokens[2].value, '-10')
    
    def test_chinese_characters(self):
        """Test Chinese character support"""
        code = "let 变量 = 100;"
        tokens = list(lexer(code))
        
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0].type, 'LET')
        self.assertEqual(tokens[1].type, 'IDENTIFIER')
        self.assertEqual(tokens[1].value, '变量')
        self.assertEqual(tokens[2].type, 'EQUALS')
        self.assertEqual(tokens[3].type, 'NUMBER')
        self.assertEqual(tokens[3].value, '100')
        self.assertEqual(tokens[4].type, 'SEMICOLON')

if __name__ == '__main__':
    unittest.main()