import customtkinter as ctk


class DashboardFrame(ctk.CTkFrame):
    """Home tab with stat cards (totals, high-value, quick wins, etc.),
    recent leads list, and breakdowns by difficulty/software/revenue/
    company. Refreshes on tab activation or via the Refresh button."""

    def __init__(self, parent, db, config):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.config = config

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=5, padx=20, pady=(10, 15), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            header_frame, text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header_frame, text="Refresh", width=80, command=self.refresh,
        ).grid(row=0, column=1, sticky="e")

        # Stat cards — row 1
        self.stat_cards = {}
        self._create_stat_card("Total Leads", "0", 0)
        self._create_stat_card("High Value", "0", 1)
        self._create_stat_card("Quick Wins", "0", 2)
        self._create_stat_card("Avg Score", "0", 3)
        self._create_stat_card("New", "0", 4)

        # Two-column body
        self.grid_rowconfigure(3, weight=1)

        # Left column — recent leads
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=2, column=0, columnspan=3, rowspan=2, padx=(20, 5), pady=5, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            left_frame, text="Recent Leads", font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, pady=(10, 5), sticky="w")

        self.recent_frame = ctk.CTkScrollableFrame(left_frame, height=300)
        self.recent_frame.grid(row=1, column=0, sticky="nsew")
        self.recent_frame.grid_columnconfigure(0, weight=1)

        # Right column — breakdowns
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=2, column=3, columnspan=2, rowspan=2, padx=(5, 20), pady=5, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure((1, 3, 5, 7), weight=1)

        # Difficulty breakdown
        ctk.CTkLabel(
            right_frame, text="By Difficulty", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, pady=(10, 2), sticky="w")

        self.difficulty_frame = ctk.CTkFrame(right_frame)
        self.difficulty_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        # Software breakdown
        ctk.CTkLabel(
            right_frame, text="Top Software / Products", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=2, column=0, pady=(8, 2), sticky="w")

        self.software_frame = ctk.CTkScrollableFrame(right_frame, height=120)
        self.software_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 8))

        # Revenue breakdown
        ctk.CTkLabel(
            right_frame, text="By Revenue Potential", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=4, column=0, pady=(8, 2), sticky="w")

        self.revenue_frame = ctk.CTkFrame(right_frame)
        self.revenue_frame.grid(row=5, column=0, sticky="nsew", pady=(0, 8))

        # Company / industry breakdown
        ctk.CTkLabel(
            right_frame, text="Top Companies / Industries", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=6, column=0, pady=(8, 2), sticky="w")

        self.company_frame = ctk.CTkScrollableFrame(right_frame, height=100)
        self.company_frame.grid(row=7, column=0, sticky="nsew", pady=(0, 5))

    def _create_stat_card(self, title, value, col):
        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=1, column=col, padx=6, pady=5, sticky="ew")

        val_label = ctk.CTkLabel(
            card, text=value, font=ctk.CTkFont(size=24, weight="bold")
        )
        val_label.pack(padx=15, pady=(12, 0))

        title_label = ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=11), text_color="gray"
        )
        title_label.pack(padx=15, pady=(0, 12))

        self.stat_cards[title] = val_label

    def refresh(self):
        stats = self.db.get_stats()

        self.stat_cards["Total Leads"].configure(text=str(stats.get("total", 0)))
        self.stat_cards["High Value"].configure(text=str(stats.get("high_value", 0)))
        self.stat_cards["Quick Wins"].configure(text=str(stats.get("quick_wins", 0)))
        self.stat_cards["Avg Score"].configure(text=f"{stats.get('avg_score', 0):.1f}")
        new_count = stats.get("by_status", {}).get("new", 0)
        self.stat_cards["New"].configure(text=str(new_count))

        # Recent leads
        for widget in self.recent_frame.winfo_children():
            widget.destroy()

        leads = self.db.get_leads()
        for lead in leads[:20]:
            lead_row = ctk.CTkFrame(self.recent_frame)
            lead_row.pack(fill="x", padx=3, pady=1)
            lead_row.grid_columnconfigure(2, weight=1)

            score = lead["lead_score"] or 0
            score_color = "#22c55e" if score >= 7 else "#eab308" if score >= 4 else "#ef4444"

            ctk.CTkLabel(
                lead_row, text=f"{score:.0f}", width=30,
                font=ctk.CTkFont(size=12, weight="bold"), text_color=score_color,
            ).grid(row=0, column=0, padx=(8, 4), pady=5)

            diff = lead["difficulty"] if "difficulty" in lead.keys() else ""
            diff_badge = {"quick_fix": "QUICK", "moderate": "MOD", "complex": "HARD", "major_project": "MAJOR"}.get(diff, "")
            diff_color = {"QUICK": "#22c55e", "MOD": "#3b82f6", "HARD": "#f97316", "MAJOR": "#ef4444"}.get(diff_badge, "gray")
            if diff_badge:
                ctk.CTkLabel(
                    lead_row, text=diff_badge, width=45,
                    font=ctk.CTkFont(size=9, weight="bold"), text_color=diff_color,
                ).grid(row=0, column=1, padx=2, pady=5)

            ctk.CTkLabel(
                lead_row, text=(lead["title"] or "")[:55], anchor="w",
                font=ctk.CTkFont(size=11),
            ).grid(row=0, column=2, padx=4, pady=5, sticky="w")

            sw = lead["software_product"] if "software_product" in lead.keys() else ""
            if sw:
                ctk.CTkLabel(
                    lead_row, text=sw[:12], width=80,
                    font=ctk.CTkFont(size=10), text_color="#a78bfa",
                ).grid(row=0, column=3, padx=4, pady=5)

            severity = lead["severity"] or "unknown"
            sev_colors = {"critical": "#ef4444", "high": "#f97316", "medium": "#eab308", "low": "#22c55e"}
            ctk.CTkLabel(
                lead_row, text=severity.upper()[:4], width=40,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=sev_colors.get(severity, "gray"),
            ).grid(row=0, column=4, padx=(4, 8), pady=5)

        if not leads:
            ctk.CTkLabel(
                self.recent_frame,
                text="No leads yet. Run a scrape to get started!",
                text_color="gray",
            ).pack(pady=40)

        # Difficulty breakdown
        for widget in self.difficulty_frame.winfo_children():
            widget.destroy()

        by_diff = stats.get("by_difficulty", {})
        diff_order = ["quick_fix", "moderate", "complex", "major_project"]
        diff_labels = {"quick_fix": "Quick Fix", "moderate": "Moderate", "complex": "Complex", "major_project": "Major Project"}
        diff_colors = {"quick_fix": "#22c55e", "moderate": "#3b82f6", "complex": "#f97316", "major_project": "#ef4444"}

        if by_diff:
            for i, key in enumerate(diff_order):
                count = by_diff.get(key, 0)
                if count == 0:
                    continue
                ctk.CTkLabel(
                    self.difficulty_frame,
                    text=f"{diff_labels.get(key, key)}: {count}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=diff_colors.get(key, "gray"),
                ).grid(row=i, column=0, padx=12, pady=3, sticky="w")
        else:
            ctk.CTkLabel(
                self.difficulty_frame, text="No data yet", text_color="gray"
            ).grid(row=0, column=0, padx=12, pady=8)

        # Revenue breakdown
        for widget in self.revenue_frame.winfo_children():
            widget.destroy()

        by_revenue = stats.get("by_revenue", {})
        rev_order = ["premium", "high", "medium", "low"]
        rev_labels = {"premium": "Premium ($5K+)", "high": "High ($1K-$5K)",
                       "medium": "Medium ($200-$1K)", "low": "Low (<$200)"}
        rev_colors = {"premium": "#a855f7", "high": "#22c55e",
                       "medium": "#3b82f6", "low": "gray"}

        if by_revenue:
            for i, key in enumerate(rev_order):
                count = by_revenue.get(key, 0)
                if count == 0:
                    continue
                ctk.CTkLabel(
                    self.revenue_frame,
                    text=f"{rev_labels.get(key, key)}: {count}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=rev_colors.get(key, "gray"),
                ).grid(row=i, column=0, padx=12, pady=3, sticky="w")
        else:
            ctk.CTkLabel(
                self.revenue_frame, text="No data yet", text_color="gray"
            ).grid(row=0, column=0, padx=12, pady=8)

        # Software breakdown
        for widget in self.software_frame.winfo_children():
            widget.destroy()

        by_software = stats.get("by_software", {})
        if by_software:
            for i, (sw, count) in enumerate(list(by_software.items())[:12]):
                ctk.CTkLabel(
                    self.software_frame,
                    text=f"{sw}: {count}",
                    font=ctk.CTkFont(size=11),
                    text_color="#a78bfa",
                ).pack(anchor="w", padx=10, pady=1)
        else:
            ctk.CTkLabel(
                self.software_frame, text="No data yet", text_color="gray"
            ).pack(padx=10, pady=8)

        # Company breakdown
        for widget in self.company_frame.winfo_children():
            widget.destroy()

        by_company = stats.get("by_company", {})
        if by_company:
            for i, (co, count) in enumerate(list(by_company.items())[:12]):
                ctk.CTkLabel(
                    self.company_frame,
                    text=f"{co}: {count}",
                    font=ctk.CTkFont(size=11),
                ).pack(anchor="w", padx=10, pady=1)
        else:
            ctk.CTkLabel(
                self.company_frame, text="No data yet", text_color="gray"
            ).pack(padx=10, pady=8)
