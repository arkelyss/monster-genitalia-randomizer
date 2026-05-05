#!/usr/bin/env bash
set -euo pipefail

readonly VENV_DIR=".venv"
readonly PYPROJECT_TOML="pyproject.toml"
readonly UV_INSTALL_URL="https://astral.sh/uv/install.sh"

log_info()  { echo -e "[INFO] $1"; }
log_warn()  { echo -e "[WARNING] $1"; }
log_error() { echo -e "[ERROR] $1" >&2; }
log_step()  { echo -e "[STEP] $1"; }

command_exists() {
    command -v "$1" &>/dev/null
}

# ============================================================================
check_requirements() {
    log_step "Checking requirements..."

    if ! command_exists python3; then
        log_error "python3 is not installed or not on PATH."
        log_error "Please install Python 3.11+ from https://python.org"
        exit 1
    fi

    local python_version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Found Python $python_version"

    if [[ ! -f "$PYPROJECT_TOML" ]]; then
        log_error "No $PYPROJECT_TOML found in the current directory."
        log_error "Please run this script from the monster-genitalia-randomizer root directory."
        exit 1
    fi

    log_info "Found $PYPROJECT_TOML"
}

# ============================================================================
check_uv() {
    log_step "Checking for uv..."

    if command_exists uv; then
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
        log_error "Please install curl or wget, or install uv manually from: https://docs.astral.sh/uv/"
    fi

    if ! command_exists uv; then
        log_error "uv installation appeared to succeed but 'uv' is still not on PATH."
        log_error "Try opening a new terminal and running this script again."
        exit 1
    fi

    log_info "uv installed successfully: $(uv --version)"
}

# ============================================================================
setup_venv () {
    log_step "Setting up virtual environment at $VENV_DIR"
    local perform_setup=true

    if [[ -d "$VENV_DIR" ]]; then
        echo ""
        while true; do
            log_warn "Virtual environment already exists at $VENV_DIR"
            read -p "Delete $VENV_DIR and reinstall? (y/n): " response

            case "$response" in
                y|Y)
                    log_info "Deleting $VENV_DIR"
                    rm -rf $VENV_DIR
                    perform_setup=true
                    log_info "$VENV_DIR deleted."
                    break
                    ;;
                n|N)
                    log_info "Skipping virtual environment setup."
                    perform_setup=false
                    break
                    ;;
                *)
                    echo ""
                    ;;
            esac
        done
    fi

    if [[ perform_setup == true ]]; then
        uv venv $VENV_DIR
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
            log_info "$VENV_DIR successfully created."
            log_info "Activate with: $VENV_DIR\Scripts\activate"
        else
            log_info "$VENV_DIR successfully created."
            log_info "Activate with: source $VENV_DIR/bin/activate"
        fi
    fi
}

# ============================================================================
install_dependencies() {
    log_step "Installing dependencies from $PYPROJECT_TOML"
    uv sync
    log_info "Dendencies installed successfully."
}


# ============================================================================
main () {
    echo -e "\nMGR Environment Setup"
    echo "================================"

    check_requirements
    echo ""
    check_uv
    echo ""
    setup_venv
    echo ""
    install_dependencies

    echo -e "\nMGR Setup complete!"
    echo "You may now start MGR by entering 'python -m main.py' into a terminal or by using the 'start_mgr.bat' file."
}

main "$@"
