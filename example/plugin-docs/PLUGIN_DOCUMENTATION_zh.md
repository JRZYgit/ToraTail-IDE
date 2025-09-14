# Toratail 插件开发指南

本文档提供了详细的指导，帮助开发者为 Toratail 代码编辑器开发插件。

## 目录
1. [插件系统概述](#插件系统概述)
2. [插件接口](#插件接口)
3. [创建你的第一个插件](#创建你的第一个插件)
4. [插件结构](#插件结构)
5. [实现插件方法](#实现插件方法)
6. [高级功能](#高级功能)
7. [插件安装](#插件安装)
8. [示例插件](#示例插件)

## 插件系统概述

Toratail 插件系统允许开发者通过定义良好的接口扩展代码编辑器的功能。插件可以添加语法高亮、主题定制和代码分析等功能。

## 插件接口

所有 Toratail 插件必须实现 `Plugin` 特质（trait），其定义如下：

```rust
trait Plugin {
    fn name(&self) -> &str;
    fn version(&self) -> &str;
    fn description(&self) -> &str;
    
    // 行高亮钩子
    fn highlight_line(&self, _ui: &mut egui::Ui, _content: &str) {}
    
    // 获取自定义主题（可选）
    fn get_theme(&self) -> Option<CustomTheme> { None }
    
    // 主题定制钩子
    fn customize_theme(&self, _theme: &mut egui::Style) {}
}
```

## 创建你的第一个插件

要为 Toratail 创建插件，请按照以下步骤操作：

1. 在 `src/plugins/` 目录中创建一个新的 Rust 文件
2. 实现 `Plugin` 特质
3. 将你的插件添加到插件模块

## 插件结构

一个典型的 Toratail 插件具有以下结构：

```rust
// 导入必要的特质和结构体
use crate::Plugin;
use crate::CustomTheme;

// 定义你的插件结构体
pub struct MyPlugin {
    // 插件配置和状态
}

impl MyPlugin {
    // 插件构造函数
    pub fn new() -> Self {
        Self {
            // 初始化你的插件
        }
    }
    
    // 辅助方法（可选）
}

// 实现 Plugin 特质
impl Plugin for MyPlugin {
    fn name(&self) -> &str { "我的插件" }
    fn version(&self) -> &str { "1.0.0" }
    fn description(&self) -> &str { "我的插件描述" }
    
    // 根据需要重写其他方法
}
```

## 实现插件方法

### 基本信息方法

这些方法提供关于插件的基本信息：

- **name()**: 返回插件的名称
- **version()**: 返回插件的版本
- **description()**: 返回插件的描述

### 行高亮

`highlight_line` 方法允许你的插件在编辑器中高亮代码：

```rust
fn highlight_line(&self, ui: &mut egui::Ui, content: &str) {
    // 使用 ui.painter() 绘制高亮
    // 示例：ui.painter().rect_filled(rect, 0.0, color);
}
```

### 主题定制

你的插件可以使用 `get_theme` 方法提供自定义主题：

```rust
fn get_theme(&self) -> Option<CustomTheme> {
    Some(CustomTheme {
        text_color: egui::Color32::from_rgb(220, 220, 220),
        background_color: egui::Color32::from_rgb(30, 30, 30),
    })
}
```

你还可以使用 `customize_theme` 方法自定义编辑器的样式：

```rust
fn customize_theme(&self, theme: &mut egui::Style) {
    // 修改主题
    // 示例：theme.visuals.widgets.inactive.fg_stroke.color = Color32::WHITE;
}
```

## 高级功能

### 代码分析

你的插件可以在 `highlight_line` 方法中分析代码内容。这使你能够实现以下功能：
- 语法检查
- 代码补全建议
- 错误高亮

### UI 定制

你可以使用 `highlight_line` 方法中的 `ui` 参数在编辑器中绘制自定义 UI 元素。

## 插件安装

在当前实现中，插件直接添加到 `plugins` 模块并由 `PluginManager` 在初始化期间加载。未来版本可能支持从外部文件动态加载插件。

要将你的插件添加到编辑器：

1. 将你的插件添加到 `src/plugins/mod.rs` 文件中：
   ```rust
   pub mod my_plugin;
   ```

2. 更新 `main.rs` 中的 `PluginManager::new` 方法以包含你的插件：
   ```rust
   plugins.push(Arc::new(plugins::my_plugin::MyPlugin::new()));
   ```

## 示例插件

完整的示例，请参见 `src/plugins/example_plugin.rs` 中的 `ExamplePlugin` 实现。

这个示例插件展示了所有可用的插件功能，包括：
- 语法高亮
- 主题定制
- 代码分析

---

通过遵循本指南，你可以创建强大的插件来扩展 Toratail 代码编辑器的功能。如果你有任何问题或需要进一步的帮助，请参考示例插件或联系开发团队。