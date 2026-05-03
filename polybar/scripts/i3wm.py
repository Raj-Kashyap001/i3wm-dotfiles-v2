import i3ipc
import os
import configparser

# Get the path to current-theme.ini
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THEME_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), "themes", "current-theme.ini")

def get_alert_color():
    config = configparser.ConfigParser()
    config.read(THEME_FILE)
    return config['colors'].get('alert', '#f7768e')

ALERT_COLOR = get_alert_color()
conn = i3ipc.Connection()

current_mode = 'default'

def update():
    if current_mode == 'resize':
        output = f"%{{F{ALERT_COLOR}}}|RE|%{{F-}}"
    else:
        output = ""
    print(output, flush=True)

def on_mode(conn, e):
    global current_mode
    current_mode = e.change
    update()

conn.on('mode', on_mode)

# Initial update
update()

# Start event loop
conn.main()
