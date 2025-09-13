import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QTabWidget, QVBoxLayout,
    QWidget, QPushButton, QFileDialog, QMessageBox, QMenuBar, QMenu,
    QFontDialog, QInputDialog, QSplitter, QLabel, QHBoxLayout,
    QListWidget, QSplashScreen, QPlainTextEdit, QToolBar
)
from PyQt6.QtGui import (
    QFont, QColor, QSyntaxHighlighter, QTextCharFormat,
    QTextCursor, QPalette, QPainter, QPen, QImage, QIcon, QPixmap, QAction, QFontMetrics
)
from PyQt6.QtCore import (
    Qt, QSize, QRect, QPoint, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QTimer
)

# 启动画面类
class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setPixmap(QPixmap("open.png" if os.path.exists("open.png") else self.createDefaultSplash()))
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showMessage("正在加载代码编辑器...", 
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                        Qt.GlobalColor.white)
        
    def createDefaultSplash(self):
        # 创建默认启动画面
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(45, 45, 45))
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "简约代码编辑器")
        painter.end()
        return pixmap

# 起始页类
class StartPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # 添加标题
        title = QLabel("欢迎使用 Toratail")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498db;")
        layout.addWidget(title)

        # 添加副标题
        subtitle = QLabel("一个简洁、轻量级的代码编辑器")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        layout.addWidget(subtitle)

        # 添加按钮容器
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(15)  # 增加按钮间距

        # 创建按钮并减小尺寸
        new_file_btn = QPushButton("新建文件")
        new_file_btn.setMinimumSize(100, 32)  # 减小按钮尺寸
        new_file_btn.setMaximumSize(140, 32)
        new_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_file_btn.clicked.connect(self.parent.new_file)
        button_layout.addWidget(new_file_btn)

        open_file_btn = QPushButton("打开文件")
        open_file_btn.setMinimumSize(100, 32)  # 减小按钮尺寸
        open_file_btn.setMaximumSize(140, 32)
        open_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        open_file_btn.clicked.connect(self.parent.open_file)
        button_layout.addWidget(open_file_btn)

        layout.addLayout(button_layout)

        # 添加最近文件部分
        recent_label = QLabel("最近文件")
        recent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        recent_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #555555;")
        layout.addWidget(recent_label)

        # 最近文件列表
        self.recent_files_list = QListWidget()
        self.recent_files_list.setMaximumHeight(100)
        self.recent_files_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.recent_files_list)

        # 加载最近文件
        self.load_recent_files()

    def load_recent_files(self):
        # 加载最近文件列表
        self.recent_files_list.clear()
        try:
            # 从配置文件或其他地方加载最近文件列表
            # 这里简单模拟一些最近文件
            recent_files = []
            for file_name in recent_files:
                item = QListWidgetItem(file_name)
                self.recent_files_list.addItem(item)
        except Exception as e:
            print(f"加载最近文件失败: {e}")
    
    def add_recent_file(self, file_path):
        # 将文件添加到最近文件列表
        try:
            # 检查文件是否已存在
            for i in range(self.recent_files_list.count()):
                if self.recent_files_list.item(i).text() == file_path:
                    # 如果已存在，移到顶部
                    item = self.recent_files_list.takeItem(i)
                    self.recent_files_list.insertItem(0, item)
                    return
            
            # 添加新文件到列表顶部
            self.recent_files_list.insertItem(0, file_path)
            
            # 限制列表长度
            max_recent = 5
            while self.recent_files_list.count() > max_recent:
                self.recent_files_list.takeItem(self.recent_files_list.count() - 1)
        except Exception as e:
            print(f"添加最近文件失败: {e}")
    
    # 根据主题更新样式
    def updateTheme(self, is_dark_theme):
        if is_dark_theme:
            self.setStyleSheet("background-color: #252526;")  # 设置与主题相近的背景色
            self.recent_files_list.setStyleSheet("""
                QListWidget {
                    background-color: #3c3c3c;
                    border: 1px solid #464647;
                    border-radius: 4px;
                    padding: 5px;
                    color: #cccccc;
                }
                QListWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #464647;
                    color: #cccccc;
                }
                QListWidget::item:hover {
                    background-color: #0e639c;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("background-color: #f8f9fa;")  # 设置与主题相近的背景色
            self.recent_files_list.setStyleSheet("""
                QListWidget {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 5px;
                    color: #333333;
                }
                QListWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #f0f0f0;
                    color: #333333;
                }
                QListWidget::item:hover {
                    background-color: #e8f4fd;
                    color: #3498db;
                }
            """)

# 行号显示区域
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

# 简单的语法高亮器 - 改进版
class BasicSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, is_dark_theme=False):
        super().__init__(parent)
        self.is_dark_theme = is_dark_theme
        self.setupFormats()
        self.keywords = [
            "def", "class", "import", "from", "if", "elif", "else",
            "for", "while", "in", "return", "break", "continue",
            "try", "except", "finally", "with", "as", "pass", "raise"
        ]
        
    def updateTheme(self, is_dark_theme):
        # 更新主题并重新设置格式
        self.is_dark_theme = is_dark_theme
        self.setupFormats()
        
    def setupFormats(self):
        # 根据主题设置不同的颜色
        if self.is_dark_theme:
            self.keywordFormat = QTextCharFormat()
            self.keywordFormat.setForeground(QColor(197, 134, 192))  # 紫色
            self.keywordFormat.setFontWeight(75)
            
            self.stringFormat = QTextCharFormat()
            self.stringFormat.setForeground(QColor(162, 191, 143))  # 绿色
            
            self.commentFormat = QTextCharFormat()
            self.commentFormat.setForeground(QColor(92, 99, 112))  # 灰色
            
            self.numberFormat = QTextCharFormat()
            self.numberFormat.setForeground(QColor(208, 135, 112))  # 橙色
            
            self.functionFormat = QTextCharFormat()
            self.functionFormat.setForeground(QColor(139, 195, 74))  # 浅绿色
        else:
            self.keywordFormat = QTextCharFormat()
            self.keywordFormat.setForeground(QColor(125, 60, 255))  # 紫色
            self.keywordFormat.setFontWeight(75)
            
            self.stringFormat = QTextCharFormat()
            self.stringFormat.setForeground(QColor(22, 156, 59))  # 绿色
            
            self.commentFormat = QTextCharFormat()
            self.commentFormat.setForeground(QColor(117, 113, 94))  # 灰色
            
            self.numberFormat = QTextCharFormat()
            self.numberFormat.setForeground(QColor(245, 81, 73))  # 红色
            
            self.functionFormat = QTextCharFormat()
            self.functionFormat.setForeground(QColor(20, 114, 183))  # 蓝色

    def highlightBlock(self, text):
        # 高亮数字
        inNumber = False
        numberStart = 0
        for i, char in enumerate(text):
            if char.isdigit() or (char == '.' and i > 0 and text[i-1].isdigit()):
                if not inNumber:
                    numberStart = i
                    inNumber = True
            else:
                if inNumber:
                    self.setFormat(numberStart, i - numberStart, self.numberFormat)
                    inNumber = False
        if inNumber:
            self.setFormat(numberStart, len(text) - numberStart, self.numberFormat)
        
        # 高亮关键字
        for keyword in self.keywords:
            start_index = 0
            while start_index < len(text):
                start_index = text.find(keyword, start_index)
                if start_index == -1:
                    break
                
                # 确保是完整单词
                if (start_index == 0 or not text[start_index-1].isalnum()) and \
                   (start_index + len(keyword) == len(text) or not text[start_index + len(keyword)].isalnum()):
                    self.setFormat(start_index, len(keyword), self.keywordFormat)
                
                start_index += len(keyword)
        
        # 高亮字符串
        inString = False
        stringStart = 0
        quoteChar = None
        for i, char in enumerate(text):
            if (char == '"' or char == "'") and (i == 0 or text[i-1] != '\\'):
                if inString and char == quoteChar:
                    self.setFormat(stringStart, i - stringStart + 1, self.stringFormat)
                    inString = False
                elif not inString:
                    stringStart = i
                    quoteChar = char
                    inString = True
        
        # 高亮注释
        commentPos = text.find('#')
        if commentPos != -1 and not inString:
            self.setFormat(commentPos, len(text) - commentPos, self.commentFormat)

# 代码编辑器类
class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None, is_dark_theme=False):
        super().__init__(parent)
        self.is_dark_theme = is_dark_theme
        self.lineNumberArea = LineNumberArea(self)
        self.highlighter = BasicSyntaxHighlighter(self.document(), is_dark_theme)
        
        # 设置字体 - 使用更现代的等宽字体
        font = QFont("JetBrains Mono", 11)  # 或使用 "Consolas" 作为备选
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # 设置样式 - 根据主题设置不同的颜色
        self.updateTheme()
        
        # 连接信号
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        # 初始化
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        
        # 文件路径
        self.file_path = ""
        
        # 设置边距和滚动条样式
        self.setViewportMargins(10, 5, 5, 5)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def updateTheme(self, is_dark_theme=None):
        # 如果提供了主题参数，更新实例的主题属性
        if is_dark_theme is not None:
            self.is_dark_theme = is_dark_theme
        
        # 更新语法高亮器的主题
        self.highlighter.updateTheme(self.is_dark_theme)
        
        if self.is_dark_theme:
            self.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    selection-background-color: #264f78;
                    border: none;
                }
                QScrollBar:vertical {
                    background-color: #2d2d30;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #464647;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #5a5a5a;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    background-color: #2d2d30;
                    height: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #464647;
                    min-width: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #5a5a5a;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #ffffff;
                    color: #1e1e1e;
                    selection-background-color: #add6ff;
                    border: none;
                }
                QScrollBar:vertical {
                    background-color: #f0f0f0;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #c0c0c0;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #a0a0a0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    background-color: #f0f0f0;
                    height: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #c0c0c0;
                    min-width: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #a0a0a0;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
            """)
        
        # 更新语法高亮器主题
        self.highlighter.is_dark_theme = self.is_dark_theme
        self.highlighter.setupFormats()
        self.highlighter.rehighlight()

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space + 8  # 增加一些额外的空间

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(240, 240, 240) if not self.is_dark_theme else QColor(43, 43, 43))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        # 绘制行号，改进对齐和间距
        font = painter.font()
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        painter.setFont(font)

        # 根据字体计算合适的行高
        font_metrics = QFontMetrics(font)
        line_height = font_metrics.height()

        # 计算最大行号位数以确定合适的右对齐间距
        max_lines = self.blockCount()
        max_digits = len(str(max_lines))

        # 设置行号文本颜色
        painter.setPen(QColor(120, 120, 120) if not self.is_dark_theme else QColor(180, 180, 180))

        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                # 格式化行号，使其右对齐
                number = str(blockNumber + 1)
                # 添加适当的左填充以确保对齐
                formatted_number = number.rjust(max_digits, ' ')
                # 绘制行号，增加右侧间距
                painter.drawText(-5, top, self.lineNumberArea.width() - 10, line_height, Qt.AlignmentFlag.AlignRight, formatted_number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            # 根据主题设置当前行高亮颜色
            if self.is_dark_theme:
                selection.format.setBackground(QColor(40, 40, 40))
            else:
                selection.format.setBackground(QColor(245, 245, 245))
            
            cursor = self.textCursor()
            cursor.clearSelection()
            
            selection.cursor = cursor
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)

