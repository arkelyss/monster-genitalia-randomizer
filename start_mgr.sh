#!/usr/bin/env bash
set -euo pipefail

readonly VENV_DIR=".venv"
readonly PYPROJECT_TOML="pyproject.toml"
readonly MAIN_PY="main.py"
readonly UV_INSTALL_URL="https://astral.sh/uv/install.sh"
readonly REMOTE="origin"
readonly BRANCH="develop"

log_info()  { echo -e "[INFO] $1"; }
log_warn()  { echo -e "[WARNING] $1"; }
log_error() { echo -e "[ERROR] $1" >&2; }
log_step()  { echo -e "[STEP] $1"; }

command_exists() {
    command -v "$1" &>/dev/null
}

# ============================================================================
HAS_GIT=false
HAS_GIT_REPO=false
HAS_PYTHON=false
PYTHON_OK=false         # version meets pyproject.toml requires-python
HAS_UV=false
HAS_VENV=false
DEPS_SYNCED=false       # true if uv.lock is not newer than .venv
JUST_PULLED=false

# ============================================================================
check_git() {
    if command_exists git; then
        HAS_GIT=true
    else
        log_warn "git not found. Update checks will be skipped."
        log_warn "Install git from https://git-scm.com if you want automatic updates."
    fi

    if [[ "$HAS_GIT" == true && -d ".git" ]]; then
        HAS_GIT_REPO=true
    elif [[ "$HAS_GIT" == true ]]; then
        log_warn "No .git folder found. If you downloaded a ZIP, update checks are unavailable."
        log_warn "To get automatic updates, clone the repository instead."
    fi
}

# ============================================================================
check_python() {
    log_step "Checking Python..."

    if ! command_exists python3; then
        log_error "python3 is not installed or not on PATH."
        log_error "Please install Python 3.11+ from https://python.org"
        return
    fi

    HAS_PYTHON=true
    local python_version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Found Python $python_version"

    if [[ ! -f "$PYPROJECT_TOML" ]]; then
        log_error "No $PYPROJECT_TOML found. Please run this script from the MGR root directory."
        exit 1
    fi

    # Extract requires-python minimum version from pyproject.toml (handles >=3.x or ~=3.x)
    local required_version
    required_version=$(grep 'requires-python' "$PYPROJECT_TOML" \
        | grep -oE '[0-9]+\.[0-9]+' \
        | head -1)

    if [[ -n "$required_version" ]]; then
        local required_major required_minor current_major current_minor
        required_major=$(echo "$required_version" | cut -d. -f1)
        required_minor=$(echo "$required_version" | cut -d. -f2)
        current_major=$(python3 -c "import sys; print(sys.version_info.major)")
        current_minor=$(python3 -c "import sys; print(sys.version_info.minor)")

        if (( current_major > required_major )) || \
           (( current_major == required_major && current_minor >= required_minor )); then
            PYTHON_OK=true
            log_info "Python version meets requirement (>= $required_version)"
        else
            log_warn "Python $python_version is below required version $required_version."
            log_warn "Please install Python $required_version+ from https://python.org"
            PYTHON_OK=false
        fi
    else
        # No requires-python found, assume OK
        PYTHON_OK=true
    fi
}

# ============================================================================
check_uv() {
    log_step "Checking for uv..."

    if command_exists uv; then
        HAS_UV=true
        log_info "Found uv: $(uv --version)"
        return 0
    fi

    log_warn "uv not found. Installing uv..."

    if command_exists curl; then
        curl -LsSf "$UV_INSTALL_URL" | sh
    elif command_exists wget; then
        wget -qO- "$UV_INSTALL_URL" | sh
    elif command_exists powershell; then
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    else
        log_error "Could not find curl or wget. Cannot install uv automatically."
        log_error "Please install uv manually from: https://docs.astral.sh/uv/"
        return
    fi

    # Reload PATH in case uv was just added
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

    if command_exists uv; then
        HAS_UV=true
        log_info "uv installed successfully: $(uv --version)"
    else
        log_error "uv installation appeared to succeed but 'uv' is still not on PATH."
        log_error "Try opening a new terminal and running this script again."
    fi
}

# ============================================================================
check_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        HAS_VENV=true
        log_info "Found virtual environment at $VENV_DIR"
    else
        log_warn "No virtual environment found at $VENV_DIR"
    fi
}

# ============================================================================
check_deps_synced() {
    if [[ "$HAS_VENV" == false ]]; then
        DEPS_SYNCED=false
    else
        DEPS_SYNCED=true
    fi
}

# ============================================================================
run_environment_check() {
    echo ""
    log_step "Checking environment..."
    echo ""

    check_git
    echo ""
    check_python
    echo ""
    check_uv
    echo ""
    check_venv
    check_deps_synced
}

# ============================================================================
check_for_updates() {
    if [[ "$HAS_GIT" == false || "$HAS_GIT_REPO" == false ]]; then
        return
    fi

    echo ""
    log_step "Checking for updates..."

    # Check remote is reachable before fetching
    if ! git ls-remote --exit-code "$REMOTE" &>/dev/null; then
        log_warn "Could not reach $REMOTE. Skipping update check."
        log_warn "Check your internet connection and try again."
        return
    fi

    git fetch "$REMOTE" "$BRANCH" --quiet

    local local_hash remote_hash
    local_hash=$(git rev-parse HEAD)
    remote_hash=$(git rev-parse "$REMOTE/$BRANCH")

    if [[ "$local_hash" == "$remote_hash" ]]; then
        log_info "Already up to date."
        return
    fi

    # Updates are available — show changelog
    echo ""
    log_info "Updates are available:"
    echo ""
    git log HEAD.."$REMOTE/$BRANCH" --oneline | sed 's/^/  /'
    echo ""

    local response
    while true; do
        read -rp "Would you like to pull these updates? (y/n): " response
        case "$response" in
            y|Y) do_update; break ;;
            n|N) log_info "Skipping update."; break ;;
            *)   echo "" ;;
        esac
    done
}

