#!/bin/bash

CONFIG_FILE="$HOME/.config/opencode/opencode.json"
BACKUP_FILE="$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
SCRIPT_CONFIG="$HOME/.update-models-config"

# Check for existing config or prompt user
if [ -f "$SCRIPT_CONFIG" ]; then
    source "$SCRIPT_CONFIG"
else
    # Prompt for Ollama
    echo "For Ollama: Run on same PC or local network?"
    read -p "Enter 'local' for same PC (localhost), 'network' for local network: " ollama_choice
    if [ "$ollama_choice" = "local" ]; then
        OLLAMA_URL="http://localhost:11434/v1/models"
    elif [ "$ollama_choice" = "network" ]; then
        read -p "Enter the local IP address for the Ollama machine: " ollama_ip
        OLLAMA_URL="http://$ollama_ip:11434/v1/models"
    else
        echo "Invalid choice, defaulting to localhost"
        OLLAMA_URL="http://localhost:11434/v1/models"
    fi

    # Prompt for LM Studio
    echo "For LM Studio: Run on same PC or local network?"
    read -p "Enter 'local' for same PC (localhost), 'network' for local network: " lmstudio_choice
    if [ "$lmstudio_choice" = "local" ]; then
        LMSTUDIO_URL="http://localhost:1234/v1/models"
    elif [ "$lmstudio_choice" = "network" ]; then
        read -p "Enter the local IP address for the LM Studio machine: " lmstudio_ip
        LMSTUDIO_URL="http://$lmstudio_ip:1234/v1/models"
    else
        echo "Invalid choice, defaulting to localhost"
        LMSTUDIO_URL="http://localhost:1234/v1/models"
    fi

    # Prompt for Llama.cpp
    echo "For Llama.cpp: Run on same PC or local network?"
    read -p "Enter 'local' for same PC (localhost), 'network' for local network: " llama_choice
    if [ "$llama_choice" = "local" ]; then
        LLAMA_URL="http://localhost:8080/v1/models"
    elif [ "$llama_choice" = "network" ]; then
        read -p "Enter the local IP address for the Llama.cpp machine: " llama_ip
        LLAMA_URL="http://$llama_ip:8080/v1/models"
    else
        echo "Invalid choice, defaulting to localhost"
        LLAMA_URL="http://localhost:8080/v1/models"
    fi

    # Save config
    echo "OLLAMA_URL=\"$OLLAMA_URL\"" > "$SCRIPT_CONFIG"
    echo "LMSTUDIO_URL=\"$LMSTUDIO_URL\"" >> "$SCRIPT_CONFIG"
    echo "LLAMA_URL=\"$LLAMA_URL\"" >> "$SCRIPT_CONFIG"
    echo "Configuration saved to $SCRIPT_CONFIG"
fi

# Set base URLs for Python
OLLAMA_BASE="${OLLAMA_URL%/models}"
LMSTUDIO_BASE="${LMSTUDIO_URL%/models}"
LLAMA_BASE="${LLAMA_URL%/models}"

# Function to fetch and parse models
fetch_models() {
    local url=$1
    local name=$2
    local models_json=$(curl --connect-timeout 15 --max-time 15 -s "$url")

    if [[ $? -ne 0 ]]; then
        return 1
    fi

    local model_ids=$(echo "$models_json" | jq -r 'if .data and (.data | type) == "array" then .data[].id else empty end')

    if [[ -z "$model_ids" ]]; then
        return 1
    fi

    echo "$model_ids"
}

# Fetch Ollama models
OLLAMA_IDS=$(fetch_models "$OLLAMA_URL" "Ollama")
OLLAMA_SUCCESS=$?

# Fetch LM Studio models
LMSTUDIO_IDS=$(fetch_models "$LMSTUDIO_URL" "LM Studio")
LMSTUDIO_SUCCESS=$?

# Fetch Llama.cpp models
LLAMA_IDS=$(fetch_models "$LLAMA_URL" "Llama.cpp")
LLAMA_SUCCESS=$?

