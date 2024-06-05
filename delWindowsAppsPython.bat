@echo off
cd "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"
rem 删除所有Python相关应用
del /f /q python.exe
pause
exit
