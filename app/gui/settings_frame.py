import customtkinter as ctk


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, db, config):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.config = config

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="Settings", font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(10, 20), sticky="w")

        # --- API Keys ---
        api_frame = ctk.CTkFrame(self)
        api_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        api_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            api_frame, text="API Keys", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")

        ctk.CTkLabel(api_frame, text="Anthropic API Key:").grid(
            row=1, column=0, padx=15, pady=5, sticky="w"
        )
        anthropic_row = ctk.CTkFrame(api_frame, fg_color="transparent")
        anthropic_row.grid(row=1, column=1, padx=(0, 15), pady=5, sticky="ew")
        anthropic_row.grid_columnconfigure(0, weight=1)

        self.anthropic_key = ctk.CTkEntry(
            anthropic_row, show="*", placeholder_text="sk-ant-..."
        )
        self.anthropic_key.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            anthropic_row, text="Test", width=60,
            command=self._test_api_key,
        ).grid(row=0, column=1)

        ctk.CTkLabel(api_frame, text="GitHub Token (optional):").grid(
            row=2, column=0, padx=15, pady=5, sticky="w"
        )
        self.github_token = ctk.CTkEntry(
            api_frame, show="*", placeholder_text="ghp_... (increases GitHub rate limits)"
        )
        self.github_token.grid(row=2, column=1, padx=(0, 15), pady=(5, 10), sticky="ew")

        ctk.CTkLabel(
            api_frame,
            text="Only the Anthropic key is required. All scrapers work without keys.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")

        # --- Scraper Settings ---
        scraper_frame = ctk.CTkFrame(self)
        scraper_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        scraper_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            scraper_frame,
            text="Scraper Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")

        ctk.CTkLabel(scraper_frame, text="Keywords (comma-separated):").grid(
            row=1, column=0, padx=15, pady=5, sticky="w"
        )
        self.keywords_entry = ctk.CTkEntry(scraper_frame)
        self.keywords_entry.grid(row=1, column=1, padx=(0, 15), pady=5, sticky="ew")

        ctk.CTkLabel(scraper_frame, text="Min Lead Score (1-10):").grid(
            row=2, column=0, padx=15, pady=5, sticky="w"
        )
        self.min_score_entry = ctk.CTkEntry(scraper_frame, width=60)
        self.min_score_entry.grid(
            row=2, column=1, padx=(0, 15), pady=(5, 15), sticky="w"
        )

        # Save
        ctk.CTkButton(
            self,
            text="Save Settings",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._save,
        ).grid(row=3, column=0, padx=20, pady=15, sticky="ew")

        # Database backup
        backup_frame = ctk.CTkFrame(self)
        backup_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        backup_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            backup_frame, text="Database",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            backup_frame,
            text="Back up your leads database to a safe location.",
            font=ctk.CTkFont(size=11), text_color="gray",
        ).grid(row=1, column=0, padx=15, pady=(0, 8), sticky="w")

        ctk.CTkButton(
            backup_frame, text="Backup Database", width=160,
            command=self._backup_db,
        ).grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")

        self.status_label = ctk.CTkLabel(self, text="", text_color="#22c55e")
        self.status_label.grid(row=5, column=0, padx=20, pady=5)

        self._load_values()

    def _load_values(self):
        fields = [
            (self.anthropic_key, "anthropic_api_key"),
            (self.github_token, "github_token"),
        ]
        for entry, key in fields:
            val = self.config.get(key, "")
            if val:
                entry.insert(0, val)

        kws = self.config.get("keywords", [])
        self.keywords_entry.insert(0, ", ".join(kws))

        ms = self.config.get("min_lead_score", 5.0)
        self.min_score_entry.insert(0, str(ms))

    def _save(self):
        self.config.set("anthropic_api_key", self.anthropic_key.get().strip())
        self.config.set("github_token", self.github_token.get().strip())

        kws = [k.strip() for k in self.keywords_entry.get().split(",") if k.strip()]
        self.config.set("keywords", kws)

        try:
            self.config.set("min_lead_score", float(self.min_score_entry.get()))
        except ValueError:
            pass

        self.config.save()
        self.status_label.configure(text="Settings saved!")
        self.after(3000, lambda: self.status_label.configure(text=""))

    def _test_api_key(self):
        """Make a tiny request to Anthropic to verify the key works."""
        import threading

        key = self.anthropic_key.get().strip()
        if not key:
            self.status_label.configure(
                text="Enter an API key first.", text_color="#ef4444",
            )
            return

        self.status_label.configure(
            text="Testing API key...", text_color="gray",
        )

        def _run():
            try:
                from anthropic import Anthropic
                client = Anthropic(api_key=key)
                resp = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Reply with: OK"}],
                )
                ok = bool(resp.content)
                msg = "API key works!" if ok else "API key got empty response."
                color = "#22c55e" if ok else "#ef4444"
            except Exception as e:
                msg = f"API key failed: {type(e).__name__}: {str(e)[:80]}"
                color = "#ef4444"
            self.after(0, lambda: self.status_label.configure(text=msg, text_color=color))
            self.after(5000, lambda: self.status_label.configure(text=""))

        threading.Thread(target=_run, daemon=True).start()

    def _backup_db(self):
        """Copy the SQLite DB to a user-chosen location."""
        from tkinter import filedialog
        from datetime import datetime
        import shutil
        import os

        # Find the active database path
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "forum_parser.db",
        )
        if not os.path.exists(db_path):
            self.status_label.configure(
                text="No database file found.", text_color="#ef4444",
            )
            return

        default_name = f"forum_parser_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
        target = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")],
            initialfile=default_name,
        )
        if not target:
            return

        try:
            shutil.copy2(db_path, target)
            self.status_label.configure(
                text=f"Backed up to {os.path.basename(target)}",
                text_color="#22c55e",
            )
        except Exception as e:
            self.status_label.configure(
                text=f"Backup failed: {e}", text_color="#ef4444",
            )
        self.after(5000, lambda: self.status_label.configure(text=""))

    def refresh(self):
        pass
