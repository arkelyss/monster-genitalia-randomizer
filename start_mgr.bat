@echo off
setlocal enabledelayedexpansion

set VENV_DIR=.venv
set PYPROJECT_TOML=pyproject.toml
set MAIN_PY=main.py
set UV_INSTALL_URL=https://astral.sh/uv/install.ps1
set REMOTE=origin
set BRANCH=develop

:: ============================================================================
set HAS_GIT=false
set HAS_GIT_REPO=false
set HAS_PYTHON=false
set PYTHON_OK=false
set HAS_UV=false
set HAS_VENV=false
set DEPS_SYNCED=false
set JUST_PULLED=false

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
:check_git
    where git >nul 2>&1
    if not errorlevel 1 (
        set HAS_GIT=true
    ) else (
        call :log_warn "git not found. Update checks will be skipped."
        call :log_warn "Install git from https://git-scm.com if you want automatic updates."
        exit /b 0
    )

    if exist ".git\" (
        set HAS_GIT_REPO=true
    ) else (
        call :log_warn "No .git folder found. If you downloaded the ZIP, update checks are unavailable."
        call :log_warn "To get automatic updates, clone the repository instead."
    )
    exit /b 0

:: ============================================================================
:check_python
    call :log_step "Checking Python..."

    where python >nul 2>&1
    if errorlevel 1 (
        call :log_error "python is not installed or not on PATH."
        call :log_error "Please install Python 3.11+ from https://python.org"
        exit /b 0
    )

    set HAS_PYTHON=true
    for /f "tokens=*" %%v in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do (
        set PYTHON_VERSION=%%v
    )
    call :log_info "Found Python !PYTHON_VERSION!"

    if not exist "%PYPROJECT_TOML%" (
        call :log_error "No %PYPROJECT_TOML% found. Please run this script from the MGR root directory."
        exit /b 1
    )

    :: Extract requires-python version using powershell for reliable regex
    for /f "tokens=*" %%v in ('powershell -command "Select-String -Path '%PYPROJECT_TOML%' -Pattern 'requires-python' | ForEach-Object { $_ -match '[0-9]+\.[0-9]+' | Out-Null; $Matches[0] }"') do (
        set REQUIRED_VERSION=%%v
    )

    if "!REQUIRED_VERSION!"=="" (
        :: No requires-python found, assume OK
        set PYTHON_OK=true
        exit /b 0
    )

    :: Compare versions
    for /f "tokens=1,2 delims=." %%a in ("!REQUIRED_VERSION!") do (
        set REQUIRED_MAJOR=%%a
        set REQUIRED_MINOR=%%b
    )
    for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
        set CURRENT_MAJOR=%%a
        set CURRENT_MINOR=%%b
    )

    if !CURRENT_MAJOR! GTR !REQUIRED_MAJOR! (
        set PYTHON_OK=true
        call :log_info "Python version meets requirement (^>= !REQUIRED_VERSION!)"
        exit /b 0
    )
    if !CURRENT_MAJOR! EQU !REQUIRED_MAJOR! (
        if !CURRENT_MINOR! GEQ !REQUIRED_MINOR! (
            set PYTHON_OK=true
            call :log_info "Python version meets requirement (^>= !REQUIRED_VERSION!)"
            exit /b 0
        )
    )

    set PYTHON_OK=false
    call :log_warn "Python !PYTHON_VERSION! is below required version !REQUIRED_VERSION!."
    call :log_warn "Please install Python !REQUIRED_VERSION!+ from https://python.org"
    exit /b 0

:: ============================================================================
:check_uv
    call :log_step "Checking for uv..."

    where uv >nul 2>&1
    if not errorlevel 1 (
        set HAS_UV=true
        for /f "tokens=*" %%v in ('uv --version') do set UV_VERSION=%%v
        call :log_info "Found uv: !UV_VERSION!"
        exit /b 0
    )

    call :log_warn "uv not found. Installing uv..."
    powershell -c "irm %UV_INSTALL_URL% | iex"

    :: Refresh PATH so uv is visible in this session
    for /f "tokens=*" %%p in ('powershell -c "[System.Environment]::GetEnvironmentVariable('PATH', 'User')"') do (
        set PATH=!PATH!;%%p
    )

    where uv >nul 2>&1
    if errorlevel 1 (
        call :log_error "uv installation appeared to succeed but 'uv' is still not on PATH."
        call :log_error "Try opening a new terminal and running this script again."
        exit /b 0
    )

    set HAS_UV=true
    for /f "tokens=*" %%v in ('uv --version') do set UV_VERSION=%%v
    call :log_info "uv installed successfully: !UV_VERSION!"
    exit /b 0

