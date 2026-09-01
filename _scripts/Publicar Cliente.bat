@echo off
setlocal
set "SRC=%~dp0"
if "%SRC:~-1%"=="\" set "SRC=%SRC:~0,-1%"

echo Publicando cliente a partir de:
echo   %SRC%
echo.
set "NOME="
set /p NOME=Nome do cliente:
if not defined NOME (
    echo Nome vazio, cancelado.
    pause
    exit /b 1
)

"C:\Python314\python.exe" "C:\Users\iohra\Desktop\Tour-Project\_scripts\novo_cliente.py" "%SRC%" "%NOME%"

echo.
pause
