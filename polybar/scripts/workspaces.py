#!/usr/bin/env python3
"""
Polybar workspace module with dynamic app icons per workspace.
Uses i3ipc to subscribe to workspace/window events for live updates,
and maps each workspace's focused window class to a Nerd Font icon.

Install: pip install i3ipc
"""

import i3ipc
import os
import configparser
from i3ipc import Event

# Get the path to current-theme.ini
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THEME_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), "themes", "current-theme.ini")

def get_colors():
    config = configparser.ConfigParser()
    config.read(THEME_FILE)
    colors = config['colors']
    return {
        'fg_active': colors.get('yellow', '#f9e2af'),
        'fg_occupied': colors.get('foreground', '#c0caf5'),
        'fg_empty': colors.get('disabled', '#414868'),
        'bg_active': colors.get('background-alt', '#24283b'),
        'bg_occupied': colors.get('background', '#1b1b26'),
        'bg_empty': colors.get('background', '#16161e'),
        'primary': colors.get('primary', '#7aa2f7'),
    }

COLORS = get_colors()

# ─── Icon Map ────────────────────────────────────────────────────────
# Keys are lowercased WM_CLASS strings. Add more as needed.
ICON_MAP = {
    # Editors / IDEs
    "code":                    "",
    "visual studio code":      "",
    "vim":                     "",
    "nvim":                    "",
    "neovim":                  "",
    "nano":                    "",
    "emacs":                   "",
    "sublime_text":            "",
    "subl":                    "",
    "jetbrains-idea":          "",
    "idea":                    "",
    "pycharm":                 "",
    "goland":                  "",
    "webstorm":                "",
    "jetbrains-studio":        "",
    "androidstudio":           "",
    "studio":                  "",

    # Browsers
    "firefox":                 "",
    "google-chrome":           "",
    "chromium":                "",
    "chromium-browser":        "",
    "brave-browser":           "󰖟",
    "brave":                   "󰖟",
    "opera":                   "",
    "vivaldi":                 "󰖟",
    "microsoft-edge":          "",
    "torrowser":               "",
    "ungoogled-chromium":      "",

    # Terminals
    "x-terminal-emulator":     "",
    "bash":                    "",
    "zsh":                     "",
    "xterm":                   "",
    "urxvt":                   "",
    "rxvt":                    "",
    "st":                      "",
    "kitty":                   "",
    "alacritty":               "",
    "gnome-terminal":          "",
    "konsole":                 "",
    "xfce4-terminal":          "",
    "mate-terminal":           "",
    "tilix":                   "",
    "terminator":              "",
    "foot":                    "",

    # File Managers
    "thunar":                  "󰉋",
    "nautilus":                "󰉋",
    "pcmanfm":                 "󰉋",
    "nemo":                    "󰉋",
    "dolphin":                 "󰉋",
    "ranger":                  "󰉋",
    "nnn":                     "󰉋",

    # Music / Media
    "spotify":                 "",
    "rhythmbox":               "󰎆",
    "audacious":               "󰎆",
    "mpv":                     "",
    "vlc":                     "󰕼",
    "youtube-dl":              "󰕾",
    "mpd":                     "󰎆",
    "ncmpcpp":                 "󰎆",
    "pitivi":                  "󰕾",
    "kdenlive":                "",
    "audacity":                "󰎆",
    "ffplay":                  "󰕾",

    # Communication
    "discord":        "󰙯",   # nf-md-discord
    "slack":          "󰒱",   # nf-md-slack
    "element":        "󰍡",   # nf-md-matrix
    "thunderbird":    "󰈹",   # nf-fa-envelope
    "mutt":           "󰈹",
    "telegram":       "󰔂",   # nf-md-telegram
    "signal":         "󰭹",   # nf-md-signal
    "teams":          "󰊻",   # nf-md-microsoft_teams
    "zoom":           "󰖑",   # nf-md-video
    "evolution":      "󰈹",


    # Graphics / Design
    "gimp":           "",   # nf-md-palette
    "inkscape":       "",
    "krita":          "",
    "blender":        "󰂫",   # nf-md-blender
    "darktable":      "",
    "gwenview":       "󰋩",   # nf-md-image
    "eog":            "󰋩",
    "display":        "󰍹",   # nf-md-monitor


    # System / Utils
    "htop":           "󰭄",   # nf-md-chart_timeline
    "btop":           "󰭄",
    "top":            "󰭄",
    "systemmonitor":  "󰭄",
    "ksysguard":      "󰭄",
    "obs":            "󰑋",
    "settings":       "󰒓",   # nf-md-cog
    "gnome-settings": "󰒓",


    # Office / Docs
    "winword.exe":         "󱎒",
    "excel.exe":           "󱎏",
    "libreoffice":         "",  # nf-fa-file_text
    "soffice.bin":         "󰈙",
    "libreoffice-writer":  "󰈙",
    "libreoffice-calc":    "󰈛",  # nf-fa-file_excel
    "libreoffice-impress": "󰈧",  # nf-fa-file_powerpoint

    "okular":          "󰈦",  # nf-fa-file_pdf
    "evince":          "󰈦",
    "xpdf":            "󰈦",
    "mupdf":           "󰈦",
    "zathura":         "󰈦",


    # Dev / Terminal
    "git":             "󰊢",   # nf-dev-git
    "python3":         "󰌠",   # nf-dev-python
    "node":            "󰌘",   # nf-dev-nodejs

    "ssh":             "󰣀",   # nf-md-console
    "tmux":            "󰆍",   # nf-oct-terminal
    "screen":          "󰆍",


    # Network / Containers
    "docker":          "󰡨",   # nf-md-docker
    "wireshark":       "󰓾",   # nf-md-radar
    "nmap":            "󰓾",


    # Launchers
    "rofi":            "󰍉",   # nf-md-magnify
    "dmenu":           "󰍉",


    # Games / Misc
    "steam":           "󰓓",   # nf-fa-steam
}
# Default icon when no app match is found
DEFAULT_ICON = "󰊠"

