#!/bin/bash

# Build script for i3wm dotfiles manager

# Clean previous build
cd dotinst || exit 1
qmake6 dotinstall_gui.pro
make clean
make

# Move binary to parent directory
mv Dotinst ../

# Run the application
cd ..
./Dotinst