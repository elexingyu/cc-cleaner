#!/usr/bin/env bash
#
# cc-cleaner installer
# https://github.com/elexingyu/cc-cleaner
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/elexingyu/cc-cleaner/master/install.sh | bash
#
# This script will:
#   1. Check for Python 3.10+
#   2. Install pipx if not present
#   3. Install cc-cleaner via pipx
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get Python version as comparable integer (e.g., 3.10 -> 310)
get_python_version() {
    "$1" -c "import sys; print(sys.version_info.major * 100 + sys.version_info.minor)" 2>/dev/null || echo "0"
}

# Find suitable Python
find_python() {
    local candidates=("python3" "python" "python3.13" "python3.12" "python3.11" "python3.10")

    for cmd in "${candidates[@]}"; do
        if command_exists "$cmd"; then
            local version
            version=$(get_python_version "$cmd")
            if [ "$version" -ge 310 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# Main installation
main() {
    echo ""
    echo -e "${GREEN}cc-cleaner${NC} - The cache cleaner for the AI Coding era"
    echo ""

    # Step 1: Check Python
    print_step "Checking Python..."

    PYTHON_CMD=$(find_python) || {
        print_error "Python 3.10+ is required but not found."
        echo ""
        echo "Please install Python 3.10 or later:"
        echo "  macOS:  brew install python@3.12"
        echo "  Ubuntu: sudo apt install python3.12"
        echo "  Other:  https://www.python.org/downloads/"
        exit 1
    }

    PYTHON_VERSION=$("$PYTHON_CMD" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Found Python $PYTHON_VERSION ($PYTHON_CMD)"

    # Step 2: Check/Install pipx
    print_step "Checking pipx..."

    if command_exists pipx; then
        print_success "pipx is already installed"
    else
        print_warning "pipx not found, installing..."

        if command_exists brew; then
            # macOS with Homebrew
            brew install pipx
            pipx ensurepath
        elif command_exists apt; then
            # Debian/Ubuntu
            sudo apt update
            sudo apt install -y pipx
            pipx ensurepath
        else
            # Fallback: install via pip
            "$PYTHON_CMD" -m pip install --user pipx
            "$PYTHON_CMD" -m pipx ensurepath
        fi

        print_success "pipx installed"

        # Reload PATH
        export PATH="$HOME/.local/bin:$PATH"
    fi

    # Step 3: Install cc-cleaner
    print_step "Installing cc-cleaner..."

    if command_exists cc-cleaner; then
        print_warning "cc-cleaner is already installed, upgrading..."
        pipx upgrade cc-cleaner || pipx install cc-cleaner --force
    else
        pipx install cc-cleaner
    fi

    print_success "cc-cleaner installed"

    # Step 4: Verify installation
    print_step "Verifying installation..."

    # Reload PATH again
    export PATH="$HOME/.local/bin:$PATH"

    if command_exists cc-cleaner; then
        VERSION=$(cc-cleaner version 2>/dev/null || echo "unknown")
        print_success "Installation complete!"
        echo ""
        echo -e "${GREEN}cc-cleaner${NC} is ready to use."
        echo ""
        echo "Quick start:"
        echo "  cc-cleaner status    # See what can be cleaned"
        echo "  cc-cleaner clean all # Clean all safe caches"
        echo ""
        echo "For more info: cc-cleaner --help"
    else
        print_warning "Installation succeeded but 'cc-cleaner' not in PATH."
        echo ""
        echo "You may need to restart your terminal or run:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "Then try: cc-cleaner --help"
    fi
}

main "$@"
