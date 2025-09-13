# Toratail 代码编辑器更新日志

## [0.2.0] - 2025-09-13 - Preview

### 新增功能

#### 字体设置功能
- 在Settings菜单下添加了"Font Settings"子菜单选项
- 实现了完整的字体设置对话框，包含以下选项：
  - 字体家族选择下拉框（支持Monospace、Serif、Sans-serif等）
  - 字体大小滑块（可在8-32之间调节）
  - 字体权重滑块（可在1-99之间调节）
  - 应用和关闭按钮
- 字体设置即时生效，无需重启应用

### 优化改进

#### 保存功能系统性优化
- 重构了文件保存逻辑，提高了性能和稳定性
- 添加了自动保存功能，默认每30秒自动保存修改过的文件
- 在Settings菜单中添加了自动保存配置选项：
  - 自动保存开关
  - 自动保存时间间隔滑块（可在5-300秒之间调节）
- 增强了错误处理机制，添加了详细的保存错误提示对话框
- 改进了保存路径处理，支持自动创建父目录

#### 用户体验提升
- 优化了菜单栏的响应速度和交互体验
- 改进了文件对话框的路径提示功能
- 增强了应用程序的稳定性和响应性

### 功能调整

#### "New Tab"功能调整
- 将File菜单下的"New Tab"功能从创建新标签页调整为开启一个新窗口
- 添加了优雅的失败处理，在无法启动新窗口时会回退到创建新标签页
- 保留了原有的"New"功能继续提供创建新标签页的选项

### 代码优化

#### 重构与改进
- 重构了应用状态管理，使代码更加模块化和可维护
- 优化了内存使用和资源管理
- 改进了错误处理和异常情况的处理逻辑
- 修复了多处可变借用问题，提高了代码的安全性

#### 编译优化
- 解决了未使用变量和未使用函数的警告
- 优化了导入语句结构，减少了重复导入

***

# Toratail 代码编辑器

## 项目简介
Toratail 是一个基于 Rust 和 eframe/egui 开发的现代化代码编辑器，专为提高编程效率和提供舒适的开发体验而设计。它结合了简洁的用户界面与强大的功能，适合各种规模的编程项目。

## 项目目的
本项目旨在创建一个轻量级但功能完备的代码编辑器，提供良好的代码编辑体验，同时保持界面简洁、响应迅速，让开发者能够专注于代码编写。

## 安装指南

### 前提条件
- Rust 1.70 或更高版本
- Cargo 包管理器

### 安装步骤
1. 克隆或下载项目代码到本地
2. 进入项目目录
   ```bash
   cd toratail
   ```
3. 构建项目
   ```bash
   cargo build
   ```
4. 运行编辑器
   ```bash
   cargo run
   ```

## 使用指南

### 基本操作
- **新建文件**：点击顶部菜单栏的 "Files" -> "New" 或使用快捷键 Ctrl+N
- **打开文件**：点击 "Files" -> "Open" 或使用快捷键 Ctrl+O
- **保存文件**：点击 "Files" -> "Save" 或使用快捷键 Ctrl+S
- **保存为**：点击 "Files" -> "Save As" 或使用快捷键 Ctrl+Shift+S
- **关闭文件**：点击标签页右侧的 "x" 按钮或使用快捷键 Ctrl+W

### 编辑功能
- **剪切**：Ctrl+X
- **复制**：Ctrl+C
- **粘贴**：Ctrl+V
- **查找**：Ctrl+F
- **撤销**：Ctrl+Z
- **重做**：Ctrl+Y

### 设置选项
- **字体设置**：点击 "Setting" -> "Font" 可以打开字体选择对话框
- **主题切换**：点击 "Setting" -> "Theme" 可以选择暗色或亮色主题

## 主要功能

1. **多标签页管理**：支持同时打开和编辑多个文件，通过标签页快速切换
2. **语法高亮**：支持代码的语法高亮，提高代码可读性
3. **行号显示**：显示代码行号，方便定位和参考
4. **智能缩进**：自动处理代码缩进，保持代码整洁
5. **主题切换**：提供深色和浅色两种主题，适应不同的使用环境和个人偏好
6. **字体自定义**：支持选择和调整编辑器字体，满足不同用户的需求
7. **文件操作**：支持新建、打开、保存、另存为等基本文件操作
8. **多窗口支持**：通过"New Tab"功能可以打开新窗口进行编辑
9. **自动保存**：支持配置自动保存功能，防止代码丢失
10. **文件资源管理器**：侧边栏文件浏览功能，方便文件管理
11. **保存优化**：改进的保存功能，包含错误处理和用户提示
12. **响应式设计**：界面元素自动适应窗口大小变化

## 依赖项
- eframe：基于 egui 的应用框架，用于构建图形用户界面
- egui_code_editor：egui 的代码编辑器组件
- egui_extras：egui 的额外组件

## 配置要求
- 操作系统：Windows、macOS 或 Linux
- Rust 1.70 或更高版本
- 建议至少 2GB 内存以确保流畅运行

