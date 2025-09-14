use eframe::{App, CreationContext, NativeOptions, egui, run_native};
use egui::{Context, ScrollArea, SidePanel, Color32};
use std::path::{Path, PathBuf};
use std::fs;
use std::sync::Arc;

// 导入plugins模块
mod plugins;

// Import necessary traits for font loading
use eframe::epaint::FontFamily;
use eframe::epaint::text::FontId;

// Define plugin interface
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

// Define custom theme struct
struct CustomTheme {
    text_color: Color32,
    background_color: Color32,
}

// Sample plugin implementation
struct HighlightKeywordPlugin {
    keywords: Vec<String>,
    highlight_color: Color32,
}

impl HighlightKeywordPlugin {
    fn new() -> Self {
        Self {
            keywords: vec!["fn".to_string(), "let".to_string(), "if".to_string(), "else".to_string(), "return".to_string()],
            highlight_color: Color32::from_rgb(255, 165, 0), // Orange color
        }
    }
}

impl Plugin for HighlightKeywordPlugin {
    fn name(&self) -> &str { "Keyword Highlighter" }
    fn version(&self) -> &str { "1.0.0" }
    fn description(&self) -> &str { "Highlights programming keywords in code" }
    
    // Custom implementation of line highlighting
    fn highlight_line(&self, _ui: &mut egui::Ui, content: &str) {
        // Simple keyword highlighting logic
        for line in content.lines() {
            for keyword in &self.keywords {
                if line.contains(&format!(" {}", keyword)) || line.starts_with(&format!("{}", keyword)) {
                    // In a real implementation, we would use egui's painting API to draw highlights
                    // This is a simplified placeholder
                    break;
                }
            }
        }
    }
}

// Define plugin manager
struct PluginManager {
    plugins: Vec<Arc<dyn Plugin + Send + Sync>>,
    show_install_dialog: bool,
    plugin_path: String,
}

impl PluginManager {
    fn new() -> Self {
        let mut plugins: Vec<Arc<dyn Plugin + Send + Sync>> = Vec::new();
        
        // Add built-in sample plugin
        plugins.push(Arc::new(HighlightKeywordPlugin::new()));
        
        // Add example rich plugin (showcase all plugin capabilities)
        plugins.push(Arc::new(plugins::example_plugin::ExamplePlugin::new()));
        
        Self {
            plugins,
            show_install_dialog: false,
            plugin_path: String::new(),
        }
    }
    
    // Install plugin from disk
    fn install_plugin(&mut self, path: &Path) {
        // In a real implementation, we would load a dynamic library
        // For this example, we'll just simulate plugin installation
        println!("Attempting to install plugin from: {}", path.display());
        
        // For demonstration purposes, we'll treat any .rs file as a potential plugin
        if path.extension().map_or(false, |ext| ext == "rs") {
            // In a real implementation, we would validate and load the plugin
            // For now, we'll just print a message
            println!("Plugin installation simulation successful");
        }
    }
    
    // Get active theme from plugins (first one that provides a theme)
    fn get_active_theme(&self) -> Option<CustomTheme> {
        for plugin in &self.plugins {
            if let Some(theme) = plugin.get_theme() {
                return Some(theme);
            }
        }
        None
    }
}

// Define a struct for file tabs
struct Tab {
    title: String,
    content: String,
    file_path: Option<PathBuf>,
    is_dirty: bool,
}

impl Tab {
    fn new_untitled() -> Self {
        Self {
            title: "Untitled".to_string(),
            content: String::new(),
            file_path: None,
            is_dirty: false,
        }
    }
    
    fn new_with_content(title: String, content: String) -> Self {
        Self {
            title,
            content,
            file_path: None,
            is_dirty: false,
        }
    }
    
    fn get_display_title(&self) -> String {
        if self.is_dirty {
            format!("{}*", self.title)
        } else {
            self.title.clone()
        }
    }
}

