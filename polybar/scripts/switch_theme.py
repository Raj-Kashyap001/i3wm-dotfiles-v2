#!/usr/bin/env python3

import sys
import os
import subprocess

def get_available_themes(themes_dir):
    if not os.path.exists(themes_dir):
        return []
    return sorted([f.replace('.ini', '') for f in os.listdir(themes_dir) if f.endswith('.ini') and f != 'current-theme.ini'])

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    polybar_dir = os.path.dirname(script_dir)
    themes_dir = os.path.join(polybar_dir, "themes")
    
    available_themes = get_available_themes(themes_dir)

    # Handle Rofi integration
    if len(sys.argv) > 1 and sys.argv[1] == "--rofi":
        if not available_themes:
            print("No themes available.")
            sys.exit(1)
        
        # Create a newline-separated string of themes for Rofi
        themes_string = "\n".join(available_themes)
        
        try:
            # Run Rofi and get the selected theme
            process = subprocess.Popen(['rofi', '-dmenu', '-p', 'Select Theme', '-i'], 
                                       stdin=subprocess.PIPE, 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       text=True)
            selected_theme, _ = process.communicate(input=themes_string)
            selected_theme = selected_theme.strip()
            
            if selected_theme in available_themes:
                # Recursively call the script with the selected theme name
                subprocess.run([sys.executable, __file__, selected_theme], check=True)
            sys.exit(0)
        except Exception as e:
            print(f"Rofi error: {e}")
            sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: switch_theme.py <theme_name> | --rofi")
        print(f"Available themes: {', '.join(available_themes)}")
        sys.exit(1)

    theme_name = sys.argv[1]
    theme_file = os.path.join(themes_dir, f"{theme_name}.ini")
    current_theme_file = os.path.join(themes_dir, "current-theme.ini")
    launch_script = os.path.join(polybar_dir, "launch.sh")

    if not os.path.exists(theme_file):
        print(f"Error: Theme '{theme_name}' not found at {theme_file}")
        sys.exit(1)

    try:
        # Copy the selected theme to current-theme.ini
        with open(theme_file, 'r') as src:
            content = src.read()
        with open(current_theme_file, 'w') as dst:
            dst.write(content)
        
        print(f"Theme switched to '{theme_name}'")

        # Restart Polybar
        if os.path.exists(launch_script):
            print("Restarting Polybar...")
            # Use subprocess.Popen with shell=True to match launch.sh behavior
            # and avoid blocking if possible, though launch.sh itself backgrounds polybar
            subprocess.run([launch_script], check=True, shell=True)
        else:
            print("Warning: launch.sh not found. Please restart Polybar manually.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
