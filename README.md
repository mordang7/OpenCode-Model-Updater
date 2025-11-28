# 🚀 OpenCode Model Updater

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/mordang7/OpenCode-Model-Updater)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE) <!-- Assuming MIT, add if needed -->

Keep your OpenCode AI models fresh! This handy tool automatically syncs models from your local Ollama, LM Studio, and Llama.cpp servers, ensuring you always have the latest options without manual hassle.

Now available with a modern Terminal UI for Linux and a native GUI for Windows!

## ✨ What It Does

-   🔍 **Scans** for new models on Ollama, LM Studio, and Llama.cpp (concurrently!).
-   📥 **Updates** your OpenCode config with the freshest models.
-   🗑️ **Removes** outdated models that are no longer available.
-   📊 **Visualizes** the process with progress bars and summary tables.
-   ⚙️ **Configures** itself on first run—choose localhost or network setup.
-   💾 **Persists** your server configurations so you don't have to re-enter them.

## 🛠️ How to Use

### 🐧 Linux (V5 - Recommended)

1.  **Install**:
    ```bash
    cd Update-LM-Models/V5
    chmod +x install.sh
    ./install.sh
    ```
2.  **Run**:
    Type `mu` in any terminal window.
    *(Note: `mu` stands for Model Updater)*

### 🪟 Windows (V1 - Recommended)

1.  **Install**:
    Navigate to `Update-LM-Models/Windows_V1` and double-click `install.bat`.
2.  **Run**:
    Launch "OpenCode Model Updater" from your Desktop shortcut.

### 👴 Legacy (V4 - Bash Script)
1. **Make executable**: `chmod +x Update-LM-Models/V4/update-models.sh`
2. **Run it**: `./Update-LM-Models/V4/update-models.sh`

## 📋 Requirements

-   🐳 Ollama, 🧠 LM Studio, or 🦙 Llama.cpp running locally or on your network.
-   **Linux**: Python 3 (dependencies installed via script).
-   **Windows**: Python 3 installed and added to PATH.

## 🤝 Contributing

Feel free to open issues or PRs for improvements!

## 💖 Support
If you find this tool helpful, consider supporting me on [PayPal](https://paypal.me/GeekJohn)! Every bit helps keep the project going. 🚀