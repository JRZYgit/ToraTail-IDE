use eframe::{App, CreationContext, NativeOptions, egui, run_native};
use egui::{Context, ScrollArea, SidePanel, Color32};
use std::path::{Path, PathBuf};
use std::fs;
use std::sync::Arc;
use rfd::FileDialog;

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
    
    // Code completion hook
    fn get_completions(&self, _content: &str, _cursor_pos: usize) -> Vec<String> { Vec::new() }
    
    // Apply code completion
    fn apply_completion(&self, _content: &mut String, _cursor_pos: &mut usize, _completion: &str) {}
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

// Demo plugin for installation demonstration
struct DemoPlugin {
    name: String,
}

impl DemoPlugin {
    fn new(name: String) -> Self {
        Self {
            name,
        }
    }
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
    fn name(&self) -> &str { "Keyword Highlighter [bundle]" }
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

// Implement Plugin trait for DemoPlugin
impl Plugin for DemoPlugin {
    fn name(&self) -> &str { &self.name }
    fn version(&self) -> &str { "1.0.0" }
    fn description(&self) -> &str { "A demonstration plugin installed from disk" }
    
    // Default implementations for other methods
}

// Define plugin manager
struct PluginManager {
    plugins: Vec<Arc<dyn Plugin + Send + Sync>>,
    plugin_enabled: Vec<bool>, // 存储每个插件的启用状态
    show_install_dialog: bool,
    show_uninstall_confirm: bool, // 控制是否显示卸载确认对话框
    plugin_path: String,
    plugin_to_uninstall: Option<usize>, // 存储要卸载的插件索引
}

impl PluginManager {
    fn new() -> Self {
        let mut plugins: Vec<Arc<dyn Plugin + Send + Sync>> = Vec::new();
        
        // Add built-in sample plugin
        plugins.push(Arc::new(HighlightKeywordPlugin::new()));
        
        // Add example rich plugin (showcase all plugin capabilities)
        plugins.push(Arc::new(plugins::example_plugin::ExamplePlugin::new()));
        
        // 初始化所有插件为启用状态
        let plugin_enabled = vec![true; plugins.len()];
        
        Self {
            plugins,
            plugin_enabled,
            show_install_dialog: false,
            show_uninstall_confirm: false,
            plugin_path: String::new(),
            plugin_to_uninstall: None,
        }
    }
    
    // Install plugin from disk
    fn install_plugin(&mut self, path: &Path) {
        // In a real implementation, we would load a dynamic library
        // For this example, we'll create a simple plugin as a demonstration
        println!("Attempting to install plugin from: {}", path.display());
        
        // For demonstration purposes, we'll treat any .rs file as a potential plugin
        if path.extension().map_or(false, |ext| ext == "rs") {
            // Create a simple demo plugin
            let demo_plugin = Arc::new(DemoPlugin::new(path.file_name().unwrap().to_string_lossy().into()));
            self.plugins.push(demo_plugin);
            self.plugin_enabled.push(true);
            println!("Plugin installation successful: Demo Plugin installed");
        }
    }
    
    // Get active theme from plugins (first enabled one that provides a theme)
    fn get_active_theme(&self) -> Option<CustomTheme> {
        for (i, plugin) in self.plugins.iter().enumerate() {
            if self.plugin_enabled[i] { // 只检查启用的插件
                if let Some(theme) = plugin.get_theme() {
                    return Some(theme);
                }
            }
        }
        None
    }
    
    // 获取插件的启用状态
    fn is_plugin_enabled(&self, index: usize) -> Option<bool> {
        if index < self.plugin_enabled.len() {
            Some(self.plugin_enabled[index])
        } else {
            None
        }
    }
    
    // 设置插件的启用状态
    fn set_plugin_enabled(&mut self, index: usize, enabled: bool) {
        if index < self.plugin_enabled.len() {
            self.plugin_enabled[index] = enabled;
        }
    }
    
    // 获取所有插件的名称和启用状态
    fn get_plugin_statuses(&self) -> Vec<(&str, &bool)> {
        self.plugins.iter()
            .zip(self.plugin_enabled.iter())
            .map(|(plugin, enabled)| (plugin.name(), enabled))
            .collect()
    }
    
