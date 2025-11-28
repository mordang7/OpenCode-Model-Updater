#!/usr/bin/env python3
import json
import os
import sys
import time
import threading
import urllib.request
import urllib.error
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

# Configuration Paths
CONFIG_DIR = os.path.expanduser("~/.config/opencode")
OPENCODE_CONFIG_FILE = os.path.join(CONFIG_DIR, "opencode.json")
SCRIPT_CONFIG_FILE = os.path.expanduser("~/.update-models-config")

# Initialize Rich Console
console = Console()

def load_script_config():
    """Loads the script configuration (URLs) from ~/.update-models-config."""
    config = {
        "OLLAMA_URL": "http://localhost:11434/v1/models",
        "LMSTUDIO_URL": "http://localhost:1234/v1/models",
        "LLAMA_URL": "http://localhost:8080/v1/models"
    }
    if os.path.exists(SCRIPT_CONFIG_FILE):
        try:
            with open(SCRIPT_CONFIG_FILE, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"').strip("'")
                        if key in config:
                            config[key] = value
        except Exception as e:
            console.print(f"[red]Error loading script config: {e}[/red]")
    return config

def save_script_config(config):
    """Saves the script configuration to ~/.update-models-config."""
    try:
        with open(SCRIPT_CONFIG_FILE, 'w') as f:
            for key, value in config.items():
                f.write(f'{key}="{value}"\n')
    except Exception as e:
        console.print(f"[red]Error saving script config: {e}[/red]")

def fetch_models(url, name):
    """Fetches models from a given URL."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if 'data' in data and isinstance(data['data'], list):
                    return [model['id'] for model in data['data']]
    except (urllib.error.URLError, TimeoutError, ConnectionRefusedError):
        return None
    except Exception:
        return None
    return None

def update_opencode_config(fetched_models):
    """Updates the OpenCode configuration file with fetched models."""
    if not os.path.exists(OPENCODE_CONFIG_FILE):
        console.print(f"[red]OpenCode config file not found at {OPENCODE_CONFIG_FILE}[/red]")
        return [], 0

    try:
        with open(OPENCODE_CONFIG_FILE, 'r') as f:
            opencode_config = json.load(f)
    except Exception as e:
        console.print(f"[red]Error reading OpenCode config: {e}[/red]")
        return [], 0

    total_removed = 0
    updated_providers = []

    if 'provider' not in opencode_config:
        opencode_config['provider'] = {}

    # Map internal keys to config keys and friendly names
    provider_map = {
        "OLLAMA": ("ollama", "Ollama (remote)"),
        "LMSTUDIO": ("lmstudio", "LM Studio (remote)"),
        "LLAMA": ("llamacpp", "Llama.cpp (remote)")
    }

    for key, (provider_key, provider_name) in provider_map.items():
        if key in fetched_models and fetched_models[key] is not None:
            models = fetched_models[key]
            base_url = fetched_models[f"{key}_BASE"]
            
            updated_providers.append(provider_name.split(' ')[0])

            if provider_key not in opencode_config['provider']:
                opencode_config['provider'][provider_key] = {
                    "npm": "@ai-sdk/openai-compatible",
                    "name": provider_name,
                    "options": {"baseURL": base_url},
                    "models": {}
                }
            
            # Remove non-present models
            current_models = list(opencode_config['provider'][provider_key]['models'].keys())
            for model in current_models:
                if model not in models:
                    del opencode_config['provider'][provider_key]['models'][model]
                    total_removed += 1
            
            # Add/Update models
            for model_id in models:
                friendly_name = model_id
                if provider_key == 'ollama' and ':cloud' in model_id:
                    base_name = model_id.split(':')[0].replace('-', ' ').title()
                    friendly_name = base_name + " Cloud"
                else:
                    friendly_name = model_id.replace('-', ' ').replace('/', ' ').title()
                
                opencode_config['provider'][provider_key]['models'][model_id] = {"name": friendly_name}

    # Backup
    backup_file = f"{OPENCODE_CONFIG_FILE}.backup.{int(time.time())}"
    try:
        with open(OPENCODE_CONFIG_FILE, 'r') as src, open(backup_file, 'w') as dst:
            dst.write(src.read())
    except Exception:
        pass # Fail silently on backup

    # Save
    try:
        with open(OPENCODE_CONFIG_FILE, 'w') as f:
            json.dump(opencode_config, f, indent=2)
    except Exception as e:
        console.print(f"[red]Error saving OpenCode config: {e}[/red]")
        return [], 0

    return updated_providers, total_removed

def main():
    console.clear()
    console.print(Panel.fit("[bold blue]OpenCode Model Updater V5[/bold blue]", border_style="blue"))

    config = load_script_config()
    
    # Check if we need to prompt for configuration (first run or missing)
    if not os.path.exists(SCRIPT_CONFIG_FILE):
        console.print("[yellow]Configuration not found. Let's set it up.[/yellow]")
        
        # Ollama
        choice = console.input("For [bold]Ollama[/bold]: Run on same PC (local) or network? [local/network]: ").lower()
        if choice == 'network':
            ip = console.input("Enter Ollama IP: ")
            config["OLLAMA_URL"] = f"http://{ip}:11434/v1/models"
        else:
            config["OLLAMA_URL"] = "http://localhost:11434/v1/models"

        # LM Studio
        choice = console.input("For [bold]LM Studio[/bold]: Run on same PC (local) or network? [local/network]: ").lower()
        if choice == 'network':
            ip = console.input("Enter LM Studio IP: ")
            config["LMSTUDIO_URL"] = f"http://{ip}:1234/v1/models"
        else:
            config["LMSTUDIO_URL"] = "http://localhost:1234/v1/models"

        # Llama.cpp
        choice = console.input("For [bold]Llama.cpp[/bold]: Run on same PC (local) or network? [local/network]: ").lower()
        if choice == 'network':
            ip = console.input("Enter Llama.cpp IP: ")
            config["LLAMA_URL"] = f"http://{ip}:8080/v1/models"
        else:
            config["LLAMA_URL"] = "http://localhost:8080/v1/models"
            
        save_script_config(config)
        console.print("[green]Configuration saved![/green]\n")

    # Prepare for fetching
    results = {}
    results["OLLAMA_BASE"] = config["OLLAMA_URL"].replace("/models", "")
    results["LMSTUDIO_BASE"] = config["LMSTUDIO_URL"].replace("/models", "")
    results["LLAMA_BASE"] = config["LLAMA_URL"].replace("/models", "")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        task_ollama = progress.add_task("[cyan]Checking Ollama...", total=1)
        task_lmstudio = progress.add_task("[magenta]Checking LM Studio...", total=1)
        task_llama = progress.add_task("[yellow]Checking Llama.cpp...", total=1)

        # Threads for parallel fetching
        def check_ollama():
            models = fetch_models(config["OLLAMA_URL"], "Ollama")
            results["OLLAMA"] = models
            progress.update(task_ollama, advance=1, description=f"[cyan]Ollama: {'[green]Found ' + str(len(models)) if models else '[red]Failed'}")

        def check_lmstudio():
            models = fetch_models(config["LMSTUDIO_URL"], "LM Studio")
            results["LMSTUDIO"] = models
            progress.update(task_lmstudio, advance=1, description=f"[magenta]LM Studio: {'[green]Found ' + str(len(models)) if models else '[red]Failed'}")

        def check_llama():
            models = fetch_models(config["LLAMA_URL"], "Llama.cpp")
            results["LLAMA"] = models
            progress.update(task_llama, advance=1, description=f"[yellow]Llama.cpp: {'[green]Found ' + str(len(models)) if models else '[red]Failed'}")

        t1 = threading.Thread(target=check_ollama)
        t2 = threading.Thread(target=check_lmstudio)
        t3 = threading.Thread(target=check_llama)

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

    console.print("\n[bold]Updating OpenCode Configuration...[/bold]")
    updated_providers, removed_count = update_opencode_config(results)

    # Summary Table
    table = Table(title="Update Summary")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Models Found", justify="right")

    if results.get("OLLAMA"):
        table.add_row("Ollama", "[green]Updated[/green]", str(len(results["OLLAMA"])))
    else:
        table.add_row("Ollama", "[red]Failed/Skipped[/red]", "0")

    if results.get("LMSTUDIO"):
        table.add_row("LM Studio", "[green]Updated[/green]", str(len(results["LMSTUDIO"])))
    else:
        table.add_row("LM Studio", "[red]Failed/Skipped[/red]", "0")

    if results.get("LLAMA"):
        table.add_row("Llama.cpp", "[green]Updated[/green]", str(len(results["LLAMA"])))
    else:
        table.add_row("Llama.cpp", "[red]Failed/Skipped[/red]", "0")

    console.print(table)
    
    if removed_count > 0:
        console.print(f"\n[yellow]Removed {removed_count} models that are no longer available.[/yellow]")
    
    if not updated_providers:
        console.print("\n[red]No providers were updated. Please check your connections.[/red]")
    else:
        console.print("\n[bold green]Success! OpenCode configuration has been updated.[/bold green]")
        console.print("Restart OpenCode and run [bold]/models[/bold] to see your new models.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Cancelled by user.[/red]")
        sys.exit(0)
