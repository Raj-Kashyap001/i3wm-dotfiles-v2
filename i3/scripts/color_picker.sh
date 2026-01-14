#!/bin/bash
color=$(xcolor)
echo -n "$color" | xclip -selection clipboard;
notify-send "Color Picked" "Hex code $color has been copied to clipboard."
