class ToraError(Exception):
    """Tora语言基础错误类"""
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(message)

    def __str__(self):
        if self.line is not None and self.column is not None:
            return f"Error: {self.message} at line {self.line}, column {self.column}"
        return f"Error: {self.message}"

class LexicalError(ToraError):
    """词法错误"""
    pass

class SyntaxError(ToraError):
    """语法错误"""
    pass

class SemanticError(ToraError):
    """语义错误"""
    pass