#!/usr/bin/env python3
"""
Polybar workspace module with dynamic app icons per workspace.
Uses i3ipc to subscribe to workspace/window events for live updates,
and maps each workspace's focused window class to a Nerd Font icon.

Install: pip install i3ipc
"""

import i3ipc
from i3ipc import Event

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
    "androidstudio":           "",

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

    "settings":       "󰒓",   # nf-md-cog
    "gnome-settings": "󰒓",


    # Office / Docs
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

FG_ACTIVE   = "#f9e2af"   # tertiary  — active workspace icon
FG_OCCUPIED = "#c0caf5"   # foreground — occupied but not focused
FG_EMPTY    = "#414868"   # disabled  — empty workspace
BG_ACTIVE   = "#24283b"   # background-alt (active)
BG_OCCUPIED = "#1f2335"   # darker bg
BG_EMPTY    = "#16161e"   # very dark


def class_to_icon(window_class: str | None) -> str:
    """Map a WM_CLASS string to a Nerd Font icon."""
    if not window_class:
        return DEFAULT_ICON
    key = window_class.strip().lower()
    if key in ICON_MAP:
        return ICON_MAP[key]
    for name, icon in ICON_MAP.items():
        if name in key:
            return icon
    return DEFAULT_ICON


def get_focused_class(workspace) -> str | None:
    """
    Get the window_class of the focused window in this workspace.
    Falls back to the first leaf window if nothing is focused.
    """
    focused = workspace.find_focused()
    if focused and focused.window_class:
        return focused.window_class
    leaves = workspace.leaves()
    return leaves[0].window_class if leaves else None


def render(i3: i3ipc.Connection) -> str:
    parts = []
    tree = i3.get_tree()

    # Get the workspaces sorted by number
    workspaces = sorted(tree.workspaces(), key=lambda w: w.num)

    for ws_con in workspaces:
        leaves   = ws_con.leaves()
        occupied = len(leaves) > 0
        focused_ws = tree.find_focused().workspace()
        active = focused_ws and focused_ws.id == ws_con.id

        # 1. Determine Icon
        if occupied:
            icon = class_to_icon(get_focused_class(ws_con))
        else:
            icon = DEFAULT_ICON

        # 2. Determine Style based on state
        if active:
            fg = "#f9e2af"        # dark text
            bg = "#414868"        # bright highlight (tertiary)
            ul = f"%{{u#f9e2af}}%{{+u}}"
        elif occupied:
            fg = FG_OCCUPIED
            bg = BG_OCCUPIED
            ul = "%{-u}" # Disable underline
        else:
            fg = FG_EMPTY
            bg = BG_EMPTY
            ul = "%{-u}"

        num = ws_con.num
        click = f"i3-msg workspace {ws_con.name}"

        # 3. Construct the label
        # We put the Underline tag at the start and the Reset tag at the end
        label = (
            f"{ul}"
            f"%{{B{bg}}}"
            f"%{{F{fg}}}"
            f"  {num} {icon}  "
            f"%{{F-}}%{{B-}}%{{-u}}"
        )

        parts.append(f"%{{A1:{click}:}}{label}%{{A}}")

    # Join with a space for separation between workspace buttons
    return " ".join(parts)

def on_workspace(i3: i3ipc.Connection, event):
    print(render(i3), flush=True)


def on_window(i3: i3ipc.Connection, event):
    print(render(i3), flush=True)


def main():
    i3 = i3ipc.Connection()

    # Initial render
    print(render(i3), flush=True)

    # Subscribe using i3.on() + Event enum
    i3.on(Event.WORKSPACE_FOCUS, on_workspace)
    i3.on(Event.WORKSPACE_INIT,  on_workspace)
    i3.on(Event.WORKSPACE_EMPTY, on_workspace)
    i3.on(Event.WINDOW_FOCUS,    on_window)
    i3.on(Event.WINDOW_NEW,      on_window)
    i3.on(Event.WINDOW_CLOSE,    on_window)

    # Block forever, dispatching events
    i3.main()


if __name__ == "__main__":
    main()