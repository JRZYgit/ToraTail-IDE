import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from lexer import lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from errors import ToraError

class TestSemanticAnalyzer(unittest.TestCase):
    def test_variable_declaration_and_usage(self):
        """Test variable declaration and usage"""
        code = """
        let x = 42;
        let y = x + 10;
        """
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        analyzer = SemanticAnalyzer()
        # This should not raise an exception
        analyzer.analyze(ast)
        
        # Check that variables are in the symbol table
        self.assertIn('x', analyzer.symbol_table)
        self.assertIn('y', analyzer.symbol_table)
    
    def test_undefined_variable_error(self):
        """Test that using undefined variables raises an error"""
        code = "let y = x + 10;"  # x is not defined
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        analyzer = SemanticAnalyzer()
        with self.assertRaises(ToraError):
            analyzer.analyze(ast)
    
    def test_builtin_constants(self):
        """Test that builtin constants are recognized"""
        code = """
        let pi_val = PI;
        let e_val = E;
        """
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        analyzer = SemanticAnalyzer()
        # This should not raise an exception
        analyzer.analyze(ast)
        
        # Check that builtin constants are recognized
        self.assertIn('PI', analyzer.symbol_table)
        self.assertIn('E', analyzer.symbol_table)
    
    def test_builtin_functions(self):
        """Test that builtin functions are recognized"""
        code = """
        let result = len("hello");
        let random_val = random();
        """
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        analyzer = SemanticAnalyzer()
        # This should not raise an exception
        analyzer.analyze(ast)
        
        # Check that builtin functions are recognized
        self.assertIn('len', analyzer.symbol_table)
        self.assertIn('random', analyzer.symbol_table)
    
    def test_function_call_arity(self):
        """Test function call arity checking"""
        code = """
        let result = len("hello", "world");  // len only takes one argument
        """
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        analyzer = SemanticAnalyzer()
        # This should raise an error due to wrong number of arguments
        with self.assertRaises(ToraError):
            analyzer.analyze(ast)

if __name__ == '__main__':
    unittest.main()