## 项目结构
```
toratail/
├── .gitignore      # Git 忽略文件配置
├── .ttc/           # Toratail 编译器相关文件
├── Cargo.lock      # 依赖版本锁定文件
├── Cargo.toml      # Rust 项目配置文件
├── CHANGELOG.md    # 更新日志
├── README.md       # 项目说明文档
├── icons/          # 图标资源文件夹
│   ├── icon-beta.ico
│   ├── icon-pre.ico
│   └── icon.ico
├── open.png
└── src/            # 源代码目录
    └── main.rs     # 主程序文件
```

## 开发说明
如需对项目进行扩展或修改，请按照以下步骤操作：
1. 确保已安装所有依赖项
2. 修改 src/main.rs 文件中的相关代码
3. 使用 `cargo build` 构建项目并检查错误
4. 使用 `cargo run` 测试更改以确保功能正常

## 问题反馈
如有任何问题或建议，请在项目仓库中提交 issue，我们将尽快回复和处理。

---

# Toratail Code Editor

## Project Introduction
Toratail is a modern code editor developed based on Rust and eframe/egui, designed to improve programming efficiency and provide a comfortable development experience. It combines a clean user interface with powerful features, suitable for programming projects of all sizes.

## Project Purpose
This project aims to create a lightweight yet fully functional code editor that provides a good code editing experience while maintaining a clean interface and responsive performance, allowing developers to focus on code writing.

## Installation Guide

### Prerequisites
- Rust 1.70 or higher
- Cargo package manager

### Installation Steps
1. Clone or download the project code to your local machine
2. Navigate to the project directory
   ```bash
   cd toratail
   ```
3. Build the project
   ```bash
   cargo build
   ```
4. Run the editor
   ```bash
   cargo run
   ```

## Usage Guide

### Basic Operations
- **New File**: Click "Files" -> "New" in the top menu bar or use the shortcut Ctrl+N
- **Open File**: Click "Files" -> "Open" or use the shortcut Ctrl+O
- **Save File**: Click "Files" -> "Save" or use the shortcut Ctrl+S
- **Save As**: Click "Files" -> "Save As" or use the shortcut Ctrl+Shift+S
- **Close File**: Click the "x" button on the right side of the tab or use the shortcut Ctrl+W

### Editing Features
- **Cut**: Ctrl+X
- **Copy**: Ctrl+C
- **Paste**: Ctrl+V
- **Find**: Ctrl+F
- **Undo**: Ctrl+Z
- **Redo**: Ctrl+Y

### Setting Options
- **Font Setting**: Click "Setting" -> "Font" to open the font selection dialog
- **Theme Switching**: Click "Setting" -> "Theme" to select dark or light theme

## Key Features

1. **Multi-tab Management**: Supports opening and editing multiple files simultaneously, with quick switching via tabs
2. **Syntax Highlighting**: Supports code syntax highlighting to improve code readability
3. **Line Number Display**: Shows code line numbers for easy location and reference
4. **Smart Indentation**: Automatically handles code indentation to keep code clean
5. **Theme Switching**: Provides dark and light themes to adapt to different usage environments and personal preferences
6. **Font Customization**: Supports selecting and adjusting editor fonts to meet different user needs
7. **File Operations**: Supports basic file operations such as new, open, save, save as, etc.
8. **Multi-window Support**: Open new windows for editing via the "New Tab" feature
9. **Auto-save**: Configurable auto-save functionality to prevent code loss
10. **File Explorer**: Sidebar file browsing functionality for easy file management
11. **Save Optimization**: Improved save functionality with error handling and user prompts
12. **Responsive Design**: Interface elements automatically adapt to window size changes

## Dependencies
- eframe: Application framework based on egui for building graphical user interfaces
- egui_code_editor: Code editor component for egui
- egui_extras: Additional components for egui

## Configuration Requirements
- Operating System: Windows, macOS or Linux
- Rust 1.70 or higher
- At least 2GB of memory is recommended for smooth operation

## Project Structure
```
toratail/
├── .gitignore      # Git ignore file configuration
├── .ttc/           # Toratail compiler related files
├── Cargo.lock      # Dependency version lock file
├── Cargo.toml      # Rust project configuration file
├── CHANGELOG.md    # Change log
├── README.md       # Project documentation
├── icons/          # Icon resource folder
│   ├── icon-beta.ico
│   ├── icon-pre.ico
│   └── icon.ico
├── open.png
└── src/            # Source code directory
    └── main.rs     # Main program file
```

## Development Notes
To extend or modify the project, please follow these steps:
1. Ensure all dependencies are installed
2. Modify the relevant code in the src/main.rs file
3. Use `cargo build` to build the project and check for errors
4. Use `cargo run` to test changes to ensure functionality works properly

## Feedback
If you have any questions or suggestions, please submit an issue in the project repository and we will reply and process it as soon as possible.