# 主窗口类
class CodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_theme = False  # 默认使用浅色主题
        self.initUI()
        self.current_font = QFont("JetBrains Mono", 11)  # 存储当前字体

    def initUI(self):
        # 设置窗口标题和尺寸
        self.setWindowTitle("Toratail")
        self.setGeometry(100, 100, 1000, 600)
        
        # 设置窗口图标
        if os.path.exists("icons/icon.ico"):
            self.setWindowIcon(QIcon("icons/icon.ico"))
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 设置标签页样式
        self.updateTabWidgetStyle()
        
        # 设置中心部件
        self.setCentralWidget(self.tab_widget)
        
        # 显示起始页
        self.show_start_page()
        
        # 创建菜单栏
        self.create_menus()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")

    def updateGlobalTheme(self):
        # 更新应用程序全局样式
        if self.is_dark_theme:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #cccccc;
                }
                QMenuBar {
                    background-color: #2d2d30;
                    color: #cccccc;
                    padding: 5px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    color: #cccccc;
                    padding: 5px 10px;
                }
                QMenuBar::item:hover {
                    background-color: #3e3e42;
                    color: white;
                }
                QMenu {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border: 1px solid #464647;
                }
                QMenu::item {
                    background-color: transparent;
                    color: #cccccc;
                    padding: 5px 20px;
                }
                QMenu::item:hover {
                    background-color: #0e639c;
                    color: white;
                }
                QStatusBar {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border-top: 1px solid #464647;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: white;
                    color: #333333;
                }
                QMenuBar {
                    background-color: white;
                    color: #333333;
                    padding: 5px;
                    border-bottom: 1px solid #e0e0e0;
                }
                QMenuBar::item {
                    background-color: transparent;
                    color: #333333;
                    padding: 5px 10px;
                }
                QMenuBar::item:hover {
                    background-color: #e0e0e0;
                    color: #333333;
                }
                QMenu {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #e0e0e0;
                }
                QMenu::item {
                    background-color: transparent;
                    color: #333333;
                    padding: 5px 20px;
                }
                QMenu::item:hover {
                    background-color: #e8f4fd;
                    color: #3498db;
                }
                QStatusBar {
                    background-color: white;
                    color: #333333;
                    border-top: 1px solid #e0e0e0;
                    padding: 5px;
                }
            """)

        # 更新标签页样式
        if self.is_dark_theme:
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #464647;
                    background-color: #1e1e1e;
                    top: -1px;
                    margin: 0;
                }
                QTabBar::tab {
                    background-color: #2d2d30;
                    color: #cccccc;
                    padding: 8px 16px;
                    margin-right: 1px;
                    border-bottom: 2px solid transparent;
                    font-family: 'Segoe UI';
                    font-size: 12px;
                }
                QTabBar::tab:hover {
                    background-color: #3e3e42;
                    color: white;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    color: white;
                    border-bottom: 2px solid #0e639c;
                    margin-bottom: 0;
                }
                QTabBar::close-button {
                    image: url(icons/close.png);
                    subcontrol-position: right;
                    subcontrol-origin: padding;
                    width: 14px;
                    height: 14px;
                    margin-left: 5px;
                }
                QTabBar::close-button:hover {
                    background-color: #ff6b6b;
                    border-radius: 3px;
                }
            """)
        else:
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    background-color: white;
                    top: -1px;
                    margin: 0;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    color: #555555;
                    padding: 8px 16px;
                    margin-right: 1px;
                    border-bottom: 2px solid transparent;
                    font-family: 'Segoe UI';
                    font-size: 12px;
                }
                QTabBar::tab:hover {
                    background-color: #e0e0e0;
                    color: #333333;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    color: #3498db;
                    border-bottom: 2px solid #3498db;
                    margin-bottom: 0;
                }
                QTabBar::close-button {
                    image: url(icons/close.png);
                    subcontrol-position: right;
                    subcontrol-origin: padding;
                    width: 14px;
                    height: 14px;
                    margin-left: 5px;
                }
                QTabBar::close-button:hover {
                    background-color: #ff6b6b;
                    border-radius: 3px;
                }
            """)

        # 更新工具栏样式
        toolbar = self.findChild(QToolBar)
        if toolbar:
            if self.is_dark_theme:
                toolbar.setStyleSheet("""
                    QToolBar {
                        background-color: #2d2d30;
                        border: none;
                        spacing: 10px;
                        padding: 5px;
                    }
                    QToolButton {
                        color: #cccccc;
                        background-color: transparent;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-family: 'Segoe UI';
                        font-size: 12px;
                    }
                    QToolButton:hover {
                        background-color: #3e3e42;
                        color: white;
                    }
                    QToolButton:pressed {
                        background-color: #0e639c;
                        color: white;
                    }
                """)
            else:
                toolbar.setStyleSheet("""
                    QToolBar {
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        spacing: 10px;
                        padding: 5px;
                    }
                    QToolButton {
                        color: #555555;
                        background-color: transparent;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-family: 'Segoe UI';
                        font-size: 12px;
                    }
                    QToolButton:hover {
                        background-color: #e0e0e0;
                        color: #333333;
                    }
                    QToolButton:pressed {
                        background-color: #3498db;
                        color: white;
                    }
                """)

        # 更新所有编辑器的主题
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, CodeEditor):
                widget.updateTheme(self.is_dark_theme)
            elif isinstance(widget, StartPage):
                widget.updateTheme(self.is_dark_theme)  # 更新起始页主题

    def show_start_page(self):
        start_page = StartPage(self)
        start_page.updateTheme(self.is_dark_theme)  # 初始化时应用当前主题
        self.tab_widget.addTab(start_page, "起始页")
        self.tab_widget.setCurrentIndex(0)

    def get_current_editor(self):
        return self.tab_widget.currentWidget()

    def on_text_changed(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            index = self.tab_widget.indexOf(editor)
            tab_text = self.tab_widget.tabText(index)
            
            # 如果内容已修改且标签文本没有星号，添加星号
            if editor.document().isModified() and not tab_text.endswith('*'):
                self.tab_widget.setTabText(index, tab_text + '*')
            # 如果内容未修改但标签文本有星号，移除星号
            elif not editor.document().isModified() and tab_text.endswith('*'):
                self.tab_widget.setTabText(index, tab_text[:-1])

    def on_tab_changed(self):
        editor = self.get_current_editor()
        if editor:
            if isinstance(editor, StartPage):
                self.statusBar().showMessage("欢迎使用 Toratail")
            else:
                self.statusBar().showMessage(f"当前文件: {editor.file_path if editor.file_path else '未命名'}")

    def cut(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            editor.cut()

    def close_tab(self, index):
        editor = self.tab_widget.widget(index)
        
        # 检查是否需要保存
        if hasattr(editor, 'document') and editor.document().isModified():
            reply = QMessageBox.question(
                self, "保存", "文件已修改，是否保存？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes:
                self.save_file()
        
        self.tab_widget.removeTab(index)
        
        # 如果没有标签页了，显示起始页
        if self.tab_widget.count() == 0:
            self.show_start_page()

    def copy(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            editor.copy()

    def paste(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            editor.paste()

    def find_text(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            # 简单的查找功能
            find_text, ok = QInputDialog.getText(self, "查找", "查找内容:")
            if ok and find_text:
                text = editor.toPlainText()
                pos = text.find(find_text, editor.textCursor().position())
                if pos != -1:
                    cursor = editor.textCursor()
                    cursor.setPosition(pos)
                    cursor.setPosition(pos + len(find_text), QTextCursor.MoveMode.KeepAnchor)
                    editor.setTextCursor(cursor)
                    editor.setFocus()
                else:
                    QMessageBox.information(self, "查找", f"未找到 '{find_text}'")

    def change_font(self):
        font, ok = QFontDialog.getFont(self.current_font, self, "选择字体")
        if ok:
            self.current_font = font
            # 应用字体到所有编辑器
            for i in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(i)
                if isinstance(editor, CodeEditor):
                    editor.setFont(font)
            self.statusBar().showMessage(f"已设置字体: {font.family()}, 大小: {font.pointSize()}")

    def updateTabWidgetStyle(self):
        if self.is_dark_theme:
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #464647;
                    background-color: #1e1e1e;
                    top: -1px;
                    margin: 0;
                }
                QTabBar::tab {
                    background-color: #2d2d30;
                    color: #cccccc;
                    padding: 8px 16px;
                    margin-right: 1px;
                    border-bottom: 2px solid transparent;
                    font-family: 'Segoe UI';
                    font-size: 12px;
                }
                QTabBar::tab:hover {
                    background-color: #3e3e42;
                    color: white;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    color: white;
                    border-bottom: 2px solid #0e639c;
                    margin-bottom: 0;
                }
                QTabBar::close-button {
                    image: url(icons/close.png);
                    subcontrol-position: right;
                    subcontrol-origin: padding;
                    width: 14px;
                    height: 14px;
                    margin-left: 5px;
                }
                QTabBar::close-button:hover {
                    background-color: #ff6b6b;
                    border-radius: 3px;
                }
            """)
        else:
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    background-color: white;
                    top: -1px;
                    margin: 0;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    color: #555555;
                    padding: 8px 16px;
                    margin-right: 1px;
                    border-bottom: 2px solid transparent;
                    font-family: 'Segoe UI';
                    font-size: 12px;
                }
                QTabBar::tab:hover {
                    background-color: #e0e0e0;
                    color: #333333;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    color: #3498db;
                    border-bottom: 2px solid #3498db;
                    margin-bottom: 0;
                }
                QTabBar::close-button {
                    image: url(icons/close.png);
                    subcontrol-position: right;
                    subcontrol-origin: padding;
                    width: 14px;
                    height: 14px;
                    margin-left: 5px;
                }
                QTabBar::close-button:hover {
                    background-color: #ff6b6b;
                    border-radius: 3px;
                }
            """)

    def switch_to_light_theme(self):
        self.is_dark_theme = False
        self.updateGlobalTheme()
        self.statusBar().showMessage("已切换到浅色主题")

    def switch_to_dark_theme(self):
        self.is_dark_theme = True
        self.updateGlobalTheme()
        self.statusBar().showMessage("已切换到深色主题")

    def create_menus(self):
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 新建文件动作
        new_action = QAction("新建", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # 打开文件动作
        open_action = QAction("打开", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 保存文件动作
        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # 另存为动作
        save_as_action = QAction("另存为", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        # 剪切动作
        cut_action = QAction("剪切", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        # 复制动作
        copy_action = QAction("复制", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        # 粘贴动作
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        # 查找动作
        find_action = QAction("查找", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        # 字体设置动作
        font_action = QAction("字体", self)
        font_action.triggered.connect(self.change_font)
        view_menu.addAction(font_action)
        
        view_menu.addSeparator()
        
        # 主题切换动作
        light_theme_action = QAction("浅色主题", self)
        light_theme_action.triggered.connect(self.switch_to_light_theme)
        view_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("深色主题", self)
        dark_theme_action.triggered.connect(self.switch_to_dark_theme)
        view_menu.addAction(dark_theme_action)

    def create_toolbar(self):
        # 创建工具栏
        toolbar = QToolBar("工具栏", self)
        self.addToolBar(toolbar)
        
        # 添加新建文件按钮
        new_btn = QAction("新建", self)
        new_btn.triggered.connect(self.new_file)
        toolbar.addAction(new_btn)
        
        # 添加打开文件按钮
        open_btn = QAction("打开", self)
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)
        
        # 添加保存文件按钮
        save_btn = QAction("保存", self)
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)
        
        toolbar.addSeparator()
        
        # 添加剪切按钮
        cut_btn = QAction("剪切", self)
        cut_btn.triggered.connect(self.cut)
        toolbar.addAction(cut_btn)
        
        # 添加复制按钮
        copy_btn = QAction("复制", self)
        copy_btn.triggered.connect(self.copy)
        toolbar.addAction(copy_btn)
        
        # 添加粘贴按钮
        paste_btn = QAction("粘贴", self)
        paste_btn.triggered.connect(self.paste)
        toolbar.addAction(paste_btn)

    def new_file(self):
        # 检查当前是否显示起始页
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, StartPage):
            # 如果是起始页，移除它
            self.tab_widget.removeTab(0)
        
        # 创建新的编辑器
        editor = CodeEditor(self)
        editor.updateTheme(self.is_dark_theme)
        editor.setFont(self.current_font)
        editor.textChanged.connect(self.on_text_changed)
        
        # 添加到标签页
        index = self.tab_widget.addTab(editor, "未命名")
        self.tab_widget.setCurrentIndex(index)
        
        # 添加标签页动画
        self.animateTab(index)
        
        # 设置状态栏消息
        self.statusBar().showMessage("已创建新文件")

    def animateTab(self, index):
        # 简单的标签页选中动画
        tab_bar = self.tab_widget.tabBar()
        if tab_bar and 0 <= index < tab_bar.count():
            # 这里可以添加更复杂的动画效果
            pass

    def open_file(self):
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", "所有文件 (*);;文本文件 (*.txt);;Python 文件 (*.py);;JavaScript 文件 (*.js);;HTML 文件 (*.html);;CSS 文件 (*.css)"
        )
        
        if file_path:
            try:
                # 检查文件是否已经打开
                for i in range(self.tab_widget.count()):
                    widget = self.tab_widget.widget(i)
                    if hasattr(widget, 'file_path') and widget.file_path == file_path:
                        self.tab_widget.setCurrentIndex(i)
                        return
                
                # 检查当前是否显示起始页
                current_widget = self.tab_widget.currentWidget()
                if isinstance(current_widget, StartPage):
                    # 如果是起始页，移除它
                    self.tab_widget.removeTab(0)
                
                # 创建新的编辑器
                editor = CodeEditor(self)
                editor.updateTheme(self.is_dark_theme)
                editor.setFont(self.current_font)
                editor.textChanged.connect(self.on_text_changed)
                
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    editor.setPlainText(f.read())
                
                # 设置文件路径
                editor.file_path = file_path
                
                # 添加到标签页
                index = self.tab_widget.addTab(editor, os.path.basename(file_path))
                self.tab_widget.setCurrentIndex(index)
                
                # 添加标签页动画
                self.animateTab(index)
                
                # 设置状态栏消息
                self.statusBar().showMessage(f"已打开文件: {file_path}")
                
                # 更新起始页的最近文件列表
                self.update_recent_files(file_path)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")

    def save_file(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            if hasattr(editor, 'file_path') and editor.file_path:
                try:
                    with open(editor.file_path, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                    editor.document().setModified(False)
                    index = self.tab_widget.indexOf(editor)
                    self.tab_widget.setTabText(index, os.path.basename(editor.file_path))
                    self.statusBar().showMessage(f"已保存文件: {editor.file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
            else:
                self.save_file_as()

    def save_file_as(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "另存为", "", "所有文件 (*);;文本文件 (*.txt);;Python 文件 (*.py);;JavaScript 文件 (*.js);;HTML 文件 (*.html);;CSS 文件 (*.css)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                    editor.file_path = file_path
                    editor.document().setModified(False)
                    index = self.tab_widget.indexOf(editor)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                    self.statusBar().showMessage(f"已保存文件: {file_path}")
                    
                    # 更新起始页的最近文件列表
                    self.update_recent_files(file_path)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")

    def update_recent_files(self, file_path):
        # 更新起始页的最近文件列表
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, StartPage):
                widget.add_recent_file(file_path)
                break

# 主函数
def main():
    # 创建应用
    app = QApplication(sys.argv)
    
    # 显示启动画面
    splash = SplashScreen()
    splash.show()
    
    # 模拟加载时间
    app.processEvents()
    QTimer.singleShot(1500, splash.close)
    
    # 创建主窗口
    editor = CodeEditorWindow()
    
    # 关闭启动画面并显示主窗口
    splash.finish(editor)
    editor.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == '__main__':
    main()