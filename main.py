
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import re
import subprocess
import platform

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Editor")
        self.root.geometry("1000x600")
        
        # Theme colors
        self.themes = {
            "dark": {
                "bg_color": "#1c1c1c",         # Matte black
                "text_color": "#dcdcdc",       # Light gray
                "menu_bg": "#252525",          # Slightly lighter black
                "line_number_bg": "#252525",
                "line_number_fg": "#808080",   # Gray
                "status_bar_bg": "#252525",
                "keyword_color": "#569CD6",    # Blue
                "string_color": "#CE9178",     # Orange-red
                "comment_color": "#6A9955",    # Green
                "function_color": "#DCDCAA",   # Yellow
                "number_color": "#B5CEA8",     # Light green
                "selector_color": "#D7BA7D",   # Gold
            },
            "light": {
                "bg_color": "#ffffff",         # White
                "text_color": "#000000",       # Black
                "menu_bg": "#f0f0f0",          # Light gray
                "line_number_bg": "#f0f0f0",
                "line_number_fg": "#606060",   # Dark gray
                "status_bar_bg": "#f0f0f0",
                "keyword_color": "#0000ff",    # Blue
                "string_color": "#a31515",     # Red
                "comment_color": "#008000",    # Green
                "function_color": "#795e26",   # Brown
                "number_color": "#098658",     # Dark green
                "selector_color": "#800080",   # Purple
            }
        }
        
        # Current theme
        self.current_theme = "dark"
        
        # Variables
        self.current_file = None
        self.modified = False
        self.current_language = '.py'  # Default language
        self.current_font_size = 12
        
        # Language syntax highlighting patterns
        self.syntax_patterns = {
            '.py': {
                'keywords': r'\b(and|as|assert|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b',
                'strings': r'(\'\'\'.*?\'\'\'|\"\"\".*?\"\"\"|\'.*?\'|\".*?\")',
                'comments': r'(#.*)',
                'functions': r'(?<=def\s)(\w+)(?=\()',
                'numbers': r'\b(\d+)\b',
            },
            '.bat': {
                'keywords': r'\b(echo|set|if|else|for|goto|call|exit|rem|cd|dir|type|copy|del|move)\b',
                'strings': r'(\'.*?\'|\".*?\")',
                'comments': r'(rem\s.*|::.*)$',
                'functions': r'(:\w+)',
            },
            '.cmd': {
                'keywords': r'\b(echo|set|if|else|for|goto|call|exit|rem|cd|dir|type|copy|del|move)\b',
                'strings': r'(\'.*?\'|\".*?\")',
                'comments': r'(rem\s.*|::.*)$',
                'functions': r'(:\w+)',
            },
            '.cpp': {
                'keywords': r'\b(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)\b',
                'strings': r'(\'.*?\'|\".*?\")',
                'comments': r'(//.*|/\*.*?\*/)',
                'functions': r'(\w+)(?=\s*\()',
                'numbers': r'\b(\d+)\b',
            },
            '.cs': {
                'keywords': r'\b(abstract|as|base|bool|break|byte|case|catch|char|checked|class|const|continue|decimal|default|delegate|do|double|else|enum|event|explicit|extern|false|finally|fixed|float|for|foreach|goto|if|implicit|in|int|interface|internal|is|lock|long|namespace|new|null|object|operator|out|override|params|private|protected|public|readonly|ref|return|sbyte|sealed|short|sizeof|stackalloc|static|string|struct|switch|this|throw|true|try|typeof|uint|ulong|unchecked|unsafe|ushort|using|virtual|void|volatile|while)\b',
                'strings': r'(\'.*?\'|\".*?\")',
                'comments': r'(//.*|/\*.*?\*/)',
                'functions': r'(\w+)(?=\s*\()',
                'numbers': r'\b(\d+)\b',
            },
            '.js': {
                'keywords': r'\b(break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|finally|for|function|if|import|in|instanceof|new|return|super|switch|this|throw|try|typeof|var|void|while|with|yield)\b',
                'strings': r'(\'.*?\'|\".*?\"|\`.*?\`)',
                'comments': r'(//.*|/\*.*?\*/)',
                'functions': r'(\w+)(?=\s*\()',
                'numbers': r'\b(\d+)\b',
            },
            '.html': {
                'keywords': r'(<[^>]*>)',
                'strings': r'(\'.*?\'|\".*?\")',
                'comments': r'(<!--.*?-->)',
            },
            '.css': {
                'keywords': r'(@media|@keyframes|@font-face|@import|[a-z-]+\s*:)',
                'strings': r'(\'.*?\'|\".*?\")',
                'comments': r'(/\*.*?\*/)',
                'selectors': r'([.#][\w-]+)',
            },
        }
        
        # Default extension
        self.default_ext = '.py'
        
        # Apply initial theme
        self.apply_theme()
        
        # Create Menu
        self.create_menu()
        
        # Create Editor Area with Line Numbers
        self.create_editor_with_line_numbers()
        
        # Create Status Bar
        self.create_status_bar()
        
        # Set up key bindings
        self.setup_key_bindings()
        
        # Initialize with empty file
        self.new_file()

        # If a file was passed via command-line (e.g., Open With), open it
        if len(sys.argv) > 1:
            file_to_open = sys.argv[1]
            if os.path.isfile(file_to_open):
                self.open_specific_file(file_to_open)
        
        # Set focus to the text editor
        self.text_editor.focus_set()

    def apply_theme(self):
        # Get current theme colors
        theme = self.themes[self.current_theme]
        
        # Apply to root window
        self.root.configure(bg=theme["bg_color"])
        
        # Store theme colors as instance variables
        self.bg_color = theme["bg_color"]
        self.text_color = theme["text_color"]
        self.menu_bg = theme["menu_bg"]
        self.line_number_bg = theme["line_number_bg"]
        self.line_number_fg = theme["line_number_fg"]
        self.status_bar_bg = theme["status_bar_bg"]
        
        # Update UI if it exists
        if hasattr(self, 'text_editor'):
            self.text_editor.config(bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color)
            self.line_numbers.config(bg=self.line_number_bg, fg=self.line_number_fg)
            self.status_bar.config(bg=self.status_bar_bg)
            self.status_text.config(bg=self.status_bar_bg, fg=self.text_color)
            self.line_col_text.config(bg=self.status_bar_bg, fg=self.text_color)
            self.language_text.config(bg=self.status_bar_bg, fg=self.text_color)
            self.theme_text.config(bg=self.status_bar_bg, fg=self.text_color)
            
            # Re-apply syntax highlighting
            self.apply_syntax_highlighting()

    def toggle_theme(self):
        # Toggle between light and dark themes
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        
        # Update theme display in status bar
        self.theme_text.config(text=f"Theme: {self.current_theme.capitalize()}")
        
        # Apply the new theme
        self.apply_theme()

    def create_menu(self):
        # Menu bar
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Language menu
        language_menu = tk.Menu(menu_bar, tearoff=0)
        language_menu.add_command(label="Python", command=lambda: self.set_language('.py'))
        language_menu.add_command(label="C++", command=lambda: self.set_language('.cpp'))
        language_menu.add_command(label="C#", command=lambda: self.set_language('.cs'))
        language_menu.add_command(label="JavaScript", command=lambda: self.set_language('.js'))
        language_menu.add_command(label="HTML", command=lambda: self.set_language('.html'))
        language_menu.add_command(label="CSS", command=lambda: self.set_language('.css'))
        menu_bar.add_cascade(label="Language", menu=language_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        settings_menu.add_separator()
        settings_menu.add_command(label="Preferences...", command=self.open_preferences, accelerator="Ctrl+,")
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # Debug menu
        debug_menu = tk.Menu(menu_bar, tearoff=0)
        debug_menu.add_command(label="Run", command=self.run_file, accelerator="F5")
        debug_menu.add_command(label="Run in Terminal", command=self.run_in_terminal)
        debug_menu.add_separator()
        menu_bar.add_cascade(label="Debug", menu=debug_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Check for Updates...", command=self.check_update)
        help_menu.add_separator()
        help_menu.add_command(label="About TurtleIDE", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)

    def check_update(self):
        messagebox.showinfo("No Updates found!", "Your on the newest version of TurtleIDE.")

    def show_about(self):
        # Create about dialog
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About TurtleIDE")
        about_dialog.geometry("350x200")
        about_dialog.transient(self.root)
        about_dialog.resizable(False, False)
        
        # Configure dialog with current theme
        about_dialog.configure(bg=self.bg_color)
        
        # Logo/title
        title_label = tk.Label(about_dialog, text="TurtleIDE 1.2", 
                             font=("Helvetica", 16, "bold"),
                             bg=self.bg_color, fg=self.text_color)
        title_label.pack(pady=(20, 5))
        
        # Subtitle
        subtitle_label = tk.Label(about_dialog, text="A lightweight code editor for Python and more",
                                font=("Helvetica", 10),
                                bg=self.bg_color, fg=self.text_color)
        subtitle_label.pack(pady=(0, 15))
        
        # Version info
        version_frame = tk.Frame(about_dialog, bg=self.bg_color)
        version_frame.pack(fill="x", padx=30)
        
        version_info = tk.Label(version_frame, 
                              text="Version: 1.2 (Build 2025.04.26)\nPython Version: 3.10+\nTkinter GUI Framework",
                              justify=tk.LEFT, bg=self.bg_color, fg=self.text_color)
        version_info.pack(anchor="w", pady=5)
        
        # Copyright
        copyright_label = tk.Label(about_dialog, text="© 2025 Turtle",
                                 font=("Helvetica", 8),
                                 bg=self.bg_color, fg=self.text_color)
        copyright_label.pack(side="bottom", pady=10)
        
        # OK button
        ok_button = tk.Button(about_dialog, text="OK", 
                            command=about_dialog.destroy,
                            width=10, bg=self.menu_bg, fg=self.text_color)
        ok_button.pack(pady=10)
        
        # Make dialog modal
        about_dialog.grab_set()
        about_dialog.focus_set()

    def open_preferences(self):
        # Create preferences dialog
        pref_dialog = tk.Toplevel(self.root)
        pref_dialog.title("Preferences")
        pref_dialog.geometry("500x400")
        pref_dialog.transient(self.root)
        pref_dialog.resizable(True, True)
        
        # Configure dialog with current theme
        pref_dialog.configure(bg=self.bg_color)
        
        # Create a notebook with tabs
        notebook = ttk.Notebook(pref_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Define tab style
        style = ttk.Style()
        if self.current_theme == "dark":
            # Configure for dark theme
            style.configure("TNotebook", background=self.bg_color, borderwidth=0)
            style.configure("TNotebook.Tab", background=self.menu_bg, foreground=self.text_color, padding=[10, 5])
            style.map("TNotebook.Tab", background=[("selected", self.bg_color)])
        else:
            # Configure for light theme
            style.configure("TNotebook", background=self.bg_color, borderwidth=0)
            style.configure("TNotebook.Tab", background=self.menu_bg, foreground=self.text_color, padding=[10, 5])
            style.map("TNotebook.Tab", background=[("selected", "#ffffff")])
        
        # General tab
        general_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(general_tab, text="General")
        
        # Editor tab
        editor_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(editor_tab, text="Editor")
        
        # Add theme selection to general tab
        theme_label = tk.Label(general_tab, text="Theme:", bg=self.bg_color, fg=self.text_color, font=("Helvetica", 12))
        theme_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Theme selection radio buttons
        theme_var = tk.StringVar(value=self.current_theme)
        
        # Radio button frame
        radio_frame = tk.Frame(general_tab, bg=self.bg_color)
        radio_frame.pack(fill="x", padx=30, pady=5)
        
        light_radio = tk.Radiobutton(radio_frame, text="Light Theme", variable=theme_var, value="light", 
                                    bg=self.bg_color, fg=self.text_color, selectcolor=self.line_number_bg,
                                    activebackground=self.bg_color, activeforeground=self.text_color)
        light_radio.pack(anchor="w", pady=5)
        
        dark_radio = tk.Radiobutton(radio_frame, text="Dark Theme", variable=theme_var, value="dark",
                                   bg=self.bg_color, fg=self.text_color, selectcolor=self.line_number_bg,
                                   activebackground=self.bg_color, activeforeground=self.text_color)
        dark_radio.pack(anchor="w", pady=5)
        
        # Add editor settings
        font_label = tk.Label(editor_tab, text="Editor Font:", bg=self.bg_color, fg=self.text_color, font=("Helvetica", 12))
        font_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Font options frame
        font_frame = tk.Frame(editor_tab, bg=self.bg_color)
        font_frame.pack(fill="x", padx=30, pady=5)
        
        # Font family combobox
        tk.Label(font_frame, text="Font Family:", bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, sticky="w", pady=5)
        font_family = ttk.Combobox(font_frame, values=["Consolas", "Courier New", "Monaco", "Menlo"], width=20)
        font_family.current(0)
        font_family.grid(row=0, column=1, padx=10, pady=5)
        
        # Font size combobox
        tk.Label(font_frame, text="Font Size:", bg=self.bg_color, fg=self.text_color).grid(row=1, column=0, sticky="w", pady=5)
        font_size = ttk.Combobox(font_frame, values=["9", "10", "11", "12", "14", "16", "18"], width=5)
        font_size.current(3)  # Default to 12
        font_size.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Tab size
        tk.Label(font_frame, text="Tab Size:", bg=self.bg_color, fg=self.text_color).grid(row=2, column=0, sticky="w", pady=5)
        tab_size = ttk.Combobox(font_frame, values=["2", "4", "8"], width=5)
        tab_size.current(1)  # Default to 4
        tab_size.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Buttons frame
        button_frame = tk.Frame(pref_dialog, bg=self.bg_color)
        button_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", 
                                 command=pref_dialog.destroy,
                                 bg=self.menu_bg, fg=self.text_color)
        cancel_button.pack(side="right", padx=5)
        
        # Apply button
        def apply_settings():
            new_theme = theme_var.get()
            if new_theme != self.current_theme:
                self.current_theme = new_theme
                self.theme_text.config(text=f"Theme: {self.current_theme.capitalize()}")
                self.apply_theme()
            pref_dialog.destroy()
        
        apply_button = tk.Button(button_frame, text="Apply", 
                               command=apply_settings,
                               bg=self.menu_bg, fg=self.text_color)
        apply_button.pack(side="right", padx=5)
        
        # Make dialog modal
        pref_dialog.grab_set()
        pref_dialog.focus_set()

    def open_theme_settings(self):
        # Create a simpler theme dialog
        theme_dialog = tk.Toplevel(self.root)
        theme_dialog.title("Theme Settings")
        theme_dialog.geometry("300x150")
        theme_dialog.transient(self.root)
        theme_dialog.resizable(False, False)
        theme_dialog.configure(bg=self.bg_color)
        
        # Theme label
        theme_label = tk.Label(theme_dialog, text="Select Theme:", 
                              font=("Helvetica", 12), bg=self.bg_color, fg=self.text_color)
        theme_label.pack(pady=(20, 15))
        
        # Theme buttons frame
        button_frame = tk.Frame(theme_dialog, bg=self.bg_color)
        button_frame.pack(fill="x", padx=20)
        
        # Light theme button
        light_button = tk.Button(button_frame, text="Light Theme", width=12,
                               command=lambda: self.change_theme("light", theme_dialog),
                               bg=self.menu_bg, fg=self.text_color)
        light_button.pack(side="left", padx=5)
        
        # Dark theme button
        dark_button = tk.Button(button_frame, text="Dark Theme", width=12,
                              command=lambda: self.change_theme("dark", theme_dialog),
                              bg=self.menu_bg, fg=self.text_color)
        dark_button.pack(side="right", padx=5)
        
        # Current theme indicator
        current_label = tk.Label(theme_dialog, text=f"Current: {self.current_theme.capitalize()} Theme",
                                bg=self.bg_color, fg=self.text_color)
        current_label.pack(pady=(15, 0))
        
        # Make dialog modal
        theme_dialog.grab_set()
        theme_dialog.focus_set()

    def change_theme(self, theme, dialog=None):
        # Change the theme
        self.current_theme = theme
        
        # Update theme indicator in status bar
        self.theme_text.config(text=f"Theme: {self.current_theme.capitalize()}")
        
        # Apply the theme
        self.apply_theme()
        
        # Close dialog if provided
        if dialog:
            dialog.destroy()

    def create_editor_with_line_numbers(self):
        # Main frame to hold everything
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the line numbers and text editor
        self.editor_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers text widget
        self.line_numbers = tk.Text(self.editor_frame, width=4, padx=4, bg=self.line_number_bg, 
                                   fg=self.line_number_fg, bd=0, takefocus=0,
                                   highlightthickness=0, state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Text editor widget with scrollbar
        self.text_editor = ScrolledText(self.editor_frame, bg=self.bg_color, fg=self.text_color, 
                                       insertbackground=self.text_color, 
                                       font=('Consolas', 12), undo=True, wrap='none')
        self.text_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Fix bindtags
        self.text_editor.bindtags(('Text', str(self.text_editor), str(self.root), "all"))
        
        # Get the scrollbar from ScrolledText widget
        scrollbar = self.text_editor.vbar
        
        # Binding scrollbar to update line numbers
        scrollbar.config(command=self.on_scrollbar_scroll)
        
        # Ensure text editor is in normal state
        self.text_editor.config(state='normal')
        
        # Bind events for line numbers update
        self.text_editor.bind('<KeyRelease>', self.update_cursor_position)
        self.text_editor.bind('<ButtonRelease-1>', self.update_cursor_position)
        self.text_editor.bind('<MouseWheel>', self.update_cursor_position)
        
        # Add click handler to ensure focus
        self.text_editor.bind('<Button-1>', lambda e: self.text_editor.focus_set())
        
        # Set tab size
        self.text_editor.config(tabs=('0.5c', '1c', '1.5c', '2c'))

    def on_scrollbar_scroll(self, *args):
        # Handle scrollbar movement and update line numbers view
        self.text_editor.yview(*args)
        self.line_numbers.yview(*args)

    def create_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg=self.status_bar_bg)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status label
        self.status_text = tk.Label(self.status_bar, text="Ready", 
                                   bg=self.status_bar_bg, fg=self.text_color, anchor=tk.W)
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # Theme indicator
        self.theme_text = tk.Label(self.status_bar, text=f"Theme: {self.current_theme.capitalize()}", 
                                  bg=self.status_bar_bg, fg=self.text_color)
        self.theme_text.pack(side=tk.RIGHT, padx=5)
        
        # Line:Column indicator
        self.line_col_text = tk.Label(self.status_bar, text="Ln 1, Col 0", 
                                     bg=self.status_bar_bg, fg=self.text_color)
        self.line_col_text.pack(side=tk.RIGHT, padx=5)
        
        # Current language indicator
        self.language_text = tk.Label(self.status_bar, text="Python", 
                                    bg=self.status_bar_bg, fg=self.text_color)
        self.language_text.pack(side=tk.RIGHT, padx=5)

    def setup_key_bindings(self):
        # File operations
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_file_as())  # Ctrl+Shift+S
        
        # Edit operations
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-f>', lambda e: self.find_text())

        #Zoom operations
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-equal>', lambda e: self.zoom_in())  # Same key as plus, without shift
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        
        # Preferences
        self.root.bind('<Control-comma>', lambda e: self.open_preferences())
        
        # Cursor position tracking
        self.text_editor.bind('<KeyRelease>', self.update_cursor_position)
        
        # Check for modification
        self.text_editor.bind('<<Modified>>', self.set_modified)

        # Debug key bindings
        self.root.bind('<F5>', lambda e: self.run_file())

    def new_file(self):
        if self.modified:
            if not self.prompt_save_changes():
                return
        
        self.text_editor.delete(1.0, tk.END)
        self.current_file = None
        self.modified = False
        self.update_title()
        self.update_line_numbers()
        self.set_language(self.default_ext)
        # Ensure focus is set after creating a new file
        self.text_editor.focus_set()

    def open_file(self):
        if self.modified:
            if not self.prompt_save_changes():
                return
        
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Files", "*.*"),
                ("Python Files", "*.py"),
                ("Batch Files", "*.bat *.cmd"),
                ("C++ Files", "*.cpp *.h"),
                ("C# Files", "*.cs"),
                ("JavaScript Files", "*.js"),
                ("HTML Files", "*.html *.htm"),
                ("CSS Files", "*.css"),
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, content)
                self.current_file = file_path
                self.modified = False
                self.update_title()
                
                # Set language based on file extension
                _, ext = os.path.splitext(file_path)
                if ext.lower() in self.syntax_patterns:
                    self.set_language(ext.lower())
                else:
                    self.set_language(self.default_ext)
                
                self.update_line_numbers()
                self.status_text.config(text=f"Opened: {os.path.basename(file_path)}")
                # Ensure focus after opening file
                self.text_editor.focus_set()
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def open_specific_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(tk.END, content)
            self.current_file = path
            self.modified = False
            self.apply_syntax_highlighting()
        except Exception as e:
            messagebox.showerror("Open File Error", f"Could not open file:\n{e}")

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        
        try:
            with open(self.current_file, 'w') as file:
                content = self.text_editor.get(1.0, tk.END)
                file.write(content)
            
            self.modified = False
            self.update_title()
            self.status_text.config(text=f"Saved: {os.path.basename(self.current_file)}")
            # Ensure focus after saving
            self.text_editor.focus_set()
            return True
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            return False

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python Files", "*.py"),
                ("Batch Files", "*.bat *.cmd"),
                ("C++ Files", "*.cpp"),
                ("Header Files", "*.h"),
                ("C# Files", "*.cs"),
                ("JavaScript Files", "*.js"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("All Files", "*.*"),
            ]
        )
        
        if file_path:
            self.current_file = file_path
            # Update language based on new file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() in self.syntax_patterns:
                self.set_language(ext.lower())
            return self.save_file()
        
        return False

    def exit_app(self):
        if self.modified:
            if not self.prompt_save_changes():
                return
        self.root.destroy()

    def prompt_save_changes(self):
        response = messagebox.askyesnocancel("Unsaved Changes", 
                                           "You have unsaved changes. Would you like to save them?")
        if response is None:  # Cancel
            return False
        elif response:  # Yes
            return self.save_file()
        else:  # No
            return True

    def undo(self):
        try:
            self.text_editor.edit_undo()
            # Ensure focus after undo
            self.text_editor.focus_set()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text_editor.edit_redo()
            # Ensure focus after redo
            self.text_editor.focus_set()
        except tk.TclError:
            pass

    def cut(self):
        if self.text_editor.tag_ranges(tk.SEL):
            self.text_editor.event_generate("<<Cut>>")
            # Ensure focus after cut
            self.text_editor.focus_set()

    def copy(self):
        if self.text_editor.tag_ranges(tk.SEL):
            self.text_editor.event_generate("<<Copy>>")
            # Ensure focus after copy
            self.text_editor.focus_set()

    def paste(self):
        self.text_editor.event_generate("<<Paste>>")
        # Ensure focus after paste
        self.text_editor.focus_set()

    def select_all(self):
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)
        # Ensure focus after select all
        self.text_editor.focus_set()

    def find_text(self):
        # Create a simple find dialog
        find_dialog = tk.Toplevel(self.root)
        find_dialog.title("Find")
        find_dialog.geometry("300x100")
        find_dialog.transient(self.root)
        find_dialog.resizable(False, False)
        
        # Configure find dialog with current theme
        find_dialog.configure(bg=self.menu_bg)
        
        # Create widgets
        find_label = tk.Label(find_dialog, text="Find what:", bg=self.menu_bg, fg=self.text_color)
        find_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        find_entry = tk.Entry(find_dialog, width=25, bg=self.bg_color, fg=self.text_color,
                             insertbackground=self.text_color)
        find_entry.grid(row=0, column=1, padx=5, pady=5)
        find_entry.focus_set()
        
        case_var = tk.BooleanVar()
        case_check = tk.Checkbutton(find_dialog, text="Match case", variable=case_var,
                                   bg=self.menu_bg, fg=self.text_color, 
                                   selectcolor=self.bg_color, activebackground=self.menu_bg,
                                   activeforeground=self.text_color)
        case_check.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Find function
        def do_find():
            start_pos = self.text_editor.index(tk.INSERT)
            search_str = find_entry.get()
            if not search_str:
                return
            
            # Remove any existing highlights
            self.text_editor.tag_remove('found', '1.0', tk.END)
            
            # Find the text
            if case_var.get():
                pos = self.text_editor.search(search_str, start_pos, stopindex=tk.END, nocase=0)
            else:
                pos = self.text_editor.search(search_str, start_pos, stopindex=tk.END, nocase=1)
            
            if not pos:
                # Try from the beginning if not found
                if case_var.get():
                    pos = self.text_editor.search(search_str, '1.0', stopindex=tk.END, nocase=0)
                else:
                    pos = self.text_editor.search(search_str, '1.0', stopindex=tk.END, nocase=1)
                
                if not pos:
                    messagebox.showinfo("Find", "Text not found")
                    return
            
            # Calculate end position
            end_pos = f"{pos}+{len(search_str)}c"
            
            # Highlight found text
            self.text_editor.tag_add('found', pos, end_pos)
            self.text_editor.tag_config('found', background='yellow', foreground='black')
            
            # Move cursor to the end of the found text
            self.text_editor.mark_set(tk.INSERT, end_pos)
            self.text_editor.see(pos)
            
            # Ensure text editor gets focus after finding
            self.text_editor.focus_set()
        
        find_button = tk.Button(find_dialog, text="Find Next", command=do_find,
                              bg=self.menu_bg, fg=self.text_color)
        find_button.grid(row=1, column=1, padx=5, pady=5, sticky="e")
        
        # Bind Enter key to find
        find_entry.bind('<Return>', lambda e: do_find())
        
        # Make dialog modal
        find_dialog.grab_set()
        find_dialog.wait_window()
        
        # Return focus to text editor after closing dialog
        self.text_editor.focus_set()

    def start_position_tracking(self):
        """Start periodic cursor position tracking"""
        self.update_cursor_position()
        self.position_tracking_id = self.root.after(100, self.start_position_tracking)

    def stop_position_tracking(self):
        """Stop the cursor position tracking"""
        if hasattr(self, 'position_tracking_id'):
            self.root.after_cancel(self.position_tracking_id)

    def zoom_in(self):
        """Increase the font size of the editor text"""
        self.current_font_size += 1
        if self.current_font_size > 36:
            self.current_font_size = 36  # Maximum size
    
        # Update both the editor and line numbers
        self.text_editor.config(font=('Consolas', self.current_font_size))
        self.line_numbers.config(font=('Consolas', self.current_font_size))
    
        # Update the status bar to show current zoom level
        zoom_percent = int((self.current_font_size / 12) * 100)
        self.status_text.config(text=f"Zoom: {zoom_percent}%")
    
        # Ensure line numbers stay in sync
        self.update_line_numbers()
    
        # Ensure focus returns to the editor
        self.text_editor.focus_set()

    def zoom_out(self):
        """Decrease the font size of the editor text"""
        self.current_font_size -= 1
        if self.current_font_size < 6:
            self.current_font_size = 6  # Minimum size
    
        # Update both the editor and line numbers
        self.text_editor.config(font=('Consolas', self.current_font_size))
        self.line_numbers.config(font=('Consolas', self.current_font_size))
    
        # Update the status bar to show current zoom level
        zoom_percent = int((self.current_font_size / 12) * 100)
        self.status_text.config(text=f"Zoom: {zoom_percent}%")
    
        # Ensure line numbers stay in sync
        self.update_line_numbers()
    
        # Ensure focus returns to the editor
        self.text_editor.focus_set()

    def reset_zoom(self):
        """Reset font size to default"""
        self.current_font_size = 12  # Default size
    
        # Update both the editor and line numbers
        self.text_editor.config(font=('Consolas', self.current_font_size))
        self.line_numbers.config(font=('Consolas', self.current_font_size))
    
        # Update the status bar
        self.status_text.config(text="Zoom reset to 100%")
    
        # Ensure line numbers stay in sync
        self.update_line_numbers()
    
        # Ensure focus returns to the editor
        self.text_editor.focus_set()

    def set_language(self, ext):
        language_names = {
            '.py': 'Python',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.js': 'JavaScript',
            '.html': 'HTML',
            '.css': 'CSS'
        }
        
        self.current_language = ext
        self.language_text.config(text=language_names.get(ext, 'Plain Text'))
        
        # Apply syntax highlighting
        self.apply_syntax_highlighting()

    def apply_syntax_highlighting(self):
        # Clear all existing tags
        for tag in self.text_editor.tag_names():
            if tag != "sel":  # Don't remove selection tag
                self.text_editor.tag_remove(tag, "1.0", tk.END)
        
        # Get the current text
        content = self.text_editor.get("1.0", tk.END)
        
        # Apply new syntax highlighting based on language
        if self.current_language in self.syntax_patterns:
            patterns = self.syntax_patterns[self.current_language]
            
            # Get theme colors
            theme = self.themes[self.current_theme]
            
            # Set up style tags
            self.text_editor.tag_configure('keyword', foreground=theme["keyword_color"]) 
            self.text_editor.tag_configure('string', foreground=theme["string_color"])
            self.text_editor.tag_configure('comment', foreground=theme["comment_color"])
            self.text_editor.tag_configure('function', foreground=theme["function_color"])
            self.text_editor.tag_configure('number', foreground=theme["number_color"])
            self.text_editor.tag_configure('selector', foreground=theme["selector_color"])
            
            # Apply patterns
            for pattern_type, pattern in patterns.items():
                self.highlight_pattern(pattern, pattern_type)

    def highlight_pattern(self, pattern, tag_name):
        # Apply regex pattern
        content = self.text_editor.get("1.0", tk.END)
        for match in re.finditer(pattern, content, re.MULTILINE):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            self.text_editor.tag_add(tag_name, start_index, end_index)

    def update_on_keyrelease(self, event=None):
        # Update the syntax highlighting
        self.apply_syntax_highlighting()
        
        # Update line numbers
        self.update_line_numbers()
        
        # Update cursor position
        self.update_cursor_position()

    def update_line_numbers(self):
        # Get the total number of lines
        line_count = int(self.text_editor.index(tk.END).split('.')[0]) - 1
        
        # Update the line number display
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        
        # Generate line numbers text
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
            
        # Ensure the line numbers and editor are synchronized
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.text_editor.yview()[0])

    def on_mousewheel(self, event=None):
        # Update line numbers after scrolling
        self.line_numbers.yview_moveto(self.text_editor.yview()[0])

    def update_cursor_position(self, event=None):
        # Get cursor position
        try:
            cursor_pos = self.text_editor.index(tk.INSERT)
            line, column = cursor_pos.split('.')

            #Convert string
            line_num = int(line)
            col_num = int(column)
        
            # Update status bar
            self.line_col_text.config(text=f"Ln {line_num}, Col {col_num}")

            self.update_line_numbers()
        except Exception as e:
            self.line_col_text.config(text="Ln 1, Col 0")
        

    def set_modified(self, event=None):
        if not self.modified:
            self.modified = True
            self.update_title()
        self.text_editor.edit_modified(False)  # Reset the modification flag

    def update_title(self):
        # Update window title with filename and modification status
        if self.current_file:
            filename = os.path.basename(self.current_file)
        else:
            filename = "Untitled"
        
        modified_indicator = "*" if self.modified else ""
        self.root.title(f"{modified_indicator}{filename} - TurtleIDE 1.2")

    def run_file(self):
        # First save the file if needed
        if self.modified:
            if not self.save_file():
                return
        
        # Check if there's a file to run
        if not self.current_file:
            messagebox.showinfo("Run", "Please save the file first.")
            return
        
        try:
            # Create a simple output window
            output_window = tk.Toplevel(self.root)
            output_window.title(f"Output: {os.path.basename(self.current_file)}")
            output_window.geometry("700x400")
            output_window.configure(bg=self.bg_color)
            
            # Output text area
            output_text = ScrolledText(output_window, bg=self.bg_color, fg=self.text_color, 
                                      font=('Consolas', 12), wrap='word')
            output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Check file extension
            file_ext = os.path.splitext(self.current_file)[1].lower()
        
            # Run based on file type
            if file_ext in ['.py']:
                # Python files
                process = subprocess.Popen([sys.executable, self.current_file], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          text=True)
            elif file_ext in ['.bat', '.cmd']:
                # Batch files - on Windows, run directly
                if platform.system() == "Windows":
                    process = subprocess.Popen([self.current_file], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE,
                                              shell=True,
                                              text=True)
                else:
                    # Non-Windows systems typically can't run .bat/.cmd directly
                    output_text.insert(tk.END, "Batch files can only be executed on Windows systems.")
                    output_text.config(state='disabled')
                    return
            else:
                messagebox.showinfo("Run", "Only Python and Batch files can be executed.")
                return
        
            # Get the output
            stdout, stderr = process.communicate()
        
            # Display the output
            if stdout:
                output_text.insert(tk.END, stdout)
        
            if stderr:
                output_text.insert(tk.END, "\n--- ERRORS ---\n", "error")
                output_text.insert(tk.END, stderr, "error")
                output_text.tag_config("error", foreground="#ff5555")
        
            # Show the exit code
            output_text.insert(tk.END, f"\n\n--- Process completed with exit code: {process.returncode} ---")
        
            # Make output read-only
            output_text.config(state='disabled')
        
            # Status update
            self.status_text.config(text=f"Executed: {os.path.basename(self.current_file)}")
        
        except Exception as e:
            messagebox.showerror("Run Error", f"Failed to run file: {str(e)}")

    def run_in_terminal(self):
        # First save the file if needed
        if self.modified:
            if not self.save_file():
                return
        
        # Check if there's a file to run
        if not self.current_file:
            messagebox.showinfo("Run", "Please save the file first.")
            return
        
        # Get file extension
        file_ext = os.path.splitext(self.current_file)[1].lower()

        # Check if it's supported file type
        if file_ext not in ['.py', '.bat', '.cmd']:
            messagebox.showinfo("Run", "Only Python and Batch files can be executed.")
        
        try:
            # Get the directory containing the file
            file_dir = os.path.dirname(self.current_file)
            file_name = os.path.basename(self.current_file)
            
            # Determine the command based on the OS
            if platform.system() == "Windows":
                # On Windows
                if file_ext in ['.bat', '.cmd']:
                    cmd = f'start cmd /K "cd /d {file_dir} && "{file_name}" && pause"'
                else:
                    cmd = f'start cmd /K "cd /d {file_dir} && python "{os.path.basename(self.current_file)}" && pause"'
                subprocess.call(cmd, shell=True)
            elif platform.system() == "Darwin":  # macOS
                # On macOS, open a new Terminal
                applescript = f'''
                tell application "Terminal"
                    do script "cd '{file_dir}' && python3 '{os.path.basename(self.current_file)}'; echo; echo Press any key to continue...; read -n 1"
                end tell
                '''
                subprocess.run(["osascript", "-e", applescript])
            else:  # Linux and other Unix-like systems
                # Try common terminals
                terminals = ["gnome-terminal", "xterm", "konsole"]
                cmd = None
                
                for term in terminals:
                    try:
                        subprocess.run(["which", term], stdout=subprocess.PIPE, check=True)
                        if term == "gnome-terminal":
                            cmd = [term, "--", "bash", "-c", f"cd '{file_dir}' && python3 '{os.path.basename(self.current_file)}'; echo; read -p 'Press Enter to continue...'"]
                        else:
                            cmd = [term, "-e", f"bash -c \"cd '{file_dir}' && python3 '{os.path.basename(self.current_file)}'; echo; read -p 'Press Enter to continue...'\""]
                        break
                    except subprocess.CalledProcessError:
                        continue
                
                if cmd:
                    subprocess.Popen(cmd)
                else:
                    messagebox.showerror("Error", "Could not find a suitable terminal emulator.")
                    return
            
            # Status update
            self.status_text.config(text=f"Launched in terminal: {os.path.basename(self.current_file)}")
            
        except Exception as e:
            messagebox.showerror("Run Error", f"Failed to run in terminal: {str(e)}")

def main():
    root = tk.Tk()
    editor = CodeEditor(root)
    root.protocol("WM_DELETE_WINDOW", editor.exit_app)  # Handle window close event
    
    # Set initial focus
    root.after(100, editor.text_editor.focus_set)
    
    # Configure macOS app icon and menu
    if root.tk.call('tk', 'windowingsystem') == 'aqua':  # Check if running on macOS
        # Set up the macOS menu
        root.createcommand('::tk::mac::ShowPreferences', editor.open_preferences)
        root.createcommand('::tk::mac::Quit', editor.exit_app)
        root.createcommand('::tk::mac::ShowHelp', lambda: messagebox.showinfo("Help", "TurtleIDE Help"))
        
        # Modify the apple menu
        apple_menu = tk.Menu(root.nametowidget('.menubar'), name='apple')
        apple_menu.add_command(label='About TurtleIDE')
        root.config(menu=apple_menu)
    
    root.mainloop()

if __name__ == "__main__":
    main()
