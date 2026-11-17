@echo off
rem Starts the heritage3d virtual museum on this laptop and opens it in Chrome.
rem Needs Python and an internet connection (the 3D library three.js loads from a CDN).
cd /d "%~dp0..\..\museum"
start "" "http://localhost:8000"
python -m http.server 8000
