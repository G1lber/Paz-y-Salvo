@echo off
REM =============================================
REM Exportar base de datos MySQL local
REM =============================================
REM Requisito: tener mysqldump en el PATH
REM (viene con XAMPP, WAMP o MySQL Workbench)
REM =============================================

set DB_NAME=pazysalvo
set DB_USER=root
set DB_PASS=root
set DB_HOST=localhost
set OUTPUT_FILE=pazysalvo_dump.sql

echo Exportando base de datos %DB_NAME%...
mysqldump -h %DB_HOST% -u %DB_USER% -p%DB_PASS% %DB_NAME% > %OUTPUT_FILE%

if %ERRORLEVEL% == 0 (
    echo Exportacion exitosa: %OUTPUT_FILE%
) else (
    echo Error al exportar. Verifica que mysqldump este en el PATH.
    echo Tambien puedes usar el panel de phpMyAdmin o MySQL Workbench.
)