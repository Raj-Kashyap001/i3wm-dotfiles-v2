#!/bin/bash

# Ensure flameshot is running
pgrep -x flameshot > /dev/null || flameshot &

# Capture and pipe to xclip
# --raw outputs the image data to stdout
# xclip then grabs that data and holds it in the clipboard
flameshot gui --raw | xclip -selection clipboard -t image/png
