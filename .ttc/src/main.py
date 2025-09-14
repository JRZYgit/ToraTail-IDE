import sys
import os
import argparse

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from repl import REPL
from errors import ToraError
from package_manager import PackageManager

def read_file(filename):
    """读取文件内容"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def execute_code(code):
    """执行Tora代码"""
    try:
        # 词法分析
        tokens = list(lexer(code))
        
        # 语法分析
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        # 语义分析
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        
        # 代码生成
        code_generator = CodeGenerator()
        generated_code = code_generator.generate(ast)
        
        # 执行生成的代码
        exec(generated_code)
        
    except ToraError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Runtime Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    # 手动解析参数，避免冲突
    if len(sys.argv) == 1:
        # 如果没有参数，启动REPL
        repl = REPL()
        repl.start()
        return
    
    # 检查第一个参数
    first_arg = sys.argv[1]
    
    # 如果第一个参数是文件（以.tora结尾或包含路径分隔符）
    if first_arg.endswith('.tora') or '\\' in first_arg or '/' in first_arg:
        # 执行文件
        code = read_file(first_arg)
        execute_code(code)
        return
    
    # 如果第一个参数是--repl
    if first_arg == "--repl":
        repl = REPL()
        repl.start()
        return
    
    # 否则处理包管理器命令
    parser = argparse.ArgumentParser(description="Tora Language Interpreter")
    subparsers = parser.add_subparsers(dest='command', help='Package manager commands', required=False)
    
    # init命令
    init_parser = subparsers.add_parser('init', help='Initialize a new Tora project')
    init_parser.add_argument('name', nargs='?', help='Project name')
    init_parser.add_argument('--version', default='0.1.0', help='Project version')
    init_parser.add_argument('--description', default='', help='Project description')
    init_parser.add_argument('--author', default='', help='Project author')
    
    # install命令
    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package', help='Package name[@version]')
    install_parser.add_argument('--dev', action='store_true', help='Install as dev dependency')
    
    # uninstall命令
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package', help='Package name')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='List installed packages')
    list_parser.add_argument('--all', action='store_true', help='List all packages including dev')
    
    # update命令
    update_parser = subparsers.add_parser('update', help='Update a package')
    update_parser.add_argument('package', help='Package name')
    
    # update-all命令
    subparsers.add_parser('update-all', help='Update all packages')
    
    # search命令
    search_parser = subparsers.add_parser('search', help='Search for packages')
    search_parser.add_argument('query', help='Search query')
    
    # info命令
    info_parser = subparsers.add_parser('info', help='Show package information')
    info_parser.add_argument('package', help='Package name')
    
    # publish命令
    subparsers.add_parser('publish', help='Publish current package')
    
    # clean-cache命令
    subparsers.add_parser('clean-cache', help='Clean package cache')
    
    # project-info命令
    subparsers.add_parser('project-info', help='Show project information')
    
    args = parser.parse_args()
    
    # 包管理器命令处理
    if args.command:
        pm = PackageManager()
        if args.command == 'init':
            pm.init_project(args.name, args.version, args.description, args.author)
        elif args.command == 'install':
            if '@' in args.package:
                package_name, version = args.package.split('@', 1)
                pm.install_package(package_name, version, args.dev)
            else:
                pm.install_package(args.package, dev=args.dev)
        elif args.command == 'uninstall':
            pm.uninstall_package(args.package)
        elif args.command == 'list':
            pm.list_packages(args.all)
        elif args.command == 'update':
            pm.update_package(args.package)
        elif args.command == 'update-all':
            pm.update_all_packages()
        elif args.command == 'search':
            pm.search_packages(args.query)
        elif args.command == 'info':
            pm.info_package(args.package)
        elif args.command == 'publish':
            pm.publish_package()
        elif args.command == 'clean-cache':
            pm.clean_cache()
        elif args.command == 'project-info':
            pm.show_project_info()
        return
    
    # 如果指定了--repl参数，启动REPL
    if args.repl:
        repl = REPL()
        repl.start()
        return
    
    # 如果指定了文件，执行文件
    if args.file:
        code = read_file(args.file)
        execute_code(code)
        return
    
    # 如果没有参数，启动REPL
    repl = REPL()
    repl.start()

if __name__ == "__main__":
    main()