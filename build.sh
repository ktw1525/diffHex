#!/bin/sh
# Install pyinstaller if not already installed
pip install pyinstaller

sudo apt update -y
sudo apt upgrade -y
sudo apt install libpython3-dev -y


# Run pyinstaller with the specified options
pyinstaller --onefile --name hexEditor --add-data "logo.png:." --hidden-import PIL._tkinter_finder --collect-submodules PIL main.py


# Output file will be located in ./dist/hexEditor
echo "Build complete. The executable is located in the dist folder."
