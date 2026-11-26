@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Campus Trade - Stop All
echo ============================================
echo.

powershell -NoProfile -Command ^
    "$ports = @(5000, 2064); foreach ($p in $ports) { Write-Host ('[port ' + $p + '] searching...'); $ids = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($id in $ids) { taskkill /PID $id /T /F 2>$null | Out-Null; Write-Host ('  killed PID=' + $id) } }; Write-Host 'Done.'"

echo.
pause
