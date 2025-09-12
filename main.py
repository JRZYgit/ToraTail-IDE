import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPlainTextEdit, QTextEdit,
                             QFileDialog, QMessageBox, QVBoxLayout, 
                             QHBoxLayout, QWidget, QSplitter, QMenuBar, 
                             QMenu, QStatusBar, QSplashScreen, QTabWidget, QToolBar, 
                             QInputDialog, QLabel, QPushButton, QFontDialog)
from PyQt6.QtCore import Qt, QSize, QTimer, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFont, QPainter, QColor, QTextCharFormat, QSyntaxHighlighter, QPixmap, QAction

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
        self.initUI()
        
    def initUI(self):
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # 添加标题
        title_label = QLabel("Toratail")
        title_font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #3498db;")
        layout.addWidget(title_label)
        
        # 添加副标题
        subtitle_label = QLabel("轻量级的代码编辑工具")
        subtitle_font = QFont("Segoe UI", 14, QFont.Weight.Light)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle_label)
        
        # 添加按钮区域
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建带样式的按钮函数
        def createStyledButton(text, callback):
            button = QPushButton(text)
            button.setMinimumSize(200, 40)
            button.setMaximumWidth(200)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
            """)
            button.clicked.connect(callback)
            return button
        
        # 新建文件按钮
        new_button = createStyledButton("新建文件", self.new_file)
        button_layout.addWidget(new_button)
        
        # 打开文件按钮
        open_button = createStyledButton("打开文件", self.open_file)
        button_layout.addWidget(open_button)
        
        layout.addLayout(button_layout, 1)
        
        # 添加最近文件区域
        recent_label = QLabel("最近文件")
        recent_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        recent_label.setStyleSheet("color: #7f8c8d;")
        recent_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(recent_label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        
        # 设置背景颜色和渐变效果
        self.setStyleSheet("background-color: #f8f9fa;")
    
    def new_file(self):
        if self.parent:
            self.parent.new_file()
    
    def open_file(self):
        if self.parent:
            self.parent.open_file()

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

    def updateTheme(self):
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
        
        # 根据主题设置行号区域背景色
        if self.is_dark_theme:
            painter.fillRect(event.rect(), QColor(37, 37, 38))
            painter.setPen(QColor(128, 128, 128))
        else:
            painter.fillRect(event.rect(), QColor(245, 245, 245))
            painter.setPen(QColor(100, 100, 100))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        font = painter.font()
        font.setFamily("JetBrains Mono" if self.font().family() == "JetBrains Mono" else "Consolas")
        font.setPointSize(self.font().pointSize())
        painter.setFont(font)
        
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)
                painter.drawText(
                    0, 
                    int(top), 
                    self.lineNumberArea.width() - 8,  # 右边留出一些空间
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, 
                    number
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

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
        # 设置应用程序的全局样式
        if self.is_dark_theme:
            app_style = """
                QMainWindow {
                    background-color: #252526;
                    color: #d4d4d4;
                }
                QMenuBar {
                    background-color: #252526;
                    color: #d4d4d4;
                    padding: 5px 0;
                }
                QMenuBar::item {
                    padding: 5px 10px;
                    color: #d4d4d4;
                    background-color: transparent;
                }
                QMenuBar::item:selected {
                    background-color: #0e639c;
                    color: white;
                }
                QMenu {
                    background-color: #2d2d30;
                    color: #d4d4d4;
                    border: 1px solid #464647;
                    padding: 2px;
                }
                QMenu::item {
                    padding: 5px 20px 5px 25px;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: #0e639c;
                    color: white;
                }
                QStatusBar {
                    background-color: #252526;
                    color: #cccccc;
                    border-top: 1px solid #3e3e42;
                }
            """
        else:
            app_style = """
                QMainWindow {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QMenuBar {
                    background-color: #f0f0f0;
                    color: #333333;
                    padding: 5px 0;
                    border-bottom: 1px solid #e0e0e0;
                }
                QMenuBar::item {
                    padding: 5px 10px;
                    color: #333333;
                    background-color: transparent;
                }
                QMenuBar::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QMenu {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #e0e0e0;
                    padding: 2px;
                }
                QMenu::item {
                    padding: 5px 20px 5px 25px;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QStatusBar {
                    background-color: #f0f0f0;
                    color: #555555;
                    border-top: 1px solid #e0e0e0;
                }
            """
        
        self.setStyleSheet(app_style)
        
        # 更新标签页样式
        self.updateTabWidgetStyle()
        
        # 更新所有编辑器的主题
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, CodeEditor):
                widget.is_dark_theme = self.is_dark_theme
                widget.updateTheme()
            elif isinstance(widget, StartPage):
                # 更新起始页主题
                if self.is_dark_theme:
                    widget.setStyleSheet("background-color: #252526;")
                    for child in widget.findChildren(QLabel):
                        if child.text() == "Toratail":
                            child.setStyleSheet("color: #3498db;")
                        else:
                            child.setStyleSheet("color: #bbbbbb;")
                else:
                    widget.setStyleSheet("background-color: #f8f9fa;")
                    for child in widget.findChildren(QLabel):
                        if child.text() == "Toratail":
                            child.setStyleSheet("color: #3498db;")
                        else:
                            child.setStyleSheet("color: #7f8c8d;")

    def updateTabWidgetStyle(self):
        if self.is_dark_theme:
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #3e3e42;
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

    def create_menus(self):
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        new_action = QAction("新建", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("编辑")
        
        cut_action = QAction("剪切", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("复制", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("查找", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        # 设置菜单
        settings_menu = self.menuBar().addMenu("设置")
        
        font_action = QAction("字体设置", self)
        font_action.triggered.connect(self.change_font)
        settings_menu.addAction(font_action)
        
        # 主题切换菜单
        theme_menu = settings_menu.addMenu("主题")
        
        light_theme_action = QAction("浅色主题", self)
        light_theme_action.setCheckable(True)
        light_theme_action.setChecked(not self.is_dark_theme)
        light_theme_action.triggered.connect(self.switch_to_light_theme)
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("深色主题", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.setChecked(self.is_dark_theme)
        dark_theme_action.triggered.connect(self.switch_to_dark_theme)
        theme_menu.addAction(dark_theme_action)

    def create_toolbar(self):
        toolbar = QToolBar("工具栏", self)
        self.addToolBar(toolbar)
        
        # 设置工具栏样式
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
        
        # 创建工具栏按钮
        new_action = QAction("新建", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        cut_action = QAction("剪切", self)
        cut_action.triggered.connect(self.cut)
        toolbar.addAction(cut_action)
        
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(self.copy)
        toolbar.addAction(copy_action)
        
        paste_action = QAction("粘贴", self)
        paste_action.triggered.connect(self.paste)
        toolbar.addAction(paste_action)

    def new_file(self):
        # 如果当前是起始页，则移除起始页
        if self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), StartPage):
            self.tab_widget.removeTab(0)
        
        editor = CodeEditor(is_dark_theme=self.is_dark_theme)
        editor.setFont(self.current_font)  # 使用当前设置的字体
        editor.textChanged.connect(self.on_text_changed)
        
        # 添加标签页动画
        index = self.tab_widget.addTab(editor, "未命名")
        self.tab_widget.setCurrentIndex(index)
        
        # 为新标签添加简单动画效果
        self.animateTab(index)

    def animateTab(self, index):
        # 简单的标签动画效果
        tab_bar = self.tab_widget.tabBar()
        rect = tab_bar.tabRect(index)
        animation = QPropertyAnimation(tab_bar, b"geometry")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.setStartValue(rect)
        animation.setEndValue(rect)
        animation.start()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", "所有文件 (*);;Python 文件 (*.py);;文本文件 (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # 检查是否已有相同文件的标签页
                for i in range(self.tab_widget.count()):
                    editor = self.tab_widget.widget(i)
                    if hasattr(editor, 'file_path') and editor.file_path == file_path:
                        self.tab_widget.setCurrentIndex(i)
                        return
                
                # 如果当前是起始页，则移除起始页
                if self.tab_widget.count() == 1 and isinstance(self.tab_widget.widget(0), StartPage):
                    self.tab_widget.removeTab(0)
                
                # 创建新标签页
                editor = CodeEditor(is_dark_theme=self.is_dark_theme)
                editor.setFont(self.current_font)  # 使用当前设置的字体
                editor.setPlainText(content)
                editor.file_path = file_path
                editor.textChanged.connect(self.on_text_changed)
                
                # 获取文件名作为标签
                file_name = os.path.basename(file_path)
                index = self.tab_widget.addTab(editor, file_name)
                self.tab_widget.setCurrentIndex(index)
                
                # 添加标签动画
                self.animateTab(index)
                
                self.statusBar().showMessage(f"已打开文件: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")

    def save_file(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            if editor.file_path:
                try:
                    with open(editor.file_path, 'w', encoding='utf-8') as file:
                        file.write(editor.toPlainText())
                    editor.document().setModified(False)
                    self.statusBar().showMessage(f"已保存文件: {editor.file_path}")
                    
                    # 更新标签文本（移除星号）
                    index = self.tab_widget.indexOf(editor)
                    file_name = os.path.basename(editor.file_path)
                    self.tab_widget.setTabText(index, file_name)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
            else:
                self.save_file_as()

    def save_file_as(self):
        editor = self.get_current_editor()
        if editor and not isinstance(editor, StartPage):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "另存为", "", "所有文件 (*);;Python 文件 (*.py);;文本文件 (*.txt)"
            )
            
            if file_path:
                editor.file_path = file_path
                self.save_file()
                
                # 更新标签文本
                index = self.tab_widget.indexOf(editor)
                file_name = os.path.basename(file_path)
                self.tab_widget.setTabText(index, file_name)

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

    def show_start_page(self):
        start_page = StartPage(self)
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

    def switch_to_light_theme(self):
        self.is_dark_theme = False
        self.updateGlobalTheme()
        self.statusBar().showMessage("已切换到浅色主题")

    def switch_to_dark_theme(self):
        self.is_dark_theme = True
        self.updateGlobalTheme()
        self.statusBar().showMessage("已切换到深色主题")

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