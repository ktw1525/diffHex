@echo off
REM Install pyinstaller if not already installed
pip install pyinstaller

REM Run pyinstaller with the specified options
pyinstaller --onefile --name hexEditor --add-data "logo.png;." --hidden-import PIL._tkinter_finder main.py

REM Output file will be located in ./dist/hexEditor
echo Build complete. The executable is located in the dist folder.
