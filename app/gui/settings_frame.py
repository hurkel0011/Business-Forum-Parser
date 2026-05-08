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
        self.anthropic_key = ctk.CTkEntry(
            api_frame, show="*", placeholder_text="sk-ant-..."
        )
        self.anthropic_key.grid(row=1, column=1, padx=(0, 15), pady=5, sticky="ew")

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

        self.status_label = ctk.CTkLabel(self, text="", text_color="#22c55e")
        self.status_label.grid(row=4, column=0, padx=20, pady=5)

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

    def refresh(self):
        pass