# If all failed, show message and exit without changes
if [[ $OLLAMA_SUCCESS -ne 0 && $LMSTUDIO_SUCCESS -ne 0 && $LLAMA_SUCCESS -ne 0 ]]; then
    echo "All Servers could not be reached - No Changes were Made"
    exit 0
fi

# Backup config (only if at least one succeeded)
cp "$CONFIG_FILE" "$BACKUP_FILE" && echo "Backup created: $BACKUP_FILE"

# Use Python to update JSON
cat << EOF > update.py
import json
import sys

config_file = sys.argv[1]
ollama_str = sys.argv[2] if len(sys.argv) > 2 else ''
lmstudio_str = sys.argv[3] if len(sys.argv) > 3 else ''
llama_str = sys.argv[4] if len(sys.argv) > 4 else ''

# Load config
with open(config_file, 'r') as f:
    config = json.load(f)

total_removed = 0

# Helper to add/update provider
def update_provider(config, provider_name, models_str, base_url):
    global total_removed
    if 'provider' not in config:
        config['provider'] = {}
    if provider_name not in config['provider']:
        config['provider'][provider_name] = {
            "npm": "@ai-sdk/openai-compatible",
            "name": provider_name.replace('-', ' ').title() + " (remote)",
            "options": {"baseURL": base_url},
            "models": {}
        }
    if models_str.strip():
        model_ids = models_str.strip().split('\n')
        # Remove non-present models
        if provider_name in config['provider']:
            current_models = list(config['provider'][provider_name]['models'].keys())
            for model in current_models:
                if model not in model_ids:
                    del config['provider'][provider_name]['models'][model]
                    total_removed += 1
        # Add/update models
        for model_id in model_ids:
            if model_id.strip():
                # Improved naming: For Ollama cloud models, take base name before ':', title it, add " Cloud"
                # For LM Studio, keep full ID formatted (fallback for general cases)
                if provider_name == 'ollama' and ':cloud' in model_id:
                    base_name = model_id.split(':')[0].replace('-', ' ').title()
                    friendly_name = base_name + " Cloud"
                else:
                    # General fallback: title the full ID, replacing '-' with ' '
                    friendly_name = model_id.replace('-', ' ').replace('/', ' ').title()
                
                config['provider'][provider_name]['models'][model_id] = {"name": friendly_name}

# Update Ollama
if ollama_str:
    update_provider(config, 'ollama', ollama_str, "$OLLAMA_BASE")

# Update LM Studio
if lmstudio_str:
    update_provider(config, 'lmstudio', lmstudio_str, "$LMSTUDIO_BASE")

# Update Llama.cpp
if llama_str:
    update_provider(config, 'llamacpp', llama_str, "$LLAMA_BASE")

# Write back
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

if total_removed > 0:
    print(f"{total_removed} Non Present Models were Removed!")

print(f"Config updated at {config_file}")
EOF

# Run Python script
python3 update.py "$CONFIG_FILE" "$OLLAMA_IDS" "$LMSTUDIO_IDS" "$LLAMA_IDS"

# Show update message
updated_providers=()
if [[ $OLLAMA_SUCCESS -eq 0 ]]; then updated_providers+=("Ollama"); fi
if [[ $LMSTUDIO_SUCCESS -eq 0 ]]; then updated_providers+=("LM Studio"); fi
if [[ $LLAMA_SUCCESS -eq 0 ]]; then updated_providers+=("Llama.cpp"); fi

if [ ${#updated_providers[@]} -eq 3 ]; then
    echo "All Ollama, LM Studio & Llama.cpp models were Updated!"
elif [ ${#updated_providers[@]} -eq 2 ]; then
    echo "Only the ${updated_providers[0]} & ${updated_providers[1]} models were Updated!"
elif [ ${#updated_providers[@]} -eq 1 ]; then
    echo "Only the ${updated_providers[0]} models were Updated!"
fi

# Clean up
rm update.py

echo "Done! Restart OpenCode and run /models to see updates."