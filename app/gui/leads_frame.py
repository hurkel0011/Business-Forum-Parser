import csv
import webbrowser
import customtkinter as ctk
from tkinter import filedialog


class LeadsFrame(ctk.CTkFrame):
    def __init__(self, parent, db, config):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.config = config

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame, text="Leads", font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header_frame, text="Export CSV", width=100, command=self._export_csv
        ).grid(row=0, column=1, padx=5)

        ctk.CTkButton(
            header_frame, text="Refresh", width=80, command=self.refresh
        ).grid(row=0, column=2, padx=5)

        # Filters
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Source:").grid(
            row=0, column=0, padx=(15, 5), pady=10
        )
        self.source_filter = ctk.CTkComboBox(
            filter_frame, values=["All"], width=160, command=lambda _: self.refresh()
        )
        self.source_filter.grid(row=0, column=1, padx=5, pady=10)

        ctk.CTkLabel(filter_frame, text="Severity:").grid(
            row=0, column=2, padx=(15, 5), pady=10
        )
        self.severity_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All", "critical", "high", "medium", "low"],
            width=120,
            command=lambda _: self.refresh(),
        )
        self.severity_filter.grid(row=0, column=3, padx=5, pady=10)

        ctk.CTkLabel(filter_frame, text="Status:").grid(
            row=0, column=4, padx=(15, 5), pady=10
        )
        self.status_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All", "new", "contacted", "in_progress", "won", "lost"],
            width=120,
            command=lambda _: self.refresh(),
        )
        self.status_filter.grid(row=0, column=5, padx=5, pady=10)

        ctk.CTkLabel(filter_frame, text="Min Score:").grid(
            row=0, column=6, padx=(15, 5), pady=10
        )
        self.score_filter = ctk.CTkEntry(filter_frame, width=50, placeholder_text="0")
        self.score_filter.grid(row=0, column=7, padx=(0, 15), pady=10)

        # Column headers
        header_row = ctk.CTkFrame(self)
        header_row.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        header_row.grid_columnconfigure(2, weight=1)

        cols = [
            ("Score", 50), ("Severity", 70), ("Title", 0),
            ("Source", 130), ("Category", 100), ("Status", 100),
        ]
        for i, (name, width) in enumerate(cols):
            kw = {"width": width} if width else {}
            lbl = ctk.CTkLabel(
                header_row,
                text=name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="gray",
                **kw,
            )
            if i == 2:
                lbl.grid(row=0, column=i, padx=5, pady=8, sticky="ew")
            else:
                lbl.grid(row=0, column=i, padx=5, pady=8)

        # Leads list
        self.leads_scroll = ctk.CTkScrollableFrame(self)
        self.leads_scroll.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")
        self.leads_scroll.grid_columnconfigure(2, weight=1)

        # Detail panel
        self.detail_frame = ctk.CTkFrame(self)
        self.detail_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.detail_frame.grid_columnconfigure(0, weight=1)

        self.detail_label = ctk.CTkLabel(
            self.detail_frame,
            text="Click a lead to see details",
            text_color="gray",
            wraplength=900,
            justify="left",
        )
        self.detail_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.open_url_btn = ctk.CTkButton(
            self.detail_frame, text="Open URL", width=80, state="disabled",
            command=self._open_url,
        )
        self.open_url_btn.grid(row=0, column=1, padx=(5, 15), pady=10)
        self._current_url = None

    def _build_filters(self):
        filters = {}
        source = self.source_filter.get()
        if source and source != "All":
            filters["source"] = source
        severity = self.severity_filter.get()
        if severity and severity != "All":
            filters["severity"] = severity
        status = self.status_filter.get()
        if status and status != "All":
            filters["status"] = status
        score_text = self.score_filter.get().strip()
        if score_text:
            try:
                filters["min_score"] = float(score_text)
            except ValueError:
                pass
        return filters or None

    def refresh(self):
        leads = self.db.get_leads(self._build_filters())

        all_leads = self.db.get_leads()
        sources = sorted(set(l["source"] for l in all_leads if l["source"]))
        self.source_filter.configure(values=["All"] + sources)

        for widget in self.leads_scroll.winfo_children():
            widget.destroy()

        for lead in leads:
            row = ctk.CTkFrame(self.leads_scroll, cursor="hand2")
            row.pack(fill="x", padx=2, pady=1)
            row.grid_columnconfigure(2, weight=1)
            row.bind("<Button-1>", lambda e, l=lead: self._show_detail(l))

            score = lead["lead_score"] or 0
            score_color = (
                "#22c55e" if score >= 7 else "#eab308" if score >= 4 else "#ef4444"
            )

            ctk.CTkLabel(
                row, text=f"{score:.0f}", width=50,
                font=ctk.CTkFont(weight="bold"), text_color=score_color,
            ).grid(row=0, column=0, padx=5, pady=6)

            sev = (lead["severity"] or "unknown").upper()
            sev_colors = {
                "CRITICAL": "#ef4444", "HIGH": "#f97316",
                "MEDIUM": "#eab308", "LOW": "#22c55e",
            }
            ctk.CTkLabel(
                row, text=sev, width=70,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=sev_colors.get(sev, "gray"),
            ).grid(row=0, column=1, padx=5, pady=6)

            ctk.CTkLabel(
                row, text=(lead["title"] or "")[:70], anchor="w"
            ).grid(row=0, column=2, padx=5, pady=6, sticky="ew")

            ctk.CTkLabel(
                row, text=lead["source"] or "", width=130,
                font=ctk.CTkFont(size=11), text_color="gray",
            ).grid(row=0, column=3, padx=5, pady=6)

            ctk.CTkLabel(
                row, text=lead["category"] or "", width=100,
                font=ctk.CTkFont(size=11),
            ).grid(row=0, column=4, padx=5, pady=6)

            status_menu = ctk.CTkComboBox(
                row,
                values=["new", "contacted", "in_progress", "won", "lost"],
                width=100,
                font=ctk.CTkFont(size=11),
                command=lambda val, lid=lead["id"]: self._update_status(lid, val),
            )
            status_menu.set(lead["status"] or "new")
            status_menu.grid(row=0, column=5, padx=5, pady=6)

        if not leads:
            ctk.CTkLabel(
                self.leads_scroll,
                text="No leads match your filters.",
                text_color="gray",
            ).pack(pady=40)

    def _show_detail(self, lead):
        self._current_url = lead["url"]
        self.open_url_btn.configure(state="normal" if self._current_url else "disabled")
        detail_text = (
            f"Title: {lead['title']}\n"
            f"Source: {lead['source']}  |  Author: {lead['author'] or 'unknown'}\n"
            f"URL: {lead['url'] or 'N/A'}\n"
            f"Score: {lead['lead_score']}  |  Severity: {lead['severity']}  |  "
            f"Fixability: {lead['fixability_score']}/10  |  Category: {lead['category']}\n"
            f"Company: {lead['company_info'] or 'unknown'}\n\n"
            f"{(lead['content'] or '')[:400]}"
        )
        self.detail_label.configure(text=detail_text)

    def _open_url(self):
        if self._current_url:
            webbrowser.open(self._current_url)

    def _update_status(self, lead_id, status):
        self.db.update_lead_status(lead_id, status)

    def _export_csv(self):
        leads = self.db.get_leads()
        if not leads:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="leads_export.csv",
        )
        if not filepath:
            return

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Score", "Severity", "Title", "Source", "Category",
                "Fixability", "Author", "URL", "Company", "Status", "Content",
            ])
            for lead in leads:
                writer.writerow([
                    lead["lead_score"], lead["severity"], lead["title"],
                    lead["source"], lead["category"], lead["fixability_score"],
                    lead["author"], lead["url"], lead["company_info"],
                    lead["status"], (lead["content"] or "")[:500],
                ])
