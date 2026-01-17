#!/usr/bin/env bash

# Relaunch with custom theme overrides to lower the height
# padding: 4px 20px -> 4px top/bottom (Lower Height), 20px left/right
if [ -z "${ROFI_RETV+x}" ]; then
    exec rofi -show powermenu -modi "powermenu:$0" "$@" \
    -font "Sans 20" \
    -theme-str 'element { padding: 4px 20px; } listview { lines: 6; fixed-height: false; }'
fi

set -e
set -u

all=(shutdown reboot suspend hibernate logout lockscreen)
show=("${all[@]}")

declare -A texts
texts[lockscreen]="Lock Screen"
texts[logout]="Log Out"
texts[suspend]="Suspend"
texts[hibernate]="Hibernate"
texts[reboot]="Reboot"
texts[shutdown]="Shut Down"

declare -A icons
icons[lockscreen]="\Uf033e"
icons[logout]="\Uf0343"
icons[suspend]="\Uf04b2"
icons[hibernate]="\Uf02ca"
icons[reboot]="\Uf0709"
icons[shutdown]="\Uf0425"

declare -A actions
actions[lockscreen]="loginctl lock-session ${XDG_SESSION_ID-}"
actions[logout]="pkill -U $(whoami)"
actions[suspend]="systemctl suspend"
actions[hibernate]="systemctl hibernate"
actions[reboot]="systemctl reboot"
actions[shutdown]="systemctl poweroff"

confirmations=()
dryrun=false
showsymbols=true
showtext=true

function write_message {
    # Using 'large' instead of 'xx-large' helps lower the height further
    # while 'letter-spacing' maintains your 10px-style gap.
    local icon_style="font_size=\"large\" letter-spacing=\"10240\""
    local text_style="font_size=\"large\""
    
    if [ -z ${symbols_font+x} ]; then
        icon="<span $icon_style>$1</span>"
    else
        icon="<span font=\"${symbols_font}\" $icon_style>$1</span>"
    fi
    
    text="<span $text_style><b>\u00A0$2</b></span>"
    
    if [ "$showsymbols" = "true" ]; then
        if [ "$showtext" = "true" ]; then
            echo -n "\u200e$icon$text"
        else
            echo -n "\u200e$icon"
        fi
    else
        echo -n "$text"
    fi
}

function print_selection {
    echo -e "$1" | $(read -r -d '' entry; echo "echo $entry")
}

declare -A messages
for entry in "${all[@]}"; do
    messages[$entry]=$(write_message "${icons[$entry]}" "${texts[$entry]}")
done

if [ $# -gt 0 ]; then
    selection="${@}"
fi

echo -e "\0no-custom\x1ftrue"
echo -e "\0markup-rows\x1ftrue"

if [ -z "${selection+x}" ]; then
    echo -e "\0prompt\x1fPower "
    for entry in "${show[@]}"; do
        echo -e "${messages[$entry]}\0icon\x1f${icons[$entry]}"
    done
else
    for entry in "${show[@]}"; do
        if [ "$selection" = "$(print_selection "${messages[$entry]}")" ]; then
            if [ $dryrun = true ]; then
                echo "Selected: $entry" >&2
            else
                ${actions[$entry]}
            fi
            exit 0
        fi
    done
fi
