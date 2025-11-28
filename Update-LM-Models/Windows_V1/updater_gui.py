import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import threading
import urllib.request
import urllib.error
import time

# Configuration Paths (Windows Specific)
# Assuming OpenCode stores config in %USERPROFILE%/.config/opencode/opencode.json on Windows as well, 
# or we can adapt if it's in AppData. For now, following the Linux pattern which is common for cross-platform tools.
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "opencode")
OPENCODE_CONFIG_FILE = os.path.join(CONFIG_DIR, "opencode.json")
SCRIPT_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".update-models-config-win")

class ModelUpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenCode Model Updater")
        self.root.geometry("600x500")
        
        self.config = {
            "OLLAMA_URL": "http://localhost:11434/v1/models",
            "LMSTUDIO_URL": "http://localhost:1234/v1/models",
            "LLAMA_URL": "http://localhost:8080/v1/models"
        }
        self.load_config()

        # Styles
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", padding=5)

        # Main Frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Server Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        # Ollama
        ttk.Label(config_frame, text="Ollama URL:").grid(row=0, column=0, sticky=tk.W)
        self.ollama_entry = ttk.Entry(config_frame, width=50)
        self.ollama_entry.insert(0, self.config["OLLAMA_URL"])
        self.ollama_entry.grid(row=0, column=1, padx=5, pady=5)

        # LM Studio
        ttk.Label(config_frame, text="LM Studio URL:").grid(row=1, column=0, sticky=tk.W)
        self.lmstudio_entry = ttk.Entry(config_frame, width=50)
        self.lmstudio_entry.insert(0, self.config["LMSTUDIO_URL"])
        self.lmstudio_entry.grid(row=1, column=1, padx=5, pady=5)

        # Llama.cpp
        ttk.Label(config_frame, text="Llama.cpp URL:").grid(row=2, column=0, sticky=tk.W)
        self.llama_entry = ttk.Entry(config_frame, width=50)
        self.llama_entry.insert(0, self.config["LLAMA_URL"])
        self.llama_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.save_btn = ttk.Button(btn_frame, text="Save Config", command=self.save_config_ui)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.update_btn = ttk.Button(btn_frame, text="Update Models", command=self.start_update)
        self.update_btn.pack(side=tk.RIGHT, padx=5)

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)

        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def load_config(self):
        if os.path.exists(SCRIPT_CONFIG_FILE):
            try:
                with open(SCRIPT_CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config_ui(self):
        self.config["OLLAMA_URL"] = self.ollama_entry.get()
        self.config["LMSTUDIO_URL"] = self.lmstudio_entry.get()
        self.config["LLAMA_URL"] = self.llama_entry.get()
        
        try:
            with open(SCRIPT_CONFIG_FILE, 'w') as f:
                json.dump(self.config, f)
            self.log("Configuration saved.")
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except Exception as e:
            self.log(f"Error saving config: {e}")
            messagebox.showerror("Error", f"Could not save config: {e}")

    def fetch_models(self, url):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if 'data' in data and isinstance(data['data'], list):
                        return [model['id'] for model in data['data']]
        except Exception as e:
            return None
        return None

    def start_update(self):
        self.update_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.progress['value'] = 0
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        
        # Update config from UI first
        self.config["OLLAMA_URL"] = self.ollama_entry.get()
        self.config["LMSTUDIO_URL"] = self.lmstudio_entry.get()
        self.config["LLAMA_URL"] = self.llama_entry.get()

        threading.Thread(target=self.run_update_process).start()

    def run_update_process(self):
        results = {}
        results["OLLAMA_BASE"] = self.config["OLLAMA_URL"].replace("/models", "")
        results["LMSTUDIO_BASE"] = self.config["LMSTUDIO_URL"].replace("/models", "")
        results["LLAMA_BASE"] = self.config["LLAMA_URL"].replace("/models", "")

        # Step 1: Check Ollama
        self.log("Checking Ollama...")
        models = self.fetch_models(self.config["OLLAMA_URL"])
        results["OLLAMA"] = models
        if models:
            self.log(f"Ollama: Found {len(models)} models.")
        else:
            self.log("Ollama: Connection failed or no models found.")
        self.progress['value'] = 33

        # Step 2: Check LM Studio
        self.log("Checking LM Studio...")
        models = self.fetch_models(self.config["LMSTUDIO_URL"])
        results["LMSTUDIO"] = models
        if models:
            self.log(f"LM Studio: Found {len(models)} models.")
        else:
            self.log("LM Studio: Connection failed or no models found.")
        self.progress['value'] = 66

        # Step 3: Check Llama.cpp
        self.log("Checking Llama.cpp...")
        models = self.fetch_models(self.config["LLAMA_URL"])
        results["LLAMA"] = models
        if models:
            self.log(f"Llama.cpp: Found {len(models)} models.")
        else:
            self.log("Llama.cpp: Connection failed or no models found.")
        self.progress['value'] = 90

        # Step 4: Update Config
        self.log("Updating OpenCode configuration...")
        updated_providers, removed_count = self.update_opencode_config(results)
        
        self.progress['value'] = 100
        self.log("-" * 30)
        if updated_providers:
            self.log(f"Updated providers: {', '.join(updated_providers)}")
            if removed_count > 0:
                self.log(f"Removed {removed_count} unavailable models.")
            self.log("Success! Restart OpenCode to see changes.")
            messagebox.showinfo("Update Complete", "OpenCode configuration updated successfully!")
        else:
            self.log("No updates made. Check your connections.")
            messagebox.showwarning("Update Failed", "No providers could be reached.")

        self.root.after(0, lambda: self.update_btn.config(state='normal'))
        self.root.after(0, lambda: self.save_btn.config(state='normal'))

    def update_opencode_config(self, fetched_models):
        if not os.path.exists(OPENCODE_CONFIG_FILE):
            self.log(f"Error: Config file not found at {OPENCODE_CONFIG_FILE}")
            return [], 0

        try:
            with open(OPENCODE_CONFIG_FILE, 'r') as f:
                opencode_config = json.load(f)
        except Exception as e:
            self.log(f"Error reading OpenCode config: {e}")
            return [], 0

        total_removed = 0
        updated_providers = []

        if 'provider' not in opencode_config:
            opencode_config['provider'] = {}

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
            pass

        # Save
        try:
            with open(OPENCODE_CONFIG_FILE, 'w') as f:
                json.dump(opencode_config, f, indent=2)
        except Exception as e:
            self.log(f"Error saving OpenCode config: {e}")
            return [], 0

        return updated_providers, total_removed

if __name__ == "__main__":
    root = tk.Tk()
    app = ModelUpdaterApp(root)
    root.mainloop()
