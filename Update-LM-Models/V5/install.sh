#!/bin/bash

echo "Installing OpenCode Model Updater V5 (Linux TUI)..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies (rich)..."
pip3 install rich --user

# Determine install location
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/model_updater.py"
TARGET_PATH="$INSTALL_DIR/mu"

# Create the wrapper script
echo "Creating 'mu' command in $INSTALL_DIR..."
cat << EOF > "$TARGET_PATH"
#!/bin/bash
python3 "$SCRIPT_PATH" "\$@"
EOF

chmod +x "$TARGET_PATH"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Warning: $HOME/.local/bin is not in your PATH."
    echo "Add the following to your shell config (.bashrc, .zshrc, etc.):"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "Installation complete!"
echo "You can now run the updater by typing 'mu' in your terminal."
echo "(You may need to restart your terminal or source your shell config first if ~/.local/bin was just added to PATH)"
