# 🚀 OpenCode Model Updater

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/mordang7/OpenCode-Model-Updater)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE) <!-- Assuming MIT, add if needed -->

Keep your OpenCode AI models fresh! This handy script automatically syncs models from your local Ollama and LM Studio servers, ensuring you always have the latest options without manual hassle.

## ✨ What It Does

-   🔍 **Scans** for new models on Ollama and LM Studio.
-   📥 **Updates** your OpenCode config with the freshest models.
-   🗑️ **Removes** outdated models that are no longer available.
-   💬 **Notifies** you with clear messages about changes made.
-   ⚙️ **Configures** itself on first run—choose localhost or network setup!

## 🛠️ How to Use

1. **Make executable**: `chmod +x Update-LM-Models/V3/update-models.sh`
2. **Run it**: `./Update-LM-Models/V3/update-models.sh`
3. **First-time setup**: Answer prompts for Ollama and LM Studio (localhost or enter network IP).
4. **Enjoy**: Restart OpenCode and type `/models` to see your updated list!

## 📋 Requirements

-   🐳 Ollama or 🧠 LM Studio running locally or on your network.
-   🛠️ Tools: `curl`, `jq`, `python3`.

## 🤝 Contributing

Feel free to open issues or PRs for improvements!
