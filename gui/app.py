"""Interface Tkinter avec panneau d'anomalies."""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import asyncio
import json
from pathlib import Path

from core.config_loader import ConfigBundle
from core.scanner import MultiEngineScanner
from core.transients import protocole_attente


class UncoverEchoGUI:
    def __init__(self, root, config: ConfigBundle):
        self.root = root
        self.config = config
        self.colors = config.ui["theme"]["colors"]
        self.fonts = config.ui["theme"]["fonts"]
        self.scanner = MultiEngineScanner(config)
        self._last_report = None
        self._scan_in_progress = False

        self.root.title(config.ui["window"]["title"])
        self.root.geometry(config.ui["window"]["geometry"])
        self.root.configure(bg=self._c(config.ui["window"]["bg_color"]))

        self._build_ui()

    def _c(self, name: str) -> str:
        return self.colors.get(name, "#000000")

    # ------------------------------------------------------------------ #

    def _build_ui(self):
        main = tk.Frame(self.root, bg=self._c("BLUE"))
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_header(main)
        self._build_controls(main)

        split = tk.Frame(main, bg=self._c("BLUE"))
        split.pack(fill=tk.BOTH, expand=True, pady=5)

        left = tk.Frame(split, bg=self._c("BLUE"))
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self._build_terminal(left)

        right = tk.Frame(split, bg=self._c("BLUE"), width=550)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5)
        self._build_anomaly_panel(right)

        self._build_status(main)

    def _build_header(self, parent):
        header_path = Path(self.config.ui["templates"]["header_file"])
        text = header_path.read_text(encoding="utf-8") if header_path.exists() else "UNCOVER-ECHO"
        tk.Label(parent, text=text, fg=self._c("CYAN"), bg=self._c("BLUE"),
                 font=tuple(self.fonts["header"]), justify=tk.LEFT).pack(anchor=tk.W)

    def _build_controls(self, parent):
        ctrl = tk.LabelFrame(parent, text=" [ CONTRÔLE MULTI-MOTEURS ] ",
                              bg=self._c("BLUE"), fg=self._c("WHITE"),
                              font=("Courier New", 10, "bold"))
        ctrl.pack(fill=tk.X, pady=5)

        tk.Label(ctrl, text="Preset:", bg=self._c("BLUE"),
                  fg=self._c("YELLOW"), font=tuple(self.fonts["label"])
                  ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.preset_var = tk.StringVar(value="kubernetes")
        ttk.Combobox(ctrl, textvariable=self.preset_var,
                     values=list(self.config.presets.keys()),
                     width=25, font=tuple(self.fonts["label"])
                     ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(ctrl, text="Query:", bg=self._c("BLUE"),
                  fg=self._c("YELLOW"), font=tuple(self.fonts["label"])
                  ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.query_entry = tk.Entry(ctrl, width=70, bg=self._c("BLUE"),
                                     fg=self._c("GREEN"), font=tuple(self.fonts["label"]),
                                     insertbackground=self._c("WHITE"))
        self.query_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(ctrl, text="Moteurs:", bg=self._c("BLUE"),
                  fg=self._c("YELLOW"), font=tuple(self.fonts["label"])
                  ).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        eng_frame = tk.Frame(ctrl, bg=self._c("BLUE"))
        eng_frame.grid(row=2, column=1, sticky=tk.W, padx=5)
        self.engine_vars = {}
        for eng in self.scanner.available_engines():
            var = tk.BooleanVar(value=(eng == "shodan"))
            self.engine_vars[eng] = var
            tk.Checkbutton(eng_frame, text=eng.upper(), variable=var,
                           bg=self._c("BLUE"), fg=self._c("LIGHT_GREEN"),
                           selectcolor=self._c("BLUE"),
                           font=tuple(self.fonts["label"])).pack(side=tk.LEFT, padx=5)

        btns = tk.Frame(ctrl, bg=self._c("BLUE"))
        btns.grid(row=3, column=0, columnspan=2, pady=5)
        self.buttons = {}
        for key, label, cmd, bg, fg in [
            ("preset", "[ SCAN PRESET ]", self.scan_preset, "GREEN", "BLACK"),
            ("custom", "[ SCAN CUSTOM ]", self.scan_custom, "CYAN", "BLACK"),
            ("anomalies", "[ ANOMALIES ]", self.scan_anomalies, "OMEGA", "BLACK"),
            ("clear", "[ CLEAR ]", self.clear, "RED", "WHITE"),
            ("export", "[ EXPORT ]", self.export, "YELLOW", "BLACK"),
        ]:
            b = tk.Button(btns, text=label, command=cmd,
                          bg=self._c(bg), fg=self._c(fg),
                          font=tuple(self.fonts["button"]))
            b.pack(side=tk.LEFT, padx=4)
            self.buttons[key] = b

    def _build_terminal(self, parent):
        self.terminal = scrolledtext.ScrolledText(
            parent, wrap=tk.WORD, font=tuple(self.fonts["terminal"]),
            bg=self._c("BLUE"), fg=self._c("GREEN"),
            insertbackground=self._c("WHITE"), relief=tk.SUNKEN)
        self.terminal.pack(fill=tk.BOTH, expand=True)
        for tag, col in [("info", "CYAN"), ("success", "GREEN"), ("warning", "YELLOW"),
                          ("error", "RED"), ("engine", "PURPLE"), ("omega", "OMEGA")]:
            self.terminal.tag_configure(tag, foreground=self._c(col))

    def _build_anomaly_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" [ ANOMALIES DE VERSION/DATE ] ",
                               bg=self._c("BLUE"), fg=self._c("OMEGA"),
                               font=("Courier New", 10, "bold"))
        frame.pack(fill=tk.BOTH, expand=True)

        self.anomaly_text = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, font=tuple(self.fonts["terminal"]),
            bg=self._c("BLUE"), fg=self._c("OMEGA"),
            relief=tk.FLAT, state=tk.DISABLED)
        self.anomaly_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.anomaly_text.tag_configure("critical", foreground=self._c("LIGHT_RED"))
        self.anomaly_text.tag_configure("omega", foreground=self._c("OMEGA"))
        self.anomaly_text.tag_configure("normal", foreground=self._c("LIGHT_GREEN"))

    def _build_status(self, parent):
        self.status = tk.Label(parent, text="READY.",
                                bg=self._c("BLUE"), fg=self._c("GREEN"),
                                font=tuple(self.fonts["label"]), anchor=tk.W)
        self.status.pack(fill=tk.X, pady=(5, 0))

    # ------------------------------------------------------------------ #

    def log(self, msg, tag=None):
        self.terminal.insert(tk.END, msg + "\n", tag)
        self.terminal.see(tk.END)
        self.root.update_idletasks()

    def clear(self):
        self.terminal.delete(1.0, tk.END)
        self.anomaly_text.config(state=tk.NORMAL)
        self.anomaly_text.delete(1.0, tk.END)
        self.anomaly_text.config(state=tk.DISABLED)

    def _set_busy(self, busy: bool):
        self._scan_in_progress = busy
        state = tk.DISABLED if busy else tk.NORMAL
        for key in ("preset", "custom", "anomalies"):
            self.buttons[key].config(state=state)
        self.status.config(text="SCAN EN COURS..." if busy else "READY.")

    # ------------------------------------------------------------------ #

    def scan_preset(self):
        if self._scan_in_progress:
            return
        preset = self.preset_var.get()
        engines = [n for n, v in self.engine_vars.items() if v.get()]
        self.clear()
        self._run_async(self._do_preset(preset, engines))

    def scan_custom(self):
        if self._scan_in_progress:
            return
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Erreur", "Query vide")
            return
        engines = [n for n, v in self.engine_vars.items() if v.get()]
        self.clear()
        self._run_async(self._do_custom(query, engines))

    def scan_anomalies(self):
        self.preset_var.set("temporal-anomaly")
        self.scan_preset()

    def _run_async(self, coro):
        self._set_busy(True)

        def runner():
            try:
                asyncio.run(coro)
            finally:
                self.root.after(0, lambda: self._set_busy(False))

        threading.Thread(target=runner, daemon=True).start()

    async def _do_preset(self, preset, engines):
        await protocole_attente(self.config.transients, log_fn=self.log)
        report = self.scanner.scan_preset(preset, engines, limit=50)
        self._last_report = report
        self.root.after(0, lambda: self._display(report))

    async def _do_custom(self, query, engines):
        await protocole_attente(self.config.transients, log_fn=self.log)
        report = self.scanner.scan(query, engines, limit=50)
        self._last_report = report
        self.root.after(0, lambda: self._display(report))

    # ------------------------------------------------------------------ #

    def _display(self, report):
        for eng, results in report.results_by_engine.items():
            self.log(f"\n{eng.upper()} : {len(results)} résultats", "engine")
            for i, r in enumerate(results[:5], 1):
                flag = " [SIM]" if r.simulated else ""
                self.log(f"  [{i}] {r.ip}:{r.port} — {r.product} {r.version}{flag}", "info")

        self.log(f"\n{'='*70}", "info")
        self.log(f"✓ Total : {report.total_results} actifs", "success")
        self.log(f"⚠ Anomalies détectées : {report.total_transients}", "omega")
        self.log(f"{'='*70}", "info")

        self.anomaly_text.config(state=tk.NORMAL)
        self.anomaly_text.delete(1.0, tk.END)
        self.anomaly_text.insert(tk.END,
            f"seuil critique < {self.scanner.transient_analyzer.seuil_critique}\n"
            f"année de référence : {self.scanner.transient_analyzer.strate_ref}\n"
            f"{'─'*40}\n\n")

        if not report.transients:
            self.anomaly_text.insert(tk.END, "Aucune anomalie détectée.\n", "normal")
        else:
            for t in report.transients:
                tag = "omega" if t.is_omega else ("critical" if t.is_critical else "normal")
                self.anomaly_text.insert(tk.END,
                    f"● delta={t.delta:.3f}  année={t.strate_origine} "
                    f"({t.strate_classe.value})\n"
                    f"  service: {t.service_signature}\n"
                    f"  signaux: {', '.join(t.signals_detected)}\n"
                    f"  confiance: {t.confidence:.2f}\n\n", tag)

        self.anomaly_text.config(state=tk.DISABLED)

    def export(self):
        if not self._last_report:
            messagebox.showinfo("Export", "Aucun scan à exporter.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"uncover_echo_{self._last_report.scan_id}.json")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._last_report.to_dict(), f, indent=2, ensure_ascii=False)
            self.log(f"\n[✓] Export : {path}", "success")
