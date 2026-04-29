@echo off
REM ============================================================
REM Esinta Emulation Framework - BadDownloader Stage 2
REM FOR AUTHORIZED SECURITY TESTING ONLY
REM ============================================================

echo [*] BadDownloader payload executing...
echo [*] Running discovery commands...

whoami
ipconfig /all
systeminfo
net user

echo [*] Establishing persistence...
schtasks /create /tn "BadDownloader" /tr "calc.exe" /sc daily /st 08:00 /f

echo [*] Launching payload...
calc.exe

echo [*] BadDownloader complete.