def class_to_icon(win_class: str | None, win_name: str | None) -> str:
    """Map WM_CLASS or Window Title to a Nerd Font icon."""
    if win_name:
        name_lower = win_name.lower()
        if "whatsapp" in name_lower:
            return "󰖣"
        if "spotify" in name_lower:
            return ""
        if "discord" in name_lower:
            return "󰙯"

    if not win_class:
        return DEFAULT_ICON
    
    key = win_class.strip().lower()
    if key in ICON_MAP:
        return ICON_MAP[key]
    
    for name, icon in ICON_MAP.items():
        if name in key:
            return icon
            
    return DEFAULT_ICON

def get_focused_info(workspace):
    """Returns (window_class, window_name) for the focused window in workspace."""
    focused = workspace.find_focused()
    if focused and focused.name:
        return focused.window_class, focused.name
    
    leaves = workspace.leaves()
    if leaves:
        return leaves[0].window_class, leaves[0].name
        
    return None, None

def render(i3: i3ipc.Connection) -> str:
    parts = []
    tree = i3.get_tree()
    workspaces = sorted(tree.workspaces(), key=lambda w: w.num)

    for ws_con in workspaces:
        leaves = ws_con.leaves()
        occupied = len(leaves) > 0
        focused_node = tree.find_focused()
        active = False
        temp = focused_node
        while temp:
            if temp.type == 'workspace' and temp.id == ws_con.id:
                active = True
                break
            temp = temp.parent

        if occupied:
            win_class, win_name = get_focused_info(ws_con)
            icon = class_to_icon(win_class, win_name)
        else:
            icon = DEFAULT_ICON

        if active:
            fg = COLORS['fg_active']
            bg = COLORS['bg_active']
            ul = f"%{{u{COLORS['fg_active']}}}%{{+u}}"
        elif occupied:
            fg = COLORS['fg_occupied']
            bg = COLORS['bg_occupied']
            ul = "%{-u}"
        else:
            fg = COLORS['fg_empty']
            bg = COLORS['bg_empty']
            ul = "%{-u}"

        num = ws_con.num
        click = f"i3-msg workspace {ws_con.name}"

        label = (
            f"{ul}"
            f"%{{B{bg}}}"
            f"%{{F{fg}}}"
            f"  {num} {icon}  "
            f"%{{F-}}%{{B-}}%{{-u}}"
        )

        parts.append(f"%{{A1:{click}:}}{label}%{{A}}")

    return " ".join(parts)

def on_workspace(i3: i3ipc.Connection, event):
    print(render(i3), flush=True)

def on_window(i3: i3ipc.Connection, event):
    print(render(i3), flush=True)

def main():
    i3 = i3ipc.Connection()
    print(render(i3), flush=True)
    i3.on(Event.WORKSPACE_FOCUS, on_workspace)
    i3.on(Event.WORKSPACE_INIT,  on_workspace)
    i3.on(Event.WORKSPACE_EMPTY, on_workspace)
    i3.on(Event.WINDOW_FOCUS,    on_window)
    i3.on(Event.WINDOW_NEW,      on_window)
    i3.on(Event.WINDOW_CLOSE,    on_window)
    i3.on(Event.WINDOW_MOVE,     on_window)
    i3.on(Event.WINDOW_TITLE,    on_window)
    i3.main()

if __name__ == "__main__":
    main()
