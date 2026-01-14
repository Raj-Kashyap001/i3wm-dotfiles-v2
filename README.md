# i3wm Dotfiles with GUI installer

My Arch Rice with i3wm and polybar

## Preview

<img src="./screenshot.png">

## Features

- **Dotfiles Management**: Install, backup, and restore various dotfile configurations

## Requirements

- i3
- polybar
- waypaper
- feh
- nm-applet
- playerctl
- picom

`Only if need GUI dotfiles installer`

- Qt 6.2 or higher
- Qt Quick Controls 2
- Qt Quick Controls Material Style
- Standard C++ build tools

## Usage

1. Give persmission to execute on script for i3 and polybar in

```bash
chmod +x polybar/scripts/*.sh
chmod +x i3/scripts/*.{sh,py}
```

2. Installer the fonts in `fonts` directory if not have installed.

3. Download the binary from [releases](https://github.com/Raj-Kashyap001/repo/releases) section.

4. Run the application:

   ```bash
   ./Dotinst
   ```

5. Select dotfile components to install and click "Install Selected"

## Building Installer from source

1. Install dependencies:

   ```bash
   sudo apt-get install qt6-base-dev qt6-declarative-dev libqt6quickcontrols2-6 libqt6quickcontrols2-6-dev
   ```

2. Build the application:

   ```bash
   cd dotinst
   qmake
   make

   # or

   chmod +x build_installer.sh
   ./build_installer.sh
   ```

## Troubleshooting

If the application crashes:

- Copy paste configs to there corrosponding locations that's it....
  (ignore below probably)
- Ensure all required Qt libraries are installed
- Verify that the theme icons exist in the correct location
- Check that all resource files are properly included in the Qt resource system

## License

This project is licensed under the MIT License.