:: ============================================================================
:check_venv
    if exist "%VENV_DIR%\" (
        set HAS_VENV=true
        call :log_info "Found virtual environment at %VENV_DIR%"
    ) else (
        call :log_warn "No virtual environment found at %VENV_DIR%"
    )
    exit /b 0

:: ============================================================================
:check_deps_synced
    if "!HAS_VENV!"=="false" (
        set DEPS_SYNCED=false
        exit /b 0
    )

    if not exist "uv.lock" (
        set DEPS_SYNCED=true
        exit /b 0
    )

    :: Compare timestamps: is uv.lock newer than .venv?
    for /f "tokens=*" %%r in ('powershell -command "(Get-Item 'uv.lock').LastWriteTime -gt (Get-Item '%VENV_DIR%').LastWriteTime"') do (
        set LOCK_NEWER=%%r
    )

    if /i "!LOCK_NEWER!"=="True" (
        set DEPS_SYNCED=false
        call :log_warn "uv.lock is newer than %VENV_DIR% -- dependencies may be out of sync."
    ) else (
        set DEPS_SYNCED=true
    )
    exit /b 0

:: ============================================================================
:run_environment_check
    echo.
    call :log_step "Checking environment..."
    echo.

    call :check_git
    echo.
    call :check_python
    if errorlevel 1 exit /b 1
    echo.
    call :check_uv
    echo.
    call :check_venv
    call :check_deps_synced
    exit /b 0

:: ============================================================================
:check_for_updates
    if "!HAS_GIT!"=="false" exit /b 0
    if "!HAS_GIT_REPO!"=="false" exit /b 0

    echo.
    call :log_step "Checking for updates..."

    :: Check remote is reachable before fetching
    git ls-remote --exit-code %REMOTE% >nul 2>&1
    if errorlevel 1 (
        call :log_warn "Could not reach %REMOTE%. Skipping update check."
        call :log_warn "Check your internet connection and try again."
        exit /b 0
    )

    git fetch %REMOTE% %BRANCH% --quiet

    for /f "tokens=*" %%h in ('git rev-parse HEAD') do set LOCAL_HASH=%%h
    for /f "tokens=*" %%h in ('git rev-parse %REMOTE%/%BRANCH%') do set REMOTE_HASH=%%h

    if "!LOCAL_HASH!"=="!REMOTE_HASH!" (
        call :log_info "Already up to date."
        exit /b 0
    )

    :: Updates available - show changelog
    echo.
    call :log_info "Updates are available:"
    echo.
    for /f "tokens=*" %%l in ('git log HEAD..%REMOTE%/%BRANCH% --oneline') do (
        echo   %%l
    )
    echo.

    :ask_update_loop
        set /p UPDATE_RESPONSE="Would you like to pull these updates? (y/n): "
        if /i "!UPDATE_RESPONSE!"=="y" (
            call :do_update
        ) else if /i "!UPDATE_RESPONSE!"=="n" (
            call :log_info "Skipping update."
        ) else (
            echo.
            goto :ask_update_loop
        )
    exit /b 0

:: ============================================================================
:do_update
    :: Check for dirty working tree before touching anything
    git diff --quiet >nul 2>&1
    if errorlevel 1 (
        call :log_error "You have local changes that would be overwritten by the update."
        call :log_error "Please back up or discard your changes and run setup again."
        call :log_error "  To discard changes: git restore ."
        exit /b 0
    )
    git diff --cached --quiet >nul 2>&1
    if errorlevel 1 (
        call :log_error "You have staged changes that would be overwritten by the update."
        call :log_error "Please back up or discard your changes and run setup again."
        call :log_error "  To discard changes: git restore --staged ."
        exit /b 0
    )

    call :log_step "Pulling updates from %REMOTE%/%BRANCH%..."
    git pull %REMOTE% %BRANCH%
    if errorlevel 1 (
        call :log_error "git pull failed. Your environment has not been changed."
        call :log_error "Check your internet connection or resolve any conflicts manually."
        exit /b 0
    )

    call :log_info "Pull successful."

    :: Check if Python version requirement changed after pull
    call :check_python
    if "!PYTHON_OK!"=="false" (
        call :log_warn "The update requires a newer Python version."
        call :log_warn "Please update Python and re-run setup before using MGR."
        exit /b 0
    )

    if "!HAS_UV!"=="false" (
        call :log_error "uv is not available. Cannot sync dependencies."
        exit /b 0
    )

    call :log_step "Syncing dependencies..."
    uv sync
    if errorlevel 1 (
        call :log_error "uv sync failed. Your code was updated but dependencies may be incomplete."
        call :log_error "Try running 'Sync dependencies' from the menu, or re-run setup."
        exit /b 0
    )

    set JUST_PULLED=true
    set HAS_VENV=true
    set DEPS_SYNCED=true
    call :log_info "Dependencies synced successfully."
    echo.
    call :log_info "MGR is up to date and ready to use."
    exit /b 0

