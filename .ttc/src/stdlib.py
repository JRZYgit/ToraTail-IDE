"""
Tora标准库模块
提供内置函数和常用功能的实现
"""

import math
import random
import datetime

# 内置函数映射表
BUILTIN_FUNCTIONS = {
    # 输出函数
    "print": "print",
    "println": "print",
    
    # 字符串函数
    "len": "len",
    "str": "str",
    "int": "int",
    "float": "float",
    
    # 数学函数
    "abs": "abs",
    "max": "max",
    "min": "min",
    "pow": "pow",
    "sqrt": "math.sqrt",
    "sin": "math.sin",
    "cos": "math.cos",
    "tan": "math.tan",
    "log": "math.log",
    "log10": "math.log10",
    "ceil": "math.ceil",
    "floor": "math.floor",
    "round": "round",
    
    # 列表函数
    "push": "list.append",  # 注意：在Python中是append而不是push
    "pop": "list.pop",
    "contains": "lambda lst, item: item in lst",
    "sum": "sum",
    "average": "lambda lst: sum(lst) / len(lst) if lst else 0",
    "max_list": "max",
    "min_list": "min",
    
    # 随机数函数
    "random": "random_module.random",
    "randint": "random_module.randint",
    
    # 时间函数
    "time": "datetime.datetime.now",
    "timestamp": "lambda: datetime.datetime.now().timestamp()",
    
    # 类型检查函数
    "is_int": "lambda x: isinstance(x, int)",
    "is_float": "lambda x: isinstance(x, float)",
    "is_str": "lambda x: isinstance(x, str)",
    "is_bool": "lambda x: isinstance(x, bool)",
    "is_list": "lambda x: isinstance(x, list)",
}

# 内置常量
BUILTIN_CONSTANTS = {
    "PI": "math.pi",
    "E": "math.e",
    "TRUE": "True",
    "FALSE": "False",
    "NONE": "None",
}

def get_builtin_imports():
    """获取需要导入的Python模块"""
    return [
        "import math",
        "import random",
        "import datetime",
    ]

def get_builtin_functions():
    """获取内置函数映射"""
    return BUILTIN_FUNCTIONS

def get_builtin_constants():
    """获取内置常量映射"""
    return BUILTIN_CONSTANTS

def generate_stdlib_code():
    """生成标准库代码"""
    code_lines = []
    
    # 添加导入语句
    code_lines.extend(get_builtin_imports())
    code_lines.append("")
    
    # 添加常量定义
    for name, value in BUILTIN_CONSTANTS.items():
        code_lines.append(f"{name} = {value}")
    code_lines.append("")
    
    # 检查是否需要导入random_module
    need_random_module = any(value.startswith("random_module.") for value in BUILTIN_FUNCTIONS.values())
    if need_random_module and not any("import random as random_module" in line for line in code_lines):
        code_lines.append("import random as random_module")
    
    # 添加函数定义
    for name, value in BUILTIN_FUNCTIONS.items():
        # 特殊处理lambda函数
        if value.startswith("lambda"):
            code_lines.append(f"{name} = {value}")
        # 特殊处理需要别名的函数
        elif value != name and not value.startswith("lambda"):
            # 特殊处理random模块的函数，避免冲突
            if value.startswith("random."):
                code_lines.append(f"{name} = random_module.{value.split(".", 1)[1]}")
            else:
                code_lines.append(f"{name} = {value}")
    code_lines.append("")
    
    return "\n".join(code_lines)