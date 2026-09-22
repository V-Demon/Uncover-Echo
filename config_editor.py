#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ ATELIER DE RÉSONANCE CONFIGURATIONNELLE v1.0 ⚙️
Éditeur Tkinter Feng-Shui pour Uncover-Echo (MTT-2075)
Fusionne la rigueur YAML avec l'harmonie des strates temporelles.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yaml
import os
import random

# --- Palette de couleurs runiques & Feng-Shui sombre ---
COLORS = {
    "bg_dark": "#0a0a0f",
    "bg_panel": "#12121a",
    "text_main": "#e0e0e0",
    "accent_rune": "#8A2BE2",  # BlueViolet (Ansuz / Communication)
    "accent_gold": "#FFD700",  # Or (Harmonie / Feng-Shui)
    "accent_glitch": "#00ff41", # Vert terminal
    "border": "#2a2a3a"
}

# --- Templates de configuration lore-friendly ---
TEMPLATES = {
    "🌌 Mode Caen-Profonde (Furtif)": {
        "engines": {
            "shodan": {"api_key": "", "rate_limit": 0.5, "simulate_on_missing_key": True},
            "censys": {"api_id": "", "api_secret": "", "rate_limit": 0.3, "simulate_on_missing_key": True}
        },
        "scanner": {"timeout": 45, "cache_ttl": 3600, "max_retries": 5, "backoff_factor": 1.0},
        "ui": {"theme": "dark_runic", "log_level": "WARNING"}
    },
    "🕰️ Chasseur de Strates 2075 (Agressif)": {
        "engines": {
            "shodan": {"api_key": "", "rate_limit": 2.0, "simulate_on_missing_key": False},
            "fofa": {"email": "", "api_key": "", "rate_limit": 1.5, "simulate_on_missing_key": False}
        },
        "scanner": {"timeout": 15, "cache_ttl": 300, "max_retries": 2, "backoff_factor": 0.3},
        "ui": {"theme": "glitch_terminal", "log_level": "DEBUG"}
    },
    "☯️ Équilibre Feng-Shui (Par défaut)": {
        "engines": {
            "shodan": {"api_key": "", "rate_limit": 1.0, "simulate_on_missing_key": True},
            "censys": {"api_id": "", "api_secret": "", "rate_limit": 1.0, "simulate_on_missing_key": True},
            "zoomeye": {"username": "", "password": "", "rate_limit": 1.0, "simulate_on_missing_key": True}
        },
        "scanner": {"timeout": 30, "cache_ttl": 1800, "max_retries": 3, "backoff_factor": 0.5},
        "ui": {"theme": "balanced", "log_level": "INFO"}
    },
    "📜 Codex Stein (Exploration Mémétique)": {
        "engines": {
            "shodan": {"api_key": "", "rate_limit": 0.8, "simulate_on_missing_key": True},
            "censys": {"api_id": "", "api_secret": "", "rate_limit": 0.8, "simulate_on_missing_key": True}
        },
        "scanner": {"timeout": 60, "cache_ttl": 7200, "max_retries": 4, "backoff_factor": 0.8},
        "ui": {"theme": "sufi_poetic", "log_level": "INFO"}
    }
}

class FengShuiConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ Atelier de Résonance Configurationnelle ⚙️")
        self.root.geometry("900x700")
        self.root.configure(bg=COLORS["bg_dark"])
        
        self.current_file = None
        self.config_data = {}

        self.setup_style()
        self.build_ui()
        self.load_template("☯️ Équilibre Feng-Shui (Par défaut)")
        self.log("🌀 Initialisation de l'Atelier. Les flux sont stables.")

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_main"], font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLORS["accent_gold"])
        style.configure("TButton", background=COLORS["bg_panel"], foreground=COLORS["text_main"], bordercolor=COLORS["accent_rune"])
        style.map("TButton", background=[("active", COLORS["accent_rune"])])
        style.configure("TCombobox", fieldbackground=COLORS["bg_panel"], background=COLORS["bg_panel"], foreground=COLORS["text_main"])

    def build_ui(self):
        # --- Header ---
        header = ttk.Label(self.root, text="⚙️ ATELIER DE RÉSONANCE CONFIGURATIONNELLE ⚙️", style="Title.TLabel")
        header.pack(pady=10)

        # --- Main Container ---
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left Panel: Templates & File Ops
        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(left_panel, text="📂 Templates Mémétiques", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(left_panel, textvariable=self.template_var, values=list(TEMPLATES.keys()), state="readonly")
        self.template_combo.pack(fill=tk.X, pady=(0, 15))
        self.template_combo.bind("<<ComboboxSelected>>", lambda e: self.load_template(self.template_var.get()))

        ttk.Button(left_panel, text="📥 Charger un fichier YAML", command=self.load_file).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="📤 Sauvegarder sous...", command=self.save_file).pack(fill=tk.X, pady=5)
        
        # Feng-Shui Action Button
        fengshui_btn = tk.Button(left_panel, text="☯️ Harmoniser le Flux", bg=COLORS["accent_gold"], fg="#000", 
                                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, cursor="hand2", command=self.harmonize_flux)
        fengshui_btn.pack(fill=tk.X, pady=20)

        # Center Panel: Configuration Form
        center_panel = ttk.Frame(main_frame)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Notebook for categories
        self.notebook = ttk.Notebook(center_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.frame_engines = ttk.Frame(self.notebook)
        self.frame_scanner = ttk.Frame(self.notebook)
        self.frame_ui = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_engines, text="🌐 Moteurs (Engines)")
        self.notebook.add(self.frame_scanner, text="⏱️ Scanner & Temps")
        self.notebook.add(self.frame_ui, text="👁️ Interface & Logs")

        self.build_engine_form()
        self.build_scanner_form()
        self.build_ui_form()

        # Bottom Panel: Log Console
        log_frame = ttk.LabelFrame(main_frame, text="📜 Journal des Transitoires")
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=6, bg=COLORS["bg_panel"], fg=COLORS["accent_glitch"], 
                                font=("Consolas", 9), relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def build_engine_form(self):
        # Simplified for demo: Shodan & Censys
        row = 0
        ttk.Label(self.frame_engines, text="SHODAN_API_KEY:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.shodan_key = ttk.Entry(self.frame_engines, width=40)
        self.shodan_key.grid(row=row, column=1, pady=5)
        
        row += 1
        ttk.Label(self.frame_engines, text="SHODAN Rate Limit:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.shodan_rate = ttk.Entry(self.frame_engines, width=10)
        self.shodan_rate.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        self.shodan_sim = tk.BooleanVar()
        ttk.Checkbutton(self.frame_engines, text="Simulation si clé manquante", variable=self.shodan_sim).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)

    def build_scanner_form(self):
        row = 0
        ttk.Label(self.frame_scanner, text="Timeout (secondes):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.timeout = ttk.Entry(self.frame_scanner, width=10)
        self.timeout.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(self.frame_scanner, text="Cache TTL (secondes):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cache_ttl = ttk.Entry(self.frame_scanner, width=10)
        self.cache_ttl.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(self.frame_scanner, text="Max Retries:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.max_retries = ttk.Entry(self.frame_scanner, width=10)
        self.max_retries.grid(row=row, column=1, sticky=tk.W, pady=5)

    def build_ui_form(self):
        row = 0
        ttk.Label(self.frame_ui, text="Niveau de Log:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.log_level = ttk.Combobox(self.frame_ui, values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=15)
        self.log_level.grid(row=row, column=1, sticky=tk.W, pady=5)

    def load_template(self, template_name):
        self.config_data = TEMPLATES.get(template_name, TEMPLATES["☯️ Équilibre Feng-Shui (Par défaut)"])
        self.apply_data_to_ui()
        self.log(f"📜 Template chargé : {template_name}")

    def apply_data_to_ui(self):
        # Engines
        engines = self.config_data.get("engines", {})
        shodan = engines.get("shodan", {})
        self.shodan_key.delete(0, tk.END)
        self.shodan_key.insert(0, shodan.get("api_key", ""))
        self.shodan_rate.delete(0, tk.END)
        self.shodan_rate.insert(0, str(shodan.get("rate_limit", 1.0)))
        self.shodan_sim.set(shodan.get("simulate_on_missing_key", True))

        # Scanner
        scanner = self.config_data.get("scanner", {})
        self.timeout.delete(0, tk.END)
        self.timeout.insert(0, str(scanner.get("timeout", 30)))
        self.cache_ttl.delete(0, tk.END)
        self.cache_ttl.insert(0, str(scanner.get("cache_ttl", 1800)))
        self.max_retries.delete(0, tk.END)
        self.max_retries.insert(0, str(scanner.get("max_retries", 3)))

        # UI
        ui = self.config_data.get("ui", {})
        self.log_level.set(ui.get("log_level", "INFO"))

    def read_ui_to_data(self):
        # Simplified sync from UI to dict
        self.config_data.setdefault("engines", {})["shodan"] = {
            "api_key": self.shodan_key.get(),
            "rate_limit": float(self.shodan_rate.get() or 1.0),
            "simulate_on_missing_key": self.shodan_sim.get()
        }
        self.config_data.setdefault("scanner", {}).update({
            "timeout": int(self.timeout.get() or 30),
            "cache_ttl": int(self.cache_ttl.get() or 1800),
            "max_retries": int(self.max_retries.get() or 3)
        })
        self.config_data.setdefault("ui", {})["log_level"] = self.log_level.get()

    def harmonize_flux(self):
        """Ajuste les paramètres selon le Nombre d'Or et les principes Feng-Shui."""
        self.read_ui_to_data()
        
        # Application du Nombre d'Or (φ ≈ 1.618) au rate limit
        new_rate = 1.618
        self.shodan_rate.delete(0, tk.END)
        self.shodan_rate.insert(0, str(new_rate))
        
        # Application d'un nombre de Fibonacci au Cache TTL (144, 233, 377...)
        fib_ttl = random.choice([144, 233, 377, 610])
        self.cache_ttl.delete(0, tk.END)
        self.cache_ttl.insert(0, str(fib_ttl))
        
        # Retries équilibré
        self.max_retries.delete(0, tk.END)
        self.max_retries.insert(0, "3")

        self.log("☯️ Harmonisation appliquée : Rate Limit aligné sur φ (1.618), Cache TTL sur une suite de Fibonacci.")
        self.log("✨ Les transitoires du Temps tissé sont maintenant en résonance stable.")

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")])
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
            self.current_file = filepath
            self.apply_data_to_ui()
            self.log(f"📥 Fichier chargé avec succès : {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Erreur de Lecture", f"Impossible de lire le fichier :\n{e}")
            self.log(f"❌ Échec de lecture : {e}")

    def save_file(self):
        self.read_ui_to_data()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            initialfile="config_harmonisee.yaml"
        )
        if not filepath:
            return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
            self.current_file = filepath
            self.log(f"📤 Configuration sauvegardée dans : {os.path.basename(filepath)}")
            messagebox.showinfo("Succès", "La configuration a été harmonisée et sauvegardée.")
        except Exception as e:
            messagebox.showerror("Erreur d'Écriture", f"Impossible de sauvegarder :\n{e}")

    def log(self, message):
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = FengShuiConfigEditor(root)
    root.mainloop()