    // 卸载指定索引的插件
    fn uninstall_plugin(&mut self, index: usize) {
        if index < self.plugins.len() {
            println!("Uninstalling plugin: {}", self.plugins[index].name());
            // 从向量中移除插件
            self.plugins.remove(index);
            self.plugin_enabled.remove(index);
        }
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
            title: "Untitled.txt".to_string(),
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
    // Theme settings
    current_theme: String,
    show_theme_dialog: bool,
    show_save_dialog: bool,
    show_save_error: bool,
    save_error_message: String,
    auto_save_enabled: bool,
    last_auto_save_time: std::time::Instant,
    auto_save_interval: u64, // in seconds
    request_new_window: bool,
    plugin_manager: PluginManager,
    show_plugin_manager: bool,
    
    // Welcome page state
    show_welcome_page: bool,
    selected_directory: PathBuf,
    
    // About dialog states
    show_about_dialog: bool,
    show_update_dialog: bool,
    
    // Tora language support
    show_tora_output: bool,
    tora_output: String,
    tora_toolchain_path: PathBuf,
    
    // Git functionality
    show_git_clone_dialog: bool,
    git_repo_url: String,
    git_clone_path: PathBuf,
    git_output: String,
    show_git_output: bool,
    
    // Code completion functionality
    show_completions: bool,
    completions_list: Vec<String>,
    selected_completion: usize,
    completion_trigger_pos: usize,
    completion_prefix: String,
}

impl CodeEditorApp {
    fn new(_cc: &CreationContext<'_>) -> Self {
        // Create initial tab with sample code
        let tabs = vec![Tab::new_untitled()];
        
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
            current_dir: current_dir.clone(),
            
            // Initialize font settings with default values
            font_family: "Monospace".to_string(),
            font_size: 14,
            font_weight: 40, // Normal weight
            show_font_settings: false,
            
            // Initialize theme settings
            current_theme: "Dark".to_string(),
            show_theme_dialog: false,
            
            // Initialize code completion functionality
            show_completions: false,
            completions_list: Vec::new(),
            selected_completion: 0,
            completion_trigger_pos: 0,
            completion_prefix: String::new(),
            
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
            show_plugin_manager: false,
            
            // Initialize welcome page state
            show_welcome_page: true,
            selected_directory: current_dir.clone(),
            
            // Initialize about dialog states
            show_about_dialog: false,
            show_update_dialog: false,
            
            // Initialize Tora language support
            show_tora_output: false,
            tora_output: String::new(),
            tora_toolchain_path: PathBuf::from("../toratail/.ttc/"),
            
            // Initialize Git functionality
            show_git_clone_dialog: false,
            git_repo_url: String::new(),
            git_clone_path: current_dir,
            git_output: String::new(),
            show_git_output: false,
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
                self.save_error_message = format!("Failure to save file: {}", err);
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
    
    // Run Tora code
    fn run_tora_code(&mut self) {
        // Clear previous output
        self.tora_output.clear();
        
        // Check if .ttc directory exists
        if !self.tora_toolchain_path.exists() {
            self.tora_output = format!("Error: Tora ToolChain not found at {}", self.tora_toolchain_path.display());
            self.show_tora_output = true;
            return;
        }
        
        // Create a temporary file to hold the Tora code
        let temp_dir = std::env::temp_dir();
        let temp_file = temp_dir.join("temp.tora");
        
        // Get content from current tab
        let content = self.tabs[self.current_tab].content.clone();
        
        // Write code to temporary file
        if let Err(err) = fs::write(&temp_file, content) {
            self.tora_output = format!("Error writing to temporary file: {}", err);
            self.show_tora_output = true;
            return;
        }
        
        // Run Tora interpreter using the toolchain
        let main_py_path = self.tora_toolchain_path.join("src/main.py");
        let result = std::process::Command::new("python")
            .arg(main_py_path)
            .arg(temp_file)
            .output();
        
        // Process the result
        match result {
            Ok(output) => {
                let stdout = String::from_utf8_lossy(&output.stdout);
                let stderr = String::from_utf8_lossy(&output.stderr);
                
                if !stdout.is_empty() {
                    self.tora_output.push_str(&stdout);
                }
                if !stderr.is_empty() {
                    if !self.tora_output.is_empty() {
                        self.tora_output.push_str("\n\n");
                    }
                    self.tora_output.push_str(&stderr);
                }
                
                if self.tora_output.is_empty() {
                    self.tora_output = "Program executed successfully with no output".to_string();
                }
            },
            Err(err) => {
                self.tora_output = format!("Error running Tora code: {}", err);
            }
        }
        
        // Show the output window
        self.show_tora_output = true;
    }
    
    // Render welcome page
    fn render_welcome_page(&mut self, ctx: &Context) {
        // Make sure the window is centered
        egui::CentralPanel::default().show(ctx, |ui| {
            // Calculate the center point
            let center_x = ui.available_width() / 2.0;
            let center_y = ui.available_height() / 2.0;
            
            // Create a vertical layout to center content
            ui.vertical_centered(|ui| {
                // Set a large font for the title
                ui.heading("Welcome to Toratail IDE");
                ui.add_space(20.0);
                
                // Main content area with a nice card layout
                egui::Frame::default()
                    .fill(ui.style().visuals.window_fill())
                    .stroke(ui.style().visuals.widgets.active.fg_stroke)
                    .rounding(8.0)
                    .show(ui, |ui| {
                        ui.set_min_size(egui::Vec2::new(500.0, 300.0));
                        ui.vertical_centered(|ui| {
                            ui.add_space(30.0);
                            
                            // Title
                            ui.label(egui::RichText::new("Toratail")
                                .font(egui::FontId::new(40.0, egui::FontFamily::Monospace))
                                .color(egui::Color32::from_rgb(100, 150, 255)));
                            ui.add_space(20.0);
                            
                            ui.label("Select the operation to start");
                            ui.add_space(30.0);
                            
                            // Action buttons
                            if ui.add_sized(
                                egui::Vec2::new(200.0, 40.0),
                                egui::Button::new("Open folder")
                            ).clicked() {
                                // Open folder dialog
                                if let Some(directory) = FileDialog::new().pick_folder() {
                                    self.current_dir = directory.clone();
                                    self.selected_directory = directory;
                                    self.show_welcome_page = false;
                                    self.show_file_explorer = true;
                                }
                            }
                            
                            ui.add_space(15.0);
                            
                            if ui.add_sized(
                                egui::Vec2::new(200.0, 40.0),
                                egui::Button::new("Open File")
                            ).clicked() {
                                // Open file dialog
                                if let Some(file_path) = FileDialog::new()
                                    .add_filter("All files", &["*"])
                                    .add_filter("Text files", &["txt"])
                                    .add_filter("Rust files", &["rs"])
                                    .add_filter("Markdown files", &["md"])
                                    .add_filter("JavaScript files", &["js"])
                                    .add_filter("Python files", &["py"])
                                    .add_filter("Tora files", &["tora"])
                                    .pick_file() {
                                    self.load_file(&file_path);
                                    self.show_welcome_page = false;
                                }
                            }
                            
                            ui.add_space(15.0);
                            
                            if ui.add_sized(
                                egui::Vec2::new(200.0, 40.0),
                                egui::Button::new("New File")
                            ).clicked() {
                                // Create a new tab and close welcome page
                                self.new_tab();
                                self.show_welcome_page = false;
                            }
                            
                            ui.add_space(15.0);
                            
                            if ui.add_sized(
                                egui::Vec2::new(200.0, 40.0),
                                egui::Button::new("Clone Git Repository")
                            ).clicked() {
                                // Show Git clone dialog
                                self.show_git_clone_dialog = true;
                            }
                            
                            ui.add_space(30.0);
                        });
                    });
                
                ui.add_space(20.0);
                
                // Recent files section
                ui.heading("Recent documents");
                ui.add_space(10.0);
                
                // Show recent files (if any)
                let recent_files: Vec<&str> = vec![]; // This would come from persistent storage in a real app
                
                if recent_files.is_empty() {
                    ui.label("No recent documents");
                } else {
                    ui.columns(2, |columns| {
                        for (i, file) in recent_files.iter().enumerate() {
                            let col_index = i % 2;
                            columns[col_index].horizontal(|ui| {
                                if ui.button("📄").clicked() {
                                    self.load_file(&std::path::Path::new(file));
                                    self.show_welcome_page = false;
                                }
                                ui.label(*file);
                            });
                        }
                    });
                }
            });
        });
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
    
    // Git clone repository
    fn git_clone_repo(&mut self) {
        // Clear previous output
        self.git_output.clear();
        
        // Check if repo URL is provided
        if self.git_repo_url.is_empty() {
            self.git_output = "Error: Repository URL cannot be empty".to_string();
            self.show_git_output = true;
            return;
        }
        
        // Check if clone path exists
        if !self.git_clone_path.exists() {
            // Try to create the directory if it doesn't exist
            if let Err(err) = fs::create_dir_all(&self.git_clone_path) {
                self.git_output = format!("Error creating directory: {}", err);
                self.show_git_output = true;
                return;
            }
        }
        
        // Get repository name from URL to create target directory
        let repo_name = self.get_repo_name(&self.git_repo_url);
        let target_path = self.git_clone_path.join(&repo_name);
        
        // Check if target directory already exists
        if target_path.exists() {
            self.git_output = format!("Error: Target directory '{}' already exists", target_path.display());
            self.show_git_output = true;
            return;
        }
        
        // Run git clone command
        let result = std::process::Command::new("git")
            .args(["clone", &self.git_repo_url, &target_path.to_string_lossy()])
            .output();
        
        // Process the result
        match result {
            Ok(output) => {
                let stdout = String::from_utf8_lossy(&output.stdout);
                let stderr = String::from_utf8_lossy(&output.stderr);
                
                if !stdout.is_empty() {
                    self.git_output.push_str(&stdout);
                }
                if !stderr.is_empty() {
                    if !self.git_output.is_empty() {
                        self.git_output.push_str("\n\n");
                    }
                    self.git_output.push_str(&stderr);
                }
                
                if output.status.success() {
                    // If successful, open the cloned repository in the file explorer
                    self.current_dir = target_path;
                    self.show_welcome_page = false;
                    self.show_file_explorer = true;
                }
            },
            Err(err) => {
                self.git_output = format!("Error running git command: {}. Make sure Git is installed.", err);
            }
        }
        
        // Show the output window
        self.show_git_output = true;
        // Close the clone dialog
        self.show_git_clone_dialog = false;
    }
    
    // Helper method to extract repository name from URL
    fn get_repo_name(&self, url: &str) -> String {
        // Handle different Git URL formats
        let path = if url.ends_with(".git") {
            &url[..url.len() - 4]
        } else {
            url
        };
        
        // Extract the last part of the URL
        if let Some(last_slash) = path.rfind('/') {
            path[last_slash + 1..].to_string()
        } else {
            "cloned_repo".to_string()
        }
    }
    
    // Get the word before the cursor
    fn get_word_before_cursor(&self, content: &str, cursor_pos: usize) -> (String, usize) {
        let chars: Vec<char> = content.chars().collect();
        let mut start_pos = cursor_pos;
        
        // Move back until we find a non-alphanumeric and non-underscore character
        while start_pos > 0 {
            let c = chars[start_pos - 1];
            if c.is_alphanumeric() || c == '_' || c == '.' {
                start_pos -= 1;
            } else {
                break;
            }
        }
        
        // Extract the word
        let prefix: String = chars[start_pos..cursor_pos].iter().collect();
        
        (prefix, start_pos)
    }
    
    // Get default completions based on prefix
    fn get_default_completions(&self, prefix: &str) -> Vec<String> {
        let mut completions = Vec::new();
        
        // Common Rust keywords and types
        let rust_keywords = vec![
            "fn", "let", "mut", "struct", "impl", "trait", "for", "in", "if", 
            "else", "match", "return", "loop", "while", "break", "continue", 
            "pub", "mod", "use", "extern", "crate", "self", "super", 
            "static", "const", "enum", "type", "where", "async", "await", 
            "unsafe", "dyn", "impl", "trait", "macro_rules",
        ];
        
        let rust_types = vec![
            "i8", "i16", "i32", "i64", "i128", "u8", "u16", "u32", 
            "u64", "u128", "usize", "isize", "f32", "f64", "bool", 
            "char", "String", "str", "Vec", "HashMap", "Option", 
            "Result", "Box", "Arc", "Rc", "Mutex", "RefCell", "Cell",
        ];
        
        // Filter keywords by prefix
        for keyword in rust_keywords {
            if keyword.starts_with(prefix) && keyword != prefix {
                completions.push(keyword.to_string());
            }
        }
        
        // Filter types by prefix
        for type_name in rust_types {
            if type_name.starts_with(prefix) && type_name != prefix {
                completions.push(type_name.to_string());
            }
        }
        
        // Also add some common functions
        let common_functions = vec![
            "println!", "print!", "format!", "panic!", "assert!",
            "dbg!", "vec!", "Box::new", "Vec::new", "HashMap::new",
        ];
        
        for func in common_functions {
            if func.starts_with(prefix) && func != prefix {
                completions.push(func.to_string());
            }
        }
        
        completions
    }

    // Trigger code completion manually
    fn trigger_code_completion(&mut self) {
        let current_content = self.tabs[self.current_tab].content.clone();
        
        // To simplify, we'll estimate cursor position based on content length
        let cursor_pos = current_content.len();
        
        // Get the word before cursor
        let (prefix, trigger_pos) = self.get_word_before_cursor(&current_content, cursor_pos);
        
        // Get completions from plugins
        let mut completions = Vec::new();
        for (i, plugin) in self.plugin_manager.plugins.iter().enumerate() {
            if self.plugin_manager.plugin_enabled[i] {
                let plugin_completions = plugin.get_completions(&current_content, cursor_pos);
                completions.extend(plugin_completions);
            }
        }
        
        // Add default completions if no plugin completions
        if completions.is_empty() {
            completions = self.get_default_completions(&prefix);
        }
        
        if !completions.is_empty() {
            self.show_completions = true;
            self.completions_list = completions;
            self.selected_completion = 0;
            self.completion_trigger_pos = trigger_pos;
            self.completion_prefix = prefix;
        }
    }
}

impl App for CodeEditorApp {
    fn update(&mut self, ctx: &Context, _frame: &mut eframe::Frame) {
        // If showing welcome page, render it instead of main editor
        if self.show_welcome_page {
            self.render_welcome_page(ctx);
            return;
        }
        
        // Check for Ctrl+Space key combination to trigger code completion
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::Space)) {
            self.trigger_code_completion();
        }
        
        // Auto-save check
        self.auto_save();
        
        // Check for F5 key press to run Tora code
        if ctx.input(|i| i.key_pressed(egui::Key::F5)) {
            self.run_tora_code();
        }
        
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
                    if ui.button("Start page").clicked() {
                        self.show_welcome_page = true;
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
                
                // Tools menu
                ui.menu_button("Tools", |ui| {
                    ui.menu_button("Tora Tools", |ui| {
                        if ui.button("Run Tora Code (F5)").clicked() {
                            self.run_tora_code();
                            ui.close_menu();
                        }
                    });
                    // Add Code completion menu item
                    if ui.button("Code completion (Ctrl+Space)").clicked() {
                        self.trigger_code_completion();
                        ui.close_menu();
                    }
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
                        if ui.button("Theme").clicked() {
                            self.show_theme_dialog = true;
                            ui.close_menu();
                        }
                        ui.checkbox(&mut self.auto_save_enabled, "Enable Auto-save");
                        ui.label("Auto-save Interval (seconds):");
                        ui.add(egui::Slider::new(&mut self.auto_save_interval, 5..=300).text("Seconds"));
                    });
                    
                    // About menu
                    ui.menu_button("About", |ui| {
                        if ui.button("Version").clicked() {
                            self.show_about_dialog = true;
                            ui.close_menu();
                        }
                        if ui.button("Check update").clicked() {
                            self.show_update_dialog = true;
                            ui.close_menu();
                        }
                    });
                    
                    // About dialog rendering
                    if self.show_about_dialog {
                        egui::Window::new("About Toratail IDE")
                            .resizable(false)
                            .show(ctx, |ui| {
                                ui.heading("Toratail IDE");
                                ui.add_space(10.0);
                                ui.label("Version: 1.0.0");
                                ui.label("A lightweight code editor built with Rust and egui");
                                ui.add_space(20.0);
                                if ui.button("OK").clicked() {
                                    self.show_about_dialog = false;
                                }
                            });
                    }
                    
                    // Update check dialog rendering
                    if self.show_update_dialog {
                        egui::Window::new("Check for Updates")
                            .resizable(false)
                            .show(ctx, |ui| {
                                ui.heading("Update Check");
                                ui.add_space(10.0);
                                ui.label("No updates available");
                                ui.add_space(20.0);
                                if ui.button("OK").clicked() {
                                    self.show_update_dialog = false;
                                }
                            });
                    }
                    
                    // Plugin menu
                    ui.menu_button("Plugin", |ui| {
                        // 打开插件管理器窗口
                        if ui.button("Manage Plugins").clicked() {
                            self.show_plugin_manager = true;
                            ui.close_menu();
                        }
                        
                        // Install plugin option
                        if ui.button("Install from Disk").clicked() {
                            self.plugin_manager.show_install_dialog = true;
                            ui.close_menu();
                        }
                    });
            });
        });
        
