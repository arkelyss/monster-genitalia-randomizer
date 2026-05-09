@echo off
setlocal enabledelayedexpansion

:: Constants
set VENV_DIR=.venv
set MAIN_PY=main.py

goto :main

:: ============================================================================
:log_info
    echo [INFO] %~1
    exit /b 0

:log_warn
    echo [WARNING] %~1
    exit /b 0

:log_error
    echo [ERROR] %~1 1>&2
    exit /b 0

:log_step
    echo [STEP] %~1
    exit /b 0

:: ============================================================================
:start_mgr
    echo.
    call :log_step "Starting MGR..."
    echo ================================

    if not exist "%MAIN_PY%" (
        call :log_error "%MAIN_PY% not found. Please make sure this script is in the right directory."
        exit /b 1
    )

    if not exist "%VENV_DIR%\" (
        call :log_error "%VENV_DIR% not found. Run setup.bat first."
        exit /b 1
    )

    echo.
    uv run python "%MAIN_PY%"
    exit /b 0

:: ============================================================================
:main
    call :start_mgr
    if errorlevel 1 exit /b 1

    endlocal
