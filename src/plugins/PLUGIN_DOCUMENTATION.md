# Toratail Plugin Development Guide

This document provides detailed instructions on how to develop plugins for the Toratail code editor.

## Table of Contents
1. [Plugin System Overview](#plugin-system-overview)
2. [Plugin Interface](#plugin-interface)
3. [Creating Your First Plugin](#creating-your-first-plugin)
4. [Plugin Structure](#plugin-structure)
5. [Implementing Plugin Methods](#implementing-plugin-methods)
6. [Advanced Features](#advanced-features)
7. [Plugin Installation](#plugin-installation)
8. [Example Plugin](#example-plugin)

## Plugin System Overview

The Toratail plugin system allows developers to extend the functionality of the code editor through a well-defined interface. Plugins can add features such as syntax highlighting, theme customization, and code analysis.

## Plugin Interface

All Toratail plugins must implement the `Plugin` trait, which is defined as follows:

```rust
trait Plugin {
    fn name(&self) -> &str;
    fn version(&self) -> &str;
    fn description(&self) -> &str;
    
    // Line highlighting hook
    fn highlight_line(&self, _ui: &mut egui::Ui, _content: &str) {}
    
    // Get custom theme (optional)
    fn get_theme(&self) -> Option<CustomTheme> { None }
    
    // Theme customization hook
    fn customize_theme(&self, _theme: &mut egui::Style) {}
}
```

## Creating Your First Plugin

To create a plugin for Toratail, follow these steps:

1. Create a new Rust file in the `src/plugins/` directory
2. Implement the `Plugin` trait
3. Add your plugin to the plugin module

## Plugin Structure

A typical Toratail plugin has the following structure:

```rust
// Import necessary traits and structs
use crate::Plugin;
use crate::CustomTheme;

// Define your plugin struct
pub struct MyPlugin {
    // Plugin configuration and state
}

impl MyPlugin {
    // Constructor for your plugin
    pub fn new() -> Self {
        Self {
            // Initialize your plugin
        }
    }
    
    // Helper methods (optional)
}

// Implement the Plugin trait
impl Plugin for MyPlugin {
    fn name(&self) -> &str { "My Plugin" }
    fn version(&self) -> &str { "1.0.0" }
    fn description(&self) -> &str { "Description of my plugin" }
    
    // Override other methods as needed
}
```

## Implementing Plugin Methods

### Basic Information Methods

These methods provide basic information about your plugin:

- **name()**: Returns the name of your plugin
- **version()**: Returns the version of your plugin
- **description()**: Returns a description of your plugin

### Line Highlighting

The `highlight_line` method allows your plugin to highlight code in the editor:

```rust
fn highlight_line(&self, ui: &mut egui::Ui, content: &str) {
    // Use ui.painter() to draw highlights
    // Example: ui.painter().rect_filled(rect, 0.0, color);
}
```

### Theme Customization

Your plugin can provide a custom theme using the `get_theme` method:

```rust
fn get_theme(&self) -> Option<CustomTheme> {
    Some(CustomTheme {
        text_color: egui::Color32::from_rgb(220, 220, 220),
        background_color: egui::Color32::from_rgb(30, 30, 30),
    })
}
```

You can also customize the editor's style using the `customize_theme` method:

```rust
fn customize_theme(&self, theme: &mut egui::Style) {
    // Modify the theme
    // Example: theme.visuals.widgets.inactive.fg_stroke.color = Color32::WHITE;
}
```

## Advanced Features

### Code Analysis

Your plugin can analyze the code content in the `highlight_line` method. This allows you to implement features such as:
- Syntax checking
- Code completion suggestions
- Error highlighting

### UI Customization

You can use the `ui` parameter in the `highlight_line` method to draw custom UI elements in the editor.

## Plugin Installation

In the current implementation, plugins are added directly to the `plugins` module and loaded by the `PluginManager` during initialization. Future versions may support dynamic loading of plugins from external files.

To add your plugin to the editor:

1. Add your plugin to the `src/plugins/mod.rs` file:
   ```rust
   pub mod my_plugin;
   ```

2. Update the `PluginManager::new` method in `main.rs` to include your plugin:
   ```rust
   plugins.push(Arc::new(plugins::my_plugin::MyPlugin::new()));
   ```

## Example Plugin

For a complete example, see the `ExamplePlugin` implementation in `src/plugins/example_plugin.rs`.

This example plugin demonstrates all available plugin features, including:
- Syntax highlighting
- Theme customization
- Code analysis

---

By following this guide, you can create powerful plugins to extend the functionality of the Toratail code editor. If you have any questions or need further assistance, please refer to the example plugin or contact the development team.