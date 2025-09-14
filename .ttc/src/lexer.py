import re
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from errors import LexicalError

# Token类型定义
TOKEN_TYPES = [
    ("PRINTLN", r"println"),  # 关键字 println (必须在PRINT之前)
    ("PRINT", r"print"),  # 关键字 print
    ("LET", r"let"),  # 关键字 let
    ("FN", r"fn"),  # 关键字 fn
    ("IF", r"if"),  # 关键字 if
    ("ELSE", r"else"),  # 关键字 else
    ("WHILE", r"while"),  # 关键字 while
    ("FOR", r"for"),  # 关键字 for
    ("RETURN", r"return"),  # 关键字 return
    ("IDENTIFIER", r"[a-zA-Z_\u4e00-\u9fff][a-zA-Z0-9_\u4e00-\u9fff]*"),  # 标识符（支持中文）
    ("NUMBER", r"-?\d+(\.\d+)?"),  # 数字（支持负数和小数）
    ("STRING", r'"([^"\\]|\\.)*"'),  # 字符串（支持转义字符）
    ("PLUS", r"\+"),  # 加号
    ("MINUS", r"-"),  # 减号
    ("MULTIPLY", r"\*"),  # 乘号
    ("DIVIDE", r"/"),  # 除号
    ("EQUALS", r"=="),  # 等于
    ("ASSIGN", r"="),  # 赋值
    ("NOT_EQUALS", r"!="),  # 不等于
    ("LESS_EQUAL", r"<="),  # 小于等于
    ("GREATER_EQUAL", r">="),  # 大于等于
    ("LESS_THAN", r"<"),  # 小于
    ("GREATER_THAN", r">"),  # 大于
    ("SEMICOLON", r";"),  # 分号
    ("COLON", r":"),  # 冒号
    ("COMMA", r","),  # 逗号
    ("LPAREN", r"\("),  # 左括号
    ("RPAREN", r"\)"),  # 右括号
    ("LBRACE", r"\{"),  # 左花括号
    ("RBRACE", r"\}"),  # 右花括号
    ("LBRACKET", r"\["),  # 左方括号
    ("RBRACKET", r"\]"),  # 右方括号
    ("COMMENT", r"//.*"),  # 注释
    ("SKIP", r"[ \t]+"),  # 忽略空白字符
    ("NEWLINE", r"\n"),  # 换行符
    ("MISMATCH", r"."),  # 捕获其他字符
]

# 编译正则表达式
TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_TYPES)
GET_TOKEN = re.compile(TOKEN_REGEX).match

class Token:
    """
    Token类，表示词法分析器生成的Token。
    """
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"

def lexer(code):
    """
    将源代码字符串分解为一系列的 Token。
    每个 Token 是一个元组，包含类型、值、行号和起始位置。
    """
    line = 1
    pos = 0
    match = GET_TOKEN(code)
    while match is not None:
        type_ = match.lastgroup
        if type_ == "NEWLINE":
            line += 1
            pos = match.end()
            match = GET_TOKEN(code, pos)
            continue
        elif type_ == "SKIP":  # 忽略空白字符
            pos = match.end()
            match = GET_TOKEN(code, pos)
            continue
        elif type_ == "COMMENT":  # 忽略注释
            pos = match.end()
            match = GET_TOKEN(code, pos)
            continue
        elif type_ == "MISMATCH":  # 捕获非法字符
            char = match.group()
            raise LexicalError(f"Unexpected character '{char}'", line, match.start() - code.rfind('\n', 0, match.start()))
        
        value = match.group(type_)
        column = match.start() - code.rfind('\n', 0, match.start())
        yield Token(type_, value, line, column)
        
        pos = match.end()
        match = GET_TOKEN(code, pos)
    
    # 添加EOF token
    yield Token("EOF", "", line, 0)