// Define application state
struct CodeEditorApp {
    tabs: Vec<Tab>,
    current_tab: usize,
    show_line_numbers: bool,
    highlight_current_line: bool,
    show_indent_guides: bool,
    wrap_lines: bool,
    show_file_explorer: bool,
    current_dir: PathBuf,
    
    // Font settings
    font_family: String,
    font_size: u16,
    font_weight: u8, // 0-99 for normal to bold
    show_font_settings: bool,
    
    // Save functionality improvements
    show_save_dialog: bool,
    show_save_error: bool,
    save_error_message: String,
    auto_save_enabled: bool,
    last_auto_save_time: std::time::Instant,
    auto_save_interval: u64, // in seconds
    request_new_window: bool,
    plugin_manager: PluginManager,
}

impl CodeEditorApp {
    fn new(_cc: &CreationContext<'_>) -> Self {
        // Create initial tab with sample code
        let tabs = vec![Tab::new_with_content(
            "main.rs".to_string(),
            "fn main() {\n    println!(\"Hello, world!\");\n}\n".to_string()
        )];
        
        // Get current directory
        let current_dir = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
        
        Self {
            tabs,
            current_tab: 0,
            show_line_numbers: true,  // Enable line numbers by default
            highlight_current_line: true,
            show_indent_guides: true,
            wrap_lines: true,
            show_file_explorer: true, // Show file explorer by default
            current_dir,
            
            // Initialize font settings with default values
            font_family: "Monospace".to_string(),
            font_size: 14,
            font_weight: 40, // Normal weight
            show_font_settings: false,
            
            // Initialize save functionality fields
            show_save_dialog: false,
            show_save_error: false,
            save_error_message: String::new(),
            auto_save_enabled: true,
            last_auto_save_time: std::time::Instant::now(),
            auto_save_interval: 30, // 30 seconds auto-save interval
            request_new_window: false,
            
            // Initialize plugin manager
            plugin_manager: PluginManager::new(),
        }
    }
    
    // Add a new tab
    fn new_tab(&mut self) {
        let new_tab = Tab::new_untitled();
        self.tabs.push(new_tab);
        self.current_tab = self.tabs.len() - 1;
    }
    
    // Close current tab
    fn close_current_tab(&mut self) {
        if self.tabs.len() <= 1 {
            // Ensure at least one tab remains
            self.tabs[0] = Tab::new_untitled();
            return;
        }
        
        self.tabs.remove(self.current_tab);
        if self.current_tab >= self.tabs.len() {
            self.current_tab = self.tabs.len() - 1;
        }
    }
    
    // Get current tab content (mutable)
    fn current_tab_content(&mut self) -> &mut String {
        &mut self.tabs[self.current_tab].content
    }
    
    // Load file from path
    fn load_file(&mut self, path: &Path) {
        if let Ok(content) = fs::read_to_string(path) {
            let title = path.file_name().unwrap().to_string_lossy().to_string();
            
            // Check if file is already open in a tab
            if let Some((index, _)) = self.tabs.iter().enumerate().find(|(_, tab)| {
                tab.file_path.as_ref().map(|p| p == path).unwrap_or(false)
            }) {
                self.current_tab = index;
            } else {
                let new_tab = Tab {
                    title,
                    content,
                    file_path: Some(path.to_path_buf()),
                    is_dirty: false,
                };
                self.tabs.push(new_tab);
                self.current_tab = self.tabs.len() - 1;
            }
        }
    }
    
    // Save current tab to file
    fn save_current_tab(&mut self) {
        let current_tab_index = self.current_tab;
        let tab_has_file_path = self.tabs[current_tab_index].file_path.is_some();
        
        if tab_has_file_path {
            let file_path = self.tabs[current_tab_index].file_path.clone().unwrap();
            let content = self.tabs[current_tab_index].content.clone();
            self.perform_save(&file_path, &content);
        } else {
            // Show save dialog if no file path is set
            self.show_save_dialog = true;
        }
    }
    
