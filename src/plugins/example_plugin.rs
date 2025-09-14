use eframe::egui::{Ui, Style, Color32, FontFamily, TextStyle, FontId}; // 导入必要的类型
use std::sync::Arc; // 用于线程安全

// 从主文件导入必要的结构体和特征
use crate::Plugin;
use crate::CustomTheme;

/**
 * 样例插件使用指南
 * 
 * 这个插件展示了如何实现Plugin接口的所有方法，包括：
 * 
 * 1. 基本信息提供：name, version, description
 * 2. 代码高亮功能：highlight_line
 * 3. 主题定制：get_theme 和 customize_theme
 * 
 * 如何使用此插件作为参考开发自己的插件：
 * 1. 创建一个实现Plugin trait的结构体
 * 2. 实现所有必要的方法
 * 3. 提供创建插件实例的函数
 * 
 * 插件可以访问的功能：
 * - 代码内容分析
 * - 语法高亮显示
 * - 主题颜色和样式调整
 * - UI元素自定义
 */
// 开发一个功能完整的样例插件，用于展示插件接口的使用
pub struct ExamplePlugin {
    // 插件配置数据
    enabled_features: ExampleFeatures,
    
    // 用于高亮的关键字集合
    keywords: Vec<String>,
    keyword_color: Color32,
    
    // 自定义主题
    dark_mode: bool,
}

// 插件功能配置结构体
struct ExampleFeatures {
    highlight_enabled: bool,
    theme_enabled: bool,
    indentation_helper: bool,
}

impl ExamplePlugin {
    pub fn new() -> Self {
        // 初始化插件，设置默认值
        Self {
            enabled_features: ExampleFeatures {
                highlight_enabled: true,
                theme_enabled: true,
                indentation_helper: true,
            },
            
            // Rust关键字集合
            keywords: vec![
                "fn".to_string(), "let".to_string(), "mut".to_string(), 
                "struct".to_string(), "impl".to_string(), "trait".to_string(), 
                "for".to_string(), "in".to_string(), "if".to_string(), 
                "else".to_string(), "match".to_string(), "return".to_string(),
                "loop".to_string(), "while".to_string(), "for".to_string(),
                "break".to_string(), "continue".to_string(), "pub".to_string(),
                "mod".to_string(), "use".to_string(), "extern".to_string(),
                "crate".to_string(), "self".to_string(), "super".to_string(),
                "static".to_string(), "const".to_string(), "enum".to_string(),
                "type".to_string(), "where".to_string(), "async".to_string(),
                "await".to_string(), "unsafe".to_string(), "dyn".to_string(),
                "impl".to_string(), "trait".to_string(), "macro_rules".to_string(),
            ],
            
            // 关键字高亮颜色 - 蓝色
            keyword_color: Color32::from_rgb(100, 149, 237),
            
            // 默认使用暗色主题
            dark_mode: true,
        }
    }
    
    // 插件内部方法：检查一行代码是否包含关键字
    fn contains_keyword(&self, line: &str) -> bool {
        for keyword in &self.keywords {
            if line.contains(&format!(" {}", keyword)) || 
               line.starts_with(&format!("{}", keyword)) ||
               line.contains(&format!("{}", keyword)) {
                return true;
            }
        }
        false
    }
    
    // 插件内部方法：检查缩进情况
    fn get_indentation_level(&self, line: &str) -> usize {
        let spaces = line.chars().take_while(|c| *c == ' ').count();
        let tabs = line.chars().take_while(|c| *c == '\t').count();
        
        // 假设一个tab等于4个空格
        spaces / 4 + tabs
    }
}

// 实现Plugin特征
impl Plugin for ExamplePlugin {
    // 返回插件名称
    fn name(&self) -> &str {
        "Example Rich Plugin"
    }
    
    // 返回插件版本
    fn version(&self) -> &str {
        "2.0.0"
    }
    
    // 返回插件描述
    fn description(&self) -> &str {
        "A comprehensive example plugin demonstrating all available interfaces: syntax highlighting, theme customization, and code analysis."
    }
    
