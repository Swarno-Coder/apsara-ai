@echo off
cd /d "%~dp0"
echo Starting Flutter Web App...
flutter pub get
flutter run -d web-server --web-port 3000
pause