# ============================================================================
do_update() {
    # Discard any local changes so the pull always succeeds cleanly
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_warn "Local changes detected. Discarding them to apply the update..."
        git reset --hard HEAD
        git clean -fd
        log_info "Local changes discarded."
    fi

    log_step "Pulling updates from $REMOTE/$BRANCH..."
    if ! git pull "$REMOTE" "$BRANCH"; then
        log_error "git pull failed. Your environment has not been changed."
        log_error "Check your internet connection or resolve any conflicts manually."
        return
    fi

    log_info "Pull successful."

    # Check if Python version requirement changed after pull
    check_python

    if [[ "$PYTHON_OK" == false ]]; then
        log_warn "The update requires a newer Python version."
        log_warn "Please update Python and re-run setup before using MGR."
        return
    fi

    if [[ "$HAS_UV" == false ]]; then
        log_error "uv is not available. Cannot sync dependencies."
        return
    fi

    log_step "Syncing dependencies..."
    if ! uv sync; then
        log_error "uv sync failed. Your code was updated but dependencies may be incomplete."
        log_error "Try running 'Sync dependencies' from the menu, or re-run setup."
        return
    fi

    JUST_PULLED=true
    HAS_VENV=true
    DEPS_SYNCED=true
    log_info "Dependencies synced successfully."
    echo ""
    log_info "MGR is up to date and ready to use."
}

# ============================================================================
print_menu() {
    echo ""
    echo "What would you like to do?"
    echo ""

    # Option 1 — Set up virtual environment
    if [[ "$HAS_VENV" == false ]]; then
        echo "  1. Set up virtual environment <- do this first"
    else
        echo "  1. Set up virtual environment"
    fi

    echo "  2. Check for updates"
    echo "  3. Start MGR"
    echo "  4. Exit"
    echo ""
}

# ============================================================================
do_setup_venv() {
    echo ""
    log_step "Setting up virtual environment at $VENV_DIR"
    local perform_setup=true

    if [[ -d "$VENV_DIR" ]]; then
        echo ""
        while true; do
            log_warn "Virtual environment already exists at $VENV_DIR"
            read -rp "Delete $VENV_DIR and reinstall? (y/n): " response
            case "$response" in
                y|Y)
                    log_info "Deleting $VENV_DIR..."
                    if ! rm -rf "$VENV_DIR"; then
                        log_error "Failed to delete $VENV_DIR. Check folder permissions."
                        return
                    fi
                    log_info "$VENV_DIR deleted."
                    perform_setup=true
                    break
                    ;;
                n|N)
                    log_info "Skipping virtual environment setup."
                    perform_setup=false
                    break
                    ;;
                *) echo "" ;;
            esac
        done
    fi

    if [[ "$perform_setup" == true ]]; then
        if [[ "$HAS_UV" == false ]]; then
            log_error "uv is not available. Cannot create virtual environment."
            return
        fi
        if ! uv venv "$VENV_DIR"; then
            log_error "Failed to create virtual environment."
            return
        fi
        HAS_VENV=true
        log_info "$VENV_DIR successfully created."

        # Automatically sync dependencies after venv creation
        echo ""
        log_step "Syncing dependencies..."
        if ! uv sync; then
            log_error "uv sync failed. Check the output above for details."
            return
        fi
        DEPS_SYNCED=true
        log_info "Dependencies synced successfully."
    fi
}

# ============================================================================
do_start_mgr() {
    echo ""

    if [[ "$HAS_VENV" == false ]]; then
        log_error "No virtual environment found. Please set up the environment first."
        return
    fi

    if [[ "$PYTHON_OK" == false ]]; then
        log_error "Python version is incompatible. Please update Python and re-run setup."
        return
    fi

    if [[ ! -f "$MAIN_PY" ]]; then
        log_error "$MAIN_PY not found. Please run this script from the MGR root directory."
        return
    fi

    log_step "Starting MGR..."
    echo "================================"
    echo ""
    uv run python "$MAIN_PY"
}

# ============================================================================
run_menu() {
    while true; do
        print_menu
        read -rp "Enter choice (1-4): " choice
        echo ""
        case "$choice" in
            1) do_setup_venv ;;
            2) check_for_updates ;;
            3)
                if [[ "$HAS_VENV" == false || "$PYTHON_OK" == false ]]; then
                    log_warn "MGR cannot start. See menu for details."
                else
                    do_start_mgr
                fi
                ;;
            4)
                log_info "Finished!"
                exit 0
                ;;
            *)
                log_warn "Invalid choice. Please enter 1, 2, 3, or 4."
                ;;
        esac
    done
}

# ============================================================================
main() {
    echo -e "\nMGR Setup"
    echo "================================"

    run_environment_check
    echo ""
    check_for_updates
    echo ""
    run_menu
}

main "$@"