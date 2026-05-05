#!/usr/bin/env bash
set -euo pipefail

readonly VENV_DIR=".venv"
readonly PYPROJECT_TOML="pyproject.toml"
readonly MAIN_PY="main.py"

log_info()  { echo -e "[INFO] $1"; }
log_warn()  { echo -e "[WARNING] $1"; }
log_error() { echo -e "[ERROR] $1" >&2; }
log_step()  { echo -e "[STEP] $1"; }

command_exists() {
    command -v "$1" &>/dev/null
}

# ============================================================================
start_mgr() {
    echo ""
    log_step "Starting MGR"
    echo "================================"

    if [[ ! -f "$MAIN_PY" ]]; then
        log_error "$MAIN_PY not found. Please make sure this script is in the right directory."
        exit 1
    fi

    if [[ ! -d "$VENV_DIR" ]]; then
        log_error "$VENV_DIR not found. Run mgr_setup first."
        exit 1
    fi

    echo ""
    uv run python "$MAIN_PY"
}

# ============================================================================
main () {
    start_mgr
}

main "$@"
