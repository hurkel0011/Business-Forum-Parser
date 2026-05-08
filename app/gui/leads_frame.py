import csv
import threading
import webbrowser
import customtkinter as ctk
from tkinter import filedialog
from ..outreach import OutreachGenerator


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

        btn_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=(5, 15), pady=10)

        self.open_url_btn = ctk.CTkButton(
            btn_frame, text="Open URL", width=80, state="disabled",
            command=self._open_url,
        )
        self.open_url_btn.grid(row=0, column=0, padx=2, pady=2)

        self.outreach_btn = ctk.CTkButton(
            btn_frame, text="Generate Outreach", width=140, state="disabled",
            fg_color="#6366f1", hover_color="#4f46e5",
            command=self._generate_outreach,
        )
        self.outreach_btn.grid(row=1, column=0, padx=2, pady=2)

        self._current_url = None
        self._current_lead = None

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
        self._current_lead = lead
        self.open_url_btn.configure(state="normal" if self._current_url else "disabled")
        self.outreach_btn.configure(state="normal")
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

    def _generate_outreach(self):
        if not self._current_lead:
            return
        api_key = self.config.get("anthropic_api_key")
        if not api_key:
            self._show_outreach_error("Set your Anthropic API key in Settings first.")
            return

        self.outreach_btn.configure(state="disabled", text="Generating...")
        lead = self._current_lead

        def _run():
            generator = OutreachGenerator(api_key)
            result = generator.generate(lead)
            self.after(0, lambda: self._show_outreach_popup(lead, result))
            self.after(0, lambda: self.outreach_btn.configure(
                state="normal", text="Generate Outreach"
            ))

        threading.Thread(target=_run, daemon=True).start()

    def _show_outreach_error(self, msg):
        popup = ctk.CTkToplevel(self)
        popup.title("Error")
        popup.geometry("400x120")
        popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text=msg, wraplength=360).pack(padx=20, pady=20)
        ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=(0, 15))

    def _show_outreach_popup(self, lead, messages):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Outreach — {(lead.get('title', ''))[:50]}")
        popup.geometry("700x620")
        popup.attributes("-topmost", True)
        popup.grid_columnconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(
            popup, text="Outreach Messages",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            popup,
            text=f"Lead: {lead.get('title', '')[:70]}",
            text_color="gray", wraplength=650,
        ).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # Opener
        opener_frame = ctk.CTkFrame(popup)
        opener_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        opener_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            opener_frame, text="Icebreaker",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#a78bfa",
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        opener_text = ctk.CTkTextbox(opener_frame, height=40)
        opener_text.grid(row=1, column=0, padx=12, pady=(0, 4), sticky="ew")
        opener_text.insert("1.0", messages.get("suggested_opener", ""))

        ctk.CTkButton(
            opener_frame, text="Copy", width=60,
            command=lambda: self._copy_text(opener_text),
        ).grid(row=1, column=1, padx=(0, 12), pady=(0, 4))

        # LinkedIn DM
        li_frame = ctk.CTkFrame(popup)
        li_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        li_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            li_frame, text="LinkedIn Message",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#0a66c2",
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        li_text = ctk.CTkTextbox(li_frame, height=100)
        li_text.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")
        li_text.insert("1.0", messages.get("linkedin_message", ""))

        ctk.CTkButton(
            li_frame, text="Copy", width=60,
            command=lambda: self._copy_text(li_text),
        ).grid(row=1, column=1, padx=(0, 12), pady=(0, 8))

        # Email
        email_frame = ctk.CTkFrame(popup)
        email_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        email_frame.grid_columnconfigure(0, weight=1)

        subj = messages.get("email_subject", "")
        ctk.CTkLabel(
            email_frame, text=f"Email  —  Subject: {subj}",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#22c55e",
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        ctk.CTkButton(
            email_frame, text="Copy Subject", width=100,
            command=lambda: self.clipboard_clear() or self.clipboard_append(subj),
        ).grid(row=0, column=1, padx=(0, 12), pady=(8, 2))

        email_text = ctk.CTkTextbox(email_frame, height=140)
        email_text.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")
        email_text.insert("1.0", messages.get("email_body", ""))

        ctk.CTkButton(
            email_frame, text="Copy", width=60,
            command=lambda: self._copy_text(email_text),
        ).grid(row=1, column=1, padx=(0, 12), pady=(0, 8))

        # Tip
        ctk.CTkLabel(
            popup,
            text="Tip: Edit the messages above before sending — personalization wins deals.",
            text_color="gray", font=ctk.CTkFont(size=11),
        ).grid(row=5, column=0, padx=20, pady=(5, 2), sticky="w")

        ctk.CTkButton(
            popup, text="Close", width=100, fg_color="gray30",
            command=popup.destroy,
        ).grid(row=6, column=0, padx=20, pady=(5, 15))

    def _copy_text(self, textbox):
        content = textbox.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(content)

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
