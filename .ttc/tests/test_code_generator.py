import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from lexer import lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator

class TestCodeGenerator(unittest.TestCase):
    def test_generate_let_statement(self):
        """Test code generation for let statements"""
        code = "let x = 42;"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        # Perform semantic analysis first
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Generate code
        generator = CodeGenerator()
        generated_code = generator.generate(ast)
        
        # Check that the generated code contains the expected Python code
        self.assertIn("x = 42", generated_code)
    
    def test_generate_function_call(self):
        """Test code generation for function calls"""
        code = "print(\"Hello\");"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        # Perform semantic analysis first
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Generate code
        generator = CodeGenerator()
        generated_code = generator.generate(ast)
        
        # Check that the generated code contains the expected Python code
        self.assertIn("print(\"Hello\")", generated_code)
    
    def test_generate_list_literal(self):
        """Test code generation for list literals"""
        code = "let arr = [1, 2, 3];"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        # Perform semantic analysis first
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Generate code
        generator = CodeGenerator()
        generated_code = generator.generate(ast)
        
        # Check that the generated code contains the expected Python code
        self.assertIn("arr = [1, 2, 3]", generated_code)
    
    def test_generate_assignment_statement(self):
        """Test code generation for assignment statements"""
        code = "x = 10;"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        # Perform semantic analysis first
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Generate code
        generator = CodeGenerator()
        generated_code = generator.generate(ast)
        
        # Check that the generated code contains the expected Python code
        self.assertIn("x = 10", generated_code)
    
    def test_generate_while_loop(self):
        """Test code generation for while loops"""
        code = "while x < 10 { x = x + 1; }"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        # Perform semantic analysis first
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Generate code
        generator = CodeGenerator()
        generated_code = generator.generate(ast)
        
        # Check that the generated code contains the expected Python code
        self.assertIn("while x < 10:", generated_code)
        self.assertIn("x = x + 1", generated_code)
    
    def test_generate_builtin_functions(self):
        """Test code generation for builtin functions"""
        code = "let result = len(\"hello\");"
        tokens = list(lexer(code))
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        # Perform semantic analysis first
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Generate code
        generator = CodeGenerator()
        generated_code = generator.generate(ast)
        
        # Check that the generated code contains the expected Python code
        self.assertIn("result = len(\"hello\")", generated_code)

if __name__ == '__main__':
    unittest.main()