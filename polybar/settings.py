import os
import sys
import shutil
import configparser
import subprocess
import json
from datetime import datetime
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib

# --- CONFIGURATION PATHS ---
POLYBAR_PATH = os.path.expanduser("~/.config/polybar")
CONFIG_FILE = os.path.join(POLYBAR_PATH, "config.ini")
THEMES_DIR = os.path.join(POLYBAR_PATH, "themes")
BACKUP_DIR = os.path.join(POLYBAR_PATH, "backups")
PRESETS_FILE = os.path.join(POLYBAR_PATH, "presets.json")

# --- DEFAULT PRESETS ---
DEFAULT_PRESETS = {
    "module_templates": {
        "custom/script": {
            "type": "custom/script",
            "exec": "",
            "interval": "5",
            "label": "%output%"
        },
        "custom/text": {
            "type": "custom/text",
            "content": "",
            "click-left": ""
        },
        "internal/battery": {
            "type": "internal/battery",
            "battery": "BAT0",
            "adapter": "AC",
            "format-charging": "<label-charging>",
            "format-discharging": "<label-discharging>",
            "label-charging": "%percentage%%",
            "label-discharging": "%percentage%%"
        },
        "internal/temperature": {
            "type": "internal/temperature",
            "thermal-zone": "0",
            "warn-temperature": "60",
            "format": "<label>",
            "label": "%temperature-c%"
        },
        "internal/filesystem": {
            "type": "internal/filesystem",
            "mount-0": "/",
            "interval": "25",
            "format-mounted": "<label-mounted>",
            "label-mounted": "%percentage_used%%"
        }
    }
}

