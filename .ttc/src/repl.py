import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from errors import ToraError

class REPL:
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self.code_generator = CodeGenerator()
        # 存储生成的Python代码的全局变量
        self.global_vars = {}

    def start(self):
        """启动REPL"""
        print("Tora Language REPL")
        print("Type 'exit' to quit")
        print()
        
        while True:
            try:
                line = input(">>> ")
                if line.strip() == "exit":
                    break
                if line.strip() == "":
                    continue
                self.execute_line(line)
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
            except EOFError:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"{e}")

    def execute_line(self, line):
        """执行单行代码"""
        try:
            # 词法分析
            tokens = list(lexer(line))
            
            # 语法分析
            parser = Parser(tokens)
            ast = parser.parse_program()
            
            # 语义分析
            self.semantic_analyzer.analyze(ast)
            
            # 代码生成
            generated_code = self.code_generator.generate(ast)
            
            # 执行生成的代码
            if generated_code.strip():
                exec(generated_code, self.global_vars)
                
        except ToraError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Runtime Error: {e}")