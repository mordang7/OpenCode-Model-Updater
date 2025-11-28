# Update Models Script Documentation

## Overview

This project contains versions of a bash script to update AI models for OpenCode by fetching from local Ollama and LM Studio servers and updating the configuration JSON file.

## Versions

-   **V1/**: Original script (moved from root).
-   **V2/**: Improved version with enhancements.
-   **V3/**: Version with user prompts for Ollama and LM Studio setup.
-   **V4/**: Latest version with Llama.cpp support added.
-   **V5/**: Linux TUI version using Python and `rich` library.
-   **Windows_V1/**: Native Windows GUI application.

## Changes Made in V2

1. **Server Timeout**: Added 15-second timeout for server reachability checks using `curl --connect-timeout 15 --max-time 15`.
2. **Failure Handling**: If both servers are unreachable, display "Both Servers could not be reached - No Changes were Made" and exit without modifying the config.
3. **Conditional Updates**:
    - If only Ollama is running: Update only Ollama models, show "Only the Ollama models were Updated!".
    - If only LM Studio is running: Update only LM Studio models, show "Only the LM Studio models were Updated!".
    - If both are running: Update both, show "Both Ollama & LM Studio models were Updated!".
4. **Model Removal**: Check for models no longer present on servers and remove them from the config, displaying "X Non Present Models were Removed!" where X is the count.
5. **Backup Adjustment**: Backup the config only if at least one server is reachable.
6. **Message Refinement**: Removed individual "Updated X models" prints; added summary messages for updates and removals.

## Changes Made in V3

1. **User Prompts**: On first run, prompts user to choose between localhost or network IP for Ollama and LM Studio setups.
2. **Dynamic URLs**: Sets OLLAMA_URL and LMSTUDIO_URL based on user input (localhost or entered IP), replacing hardcoded IPs.
3. **Config Persistence**: Saves user choices in ~/.update-models-config for future runs, avoiding re-prompting.
4. **Improved Flexibility**: Supports both local and network deployments seamlessly.

## Changes Made in V4

1. **Added Llama.cpp Support**: Prompts for Llama.cpp setup (localhost or network), fetches models from /v1/models endpoint (default port 8080), updates config with 'llamacpp' provider.
2. **Updated Failure Check**: Now checks if all three servers fail, exits with "All Servers could not be reached - No Changes were Made".
3. **Enhanced Update Messages**: Dynamically lists which providers were updated (e.g., "Only the Ollama & LM Studio models were Updated!").
4. **Config Persistence**: Saves LLAMA_URL in ~/.update-models-config.

## Changes Made in V5 (Linux TUI)

1.  **Python Rewrite**: Replaced Bash script with a robust Python script (`model_updater.py`).
2.  **Terminal UI (TUI)**: Utilizes the `rich` library to provide a modern terminal interface with:
    -   Real-time progress bars for connection checks.
    -   Formatted summary tables for update results.
    -   Colored status messages.
3.  **Global Command**: Includes an `install.sh` script that installs dependencies and creates a global `mu` command in `~/.local/bin`, allowing the updater to be run from any directory.
4.  **Parallel Processing**: Uses threading to check all three providers (Ollama, LM Studio, Llama.cpp) simultaneously for faster execution.

## New Windows Version (V1)

1.  **Native GUI**: Created a standalone Python application (`updater_gui.py`) using `tkinter`.
2.  **Visual Interface**:
    -   Input fields for configuring server URLs.
    -   "Save Config" and "Update Models" buttons.
    -   Progress bar and scrolling log window.
3.  **Desktop Integration**: Includes an `install.bat` script that automatically creates a Desktop shortcut for easy access.
4.  **Feature Parity**: Matches all features of the Linux version, including config persistence, model removal, and backup creation.

## Repository

The project has been uploaded to GitHub as "OpenCode-Model-Updater" (https://github.com/mordang7/OpenCode-Model-Updater).
-   **v5.0**: Major release adding Linux TUI and Windows GUI versions.

## Usage

### Linux (V5)
1.  **Install**: Run `./install.sh` inside the `V5` directory.
2.  **Run**: Type `mu` in any terminal window.

### Windows (V1)
1.  **Install**: Run `install.bat` inside the `Windows_V1` directory.
2.  **Run**: Double-click the "OpenCode Model Updater" shortcut on your Desktop.

## Dependencies

### Linux (V5)
-   Python 3
-   `rich` library (installed via `install.sh`)
-   OpenCode config at `$HOME/.config/opencode/opencode.json`

### Windows (V1)
-   Python 3 (must be in PATH)
-   `tkinter` (usually included with Python)
-   OpenCode config at `%USERPROFILE%\.config\opencode\opencode.json`
