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

set "SLUG="
set /p SLUG=Se for ATUALIZAR um cliente que ja existe, cole aqui a pasta dele (ex.: joao-9f21ab) - ou deixe em branco pra criar um cliente novo:
if defined SLUG (
    "C:\Python314\python.exe" "C:\Users\iohra\Desktop\Tour-Project\_scripts\novo_cliente.py" "%SRC%" "%NOME%" --atualizar "%SLUG%"
) else (
    "C:\Python314\python.exe" "C:\Users\iohra\Desktop\Tour-Project\_scripts\novo_cliente.py" "%SRC%" "%NOME%"
)

echo.
pause
