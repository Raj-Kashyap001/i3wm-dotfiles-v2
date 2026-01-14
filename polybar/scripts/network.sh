#!/bin/bash

# Check internet connectivity and which interface
if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
    # Online, check which interface has default route
    default_iface=$(ip route show default | head -1 | awk '{print $5}')
    if [[ $default_iface =~ ^(enp|eth) ]]; then
        eth_conn=$(nmcli -t -f NAME,TYPE con show --active 2>/dev/null | grep ":802-3-ethernet" | head -1 | cut -d: -f1)
        if [ -n "$eth_conn" ]; then
            echo "%{F#7aa2f7}eth:  %{F-} $eth_conn"
        else
            echo "%{F#7aa2f7}eth:  %{F-} Ethernet"
        fi
    elif [[ $default_iface =~ ^(wlan|wlp) ]]; then
        wifi_conn=$(nmcli -t -f NAME,TYPE con show --active 2>/dev/null | grep ":wireless" | head -1 | cut -d: -f1)
        if [ -n "$wifi_conn" ]; then
            echo "%{F#7aa2f7}wifi: %{F-} $wifi_conn"
        else
            essid=$(iwgetid -r 2>/dev/null)
            if [ -n "$essid" ]; then
                echo "%{F#7aa2f7}wifi: %{F-} $essid"
            else
                echo "%{F#7aa2f7}wifi: %{F-} WiFi"
            fi
        fi
    else
        echo "%{F#7aa2f7}eth: %{F-} Online"
    fi
else
    echo "%{F#f7768e}net:  %{F-} OFFLINE"
fi