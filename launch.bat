@echo off
cd /d "%~dp0"
start "" pythonw -c "import sys; sys.path.insert(0,'src'); from two_brain_studio.app import main; main()"