    // Perform the actual save operation
    fn perform_save(&mut self, file_path: &Path, content: &str) {
        // Create parent directories if they don't exist
        if let Some(parent_dir) = file_path.parent() {
            if !parent_dir.exists() {
                if let Err(err) = fs::create_dir_all(parent_dir) {
                    self.show_save_error = true;
                    self.save_error_message = format!("无法创建目录: {}", err);
                    return;
                }
            }
        }
        
        // Write the file with improved error handling
        match fs::write(file_path, content) {
            Ok(_) => {
                // Update tab status
                self.tabs[self.current_tab].is_dirty = false;
                
                // Update the tab title if it was previously "Untitled"
                if self.tabs[self.current_tab].title == "Untitled" {
                    if let Some(file_name) = file_path.file_name() {
                        self.tabs[self.current_tab].title = file_name.to_string_lossy().to_string();
                    }
                }
                
                // Update last auto-save time
                self.last_auto_save_time = std::time::Instant::now();
            },
            Err(err) => {
                self.show_save_error = true;
                self.save_error_message = format!("保存文件失败: {}", err);
            }
        }
    }
    
    // Auto-save functionality
    fn auto_save(&mut self) {
        if !self.auto_save_enabled {
            return;
        }
        
        // Check if enough time has passed since last auto-save
        if self.last_auto_save_time.elapsed().as_secs() >= self.auto_save_interval {
            // Only auto-save if the current tab is dirty and has a file path
            let current_tab = &self.tabs[self.current_tab];
            if current_tab.is_dirty && current_tab.file_path.is_some() {
                if let Some(ref file_path) = current_tab.file_path {
                    // Create a copy of necessary data to avoid borrowing issues
                    let file_path_copy = file_path.clone();
                    let content_copy = current_tab.content.clone();
                    
                    // Perform the save operation
                    self.perform_save(&file_path_copy, &content_copy);
                }
            }
        }
    }
    
    // Toggle file explorer visibility
    fn toggle_file_explorer(&mut self) {
        self.show_file_explorer = !self.show_file_explorer;
    }
    
    // List files in current directory
    fn list_files(&self) -> Vec<PathBuf> {
        let mut files = Vec::new();
        if let Ok(entries) = fs::read_dir(&self.current_dir) {
            for entry in entries.flatten() {
                files.push(entry.path());
            }
            // Sort files: directories first, then files
            files.sort_by(|a, b| {
                let a_is_dir = a.is_dir();
                let b_is_dir = b.is_dir();
                if a_is_dir && !b_is_dir {
                    std::cmp::Ordering::Less
                } else if !a_is_dir && b_is_dir {
                    std::cmp::Ordering::Greater
                } else {
                    a.file_name().cmp(&b.file_name())
                }
            });
        }
        files
    }
}

