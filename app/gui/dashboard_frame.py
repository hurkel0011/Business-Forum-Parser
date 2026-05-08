import customtkinter as ctk


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, db, config):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.config = config

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        header = ctk.CTkLabel(
            self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold")
        )
        header.grid(row=0, column=0, columnspan=4, padx=20, pady=(10, 20), sticky="w")

        self.stat_cards = {}
        self._create_stat_card("Total Leads", "0", 0)
        self._create_stat_card("High Value", "0", 1)
        self._create_stat_card("Avg Score", "0", 2)
        self._create_stat_card("New", "0", 3)

        recent_label = ctk.CTkLabel(
            self, text="Recent Leads", font=ctk.CTkFont(size=16, weight="bold")
        )
        recent_label.grid(
            row=2, column=0, columnspan=4, padx=20, pady=(30, 10), sticky="w"
        )

        self.recent_frame = ctk.CTkScrollableFrame(self, height=350)
        self.recent_frame.grid(
            row=3, column=0, columnspan=4, padx=20, pady=5, sticky="nsew"
        )
        self.recent_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        source_label = ctk.CTkLabel(
            self, text="Leads by Source", font=ctk.CTkFont(size=16, weight="bold")
        )
        source_label.grid(
            row=4, column=0, columnspan=4, padx=20, pady=(20, 10), sticky="w"
        )

        self.source_frame = ctk.CTkFrame(self)
        self.source_frame.grid(
            row=5, column=0, columnspan=4, padx=20, pady=(0, 10), sticky="ew"
        )

    def _create_stat_card(self, title, value, col):
        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=1, column=col, padx=10, pady=5, sticky="ew")

        val_label = ctk.CTkLabel(
            card, text=value, font=ctk.CTkFont(size=28, weight="bold")
        )
        val_label.pack(padx=20, pady=(15, 0))

        title_label = ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=12), text_color="gray"
        )
        title_label.pack(padx=20, pady=(0, 15))

        self.stat_cards[title] = val_label

    def refresh(self):
        stats = self.db.get_stats()

        self.stat_cards["Total Leads"].configure(text=str(stats.get("total", 0)))
        self.stat_cards["High Value"].configure(text=str(stats.get("high_value", 0)))
        self.stat_cards["Avg Score"].configure(
            text=f"{stats.get('avg_score', 0):.1f}"
        )
        new_count = stats.get("by_status", {}).get("new", 0)
        self.stat_cards["New"].configure(text=str(new_count))

        for widget in self.recent_frame.winfo_children():
            widget.destroy()

        leads = self.db.get_leads()
        for lead in leads[:20]:
            lead_row = ctk.CTkFrame(self.recent_frame)
            lead_row.pack(fill="x", padx=5, pady=2)
            lead_row.grid_columnconfigure(1, weight=1)

            score = lead["lead_score"] or 0
            score_color = (
                "#22c55e" if score >= 7 else "#eab308" if score >= 4 else "#ef4444"
            )

            score_label = ctk.CTkLabel(
                lead_row,
                text=f"{score:.0f}",
                width=35,
                font=ctk.CTkFont(weight="bold"),
                text_color=score_color,
            )
            score_label.grid(row=0, column=0, padx=(10, 5), pady=8)

            title_label = ctk.CTkLabel(
                lead_row, text=(lead["title"] or "")[:80], anchor="w"
            )
            title_label.grid(row=0, column=1, padx=5, pady=8, sticky="w")

            source_label = ctk.CTkLabel(
                lead_row,
                text=lead["source"] or "",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                width=120,
            )
            source_label.grid(row=0, column=2, padx=5, pady=8)

            severity = lead["severity"] or "unknown"
            sev_colors = {
                "critical": "#ef4444",
                "high": "#f97316",
                "medium": "#eab308",
                "low": "#22c55e",
            }
            sev_label = ctk.CTkLabel(
                lead_row,
                text=severity.upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=sev_colors.get(severity, "gray"),
                width=70,
            )
            sev_label.grid(row=0, column=3, padx=(5, 10), pady=8)

        if not leads:
            empty = ctk.CTkLabel(
                self.recent_frame,
                text="No leads yet. Run a scrape to get started!",
                text_color="gray",
            )
            empty.pack(pady=40)

        for widget in self.source_frame.winfo_children():
            widget.destroy()

        by_source = stats.get("by_source", {})
        if by_source:
            for i, (source, count) in enumerate(by_source.items()):
                lbl = ctk.CTkLabel(
                    self.source_frame, text=f"{source}: {count}", font=ctk.CTkFont(size=12)
                )
                lbl.grid(row=0, column=i, padx=15, pady=10)
        else:
            lbl = ctk.CTkLabel(self.source_frame, text="No data yet", text_color="gray")
            lbl.grid(row=0, column=0, padx=15, pady=10)