:: ============================================================================
:print_menu
    echo.
    echo What would you like to do?
    echo.

    if "!HAS_VENV!"=="false" (
        echo   1. Set up virtual environment ^<- do this first
    ) else (
        echo   1. Set up virtual environment
    )

    if "!HAS_VENV!"=="true" if "!DEPS_SYNCED!"=="false" (
        echo   2. Sync dependencies ^<- do this first
    ) else (
        echo   2. Sync dependencies
    )

    echo   3. Start MGR
    echo   4. Exit
    echo.
    exit /b 0

:: ============================================================================
:do_setup_venv
    echo.
    call :log_step "Setting up virtual environment at %VENV_DIR%"
    set PERFORM_SETUP=true

    if exist "%VENV_DIR%\" (
        echo.
        :ask_venv_loop
            call :log_warn "Virtual environment already exists at %VENV_DIR%"
            set /p VENV_RESPONSE="Delete %VENV_DIR% and reinstall? (y/n): "
            if /i "!VENV_RESPONSE!"=="y" (
                call :log_info "Deleting %VENV_DIR%..."
                rmdir /s /q "%VENV_DIR%"
                if errorlevel 1 (
                    call :log_error "Failed to delete %VENV_DIR%. Check folder permissions."
                    exit /b 0
                )
                call :log_info "%VENV_DIR% deleted."
                set PERFORM_SETUP=true
            ) else if /i "!VENV_RESPONSE!"=="n" (
                call :log_info "Skipping virtual environment setup."
                set PERFORM_SETUP=false
            ) else (
                echo.
                goto :ask_venv_loop
            )
    )

    if "!PERFORM_SETUP!"=="true" (
        if "!HAS_UV!"=="false" (
            call :log_error "uv is not available. Cannot create virtual environment."
            exit /b 0
        )
        uv venv "%VENV_DIR%"
        if errorlevel 1 (
            call :log_error "Failed to create virtual environment."
            exit /b 0
        )
        set HAS_VENV=true
        set DEPS_SYNCED=false
        call :log_info "%VENV_DIR% successfully created."
        call :log_info "Run 'Sync dependencies' to install packages."
    )
    exit /b 0

:: ============================================================================
:do_sync_deps
    echo.
    call :log_step "Syncing dependencies..."

    if "!HAS_UV!"=="false" (
        call :log_error "uv is not available. Cannot sync dependencies."
        exit /b 0
    )

    uv sync
    if errorlevel 1 (
        call :log_error "uv sync failed. Check the output above for details."
        exit /b 0
    )

    set DEPS_SYNCED=true
    set HAS_VENV=true
    call :log_info "Dependencies synced successfully."
    exit /b 0

:: ============================================================================
:do_start_mgr
    echo.

    if "!HAS_VENV!"=="false" (
        call :log_error "No virtual environment found. Please set up the environment first."
        exit /b 0
    )

    if "!PYTHON_OK!"=="false" (
        call :log_error "Python version is incompatible. Please update Python and re-run setup."
        exit /b 0
    )

    if not exist "%MAIN_PY%" (
        call :log_error "%MAIN_PY% not found. Please run this script from the MGR root directory."
        exit /b 0
    )

    call :log_step "Starting MGR..."
    echo ================================
    echo.
    uv run python "%MAIN_PY%"
    exit /b 0

:: ============================================================================
:run_menu
    call :print_menu
    set /p MENU_CHOICE="Enter choice (1-4): "
    echo.

    if "!MENU_CHOICE!"=="1" (
        call :do_setup_venv
        goto :run_menu
    )
    if "!MENU_CHOICE!"=="2" (
        call :do_sync_deps
        goto :run_menu
    )
    if "!MENU_CHOICE!"=="3" (
        if "!HAS_VENV!"=="false" (
            call :log_warn "MGR cannot start. See menu for details."
        ) else if "!PYTHON_OK!"=="false" (
            call :log_warn "MGR cannot start. See menu for details."
        ) else (
            call :do_start_mgr
        )
        goto :run_menu
    )
    if "!MENU_CHOICE!"=="4" (
        call :log_info "Finished."
        exit /b 0
    )

    call :log_warn "Invalid choice. Please enter 1, 2, 3, or 4."
    goto :run_menu

:: ============================================================================
:main
    echo.
    echo MGR Setup
    echo ================================

    call :run_environment_check
    if errorlevel 1 exit /b 1
    echo.

    call :check_for_updates
    echo.

    call :run_menu

    endlocal