class PolybarDesigner(Gtk.Window):
    def __init__(self):
        super().__init__(title="Polybar Studio")
        self.set_default_size(1100, 750)
        self.set_border_width(0)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Ensure directories exist
        os.makedirs(THEMES_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Load or create presets
        self.load_presets()
        
        # Config management
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.optionxform = str  # Preserve case
        self.unsaved_changes = False
        
        # Load config with error handling
        if os.path.exists(CONFIG_FILE):
            try:
                self.config.read(CONFIG_FILE)
            except Exception as e:
                self.show_error_dialog(f"Error loading config: {str(e)}")
                sys.exit(1)
        else:
            self.show_error_dialog(f"Config file not found: {CONFIG_FILE}")
            sys.exit(1)

        self.apply_modern_styling()
        self.build_ui()
        self.show_all()

    def load_presets(self):
        """Load module presets from file or create defaults"""
        if os.path.exists(PRESETS_FILE):
            try:
                with open(PRESETS_FILE, 'r') as f:
                    self.presets = json.load(f)
            except:
                self.presets = DEFAULT_PRESETS
        else:
            self.presets = DEFAULT_PRESETS
            self.save_presets()

    def save_presets(self):
        """Save presets to file"""
        try:
            with open(PRESETS_FILE, 'w') as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            print(f"Error saving presets: {e}")

    def apply_modern_styling(self):
        css = b"""
        * { 
            font-family: 'Inter', 'Segoe UI', 'Sans'; 
            font-size: 13px;
        }
        
        window {
            background-color: #16161e;
        }
        
        .sidebar { 
            background: linear-gradient(180deg, #1a1b26 0%, #16161e 100%);
            border-right: 1px solid #2a2b3d; 
            padding: 10px;
        }
        
        .sidebar list { 
            background: transparent; 
        }
        
        .sidebar row {
            padding: 8px 12px;
            border-radius: 6px;
            margin: 2px 0;
        }
        
        .sidebar row:hover {
            background-color: #24283b;
        }
        
        .sidebar row:selected {
            background-color: #414868;
        }
        
        .main-content { 
            background-color: #1f2335; 
            padding: 30px;
        }
        
        label { 
            color: #c0caf5; 
        }
        
        .dim-label {
            color: #565f89;
            font-size: 11px;
        }
        
        entry { 
            background: #24283b; 
            color: #c0caf5; 
            border: 1px solid #414868; 
            padding: 8px 12px; 
            border-radius: 6px;
            min-height: 32px;
        }
        
        entry:focus {
            border-color: #7aa2f7;
            box-shadow: 0 0 0 2px rgba(122, 162, 247, 0.2);
        }
        
        textview {
            background: #24283b;
            color: #c0caf5;
            border: 1px solid #414868;
            border-radius: 6px;
            padding: 8px;
        }
        
        textview text {
            background: #24283b;
            color: #c0caf5;
        }
        
        button { 
            background: #414868; 
            color: #c0caf5; 
            border-radius: 6px; 
            padding: 8px 16px;
            border: none;
            min-height: 36px;
            transition: all 0.2s;
        }
        
        button:hover { 
            background: #565f89;
        }
        
        button:active {
            background: #24283b;
        }
        
        .primary-btn {
            background: #7aa2f7;
            color: #1a1b26;
            font-weight: 600;
        }
        
        .primary-btn:hover {
            background: #89b4fa;
        }
        
        .save-btn { 
            background: #9ece6a;
            color: #1a1b26; 
            font-weight: bold;
            min-width: 200px;
        }
        
        .save-btn:hover {
            background: #b9f27c;
        }
        
        .danger-btn {
            background: #f7768e;
            color: #1a1b26;
        }
        
        .danger-btn:hover {
            background: #ff9db1;
        }
        
        .header { 
            font-size: 28px; 
            font-weight: bold; 
            color: #7aa2f7; 
            margin-bottom: 8px;
        }
        
        .subheader {
            font-size: 16px;
            font-weight: 600;
            color: #bb9af7;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        
        separator { 
            background-color: #2a2b3d;
            min-height: 1px;
        }
        
        combobox button {
            padding: 6px 12px;
        }
        
        .color-preview {
            border-radius: 6px;
            border: 2px solid #414868;
            min-width: 40px;
            min-height: 40px;
        }
        
        scrollbar {
            background: transparent;
        }
        
        scrollbar slider {
            background: #414868;
            border-radius: 10px;
            min-width: 8px;
        }
        
        scrollbar slider:hover {
            background: #565f89;
        }
        
        .info-box {
            background: #24283b;
            border-left: 3px solid #7aa2f7;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
        }
        
        .warning-box {
            background: #24283b;
            border-left: 3px solid #f9e2af;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
        }
        
        .success-box {
            background: #24283b;
            border-left: 3px solid #9ece6a;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
        }
        
        switch {
            background: #24283b;
            border: 1px solid #414868;
        }
        
        switch slider {
            background: #565f89;
        }
        
        switch:checked {
            background: #7aa2f7;
        }
        
        switch:checked slider {
            background: #c0caf5;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), 
            provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def build_ui(self):
        """Build the main UI structure"""
        # Main container
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)
        
        # Header bar
        self.create_header_bar()
        
        # Content area
        self.main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        main_vbox.pack_start(self.main_hbox, True, True, 0)

        # Sidebar Navigation
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(200)
        
        self.sidebar = Gtk.StackSidebar()
        self.sidebar.set_stack(self.stack)
        self.sidebar.set_size_request(220, -1)
        self.sidebar.get_style_context().add_class("sidebar")

        self.main_hbox.pack_start(self.sidebar, False, False, 0)
        self.main_hbox.pack_start(self.stack, True, True, 0)

        # Build Pages
        self.create_overview_page()
        self.create_theme_page()
        self.create_bar_page()
        self.create_module_pages()
        self.create_new_module_page()
        self.create_advanced_page()

        # Footer Actions
        self.add_save_footer()

    def create_header_bar(self):
        """Create custom header bar"""
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("Polybar Studio")
        header.set_subtitle("Visual Configuration Manager")
        
        # Backup button
        backup_btn = Gtk.Button(label="Backup")
        backup_btn.set_image(Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON))
        backup_btn.set_always_show_image(True)
        backup_btn.set_tooltip_text("Create backup")
        backup_btn.connect("clicked", self.create_backup)
        header.pack_start(backup_btn)
        
        # Restore button
        restore_btn = Gtk.Button(label="Restore")
        restore_btn.set_image(Gtk.Image.new_from_icon_name("document-revert", Gtk.IconSize.BUTTON))
        restore_btn.set_always_show_image(True)
        restore_btn.set_tooltip_text("Restore from backup")
        restore_btn.connect("clicked", self.show_restore_dialog)
        header.pack_start(restore_btn)
        
        # Reload button
        reload_btn = Gtk.Button(label="Reload")
        reload_btn.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON))
        reload_btn.set_always_show_image(True)
        reload_btn.set_tooltip_text("Reload configuration")
        reload_btn.connect("clicked", self.reload_config)
        header.pack_end(reload_btn)
        
        self.set_titlebar(header)

    def create_overview_page(self):
        """Create overview/dashboard page"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.get_style_context().add_class("main-content")
        box.set_margin_start(30)
        box.set_margin_end(30)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        
        # Header
        lbl = Gtk.Label(label="Dashboard", xalign=0)
        lbl.get_style_context().add_class("header")
        box.pack_start(lbl, False, False, 0)
        
        desc = Gtk.Label(label="Overview of your Polybar configuration", xalign=0)
        desc.get_style_context().add_class("dim-label")
        box.pack_start(desc, False, False, 0)
        
        box.pack_start(Gtk.Separator(), False, False, 10)
        
        # Stats grid
        stats_grid = Gtk.Grid()
        stats_grid.set_column_spacing(20)
        stats_grid.set_row_spacing(20)
        stats_grid.set_column_homogeneous(True)
        
        # Count modules
        module_count = sum(1 for s in self.config.sections() if s.startswith("module/"))
        
        # Create stat cards
        stats = [
            ("Total Modules", str(module_count), "#7aa2f7"),
            ("Color Schemes", str(len(self.config['colors'].items()) if 'colors' in self.config else 0), "#bb9af7"),
            ("Bar Instances", str(sum(1 for s in self.config.sections() if s.startswith("bar/"))), "#f9e2af"),
            ("Backups", str(len([f for f in os.listdir(BACKUP_DIR) if f.endswith('.ini')])), "#9ece6a")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = self.create_stat_card(title, value, color)
            stats_grid.attach(card, i % 2, i // 2, 1, 1)
        
        box.pack_start(stats_grid, False, False, 0)
        
        # Quick actions
        box.pack_start(Gtk.Separator(), False, False, 10)
        
        quick_lbl = Gtk.Label(label="Quick Actions", xalign=0)
        quick_lbl.get_style_context().add_class("subheader")
        box.pack_start(quick_lbl, False, False, 0)
        
        actions_grid = Gtk.Grid()
        actions_grid.set_column_spacing(15)
        actions_grid.set_row_spacing(15)
        actions_grid.set_column_homogeneous(True)
        
        # Action buttons with icons from theme
        action_buttons = [
            ("Apply Theme", self.on_theme_apply, "preferences-desktop-theme"),
            ("New Module", self.show_new_module_page, "list-add"),
            ("Backup Now", self.create_backup, "document-save"),
            ("Restart Polybar", self.restart_polybar, "view-refresh"),
        ]
        
        for i, (label, callback, icon_name) in enumerate(action_buttons):
            btn = Gtk.Button(label=label)
            btn.set_image(Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON))
            btn.set_always_show_image(True)
            btn.connect("clicked", callback)
            btn.set_size_request(200, 50)
            actions_grid.attach(btn, i % 2, i // 2, 1, 1)
        
        box.pack_start(actions_grid, False, False, 0)
        
        # Config file info
        box.pack_start(Gtk.Separator(), False, False, 10)
        
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        info_box.get_style_context().add_class("info-box")
        
        info_title = Gtk.Label(label="Configuration File", xalign=0)
        info_title.set_markup("<b>Configuration File</b>")
        info_box.pack_start(info_title, False, False, 0)
        
        info_path = Gtk.Label(label=f"Location: {CONFIG_FILE}", xalign=0)
        info_path.get_style_context().add_class("dim-label")
        info_box.pack_start(info_path, False, False, 0)
        
        if os.path.exists(CONFIG_FILE):
            mtime = datetime.fromtimestamp(os.path.getmtime(CONFIG_FILE))
            info_time = Gtk.Label(label=f"Last modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}", xalign=0)
            info_time.get_style_context().add_class("dim-label")
            info_box.pack_start(info_time, False, False, 0)
        
        box.pack_start(info_box, False, False, 0)
        
        scroll.add(box)
        self.stack.add_titled(scroll, "overview", "Overview")

    def create_stat_card(self, title, value, color):
        """Create a stat card widget"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.get_style_context().add_class("info-box")
        box.set_size_request(200, 100)
        
        value_lbl = Gtk.Label(label=value, xalign=0.5)
        value_lbl.set_markup(f"<span size='x-large' weight='bold' foreground='{color}'>{value}</span>")
        
        title_lbl = Gtk.Label(label=title, xalign=0.5)
        title_lbl.get_style_context().add_class("dim-label")
        
        box.pack_start(value_lbl, True, True, 0)
        box.pack_start(title_lbl, False, False, 0)
        
        return box

    def create_theme_page(self):
        """Create theme management page"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.get_style_context().add_class("main-content")
        box.set_margin_start(30)
        box.set_margin_end(30)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        
        lbl = Gtk.Label(label="Theme Manager", xalign=0)
        lbl.get_style_context().add_class("header")
        box.pack_start(lbl, False, False, 0)
        
        desc = Gtk.Label(label="Manage color schemes and themes", xalign=0)
        desc.get_style_context().add_class("dim-label")
        box.pack_start(desc, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 10)

        # Theme Selector Section
        theme_section = Gtk.Label(label="Saved Themes", xalign=0)
        theme_section.get_style_context().add_class("subheader")
        box.pack_start(theme_section, False, False, 0)
        
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.set_size_request(300, -1)
        self.refresh_theme_list()
        
        apply_btn = Gtk.Button(label="Apply Theme")
        apply_btn.set_image(Gtk.Image.new_from_icon_name("emblem-default", Gtk.IconSize.BUTTON))
        apply_btn.set_always_show_image(True)
        apply_btn.get_style_context().add_class("primary-btn")
        apply_btn.connect("clicked", self.on_theme_apply)
        
        save_theme_btn = Gtk.Button(label="Save Current as Theme")
        save_theme_btn.set_image(Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON))
        save_theme_btn.set_always_show_image(True)
        save_theme_btn.connect("clicked", self.save_current_theme)
        
        delete_theme_btn = Gtk.Button(label="Delete Theme")
        delete_theme_btn.set_image(Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.BUTTON))
        delete_theme_btn.set_always_show_image(True)
        delete_theme_btn.get_style_context().add_class("danger-btn")
        delete_theme_btn.connect("clicked", self.delete_theme)
        
        grid.attach(Gtk.Label(label="Select Theme:", xalign=0), 0, 0, 1, 1)
        grid.attach(self.theme_combo, 1, 0, 2, 1)
        grid.attach(apply_btn, 3, 0, 1, 1)
        grid.attach(save_theme_btn, 1, 1, 1, 1)
        grid.attach(delete_theme_btn, 2, 1, 1, 1)
        
        box.pack_start(grid, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 10)

        # Color Editor
        color_section = Gtk.Label(label="Color Palette", xalign=0)
        color_section.get_style_context().add_class("subheader")
        box.pack_start(color_section, False, False, 0)
        
        self.color_entries = {}
        color_grid = Gtk.Grid()
        color_grid.set_column_spacing(20)
        color_grid.set_row_spacing(15)
        
        if 'colors' in self.config:
            for i, (key, val) in enumerate(self.config['colors'].items()):
                # Label
                lbl = Gtk.Label(label=key, xalign=0)
                lbl.set_size_request(150, -1)
                
                # Entry
                ent = Gtk.Entry()
                ent.set_text(val)
                ent.set_size_request(200, -1)
                ent.connect("changed", lambda w: self.mark_unsaved())
                self.color_entries[key] = ent
                
                # Color preview
                preview = Gtk.DrawingArea()
                preview.set_size_request(40, 40)
                preview.get_style_context().add_class("color-preview")
                preview.connect("draw", self.draw_color_preview, val)
                
                # Update preview on entry change
                ent.connect("changed", lambda w, p=preview: self.update_color_preview(w, p))
                
                # Color picker button
                picker_btn = Gtk.Button()
                picker_btn.set_image(Gtk.Image.new_from_icon_name("gtk-select-color", Gtk.IconSize.BUTTON))
                picker_btn.set_tooltip_text("Choose color")
                picker_btn.connect("clicked", self.show_color_picker, ent, preview)
                
                color_grid.attach(lbl, 0, i, 1, 1)
                color_grid.attach(ent, 1, i, 1, 1)
                color_grid.attach(preview, 2, i, 1, 1)
                color_grid.attach(picker_btn, 3, i, 1, 1)
        
        box.pack_start(color_grid, False, False, 0)
        
        # Add new color button
        add_color_btn = Gtk.Button(label="Add New Color")
        add_color_btn.set_image(Gtk.Image.new_from_icon_name("list-add", Gtk.IconSize.BUTTON))
        add_color_btn.set_always_show_image(True)
        add_color_btn.connect("clicked", self.add_new_color)
        box.pack_start(add_color_btn, False, False, 10)
        
        scroll.add(box)
        self.stack.add_titled(scroll, "themes", "Themes")

    def create_bar_page(self):
        """Create bar configuration page"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.get_style_context().add_class("main-content")
        box.set_margin_start(30)
        box.set_margin_end(30)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        
        lbl = Gtk.Label(label="Bar Configuration", xalign=0)
        lbl.get_style_context().add_class("header")
        box.pack_start(lbl, False, False, 0)
        
        desc = Gtk.Label(label="Configure bar dimensions, position, and appearance", xalign=0)
        desc.get_style_context().add_class("dim-label")
        box.pack_start(desc, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 10)

        self.bar_entries = {}
        
        # Dimensions section
        dim_section = Gtk.Label(label="Dimensions", xalign=0)
        dim_section.get_style_context().add_class("subheader")
        box.pack_start(dim_section, False, False, 0)
        
        dim_grid = Gtk.Grid()
        dim_grid.set_column_spacing(20)
        dim_grid.set_row_spacing(12)
        dim_keys = [
            ('width', 'Width (e.g., 100% or 1920)'),
            ('height', 'Height in pixels (e.g., 26pt)'),
            ('radius', 'Corner radius (0 for square)'),
        ]
        
        for i, (key, desc_text) in enumerate(dim_keys):
            val = self.config['bar/main'].get(key, "")
            
            lbl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            lbl = Gtk.Label(label=key.replace("-", " ").title(), xalign=0)
            desc_lbl = Gtk.Label(label=desc_text, xalign=0)
            desc_lbl.get_style_context().add_class("dim-label")
            lbl_box.pack_start(lbl, False, False, 0)
            lbl_box.pack_start(desc_lbl, False, False, 0)
            
            ent = Gtk.Entry()
            ent.set_text(val)
            ent.set_size_request(300, -1)
            ent.connect("changed", lambda w: self.mark_unsaved())
            self.bar_entries[key] = ent
            
            dim_grid.attach(lbl_box, 0, i, 1, 1)
            dim_grid.attach(ent, 1, i, 1, 1)
        
        box.pack_start(dim_grid, False, False, 0)
        
        # Position section
        box.pack_start(Gtk.Separator(), False, False, 10)
        pos_section = Gtk.Label(label="Position & Spacing", xalign=0)
        pos_section.get_style_context().add_class("subheader")
        box.pack_start(pos_section, False, False, 0)
        
        pos_grid = Gtk.Grid()
        pos_grid.set_column_spacing(20)
        pos_grid.set_row_spacing(12)
        pos_keys = [
            ('bottom', 'Position at bottom (true/false)'),
            ('padding-left', 'Left padding'),
            ('padding-right', 'Right padding'),
            ('module-margin', 'Space between modules'),
        ]
        
        for i, (key, desc_text) in enumerate(pos_keys):
            val = self.config['bar/main'].get(key, "")
            
            lbl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            lbl = Gtk.Label(label=key.replace("-", " ").title(), xalign=0)
            desc_lbl = Gtk.Label(label=desc_text, xalign=0)
            desc_lbl.get_style_context().add_class("dim-label")
            lbl_box.pack_start(lbl, False, False, 0)
            lbl_box.pack_start(desc_lbl, False, False, 0)
            
            ent = Gtk.Entry()
            ent.set_text(val)
            ent.set_size_request(300, -1)
            ent.connect("changed", lambda w: self.mark_unsaved())
            self.bar_entries[key] = ent
            
            pos_grid.attach(lbl_box, 0, i, 1, 1)
            pos_grid.attach(ent, 1, i, 1, 1)
        
        box.pack_start(pos_grid, False, False, 0)
        
        # Appearance section
        box.pack_start(Gtk.Separator(), False, False, 10)
        app_section = Gtk.Label(label="Appearance", xalign=0)
        app_section.get_style_context().add_class("subheader")
        box.pack_start(app_section, False, False, 0)
        
        app_grid = Gtk.Grid()
        app_grid.set_column_spacing(20)
        app_grid.set_row_spacing(12)
        app_keys = [
            ('background', 'Background color'),
            ('foreground', 'Foreground/text color'),
            ('line-size', 'Underline thickness'),
        ]
        
        for i, (key, desc_text) in enumerate(app_keys):
            val = self.config['bar/main'].get(key, "")
            
            lbl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            lbl = Gtk.Label(label=key.replace("-", " ").title(), xalign=0)
            desc_lbl = Gtk.Label(label=desc_text, xalign=0)
            desc_lbl.get_style_context().add_class("dim-label")
            lbl_box.pack_start(lbl, False, False, 0)
            lbl_box.pack_start(desc_lbl, False, False, 0)
            
            ent = Gtk.Entry()
            ent.set_text(val)
            ent.set_size_request(300, -1)
            ent.connect("changed", lambda w: self.mark_unsaved())
            self.bar_entries[key] = ent
            
            app_grid.attach(lbl_box, 0, i, 1, 1)
            app_grid.attach(ent, 1, i, 1, 1)
        
        box.pack_start(app_grid, False, False, 0)
        
        scroll.add(box)
        self.stack.add_titled(scroll, "bar", "Bar Settings")

    def create_module_pages(self):
        """Create a page for each module"""
        for section in self.config.sections():
            if section.startswith("module/"):
                mod_name = section.replace("module/", "")
                
                scroll = Gtk.ScrolledWindow()
                scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
                
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
                box.get_style_context().add_class("main-content")
                box.set_margin_start(30)
                box.set_margin_end(30)
                box.set_margin_top(30)
                box.set_margin_bottom(30)
                
                # Header
                header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
                
                header = Gtk.Label(label=f"Module: {mod_name}", xalign=0)
                header.get_style_context().add_class("header")
                header_box.pack_start(header, True, True, 0)
                
                # Delete module button
                delete_btn = Gtk.Button(label="Delete Module")
                delete_btn.set_image(Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.BUTTON))
                delete_btn.set_always_show_image(True)
                delete_btn.get_style_context().add_class("danger-btn")
                delete_btn.connect("clicked", self.delete_module, section)
                header_box.pack_end(delete_btn, False, False, 0)
                
                box.pack_start(header_box, False, False, 0)
                
                # Module type
                mod_type = self.config[section].get('type', 'unknown')
                type_lbl = Gtk.Label(label=f"Type: {mod_type}", xalign=0)
                type_lbl.get_style_context().add_class("dim-label")
                box.pack_start(type_lbl, False, False, 0)
                
                box.pack_start(Gtk.Separator(), False, False, 10)
                
                # Module options grid
                grid = Gtk.Grid()
                grid.set_column_spacing(20)
                grid.set_row_spacing(12)
                
                module_data = {}
                for i, (key, val) in enumerate(self.config[section].items()):
                    lbl = Gtk.Label(label=key, xalign=0)
                    lbl.set_size_request(150, -1)
                    
                    # Use TextView for multi-line values
                    if '\n' in str(val) or len(str(val)) > 100:
                        scrolled = Gtk.ScrolledWindow()
                        scrolled.set_size_request(400, 100)
                        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
                        
                        textview = Gtk.TextView()
                        textview.set_wrap_mode(Gtk.WrapMode.WORD)
                        textbuffer = textview.get_buffer()
                        textbuffer.set_text(val)
                        textbuffer.connect("changed", lambda w: self.mark_unsaved())
                        scrolled.add(textview)
                        
                        module_data[key] = textbuffer
                        widget = scrolled
                    else:
                        e = Gtk.Entry()
                        e.set_text(val)
                        e.set_size_request(400, -1)
                        e.connect("changed", lambda w: self.mark_unsaved())
                        module_data[key] = e
                        widget = e
                    
                    grid.attach(lbl, 0, i, 1, 1)
                    grid.attach(widget, 1, i, 1, 1)
                
                setattr(self, f"mod_entry_{mod_name}", module_data)
                box.pack_start(grid, False, False, 0)
                
                # Add new property button
                add_prop_btn = Gtk.Button(label="Add Property")
                add_prop_btn.set_image(Gtk.Image.new_from_icon_name("list-add", Gtk.IconSize.BUTTON))
                add_prop_btn.set_always_show_image(True)
                add_prop_btn.connect("clicked", self.add_module_property, section, box, grid, module_data)
                box.pack_start(add_prop_btn, False, False, 10)
                
                scroll.add(box)
                self.stack.add_titled(scroll, f"mod_{mod_name}", f"{mod_name}")

    def create_new_module_page(self):
        """Create page for adding new modules"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.get_style_context().add_class("main-content")
        box.set_margin_start(30)
        box.set_margin_end(30)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        
        lbl = Gtk.Label(label="Create New Module", xalign=0)
        lbl.get_style_context().add_class("header")
        box.pack_start(lbl, False, False, 0)
        
        desc = Gtk.Label(label="Add a new module to your Polybar configuration", xalign=0)
        desc.get_style_context().add_class("dim-label")
        box.pack_start(desc, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 10)

        # Module name
        name_lbl = Gtk.Label(label="Module Name", xalign=0)
        name_lbl.get_style_context().add_class("subheader")
        box.pack_start(name_lbl, False, False, 0)
        
        self.new_mod_name = Gtk.Entry()
        self.new_mod_name.set_placeholder_text("e.g., weather, spotify, battery")
        self.new_mod_name.set_size_request(400, -1)
        box.pack_start(self.new_mod_name, False, False, 0)
        
        # Module type with presets
        type_lbl = Gtk.Label(label="Module Type", xalign=0)
        type_lbl.get_style_context().add_class("subheader")
        box.pack_start(type_lbl, False, False, 10)
        
        self.new_mod_type_combo = Gtk.ComboBoxText()
        for template_name in self.presets['module_templates'].keys():
            self.new_mod_type_combo.append_text(template_name)
        self.new_mod_type_combo.set_active(0)
        self.new_mod_type_combo.connect("changed", self.on_template_changed)
        box.pack_start(self.new_mod_type_combo, False, False, 0)
        
        # Or custom type
        custom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        custom_lbl = Gtk.Label(label="Or enter custom type:")
        self.new_mod_type_custom = Gtk.Entry()
        self.new_mod_type_custom.set_placeholder_text("e.g., internal/battery")
        custom_box.pack_start(custom_lbl, False, False, 0)
        custom_box.pack_start(self.new_mod_type_custom, True, True, 0)
        box.pack_start(custom_box, False, False, 0)
        
        # Template preview
        preview_lbl = Gtk.Label(label="Template Preview", xalign=0)
        preview_lbl.get_style_context().add_class("subheader")
        box.pack_start(preview_lbl, False, False, 10)
        
        self.template_preview = Gtk.TextView()
        self.template_preview.set_editable(False)
        self.template_preview.set_wrap_mode(Gtk.WrapMode.WORD)
        preview_scroll = Gtk.ScrolledWindow()
        preview_scroll.set_size_request(400, 150)
        preview_scroll.add(self.template_preview)
        box.pack_start(preview_scroll, False, False, 0)
        
        # Update preview initially
        self.on_template_changed(self.new_mod_type_combo)
        
        # Add button
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn = Gtk.Button(label="Create Module")
        btn.set_image(Gtk.Image.new_from_icon_name("list-add", Gtk.IconSize.BUTTON))
        btn.set_always_show_image(True)
        btn.get_style_context().add_class("primary-btn")
        btn.set_size_request(200, 50)
        btn.connect("clicked", self.on_add_module)
        btn_box.pack_start(btn, False, False, 0)
        box.pack_start(btn_box, False, False, 20)
        
        scroll.add(box)
        self.stack.add_titled(scroll, "add_new", "New Module")

    def create_advanced_page(self):
        """Create advanced settings page"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.get_style_context().add_class("main-content")
        box.set_margin_start(30)
        box.set_margin_end(30)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        
        lbl = Gtk.Label(label="Advanced Settings", xalign=0)
        lbl.get_style_context().add_class("header")
        box.pack_start(lbl, False, False, 0)
        
        desc = Gtk.Label(label="Raw configuration editing and advanced options", xalign=0)
        desc.get_style_context().add_class("dim-label")
        box.pack_start(desc, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 10)
        
        # Warning
        warning = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        warning.get_style_context().add_class("warning-box")
        warning_title = Gtk.Label(label="Advanced Users Only", xalign=0)
        warning_title.set_markup("<b>⚠ Advanced Users Only</b>")
        warning_desc = Gtk.Label(
            label="Editing raw config may break your Polybar. Always backup first!",
            xalign=0,
            wrap=True
        )
        warning.pack_start(warning_title, False, False, 0)
        warning.pack_start(warning_desc, False, False, 0)
        box.pack_start(warning, False, False, 0)
        
        # Raw config editor
        editor_lbl = Gtk.Label(label="Raw Configuration", xalign=0)
        editor_lbl.get_style_context().add_class("subheader")
        box.pack_start(editor_lbl, False, False, 10)
        
        self.raw_config_view = Gtk.TextView()
        self.raw_config_view.set_monospace(True)
        self.raw_config_view.set_wrap_mode(Gtk.WrapMode.NONE)
        
        # Load current config
        self.load_raw_config()
        
        editor_scroll = Gtk.ScrolledWindow()
        editor_scroll.set_size_request(-1, 400)
        editor_scroll.add(self.raw_config_view)
        box.pack_start(editor_scroll, True, True, 0)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        reload_raw_btn = Gtk.Button(label="Reload from File")
        reload_raw_btn.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON))
        reload_raw_btn.set_always_show_image(True)
        reload_raw_btn.connect("clicked", lambda w: self.load_raw_config())
        
        validate_btn = Gtk.Button(label="Validate Syntax")
        validate_btn.set_image(Gtk.Image.new_from_icon_name("emblem-default", Gtk.IconSize.BUTTON))
        validate_btn.set_always_show_image(True)
        validate_btn.connect("clicked", self.validate_config)
        
        apply_raw_btn = Gtk.Button(label="Apply Raw Config")
        apply_raw_btn.set_image(Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON))
        apply_raw_btn.set_always_show_image(True)
        apply_raw_btn.get_style_context().add_class("danger-btn")
        apply_raw_btn.connect("clicked", self.apply_raw_config)
        
        btn_box.pack_start(reload_raw_btn, False, False, 0)
        btn_box.pack_start(validate_btn, False, False, 0)
        btn_box.pack_end(apply_raw_btn, False, False, 0)
        
        box.pack_start(btn_box, False, False, 10)
        
        scroll.add(box)
        self.stack.add_titled(scroll, "advanced", "Advanced")

    def add_save_footer(self):
        """Add footer with save button"""
        footer = Gtk.ActionBar()
        
        # Status label
        self.status_label = Gtk.Label(label="All changes saved")
        self.status_label.get_style_context().add_class("dim-label")
        footer.pack_start(self.status_label)
        
        # Save button
        save_btn = Gtk.Button(label="SAVE & RESTART POLYBAR")
        save_btn.set_image(Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON))
        save_btn.set_always_show_image(True)
        save_btn.get_style_context().add_class("save-btn")
        save_btn.connect("clicked", self.save_all)
        footer.pack_end(save_btn)
        
        # Save without restart
        save_only_btn = Gtk.Button(label="Save Only")
        save_only_btn.set_image(Gtk.Image.new_from_icon_name("document-save-as", Gtk.IconSize.BUTTON))
        save_only_btn.set_always_show_image(True)
        save_only_btn.connect("clicked", lambda w: self.save_all(w, restart=False))
        footer.pack_end(save_only_btn)
        
        self.main_hbox.pack_end(footer, False, False, 0)

    # --- HELPER METHODS ---

    def mark_unsaved(self):
        """Mark that there are unsaved changes"""
        self.unsaved_changes = True
        self.status_label.set_text("Unsaved changes")
        self.status_label.set_markup("<span foreground='#f9e2af'>● Unsaved changes</span>")

    def draw_color_preview(self, widget, cr, color):
        """Draw color preview"""
        try:
            color = color.strip()
            if color.startswith('#'):
                color = color[1:]
            
            # Handle alpha
            if len(color) == 8:
                r = int(color[2:4], 16) / 255.0
                g = int(color[4:6], 16) / 255.0
                b = int(color[6:8], 16) / 255.0
            elif len(color) == 6:
                r = int(color[0:2], 16) / 255.0
                g = int(color[2:4], 16) / 255.0
                b = int(color[4:6], 16) / 255.0
            else:
                r, g, b = 0.5, 0.5, 0.5
            
            cr.set_source_rgb(r, g, b)
            cr.paint()
        except:
            cr.set_source_rgb(0.2, 0.2, 0.2)
            cr.paint()

    def update_color_preview(self, entry, preview):
        """Update color preview when entry changes"""
        color = entry.get_text()
        preview.queue_draw()
        preview.disconnect_by_func(self.draw_color_preview)
        preview.connect("draw", self.draw_color_preview, color)

    def show_color_picker(self, btn, entry, preview):
        """Show color picker dialog"""
        dialog = Gtk.ColorChooserDialog(title="Choose Color", parent=self)
        
        # Set current color
        try:
            color_str = entry.get_text().strip('#')
            if len(color_str) >= 6:
                rgba = Gdk.RGBA()
                rgba.parse('#' + color_str[-6:])
                dialog.set_rgba(rgba)
        except:
            pass
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            rgba = dialog.get_rgba()
            color_hex = '#{:02x}{:02x}{:02x}'.format(
                int(rgba.red * 255),
                int(rgba.green * 255),
                int(rgba.blue * 255)
            )
            entry.set_text(color_hex)
            self.update_color_preview(entry, preview)
        
        dialog.destroy()

    def refresh_theme_list(self):
        """Refresh the theme dropdown"""
        self.theme_combo.remove_all()
        if os.path.exists(THEMES_DIR):
            for f in sorted(os.listdir(THEMES_DIR)):
                if f.endswith(".ini"):
                    self.theme_combo.append_text(f.replace(".ini", ""))

    def on_theme_apply(self, btn):
        """Apply selected theme"""
        theme_name = self.theme_combo.get_active_text()
        if not theme_name:
            self.show_info_dialog("Please select a theme first")
            return
        
        theme_path = os.path.join(THEMES_DIR, f"{theme_name}.ini")
        if not os.path.exists(theme_path):
            self.show_error_dialog(f"Theme file not found: {theme_path}")
            return
        
        theme_cfg = configparser.ConfigParser(interpolation=None)
        theme_cfg.read(theme_path)
        
        # Update current color entries with theme values
        if 'colors' in theme_cfg:
            for key, val in theme_cfg['colors'].items():
                if key in self.color_entries:
                    self.color_entries[key].set_text(val)
        
        self.mark_unsaved()
        self.show_success_dialog(f"Theme '{theme_name}' applied! Click Save to persist changes.")

    def save_current_theme(self, btn):
        """Save current colors as a theme"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Save Current Theme"
        )
        dialog.format_secondary_text("Enter a name for this theme:")
        
        entry = Gtk.Entry()
        entry.set_placeholder_text("my-theme")
        box = dialog.get_content_area()
        box.pack_start(entry, False, False, 10)
        dialog.show_all()
        
        response = dialog.run()
        theme_name = entry.get_text().strip()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK and theme_name:
            theme_config = configparser.ConfigParser(interpolation=None)
            theme_config['colors'] = {}
            
            for key, entry in self.color_entries.items():
                theme_config['colors'][key] = entry.get_text()
            
            theme_path = os.path.join(THEMES_DIR, f"{theme_name}.ini")
            with open(theme_path, 'w') as f:
                theme_config.write(f)
            
            self.refresh_theme_list()
            self.show_success_dialog(f"Theme '{theme_name}' saved!")

    def delete_theme(self, btn):
        """Delete selected theme"""
        theme_name = self.theme_combo.get_active_text()
        if not theme_name:
            self.show_info_dialog("Please select a theme first")
            return
        
        if self.show_confirm_dialog(f"Delete theme '{theme_name}'?"):
            theme_path = os.path.join(THEMES_DIR, f"{theme_name}.ini")
            if os.path.exists(theme_path):
                os.remove(theme_path)
                self.refresh_theme_list()
                self.show_success_dialog(f"Theme '{theme_name}' deleted")

    def add_new_color(self, btn):
        """Add a new color to the palette"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Add New Color"
        )
        dialog.format_secondary_text("Enter color name and value:")
        
        box = dialog.get_content_area()
        name_entry = Gtk.Entry()
        name_entry.set_placeholder_text("color-name")
        value_entry = Gtk.Entry()
        value_entry.set_placeholder_text("#rrggbb")
        
        box.pack_start(Gtk.Label(label="Name:", xalign=0), False, False, 5)
        box.pack_start(name_entry, False, False, 5)
        box.pack_start(Gtk.Label(label="Value:", xalign=0), False, False, 5)
        box.pack_start(value_entry, False, False, 5)
        dialog.show_all()
        
        response = dialog.run()
        name = name_entry.get_text().strip()
        value = value_entry.get_text().strip()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK and name and value:
            if 'colors' not in self.config:
                self.config['colors'] = {}
            self.config['colors'][name] = value
            self.mark_unsaved()
            # Rebuild theme page
            self.stack.remove(self.stack.get_child_by_name("themes"))
            self.create_theme_page()
            self.show_all()

    def on_template_changed(self, combo):
        """Update template preview when selection changes"""
        template_name = combo.get_active_text()
        if template_name and template_name in self.presets['module_templates']:
            template = self.presets['module_templates'][template_name]
            preview_text = "\n".join([f"{k} = {v}" for k, v in template.items()])
            self.template_preview.get_buffer().set_text(preview_text)

    def on_add_module(self, btn):
        """Add a new module"""
        name = self.new_mod_name.get_text().strip()
        custom_type = self.new_mod_type_custom.get_text().strip()
        
        if not name:
            self.show_error_dialog("Please enter a module name")
            return
        
        section = f"module/{name}"
        if section in self.config:
            self.show_error_dialog(f"Module '{name}' already exists")
            return
        
        # Use custom type or template
        if custom_type:
            self.config[section] = {"type": custom_type}
        else:
            template_name = self.new_mod_type_combo.get_active_text()
            if template_name in self.presets['module_templates']:
                template = self.presets['module_templates'][template_name]
                self.config[section] = dict(template)
        
        self.mark_unsaved()
        
        # Rebuild module pages
        self.create_module_pages()
        self.show_all()
        
        # Switch to new module page
        self.stack.set_visible_child_name(f"mod_{name}")
        
        self.show_success_dialog(f"Module '{name}' created!")

    def delete_module(self, btn, section):
        """Delete a module"""
        mod_name = section.replace("module/", "")
        
        if self.show_confirm_dialog(f"Delete module '{mod_name}'?"):
            del self.config[section]
            self.mark_unsaved()
            
            # Remove from stack
            child = self.stack.get_child_by_name(f"mod_{mod_name}")
            if child:
                self.stack.remove(child)
            
            self.show_success_dialog(f"Module '{mod_name}' deleted")

    def add_module_property(self, btn, section, box, grid, module_data):
        """Add a new property to a module"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Add Module Property"
        )
        dialog.format_secondary_text("Enter property name and value:")
        
        content = dialog.get_content_area()
        name_entry = Gtk.Entry()
        name_entry.set_placeholder_text("property-name")
        value_entry = Gtk.Entry()
        value_entry.set_placeholder_text("value")
        
        content.pack_start(Gtk.Label(label="Name:", xalign=0), False, False, 5)
        content.pack_start(name_entry, False, False, 5)
        content.pack_start(Gtk.Label(label="Value:", xalign=0), False, False, 5)
        content.pack_start(value_entry, False, False, 5)
        dialog.show_all()
        
        response = dialog.run()
        prop_name = name_entry.get_text().strip()
        prop_value = value_entry.get_text().strip()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK and prop_name:
            self.config[section][prop_name] = prop_value
            self.mark_unsaved()
            
            # Rebuild the module page
            mod_name = section.replace("module/", "")
            child = self.stack.get_child_by_name(f"mod_{mod_name}")
            if child:
                self.stack.remove(child)
            
            self.create_module_pages()
            self.show_all()
            self.stack.set_visible_child_name(f"mod_{mod_name}")

    def create_backup(self, btn=None):
        """Create a backup of the current config"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"config_backup_{timestamp}.ini")
        
        try:
            shutil.copy2(CONFIG_FILE, backup_path)
            self.show_success_dialog(f"Backup created:\n{backup_path}")
        except Exception as e:
            self.show_error_dialog(f"Backup failed: {str(e)}")

    def show_restore_dialog(self, btn):
        """Show dialog to restore from backup"""
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.ini')], reverse=True)
        
        if not backups:
            self.show_info_dialog("No backups found")
            return
        
        dialog = Gtk.Dialog(title="Restore Backup", parent=self, flags=0)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Restore", Gtk.ResponseType.OK
        )
        
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_border_width(10)
        
        label = Gtk.Label(label="Select a backup to restore:")
        box.pack_start(label, False, False, 0)
        
        listbox = Gtk.ListBox()
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(400, 300)
        scroll.add(listbox)
        
        for backup in backups:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            # Parse timestamp from filename
            try:
                ts_str = backup.replace("config_backup_", "").replace(".ini", "")
                ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                date_label = Gtk.Label(label=ts.strftime("%Y-%m-%d %H:%M:%S"))
            except:
                date_label = Gtk.Label(label=backup)
            
            hbox.pack_start(date_label, True, True, 0)
            row.add(hbox)
            row.backup_file = backup
            listbox.add(row)
        
        box.pack_start(scroll, True, True, 0)
        dialog.show_all()
        
        response = dialog.run()
        selected = listbox.get_selected_row()
        
        if response == Gtk.ResponseType.OK and selected:
            backup_file = selected.backup_file
            backup_path = os.path.join(BACKUP_DIR, backup_file)
            
            try:
                shutil.copy2(backup_path, CONFIG_FILE)
                dialog.destroy()
                self.reload_config(None)
                self.show_success_dialog("Configuration restored successfully!")
            except Exception as e:
                self.show_error_dialog(f"Restore failed: {str(e)}")
        
        dialog.destroy()

    def reload_config(self, btn):
        """Reload configuration from file"""
        if self.unsaved_changes:
            if not self.show_confirm_dialog("Discard unsaved changes and reload?"):
                return
        
        self.config.read(CONFIG_FILE)
        self.unsaved_changes = False
        self.status_label.set_text("All changes saved")
        
        # Rebuild UI
        for child in self.stack.get_children():
            self.stack.remove(child)
        
        self.create_overview_page()
        self.create_theme_page()
        self.create_bar_page()
        self.create_module_pages()
        self.create_new_module_page()
        self.create_advanced_page()
        
        self.show_all()
        self.show_success_dialog("Configuration reloaded")

    def load_raw_config(self):
        """Load raw config into text view"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                content = f.read()
            self.raw_config_view.get_buffer().set_text(content)
        except Exception as e:
            self.show_error_dialog(f"Error loading config: {str(e)}")

    def validate_config(self, btn):
        """Validate config syntax"""
        buffer = self.raw_config_view.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        
        try:
            test_config = configparser.ConfigParser(interpolation=None)
            test_config.read_string(text)
            self.show_success_dialog("✓ Configuration syntax is valid!")
        except Exception as e:
            self.show_error_dialog(f"Configuration syntax error:\n{str(e)}")

    def apply_raw_config(self, btn):
        """Apply raw config changes"""
        if not self.show_confirm_dialog("Apply raw configuration changes?\nThis will overwrite current settings."):
            return
        
        buffer = self.raw_config_view.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        
        try:
            # Validate first
            test_config = configparser.ConfigParser(interpolation=None)
            test_config.read_string(text)
            
            # Write to file
            with open(CONFIG_FILE, 'w') as f:
                f.write(text)
            
            # Reload
            self.reload_config(None)
            self.show_success_dialog("Raw configuration applied!")
        except Exception as e:
            self.show_error_dialog(f"Error applying config:\n{str(e)}")

    def save_all(self, btn, restart=True):
        """Save all changes"""
        try:
            # Update Colors
            if 'colors' in self.config:
                for key, entry in self.color_entries.items():
                    self.config['colors'][key] = entry.get_text()
            
            # Update Bar
            if 'bar/main' in self.config:
                for key, entry in self.bar_entries.items():
                    self.config['bar/main'][key] = entry.get_text()

            # Update Modules
            for section in self.config.sections():
                if section.startswith("module/"):
                    mod_name = section.replace("module/", "")
                    mod_data = getattr(self, f"mod_entry_{mod_name}", None)
                    if mod_data:
                        for key, widget in mod_data.items():
                            if isinstance(widget, Gtk.TextBuffer):
                                start, end = widget.get_bounds()
                                value = widget.get_text(start, end, True)
                            else:
                                value = widget.get_text()
                            self.config[section][key] = value

            # Write to file
            with open(CONFIG_FILE, 'w') as configfile:
                self.config.write(configfile)
            
            self.unsaved_changes = False
            self.status_label.set_text("All changes saved")
            
            # Restart Polybar if requested
            if restart:
                self.restart_polybar(None)
            else:
                self.show_success_dialog("Configuration saved successfully!")
                
        except Exception as e:
            self.show_error_dialog(f"Error saving config:\n{str(e)}")

    def restart_polybar(self, btn):
        """Restart Polybar"""
        try:
            result = subprocess.run(
                ["polybar-msg", "cmd", "restart"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.show_success_dialog("Polybar restarted successfully!")
            else:
                self.show_error_dialog(f"Restart failed:\n{result.stderr}")
        except FileNotFoundError:
            self.show_error_dialog("polybar-msg command not found")
        except Exception as e:
            self.show_error_dialog(f"Error restarting Polybar:\n{str(e)}")

    def show_new_module_page(self, btn):
        """Navigate to new module page"""
        self.stack.set_visible_child_name("add_new")

    # --- DIALOG HELPERS ---

    def show_error_dialog(self, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_success_dialog(self, message):
        """Show success dialog"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Success"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_info_dialog(self, message):
        """Show info dialog"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Information"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_confirm_dialog(self, message):
        """Show confirmation dialog"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Confirm"
        )
        dialog.format_secondary_text(message)
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

if __name__ == "__main__":
    app = PolybarDesigner()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()