impl App for CodeEditorApp {
    fn update(&mut self, ctx: &Context, _frame: &mut eframe::Frame) {
        // Auto-save check
        self.auto_save();
        
        // Create menu bar
        egui::TopBottomPanel::top("menu_bar").show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                ui.menu_button("File", |ui| {
                    if ui.button("New").clicked() {
                        self.new_tab();
                        ui.close_menu();
                    }
                    if ui.button("New Tab").clicked() {
                        self.request_new_window = true;
                        ui.close_menu();
                    }
                    if ui.button("Save").clicked() {
                        self.save_current_tab();
                        ui.close_menu();
                    }
                    if ui.button("Exit").clicked() {
                        std::process::exit(0);
                    }
                });
                ui.menu_button("Edit", |ui| {
                    // In this simplified version, we only keep basic functions
                    ui.button("Undo (Ctrl+Z)").on_hover_text("Undo last operation");
                    ui.button("Redo (Ctrl+Y)").on_hover_text("Redo last operation");
                    ui.separator();
                    ui.button("Copy (Ctrl+C)").on_hover_text("Copy selected text");
                    ui.button("Cut (Ctrl+X)").on_hover_text("Cut selected text");
                    ui.button("Paste (Ctrl+V)").on_hover_text("Paste text");
                    ui.separator();
                    ui.button("Select All (Ctrl+A)").on_hover_text("Select all text");
                });
                ui.menu_button("View", |ui| {
                    ui.checkbox(&mut self.show_file_explorer, "Show File Explorer");
                    ui.checkbox(&mut self.show_line_numbers, "Show Line Numbers");
                    ui.checkbox(&mut self.highlight_current_line, "Highlight Current Line");
                    ui.checkbox(&mut self.show_indent_guides, "Show Indent Guides");
                    ui.checkbox(&mut self.wrap_lines, "Wrap Lines");
                });
                ui.menu_button("Settings", |ui| {
                        if ui.button("Font Settings").clicked() {
                            self.show_font_settings = !self.show_font_settings;
                            ui.close_menu();
                        }
                        ui.checkbox(&mut self.auto_save_enabled, "Enable Auto-save");
                        ui.label("Auto-save Interval (seconds):");
                        ui.add(egui::Slider::new(&mut self.auto_save_interval, 5..=300).text("Seconds"));
                    });
                    
                    // Plugin menu
                    ui.menu_button("Plugin", |ui| {
                        // List installed plugins
                        ui.label("Installed Plugins:");
                        ui.separator();
                        
                        for plugin in &self.plugin_manager.plugins {
                            ui.label(format!("- {} v{}", plugin.name(), plugin.version()));
                            let mut label = egui::Label::new(plugin.description());
                            ui.add_enabled(false, label);
                        }
                        
                        ui.separator();
                        
                        // Install plugin option
                        if ui.button("Install from Disk").clicked() {
                            self.plugin_manager.show_install_dialog = true;
                            ui.close_menu();
                        }
                    });
            });
        });
        
        // File Explorer Side Panel
        if self.show_file_explorer {
            SidePanel::left("file_explorer").show(ctx, |ui| {
                ui.heading("File Explorer");
                
                // Display current directory
                ui.label(format!("Current Directory: {}", self.current_dir.display()));
                ui.separator();
                
                // List files and directories
                ScrollArea::vertical().show(ui, |ui| {
                    // Back button (to parent directory)
                    if let Some(parent) = self.current_dir.parent() {
                        if ui.button("[..]").clicked() {
                            self.current_dir = parent.to_path_buf();
                        }
                    }
                    
                    // List files
                    for file in self.list_files() {
                        let file_name = file.file_name().unwrap().to_string_lossy();
                        let is_dir = file.is_dir();
                        
                        let button_text = if is_dir {
                            format!("[{}]", file_name)
                        } else {
                            file_name.to_string()
                        };
                        
                        if ui.button(button_text).clicked() {
                            if is_dir {
                                self.current_dir = file;
                            } else if file.extension().map_or(false, |ext| {
                                ext == "rs" || ext == "txt" || ext == "md" || ext == "js" || ext == "py"
                            }) {
                                self.load_file(&file);
                            }
                        }
                    }
                });
            });
        }
        
        // Tab bar
                egui::TopBottomPanel::top("tabs_bar").show(ctx, |ui| {
                    ui.horizontal(|ui| {
                        // We need to track which tabs to close
                        let mut tab_to_close = None;
                        
                        for (i, tab) in self.tabs.iter().enumerate() {
                            let tab_button = ui.button(tab.get_display_title());
                            if i == self.current_tab {
                                ui.painter().rect_stroke(
                                    tab_button.rect.expand(1.0),
                                    0.0,
                                    (1.0, egui::Color32::WHITE),
                                );
                            }
                            if tab_button.clicked() {
                                self.current_tab = i;
                            }
                            
                            // Close button for tab
                            let close_button = ui.button("✕");
                            if close_button.clicked() {
                                tab_to_close = Some(i);
                            }
                        }
                        
                        // Handle tab closing after iteration
                        if let Some(index) = tab_to_close {
                            if self.tabs.len() > 1 {
                                self.tabs.remove(index);
                                if self.current_tab >= self.tabs.len() {
                                    self.current_tab = self.tabs.len() - 1;
                                }
                            } else {
                                // Keep at least one tab
                                self.tabs[0] = Tab::new_untitled();
                            }
                        }
                        
                        // New tab button
                        if ui.button("+").clicked() {
                            self.new_tab();
                        }
                    });
                });
        
        // Main content area - code editor
        egui::CentralPanel::default().show(ctx, |ui| {
            // Show code editor
            ScrollArea::vertical().show(ui, |ui| {
                // First, make a copy of the content to avoid borrowing issues
                let content_copy = self.tabs[self.current_tab].content.clone();
                let mut new_content = content_copy.clone();
                
                // Create text edit with code editor mode
                let mut text_edit = egui::TextEdit::multiline(&mut new_content)
                    .code_editor()
                    .desired_rows(10)
                    .desired_width(f32::INFINITY);
                
                // Apply custom theme from plugins if available
                if let Some(custom_theme) = self.plugin_manager.get_active_theme() {
                    text_edit = text_edit.text_color(custom_theme.text_color);
                }
                
                // Add the text edit widget
                ui.add_sized(
                    ui.available_size(),
                    text_edit
                );
                
                // Check if the content has changed
                if content_copy != new_content {
                    self.tabs[self.current_tab].content = new_content;
                    self.tabs[self.current_tab].is_dirty = true;
                }
                
                // Apply line highlighting from plugins
                for plugin in &self.plugin_manager.plugins {
                    plugin.highlight_line(ui, &content_copy);
                }
            });
        });
        
        // Font Settings Dialog
        if self.show_font_settings {
            egui::Window::new("Font Settings")
                .resizable(false)
                .show(ctx, |ui| {
                    ui.heading("Font Preferences");
                    
                    // Font Family Selection
                    ui.label("Font Family:");
                    egui::ComboBox::from_label("")
                        .selected_text(&self.font_family)
                        .show_ui(ui, |ui| {
                            ui.selectable_value(&mut self.font_family, "Monospace".to_string(), "Monospace");
                            ui.selectable_value(&mut self.font_family, "Proportional".to_string(), "Proportional");
                        });
                    
                    // Font Size Slider
                    ui.label(format!("Font Size: {}", self.font_size));
                    ui.add(egui::Slider::new(&mut self.font_size, 8..=32).text("Size"));
                    
                    // Font Weight Slider
                    ui.label(format!("Font Weight: {}", self.font_weight));
                    ui.add(egui::Slider::new(&mut self.font_weight, 1..=99).text("Weight"));
                    
                    // Apply button
                    if ui.button("Apply").clicked() {
                        // Apply font changes to the context
                        let mut style = (*ctx.style()).clone();
                        
                        // Set the font family based on selection
                        let family = if self.font_family == "Monospace" {
                            FontFamily::Monospace
                        } else {
                            FontFamily::Proportional
                        };
                        
                        // Update the font size
                        let font_size = self.font_size as f32;
                        
                        // Update various text styles with new font settings
                        style.text_styles = [
                            (egui::TextStyle::Small, FontId::new(font_size - 2.0, family.clone())),
                            (egui::TextStyle::Body, FontId::new(font_size, family.clone())),
                            (egui::TextStyle::Button, FontId::new(font_size, family.clone())),
                            (egui::TextStyle::Heading, FontId::new(font_size + 4.0, family.clone())),
                            (egui::TextStyle::Monospace, FontId::new(font_size, FontFamily::Monospace)),
                        ].into();
                        
                        // Apply the style changes
                        ctx.set_style(style);
                        
                        // Request immediate repaint to see changes
                        ctx.request_repaint();
                    }
                    
                    // Close button
                    if ui.button("Close").clicked() {
                        self.show_font_settings = false;
                    }
                });
        }
        
        // Save Dialog
        if self.show_save_dialog {
            let mut file_path = String::new();
            let current_tab_index = self.current_tab;
            let tab_title = self.tabs[current_tab_index].title.clone();
            
            // Pre-fill with current directory and tab title
            let default_path = self.current_dir.join(&tab_title);
            
            egui::Window::new("Save As")
                .resizable(false)
                .show(ctx, |ui| {
                    ui.heading("Save File As");
                    ui.label("Enter file path:");
                    
                    // File path input
                    ui.add_sized(
                        [400.0, 24.0],
                        egui::TextEdit::singleline(&mut file_path)
                            .hint_text(&*default_path.to_string_lossy())
                    );
                    
                    ui.separator();
                    
                    ui.horizontal(|ui| {
                        if ui.button("Save").clicked() {
                            let path = if file_path.is_empty() {
                                default_path.clone()
                            } else {
                                PathBuf::from(&file_path)
                            };
                            
                            // Get content before modifying self
                            let content = self.tabs[current_tab_index].content.clone();
                            
                            // Update the tab's file path
                            self.tabs[current_tab_index].file_path = Some(path.clone());
                            
                            // Perform the save
                            self.perform_save(&path, &content);
                            
                            // Close the dialog
                            self.show_save_dialog = false;
                        }
                        
                        if ui.button("Cancel").clicked() {
                            self.show_save_dialog = false;
                        }
                    });
                });
        }
        
        // Save Error Dialog
        if self.show_save_error {
            egui::Window::new("Save Error")
                .resizable(false)
                .show(ctx, |ui| {
                    ui.heading("Error Saving File");
                    ui.label(&self.save_error_message);
                    ui.separator();
                    
                    if ui.button("OK").clicked() {
                        self.show_save_error = false;
                    }
                });
        }
        
        // Handle new window request
        if self.request_new_window {
            // Start a new instance of the application
            if let Err(_e) = std::process::Command::new(std::env::current_exe().unwrap_or_else(|_| "toratail.exe".into()))
                .spawn() {
                // If we can't start a new process, just create a new tab as fallback
                self.new_tab();
            }
            // Reset the flag regardless of whether we could start a new process
            self.request_new_window = false;
        }
        
        // Plugin Installation Dialog
        if self.plugin_manager.show_install_dialog {
            let mut selected_file = String::new();
            
            egui::Window::new("Install Plugin")
                .resizable(false)
                .show(ctx, |ui| {
                    ui.heading("Install Plugin from Disk");
                    ui.label("Select a plugin file (.rs or .dll):");
                    
                    // File path input
                    ui.add_sized(
                        [400.0, 24.0],
                        egui::TextEdit::singleline(&mut selected_file)
                            .hint_text("Path to plugin file")
                    );
                    
                    ui.separator();
                    
                    ui.horizontal(|ui| {
                        if ui.button("Browse...").clicked() {
                            // In a real application, we would open a file dialog here
                            // This is a simplified implementation
                            ui.close_menu();
                        }
                    });
                    
                    ui.separator();
                    
                    ui.horizontal(|ui| {
                        if ui.button("Install").clicked() {
                            if !selected_file.is_empty() {
                                self.plugin_manager.install_plugin(&PathBuf::from(&selected_file));
                            }
                            self.plugin_manager.show_install_dialog = false;
                        }
                        
                        if ui.button("Cancel").clicked() {
                            self.plugin_manager.show_install_dialog = false;
                        }
                    });
                });
        }
    }
}

fn main() {
    let options = NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([800.0, 600.0])
            .with_min_inner_size([400.0, 300.0]),
        ..Default::default()
    };
    
    // Start application
    run_native(
        "Toratail Code Editor",
        options,
        Box::new(|cc| Box::new(CodeEditorApp::new(cc)))
    ).expect("Failed to start application");
}
