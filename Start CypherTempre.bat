@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ╔═══════════════════════════════════════╗
echo ║   CypherTempre Chat Local Server      ║
echo ╚═══════════════════════════════════════╝
echo.

powershell -Command "try { $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.PrefixOrigin -eq 'Dhcp' } | Select-Object -First 1).IPAddress; if ($ip) { Write-Host (' 📱 Open on your phone: http://' + $ip + ':8765') } else { Write-Host ' 📱 Make sure your phone is on the same Wi-Fi' } } catch { Write-Host ' 📱 Server starting...' }"

echo 💻 Computer URL: http://127.0.0.1:8765
echo.

python -m server --host 0.0.0.0 --port 8765

echo.
echo Server stopped.
pause