        // Plugin Manager Window
        if self.show_plugin_manager {
            egui::Window::new("Plugin Manager")
                .resizable(true)
                .default_size([450.0, 500.0])
                .show(ctx, |ui| {
                    // 标题
                    ui.heading("Installed Plugins");
                    ui.separator();
                    
                    // 创建临时向量记录状态变更和要卸载的插件索引
                    let mut plugin_changes = Vec::new();
                    let mut plugins_to_uninstall: Vec<usize> = Vec::new();
                    
                    // 使用ScrollArea确保内容不会溢出
                    egui::ScrollArea::vertical().show(ui, |ui| {
                        let plugin_count = self.plugin_manager.plugins.len();
                        
                        if plugin_count == 0 {
                            ui.label("No plugins installed.");
                        } else {
                            for i in 0..plugin_count {
                                let plugin = &self.plugin_manager.plugins[i];
                                let enabled = self.plugin_manager.plugin_enabled[i];
                                let mut temp_enabled = enabled;
                                
                                // 插件名称和版本（可勾选启用/禁用）
                                if ui.checkbox(&mut temp_enabled, format!("{} v{}", plugin.name(), plugin.version())).changed() {
                                    plugin_changes.push((i, temp_enabled));
                                }
                                
                                // 显示插件描述
                                let label = egui::Label::new(plugin.description());
                                ui.add_enabled(false, label);
                                
                                // 添加卸载按钮
                                ui.horizontal(|ui| {
                                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                                        // 确保内置插件不能被卸载
                                        let can_uninstall = i >= 1; // 假设前两个是内置插件
                                        if ui.add_enabled(can_uninstall, egui::Button::new("Uninstall")).clicked() {
                                            // 不直接卸载，而是显示确认对话框
                                            self.plugin_manager.show_uninstall_confirm = true;
                                            self.plugin_manager.plugin_to_uninstall = Some(i);
                                            ui.ctx().request_repaint();
                                        }
                                    });
                                });
                                
                                ui.separator();
                            }
                        }
                    });
                    
                    // 应用所有插件状态的变更
                    for (i, enabled) in plugin_changes {
                        self.plugin_manager.set_plugin_enabled(i, enabled);
                    }
                    
                    // 移除了旧的卸载逻辑，现在使用确认对话框
                    
                    // 底部按钮
                    ui.horizontal(|ui| {
                        ui.with_layout(egui::Layout::left_to_right(egui::Align::Center), |ui| {
                            if ui.button("Install from Disk").clicked() {
                                self.plugin_manager.show_install_dialog = true;
                            }
                            
                            // 添加弹性空间来分隔按钮
                            ui.add_space(ui.available_width() - 240.0); // 确保有足够空间
                            
                            if ui.button("Close").clicked() {
                                self.show_plugin_manager = false;
                            }
                        });
                    });
                });
        }
        
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
                                ext == "rs" || ext == "txt" || ext == "md" || ext == "js" || ext == "py" || ext == "tora"
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
                            let close_button = ui.button("x");
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
        
        // 存储编辑器位置信息
        let mut text_edit_rect = egui::Rect::NOTHING;
        
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
                let response = ui.add_sized(
                    ui.available_size(),
                    text_edit.id_source(ui.make_persistent_id("code_editor"))
                );
                
                // 保存编辑器位置
                text_edit_rect = response.rect;
                
                // Handle code completion
                let current_content = self.tabs[self.current_tab].content.clone();
                
                // To simplify, we'll estimate cursor position based on content length change
                let cursor_pos = if response.changed() {
                    // When content changes, assume cursor is at the end of the new content
                    new_content.len()
                } else {
                    // Otherwise, keep the previous cursor position
                    current_content.len()
                };
                
                // Trigger code completion on certain events
                if response.changed() {
                    // Check if the last character typed is a trigger character
                    let last_char = current_content.chars().nth(cursor_pos.saturating_sub(1));
                    if let Some(c) = last_char {
                        if c.is_alphabetic() || c == '_' || c == '.' {
                            // Get the word before cursor
                            let (prefix, trigger_pos) = self.get_word_before_cursor(&current_content, cursor_pos);
                            
                            if !prefix.is_empty() && prefix.len() >= 2 {
                                // Get completions from plugins
                                let mut completions = Vec::new();
                                for (i, plugin) in self.plugin_manager.plugins.iter().enumerate() {
                                    if self.plugin_manager.plugin_enabled[i] {
                                        let plugin_completions = plugin.get_completions(&current_content, cursor_pos);
                                        completions.extend(plugin_completions);
                                    }
                                }
                                
                                // Add default completions if no plugin completions
                                if completions.is_empty() {
                                    completions = self.get_default_completions(&prefix);
                                }
                                
                                if !completions.is_empty() {
                                    self.show_completions = true;
                                    self.completions_list = completions;
                                    self.selected_completion = 0;
                                    self.completion_trigger_pos = trigger_pos;
                                    self.completion_prefix = prefix;
                                }
                            }
                        } else if c == ' ' || c == '\n' || c == ';' {
                            // Hide completions on whitespace or semicolon
                            self.show_completions = false;
                        }
                    }
                }
                
                // Handle keyboard navigation for completions
                if self.show_completions {
                    if ui.input(|i| i.key_pressed(egui::Key::ArrowDown)) {
                        self.selected_completion = (self.selected_completion + 1) % self.completions_list.len();
                        ui.ctx().request_repaint();
                    } else if ui.input(|i| i.key_pressed(egui::Key::ArrowUp)) {
                        self.selected_completion = if self.selected_completion == 0 {
                            self.completions_list.len() - 1
                        } else {
                            self.selected_completion - 1
                        };
                        ui.ctx().request_repaint();
                    } else if ui.input(|i| i.key_pressed(egui::Key::Enter)) {
                        // Apply selected completion
                        if !self.completions_list.is_empty() {
                            let selected = &self.completions_list[self.selected_completion];
                            let mut content = self.tabs[self.current_tab].content.clone();
                            
                            // Replace the prefix with the completion
                            let start_pos = self.completion_trigger_pos;
                            let end_pos = self.completion_trigger_pos + self.completion_prefix.len();
                            
                            // Make sure the positions are valid
                            if end_pos <= content.len() {
                                // Create a new string with the completion
                                let mut new_content = String::new();
                                new_content.push_str(&content[..start_pos]);
                                new_content.push_str(selected);
                                new_content.push_str(&content[end_pos..]);
                                
                                // Update the content and mark as dirty
                                self.tabs[self.current_tab].content = new_content;
                                self.tabs[self.current_tab].is_dirty = true;
                            }
                            
                            // Hide completions after applying
                            self.show_completions = false;
                        }
                        ui.ctx().request_repaint();
                    } else if ui.input(|i| i.key_pressed(egui::Key::Escape)) {
                        self.show_completions = false;
                    }
                }
                
                // Check if the content has changed
                if content_copy != new_content {
                    self.tabs[self.current_tab].content = new_content;
                    self.tabs[self.current_tab].is_dirty = true;
                }
                
                // Apply line highlighting from enabled plugins
                for (i, plugin) in self.plugin_manager.plugins.iter().enumerate() {
                    if self.plugin_manager.plugin_enabled[i] {
                        plugin.highlight_line(ui, &content_copy);
                    }
                }
            });
        });
        
        // Show code completions if needed
        if self.show_completions {
            // 显示补全窗口在编辑器下方固定位置，而不是跟随光标移动
            if text_edit_rect != egui::Rect::NOTHING {
                // Show completions window
                let window_pos = text_edit_rect.left_top() + egui::vec2(10.0, text_edit_rect.height() + 10.0);
                let window_rect = egui::Rect::from_min_size(
                    window_pos,
                    egui::vec2(300.0, 200.0),
                );
            
                egui::Window::new("Completions")
                    .resizable(false)
                    .fixed_rect(window_rect)
                    .show(ctx, |ui| {
                        ScrollArea::vertical().show(ui, |ui| {
                            for (i, completion) in self.completions_list.iter().enumerate() {
                                let is_selected = i == self.selected_completion;
                                let response = ui.selectable_label(is_selected, completion);
                                
                                if response.clicked() {
                                    self.selected_completion = i;
                                    // Apply selected completion
                                    if !self.completions_list.is_empty() {
                                        let selected = &self.completions_list[self.selected_completion];
                                        let mut content = self.tabs[self.current_tab].content.clone();
                                        
                                        // Replace the prefix with the completion
                                        let start_pos = self.completion_trigger_pos;
                                        let end_pos = self.completion_trigger_pos + self.completion_prefix.len();
                                        
                                        // Make sure the positions are valid
                                        if end_pos <= content.len() {
                                            // Create a new string with the completion
                                            let mut new_content = String::new();
                                            new_content.push_str(&content[..start_pos]);
                                            new_content.push_str(selected);
                                            new_content.push_str(&content[end_pos..]);
                                            
                                            // Update the content and mark as dirty
                                            self.tabs[self.current_tab].content = new_content;
                                            self.tabs[self.current_tab].is_dirty = true;
                                        }
                                        
                                        // Hide completions after applying
                                        self.show_completions = false;
                                    }
                                }
                            }
                        });
                    });
            }
        };
        
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
        
        // Tora Output Window
        if self.show_tora_output {
            egui::Window::new("Tora Output")
                .resizable(true)
                .default_size([600.0, 400.0])
                .show(ctx, |ui| {
                    ui.heading("Tora Program Output");
                    ui.separator();
                    
                    // Make text area for output with limited height
                    let mut output_text = self.tora_output.clone();
                    // Set a maximum height for the text area to ensure buttons are always visible
                    let max_height = 300.0; // Adjust this value as needed
                    let available_size = ui.available_size();
                    let text_area_size = [
                        available_size.x,
                        available_size.y.min(max_height)
                    ];
                    ui.add_sized(
                            text_area_size,
                            egui::TextEdit::multiline(&mut output_text)
                                .code_editor()
                                .desired_rows(10)
                                .desired_width(f32::INFINITY)
                                .interactive(false)
                        );
                    
                    ui.separator();
                    
                    ui.horizontal(|ui| {
                        if ui.button("Run Again").clicked() {
                            self.run_tora_code();
                        }
                        
                        ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                            if ui.button("Close").clicked() {
                                self.show_tora_output = false;
                            }
                        });
                    });
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
        
        // Git Clone Dialog
        if self.show_git_clone_dialog {
            egui::Window::new("Clone Git Repository")
                .resizable(false)
                .show(ctx, |ui| {
                    ui.heading("Clone Git Repository");
                    ui.add_space(10.0);
                    
                    // Repository URL input
                    ui.label("Repository URL:");
                    ui.add_sized(
                        [400.0, 24.0],
                        egui::TextEdit::singleline(&mut self.git_repo_url)
                            .hint_text("https://github.com/username/repository.git")
                    );
                    
                    ui.add_space(10.0);
                    
                    // Clone path input
                    ui.label("Destination Path:");
                    ui.horizontal(|ui| {
                        ui.add_sized(
                            [350.0, 24.0],
                            egui::TextEdit::singleline(&mut self.git_clone_path.to_string_lossy())
                                .hint_text("Path where to clone the repository")
                        );
                        
                        if ui.button("Browse...").clicked() {
                            if let Some(directory) = FileDialog::new().pick_folder() {
                                self.git_clone_path = directory;
                            }
                        }
                    });
                    
                    ui.add_space(20.0);
                    ui.separator();
                    ui.add_space(10.0);
                    
                    ui.horizontal(|ui| {
                        ui.with_layout(egui::Layout::left_to_right(egui::Align::Center), |ui| {
                            if ui.button("Clone").clicked() {
                                self.git_clone_repo();
                            }
                            
                            // Add elastic space to push cancel button to the right
                            ui.add_space(ui.available_width() - 150.0);
                            
                            if ui.button("Cancel").clicked() {
                                self.show_git_clone_dialog = false;
                            }
                        });
                    });
                });
        }
        
        // Git Output Window
        if self.show_git_output {
            egui::Window::new("Git Output")
                .resizable(true)
                .default_size([600.0, 400.0])
                .show(ctx, |ui| {
                    ui.heading("Git Clone Output");
                    ui.separator();
                    
                    // Make text area for output with limited height
                    let mut output_text = self.git_output.clone();
                    // Set a maximum height for the text area to ensure buttons are always visible
                    let max_height = 300.0;
                    let available_size = ui.available_size();
                    let text_area_size = [
                        available_size.x,
                        available_size.y.min(max_height)
                    ];
                    ui.add_sized(
                            text_area_size,
                            egui::TextEdit::multiline(&mut output_text)
                                .code_editor()
                                .desired_rows(10)
                                .desired_width(f32::INFINITY)
                                .interactive(false)
                        );
                    
                    ui.separator();
                    
                    ui.horizontal(|ui| {
                        ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                            if ui.button("Close").clicked() {
                                self.show_git_output = false;
                            }
                        });
                    });
                });
        }
        
        // Plugin Installation Dialog
        if self.plugin_manager.show_install_dialog {
            
            egui::Window::new("Install Plugin")
                .resizable(false)
                .show(ctx, |ui| {
                    ui.heading("Install Plugin from Disk");
                    ui.label("Select a plugin file (.rs or .dll):");
                    
                    // File path input using PluginManager's plugin_path field
                    ui.add_sized(
                        [400.0, 24.0],
                        egui::TextEdit::singleline(&mut self.plugin_manager.plugin_path)
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
                            if !self.plugin_manager.plugin_path.is_empty() {
                                self.plugin_manager.install_plugin(&PathBuf::from(&self.plugin_manager.plugin_path));
                                // Clear the path after installation
                                self.plugin_manager.plugin_path.clear();
                            }
                            self.plugin_manager.show_install_dialog = false;
                        }
                        
                        if ui.button("Cancel").clicked() {
                            // Clear the path on cancel
                            self.plugin_manager.plugin_path.clear();
                            self.plugin_manager.show_install_dialog = false;
                        }
                    });
                });
        }
        
        // Plugin Uninstall Confirmation Dialog
        if self.plugin_manager.show_uninstall_confirm {
            if let Some(index) = self.plugin_manager.plugin_to_uninstall {
                if index < self.plugin_manager.plugins.len() {
                    let plugin_name = self.plugin_manager.plugins[index].name().to_string();
                    
                    egui::Window::new("Confirm Uninstall")
                        .resizable(false)
                        .show(ctx, |ui| {
                            ui.heading("Confirm Plugin Uninstall");
                            ui.label(format!("Are you sure you want to uninstall '{}'?", plugin_name));
                            ui.label("This action cannot be undone.");
                            
                            ui.separator();
                            
                            ui.horizontal(|ui| {
                                ui.spacing_mut().item_spacing.x = ui.available_width() - 120.0;
                                
                                if ui.button("Uninstall").clicked() {
                                    self.plugin_manager.uninstall_plugin(index);
                                    self.plugin_manager.show_uninstall_confirm = false;
                                    self.plugin_manager.plugin_to_uninstall = None;
                                    ui.ctx().request_repaint();
                                }
                                
                                if ui.button("Cancel").clicked() {
                                    self.plugin_manager.show_uninstall_confirm = false;
                                    self.plugin_manager.plugin_to_uninstall = None;
                                }
                            });
                        });
                }
            }
        }
        
        // Theme Dialog
        if self.show_theme_dialog {
            egui::Window::new("Theme Settings")
                .resizable(false)
                .show(ctx, |ui| {
                    ui.heading("Theme Selection");
                    ui.add_space(10.0);
                    ui.label("Select IDE theme:");
                    
                    // Theme selection combo box
                    egui::ComboBox::from_label("")
                        .selected_text(&self.current_theme)
                        .show_ui(ui, |ui| {
                            ui.selectable_value(&mut self.current_theme, "Dark".to_string(), "Dark");
                            ui.selectable_value(&mut self.current_theme, "Light".to_string(), "Light");
                        });
                    
                    ui.add_space(20.0);
                    
                    // Apply button
                    if ui.button("Apply").clicked() {
                        // Apply theme changes to the context
                        let mut style = (*ctx.style()).clone();
                        let mut visuals = style.visuals.clone();
                        
                        if self.current_theme == "Light" {
                            // Light theme settings
                            visuals.dark_mode = false;
                            visuals.panel_fill = egui::Color32::WHITE;
                            visuals.window_fill = egui::Color32::WHITE;
                            visuals.widgets.noninteractive.fg_stroke.color = egui::Color32::from_rgb(50, 50, 50);
                            visuals.widgets.active.fg_stroke.color = egui::Color32::BLACK;
                            visuals.widgets.hovered.fg_stroke.color = egui::Color32::BLACK;
                        } else {
                            // Dark theme settings
                            visuals.dark_mode = true;
                            visuals.panel_fill = egui::Color32::from_rgb(30, 30, 30);
                            visuals.window_fill = egui::Color32::from_rgb(30, 30, 30);
                            visuals.widgets.noninteractive.fg_stroke.color = egui::Color32::from_rgb(200, 200, 200);
                            visuals.widgets.active.fg_stroke.color = egui::Color32::WHITE;
                            visuals.widgets.hovered.fg_stroke.color = egui::Color32::WHITE;
                        }
                        
                        style.visuals = visuals;
                        ctx.set_style(style);
                        
                        // Request immediate repaint to see changes
                        ctx.request_repaint();
                    }
                    
                    ui.separator();
                    
                    ui.horizontal(|ui| {
                        if ui.button("Close").clicked() {
                            self.show_theme_dialog = false;
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
