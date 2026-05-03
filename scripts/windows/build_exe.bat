@echo off
setlocal
cd /d "%~dp0..\.."

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

python -m pip install pyinstaller
pyinstaller --noconfirm --windowed --name OpenGLSeasonalSakura --add-data "assets;assets" main.py

echo.
echo Build selesai. Cek folder dist\OpenGLSeasonalSakura.
