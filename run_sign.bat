@echo off
setlocal
cd /d "%~dp0"
set /p heybox_ck=<cookie.txt
echo [%date% %time%] ==== start ==== >> sign_log.txt
"C:\Users\March\.workbuddy\binaries\node\versions\22.22.2\node.exe" heybox_sign.js >> sign_log.txt 2>&1
set RC=%errorlevel%
echo [%date% %time%] ==== end exit=%RC% ==== >> sign_log.txt
endlocal
