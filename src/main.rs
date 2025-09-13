use eframe::{run_native, App, CreationContext, NativeOptions};
use eframe::egui;
use egui::{Context, ScrollArea, SidePanel};
use std::path::{Path, PathBuf};
use std::fs;

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
        // Get content before borrowing file_path
        let content = self.tabs[self.current_tab].content.clone();
        
        if let Some(ref file_path) = self.tabs[self.current_tab].file_path {
            if let Err(err) = fs::write(file_path, &content) {
                // In a real app, you would show an error message here
                eprintln!("Failed to save file: {}", err);
            } else {
                self.tabs[self.current_tab].is_dirty = false;
            }
        } else {
            // In a real app, you would show a save dialog here
            // For now, we just simulate saving to a temp file
            let file_path = PathBuf::from(&self.tabs[self.current_tab].title);
            if let Err(err) = fs::write(&file_path, &content) {
                eprintln!("Failed to save file: {}", err);
            } else {
                self.tabs[self.current_tab].file_path = Some(file_path);
                self.tabs[self.current_tab].is_dirty = false;
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
        // Create menu bar
        egui::TopBottomPanel::top("menu_bar").show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                ui.menu_button("File", |ui| {
                    if ui.button("New").clicked() {
                        self.new_tab();
                        ui.close_menu();
                    }
                    if ui.button("New Tab").clicked() {
                        self.new_tab();
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
                ui.menu_button("Settings", |_ui| {
                    // Additional settings can be added here
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
                // Create text edit with code editor mode
                // Note: In this version of egui, line numbers require a custom implementation
                // and word wrapping is handled differently
                let text_edit = egui::TextEdit::multiline(self.current_tab_content())
                    .code_editor()
                    .desired_rows(10)
                    .desired_width(f32::INFINITY);
                
                // Apply text wrapping settings if available
                // In egui 0.26.x, word wrapping is often controlled by the layout or context
                
                ui.add_sized(
                    ui.available_size(),
                    text_edit
                );
                
                // Mark the tab as dirty if content has changed
                if !self.tabs[self.current_tab].is_dirty {
                    self.tabs[self.current_tab].is_dirty = true;
                }
            });
        });
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
