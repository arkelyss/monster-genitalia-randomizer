@echo off
setlocal enabledelayedexpansion

set VENV_DIR=.venv
set PYPROJECT_TOML=pyproject.toml
set UV_INSTALL_URL=https://astral.sh/uv/install.ps1

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
:check_requirements
    call :log_step "Checking requirements..."

    where python >nul 2>&1
    if errorlevel 1 (
        call :log_error "python is not installed or not on PATH."
        call :log_error "Please install Python 3.11+ from https://python.org"
        exit /b 1
    )

    for /f "tokens=*" %%v in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do (
        set PYTHON_VERSION=%%v
    )
    call :log_info "Found Python !PYTHON_VERSION!"

    if not exist "%PYPROJECT_TOML%" (
        call :log_error "No %PYPROJECT_TOML% found in the current directory."
        call :log_error "Please run this script from the monster-genitalia-randomizer root directory."
        exit /b 1
    )
    call :log_info "Found %PYPROJECT_TOML%"
    exit /b 0

:: ============================================================================
:check_uv
    call :log_step "Checking for uv..."

    where uv >nul 2>&1
    if not errorlevel 1 (
        for /f "tokens=*" %%v in ('uv --version') do set UV_VERSION=%%v
        call :log_info "Found uv: !UV_VERSION!"
        exit /b 0
    )

    call :log_warn "uv not found. Installing uv..."
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    :: Refresh PATH so uv is visible in this session
    for /f "tokens=*" %%p in ('powershell -c "[System.Environment]::GetEnvironmentVariable(\"PATH\", \"User\")"') do (
        set PATH=!PATH!;%%p
    )

    where uv >nul 2>&1
    if errorlevel 1 (
        call :log_error "uv installation appeared to succeed but 'uv' is still not on PATH."
        call :log_error "Try opening a new terminal and running this script again."
        exit /b 1
    )

    for /f "tokens=*" %%v in ('uv --version') do set UV_VERSION=%%v
    call :log_info "uv installed successfully: !UV_VERSION!"
    exit /b 0

:: ============================================================================
:setup_venv
    call :log_step "Setting up virtual environment at %VENV_DIR%"
    set PERFORM_SETUP=true

    if exist "%VENV_DIR%\" (
        call :log_warn "Virtual environment already exists at %VENV_DIR%"
        :ask_loop
            echo.
            set /p RESPONSE="Delete %VENV_DIR% and reinstall? (y/n): "
            if /i "!RESPONSE!"=="y" (
                call :log_info "Deleting %VENV_DIR%..."
                rmdir /s /q "%VENV_DIR%"
                set PERFORM_SETUP=true
                call :log_info "%VENV_DIR% deleted."
            ) else if /i "!RESPONSE!"=="n" (
                call :log_info "Skipping virtual environment setup."
                set PERFORM_SETUP=false
            ) else (
                goto :ask_loop
            )
    )

    if "!PERFORM_SETUP!"=="true" (
        uv venv "%VENV_DIR%"
        call :log_info "%VENV_DIR% successfully created."
        call :log_info "Activate with: %VENV_DIR%\Scripts\activate"
    )
    exit /b 0

:: ============================================================================
:install_dependencies
    call :log_step "Installing dependencies from %PYPROJECT_TOML%"
    uv sync
    if errorlevel 1 (
        call :log_error "Failed to install dependencies."
        exit /b 1
    )
    call :log_info "Dependencies installed successfully."
    exit /b 0

:: ============================================================================
:main
    echo.
    echo MGR Environment Setup
    echo ================================
    echo.

    call :check_requirements
    if errorlevel 1 exit /b 1
    echo.

    call :check_uv
    if errorlevel 1 exit /b 1
    echo.

    call :setup_venv
    if errorlevel 1 exit /b 1
    echo.

    call :install_dependencies
    if errorlevel 1 exit /b 1

    echo.
    echo MGR Setup complete!
    echo You may now start MGR by entering 'python -m main' into a terminal or by using the 'start_mgr.bat' file.

    endlocal