    // 实现行高亮功能
    fn highlight_line(&self, _ui: &mut Ui, content: &str) {
        // 只有在功能启用时才执行高亮逻辑
        if self.enabled_features.highlight_enabled {
            // 这里是高亮逻辑的实现
            // 在实际应用中，我们会使用egui的绘图API来绘制高亮
            
            // 简单的示例：遍历每一行代码，检查是否包含关键字
            for (line_num, line) in content.lines().enumerate() {
                if self.contains_keyword(line) {
                    // 在实际应用中，我们会在这里使用ui.painter()来绘制高亮
                    // 例如：
                    // ui.painter().rect_filled(rect, 0.0, self.keyword_color);
                    
                    // 在实际应用中，我们会在这里使用ui.painter()来绘制高亮
                    // 例如：
                    // ui.painter().rect_filled(rect, 0.0, self.keyword_color);
                }
            }
        }
        
        // 缩进辅助功能
        if self.enabled_features.indentation_helper {
            for (line_num, line) in content.lines().enumerate() {
                let indent_level = self.get_indentation_level(line);
                if indent_level > 0 {
                    // 在实际应用中，我们会在这里绘制缩进辅助线
                    // 例如：
                    // ui.painter().line_segment([pos1, pos2], (1.0, self.indentation_color));
                }
            }
        }
    }
    
    // 提供自定义主题
    fn get_theme(&self) -> Option<CustomTheme> {
        // 只有在主题功能启用时才返回主题配置
        if self.enabled_features.theme_enabled {
            if self.dark_mode {
                // 暗色主题
                Some(CustomTheme {
                    text_color: Color32::from_rgb(220, 220, 220), // 浅灰色文本
                    background_color: Color32::from_rgb(30, 30, 30), // 深灰色背景
                })
            } else {
                // 亮色主题
                Some(CustomTheme {
                    text_color: Color32::from_rgb(30, 30, 30), // 深灰色文本
                    background_color: Color32::from_rgb(250, 250, 250), // 浅灰色背景
                })
            }
        } else {
            None
        }
    }
    
    // 自定义主题钩子
    fn customize_theme(&self, theme: &mut Style) {
        // 只有在主题功能启用时才执行自定义
        if self.enabled_features.theme_enabled {
            // 修改各种文本样式的字体
            let font_family = FontFamily::Monospace;
            
            // 更新文本样式
            theme.text_styles = [
                (TextStyle::Small, FontId::new(12.0, font_family.clone())),
                (TextStyle::Body, FontId::new(14.0, font_family.clone())),
                (TextStyle::Button, FontId::new(14.0, font_family.clone())),
                (TextStyle::Heading, FontId::new(18.0, font_family.clone())),
                (TextStyle::Monospace, FontId::new(14.0, FontFamily::Monospace)),
            ].into();
            
            // 根据主题模式调整颜色
            if self.dark_mode {
                // 暗色主题颜色调整
                theme.visuals.widgets.inactive.fg_stroke.color = Color32::from_rgb(200, 200, 200);
                theme.visuals.widgets.active.fg_stroke.color = Color32::from_rgb(255, 255, 255);
                theme.visuals.widgets.hovered.fg_stroke.color = Color32::from_rgb(255, 255, 255);
                
                // 调整代码编辑器相关的颜色
                theme.visuals.selection.bg_fill = Color32::from_rgb(60, 60, 180);
            } else {
                // 亮色主题颜色调整
                theme.visuals.widgets.inactive.fg_stroke.color = Color32::from_rgb(50, 50, 50);
                theme.visuals.widgets.active.fg_stroke.color = Color32::from_rgb(0, 0, 0);
                theme.visuals.widgets.hovered.fg_stroke.color = Color32::from_rgb(0, 0, 0);
                
                // 调整代码编辑器相关的颜色
                theme.visuals.selection.bg_fill = Color32::from_rgb(180, 180, 255);
            }
        }
    }
}

// 导出创建插件的函数，便于其他开发者了解如何实例化插件
pub fn create_example_plugin() -> Arc<dyn Plugin + Send + Sync> {
    Arc::new(ExamplePlugin::new())
}