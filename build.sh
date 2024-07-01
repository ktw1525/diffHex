#!/bin/sh
# Install pyinstaller if not already installed
pip install pyinstaller

# Run pyinstaller with the specified options
pyinstaller --onefile --name hexEditor --add-data "logo.png:." --hidden-import PIL._tkinter_finder main.py

# Output file will be located in ./dist/hexEditor
echo "Build complete. The executable is located in the dist folder."
