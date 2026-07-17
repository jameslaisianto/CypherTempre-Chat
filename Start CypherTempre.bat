@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   CypherTempre — personal intelligence
echo ========================================
echo.

powershell -Command "try { $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.PrefixOrigin -eq 'Dhcp' } | Select-Object -First 1).IPAddress; if ($ip) { Write-Host ('  Phone (same Wi-Fi): http://' + $ip + ':8765') } else { Write-Host '  Tip: same Wi-Fi for phone access' } } catch { Write-Host '  Starting server...' }"

echo   Computer: http://127.0.0.1:8765
echo.

python -m server --host 0.0.0.0 --port 8765

echo.
echo Server stopped.
pause
