import i3ipc

conn = i3ipc.Connection()

current_mode = 'default'

def update():
    if current_mode == 'resize':
        output = "%{F#f7768e}|RE|%{F-}"
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
