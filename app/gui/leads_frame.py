import csv
import threading
import webbrowser
from typing import Optional

import customtkinter as ctk
from tkinter import filedialog
from ..outreach import OutreachGenerator


class LeadsFrame(ctk.CTkFrame):
    """Lead management tab: search, filter, sort, view details, generate
    outreach, edit status/notes, export CSV. The detail panel updates
    when the user clicks a row in the leads list."""

    def __init__(self, parent, db, config):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.config = config

        self.grid_columnconfigure(0, weight=1)
        # Row 4 = leads_scroll, the row that should expand to fill height
        self.grid_rowconfigure(4, weight=1)

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

        # Search box — full-text search across title/content/summary
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="Search:").grid(row=0, column=0, padx=(15, 5), pady=8)
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search across title, content, summary, solution, and notes",
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 5), pady=8, sticky="ew")
        self.search_entry.bind("<Return>", lambda _: self.refresh())
        self.search_entry.bind("<FocusOut>", lambda _: self.refresh())

        ctk.CTkButton(
            search_frame, text="Clear", width=60,
            command=self._clear_search,
        ).grid(row=0, column=2, padx=(0, 15), pady=8)

        # Filters — row 2
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(filter_frame, text="Source:").grid(row=0, column=0, padx=(15, 5), pady=5)
        self.source_filter = ctk.CTkComboBox(
            filter_frame, values=["All"], width=140, command=lambda _: self.refresh()
        )
        self.source_filter.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(filter_frame, text="Severity:").grid(row=0, column=2, padx=(10, 5), pady=5)
        self.severity_filter = ctk.CTkComboBox(
            filter_frame, values=["All", "critical", "high", "medium", "low"],
            width=100, command=lambda _: self.refresh(),
        )
        self.severity_filter.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(filter_frame, text="Difficulty:").grid(row=0, column=4, padx=(10, 5), pady=5)
        self.difficulty_filter = ctk.CTkComboBox(
            filter_frame, values=["All", "quick_fix", "moderate", "complex", "major_project"],
            width=120, command=lambda _: self.refresh(),
        )
        self.difficulty_filter.grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkLabel(filter_frame, text="Status:").grid(row=0, column=6, padx=(10, 5), pady=5)
        self.status_filter = ctk.CTkComboBox(
            filter_frame, values=["All", "new", "contacted", "in_progress", "won", "lost"],
            width=110, command=lambda _: self.refresh(),
        )
        self.status_filter.grid(row=0, column=7, padx=(5, 15), pady=5)

        # Filters — row 2
        ctk.CTkLabel(filter_frame, text="Software:").grid(row=1, column=0, padx=(15, 5), pady=5)
        self.software_filter = ctk.CTkComboBox(
            filter_frame, values=["All"], width=140, command=lambda _: self.refresh()
        )
        self.software_filter.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(filter_frame, text="Company:").grid(row=1, column=2, padx=(10, 5), pady=5)
        self.company_filter = ctk.CTkComboBox(
            filter_frame, values=["All"], width=140, command=lambda _: self.refresh()
        )
        self.company_filter.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkLabel(filter_frame, text="Min Score:").grid(row=1, column=4, padx=(10, 5), pady=5)
        self.score_filter = ctk.CTkEntry(filter_frame, width=50, placeholder_text="0")
        self.score_filter.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        # Apply filter on Enter — otherwise typing in this field would have
        # no effect until the user touches another filter
        self.score_filter.bind("<Return>", lambda _: self.refresh())
        self.score_filter.bind("<FocusOut>", lambda _: self.refresh())

        ctk.CTkLabel(filter_frame, text="Sort by:").grid(row=1, column=6, padx=(10, 5), pady=5)
        self.sort_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Highest Score", "Newest First", "Easiest First", "Hardest First", "Quickest Wins", "Best Revenue"],
            width=140, command=lambda _: self.refresh(),
        )
        self.sort_filter.set("Highest Score")
        self.sort_filter.grid(row=1, column=7, padx=(5, 15), pady=5)

        # Column headers
        header_row = ctk.CTkFrame(self)
        header_row.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        header_row.grid_columnconfigure(3, weight=1)

        cols = [
            ("Score", 40), ("Sev", 55), ("Diff", 70), ("Title", 0),
            ("Software", 100), ("Source", 100), ("Status", 90),
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
            if i == 3:  # Title column stretches
                lbl.grid(row=0, column=i, padx=5, pady=8, sticky="ew")
            else:
                lbl.grid(row=0, column=i, padx=5, pady=8)

        # Leads list
        self.leads_scroll = ctk.CTkScrollableFrame(self)
        self.leads_scroll.grid(row=4, column=0, padx=20, pady=5, sticky="nsew")
        self.leads_scroll.grid_columnconfigure(2, weight=1)

        # Detail panel
        self.detail_frame = ctk.CTkFrame(self)
        self.detail_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.detail_frame.grid_columnconfigure(0, weight=1)

        self.detail_label = ctk.CTkLabel(
            self.detail_frame,
            text="Click a lead to see details",
            text_color="gray",
            wraplength=900,
            justify="left",
        )
        self.detail_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        # Status + notes editor (row 1 spans both columns)
        editor_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        editor_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")
        editor_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(editor_frame, text="Status:", font=ctk.CTkFont(size=11)).grid(
            row=0, column=0, padx=(0, 6), pady=2, sticky="w"
        )
        self.status_editor = ctk.CTkComboBox(
            editor_frame,
            values=["new", "contacted", "in_progress", "won", "lost"],
            width=130, state="disabled",
        )
        self.status_editor.grid(row=0, column=1, padx=(0, 8), pady=2, sticky="w")

        self.save_status_btn = ctk.CTkButton(
            editor_frame, text="Save", width=70, state="disabled",
            command=self._save_status_and_notes,
        )
        self.save_status_btn.grid(row=0, column=2, padx=(0, 0), pady=2)

        ctk.CTkLabel(editor_frame, text="Notes:", font=ctk.CTkFont(size=11)).grid(
            row=1, column=0, padx=(0, 6), pady=(6, 2), sticky="nw"
        )
        self.notes_editor = ctk.CTkTextbox(editor_frame, height=60, state="disabled")
        self.notes_editor.grid(row=1, column=1, columnspan=2, padx=(0, 0), pady=(6, 2), sticky="ew")

        btn_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=(5, 15), pady=10)

        self.open_url_btn = ctk.CTkButton(
            btn_frame, text="Open URL", width=80, state="disabled",
            command=self._open_url,
        )
        self.open_url_btn.grid(row=0, column=0, padx=2, pady=2)

        self.copy_url_btn = ctk.CTkButton(
            btn_frame, text="Copy URL", width=80, state="disabled",
            fg_color="gray30", hover_color="gray40",
            command=self._copy_url,
        )
        self.copy_url_btn.grid(row=0, column=1, padx=2, pady=2)

        self.outreach_btn = ctk.CTkButton(
            btn_frame, text="Generate Outreach", width=140, state="disabled",
            fg_color="#6366f1", hover_color="#4f46e5",
            command=self._generate_outreach,
        )
        self.outreach_btn.grid(row=1, column=0, padx=2, pady=2)

        self.delete_btn = ctk.CTkButton(
            btn_frame, text="Delete Lead", width=100, state="disabled",
            fg_color="#dc2626", hover_color="#b91c1c",
            command=self._delete_lead,
        )
        self.delete_btn.grid(row=2, column=0, padx=2, pady=2)

        self._current_url = None
        self._current_lead = None
        # Tracks the lead_id of an in-flight outreach generation, if any.
        # Used to (1) prevent duplicate generations on rapid clicks and
        # (2) discard results that came back for a lead the user has
        # since navigated away from.
        self._outreach_in_flight_for: Optional[int] = None

    def _clear_search(self):
        self.search_entry.delete(0, "end")
        self.refresh()

    def _build_filters(self):
        filters = {}
        source = self.source_filter.get()
        if source and source != "All":
            filters["source"] = source
        severity = self.severity_filter.get()
        if severity and severity != "All":
            filters["severity"] = severity
        difficulty = self.difficulty_filter.get()
        if difficulty and difficulty != "All":
            filters["difficulty"] = difficulty
        status = self.status_filter.get()
        if status and status != "All":
            filters["status"] = status
        software = self.software_filter.get()
        if software and software != "All":
            filters["software_product"] = software
        company = self.company_filter.get()
        if company and company != "All":
            filters["company_info"] = company
        score_text = self.score_filter.get().strip()
        if score_text:
            try:
                filters["min_score"] = float(score_text)
            except ValueError:
                pass
        # Sort
        sort_map = {
            "Highest Score": "score",
            "Newest First": "newest",
            "Easiest First": "easiest",
            "Hardest First": "hardest",
            "Quickest Wins": "quickest",
            "Best Revenue": "revenue",
        }
        sort_val = self.sort_filter.get()
        filters["sort"] = sort_map.get(sort_val, "score")
        return filters or None

    def refresh(self):
        leads = self.db.get_leads(self._build_filters())

        # Client-side keyword search across title/content/summary/solution/notes.
        # Predicate extracted to app.pipeline_utils.search_lead_text so the
        # same logic powers filtered CSV export (below).
        from ..pipeline_utils import search_lead_text
        search_query = self.search_entry.get().strip()
        if search_query:
            leads = [l for l in leads if search_lead_text(l, search_query)]

        # Populate filter dropdowns using indexed DISTINCT queries
        # instead of pulling every lead and deduping in Python.
        # At 1000+ leads this is dramatically faster.
        self.source_filter.configure(
            values=["All"] + self.db.get_distinct_values("source")
        )
        self.software_filter.configure(
            values=["All"] + self.db.get_distinct_values("software_product")
        )
        self.company_filter.configure(
            values=["All"] + self.db.get_distinct_values("company_info")
        )

        for widget in self.leads_scroll.winfo_children():
            widget.destroy()

        # Soft cap on rendered rows. CustomTkinter on top of Tk slows
        # noticeably above a few hundred widgets, so we render at most
        # this many and show a hint to use filters/search. The DB still
        # holds all leads; this only affects what's visible at once.
        MAX_VISIBLE_LEADS = 200
        total_leads = len(leads)
        truncated = total_leads > MAX_VISIBLE_LEADS
        if truncated:
            leads = leads[:MAX_VISIBLE_LEADS]
            ctk.CTkLabel(
                self.leads_scroll,
                text=(
                    f"Showing first {MAX_VISIBLE_LEADS} of {total_leads}. "
                    "Use filters or search to narrow the list."
                ),
                font=ctk.CTkFont(size=11),
                text_color="#eab308",
            ).pack(pady=(8, 4))

        for lead in leads:
            row = ctk.CTkFrame(self.leads_scroll, cursor="hand2")
            row.pack(fill="x", padx=2, pady=1)
            row.grid_columnconfigure(3, weight=1)
            row.bind("<Button-1>", lambda e, l=lead: self._show_detail(l))

            score = lead["lead_score"] or 0
            score_color = (
                "#22c55e" if score >= 7 else "#eab308" if score >= 4 else "#ef4444"
            )
            ctk.CTkLabel(
                row, text=f"{score:.0f}", width=40,
                font=ctk.CTkFont(weight="bold"), text_color=score_color,
            ).grid(row=0, column=0, padx=4, pady=5)

            sev = (lead["severity"] or "?").upper()[:4]
            sev_colors = {"CRIT": "#ef4444", "HIGH": "#f97316", "MEDI": "#eab308", "LOW": "#22c55e"}
            ctk.CTkLabel(
                row, text=sev, width=55,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=sev_colors.get(sev, "gray"),
            ).grid(row=0, column=1, padx=4, pady=5)

            diff = lead["difficulty"] or "unknown" if "difficulty" in lead.keys() else "unknown"
            diff_short = {"quick_fix": "QUICK", "moderate": "MOD", "complex": "HARD", "major_project": "MAJOR"}.get(diff, "?")
            diff_colors = {"QUICK": "#22c55e", "MOD": "#3b82f6", "HARD": "#f97316", "MAJOR": "#ef4444"}
            ctk.CTkLabel(
                row, text=diff_short, width=70,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=diff_colors.get(diff_short, "gray"),
            ).grid(row=0, column=2, padx=4, pady=5)

            # Add a small note indicator if the lead has notes attached
            title_text = (lead["title"] or "")[:60]
            has_notes = bool((lead.get("notes") or "").strip())
            if has_notes:
                title_text = "📝 " + title_text
            ctk.CTkLabel(
                row, text=title_text, anchor="w"
            ).grid(row=0, column=3, padx=4, pady=5, sticky="ew")

            sw = (lead["software_product"] if "software_product" in lead.keys() else "") or ""
            ctk.CTkLabel(
                row, text=sw[:15], width=100,
                font=ctk.CTkFont(size=10), text_color="#a78bfa",
            ).grid(row=0, column=4, padx=4, pady=5)

            ctk.CTkLabel(
                row, text=(lead["source"] or "")[:15], width=100,
                font=ctk.CTkFont(size=10), text_color="gray",
            ).grid(row=0, column=5, padx=4, pady=5)

            status_menu = ctk.CTkComboBox(
                row,
                values=["new", "contacted", "in_progress", "won", "lost"],
                width=90, font=ctk.CTkFont(size=10),
                command=lambda val, lid=lead["id"]: self._update_status(lid, val),
            )
            status_menu.set(lead["status"] or "new")
            status_menu.grid(row=0, column=6, padx=4, pady=5)

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
        self.copy_url_btn.configure(state="normal" if self._current_url else "disabled")
        # If outreach is currently generating for this same lead, leave the
        # button in its 'Generating...' state. Otherwise reset it so the
        # text is always correct (was a UX bug: switching leads mid-generation
        # left the button labeled 'Generating...' even though it was active).
        if self._outreach_in_flight_for == lead.get("id"):
            self.outreach_btn.configure(state="disabled", text="Generating...")
        else:
            self.outreach_btn.configure(state="normal", text="Generate Outreach")
        self.delete_btn.configure(state="normal")

        # Populate status + notes editor
        self.status_editor.configure(state="readonly")
        self.status_editor.set(lead.get("status", "new") or "new")
        self.save_status_btn.configure(state="normal")
        self.notes_editor.configure(state="normal")
        self.notes_editor.delete("1.0", "end")
        self.notes_editor.insert("1.0", lead.get("notes", "") or "")

        diff = lead["difficulty"] if "difficulty" in lead.keys() else "unknown"
        hours = lead["estimated_hours"] if "estimated_hours" in lead.keys() else 0
        sw = lead["software_product"] if "software_product" in lead.keys() else ""
        rev = lead["revenue_potential"] if "revenue_potential" in lead.keys() else "unknown"
        summary = lead["summary"] if "summary" in lead.keys() else ""
        approach = lead["solution_approach"] if "solution_approach" in lead.keys() else ""

        detail_text = (
            f"Title: {lead['title']}\n"
            f"Source: {lead['source']}  |  Author: {lead['author'] or 'unknown'}\n"
            f"Score: {lead['lead_score']}  |  Severity: {lead['severity']}  |  "
            f"Fixability: {lead['fixability_score']}/10  |  Category: {lead['category']}\n"
            f"Difficulty: {diff}  |  Est. Hours: {hours}  |  Revenue: {rev}\n"
            f"Software: {sw or 'N/A'}  |  Company: {lead['company_info'] or 'unknown'}\n"
        )
        if summary:
            detail_text += f"Problem: {summary}\n"
        if approach:
            detail_text += f"Solution: {approach}\n"
        detail_text += f"\n{(lead['content'] or '')[:300]}"

        self.detail_label.configure(text=detail_text)

    def _save_status_and_notes(self):
        """Persist the status dropdown and notes textbox to the DB."""
        if not self._current_lead:
            return
        lead_id = self._current_lead["id"]
        status = self.status_editor.get()
        notes = self.notes_editor.get("1.0", "end").strip()
        # Pass empty string (not None) so the DB actually clears notes when
        # the user wipes the textbox — None means "don't touch the column"
        self.db.update_lead_status(lead_id, status, notes=notes)
        # Update local cache so subsequent refresh doesn't lose state
        self._current_lead["status"] = status
        self._current_lead["notes"] = notes
        # Flash the button text to confirm save
        self.save_status_btn.configure(text="Saved!")
        self.after(1500, lambda: self.save_status_btn.configure(text="Save"))
        # Refresh leads list so the status badge updates
        self.refresh()

    def _confirm_delete(self, title):
        """Show a modal yes/no popup, return True if user confirms."""
        popup = ctk.CTkToplevel(self)
        popup.title("Delete lead?")
        popup.geometry("420x160")
        popup.attributes("-topmost", True)
        popup.grab_set()  # modal

        ctk.CTkLabel(
            popup, text=f"Delete this lead?\n\n{title}",
            wraplength=380, justify="left",
        ).pack(padx=20, pady=(20, 10))

        result = {"confirmed": False}

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=(5, 15))

        def _confirm():
            result["confirmed"] = True
            popup.destroy()

        ctk.CTkButton(
            btn_frame, text="Cancel", width=100, fg_color="gray40",
            command=popup.destroy,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame, text="Delete", width=100, fg_color="#ef4444",
            command=_confirm,
        ).pack(side="left", padx=5)

        self.wait_window(popup)
        return result["confirmed"]

    def _open_url(self):
        if self._current_url:
            webbrowser.open(self._current_url)

    def _copy_url(self):
        if self._current_url:
            self.clipboard_clear()
            self.clipboard_append(self._current_url)

    def _update_status(self, lead_id, status):
        self.db.update_lead_status(lead_id, status)

    def _delete_lead(self):
        if not self._current_lead:
            return

        # Confirm before destructive action
        title = self._current_lead.get("title", "this lead")[:60]
        if not self._confirm_delete(title):
            return

        lead_id = self._current_lead["id"]
        self.db.delete_lead(lead_id)
        self._current_lead = None
        self._current_url = None
        self.detail_label.configure(text="Lead deleted")
        self.open_url_btn.configure(state="disabled")
        self.copy_url_btn.configure(state="disabled")
        self.outreach_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
        # Clear notes/status editor
        self.status_editor.configure(state="disabled")
        self.save_status_btn.configure(state="disabled")
        self.notes_editor.delete("1.0", "end")
        self.notes_editor.configure(state="disabled")
        self.refresh()

    def _generate_outreach(self):
        if not self._current_lead:
            return
        # Prevent a second click while one generation is already running
        # for any lead — without this guard, rapid clicks (or switching
        # leads + clicking again) would spawn parallel API calls and end
        # up showing two popups out of order.
        if self._outreach_in_flight_for is not None:
            return
        api_key = self.config.get("anthropic_api_key")
        if not api_key:
            self._show_outreach_error("Set your Anthropic API key in Settings first.")
            return

        self.outreach_btn.configure(state="disabled", text="Generating...")
        lead = self._current_lead
        lead_id = lead.get("id")
        self._outreach_in_flight_for = lead_id

        def _on_done(result):
            # Always clear the in-flight marker so future clicks work
            self._outreach_in_flight_for = None
            # Show popup for the lead we generated for (NOT necessarily
            # the currently-selected lead — user may have moved on)
            self._show_outreach_popup(lead, result)
            # Only restore the button if the user is still on this lead.
            # If they moved to a different lead, _show_detail already
            # set the correct button state.
            if self._current_lead and self._current_lead.get("id") == lead_id:
                self.outreach_btn.configure(state="normal", text="Generate Outreach")

        def _run():
            generator = OutreachGenerator(api_key)
            result = generator.generate(lead)
            self.after(0, lambda r=result: _on_done(r))

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

        # Reddit Reply (only shown for Reddit leads)
        reddit_reply = messages.get("reddit_reply", "")
        next_row = 3
        if reddit_reply and reddit_reply.strip():
            reddit_frame = ctk.CTkFrame(popup)
            reddit_frame.grid(row=next_row, column=0, padx=20, pady=5, sticky="ew")
            reddit_frame.grid_columnconfigure(0, weight=1)
            next_row += 1

            ctk.CTkLabel(
                reddit_frame, text="Reddit Reply",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#ff4500",
            ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

            reddit_text = ctk.CTkTextbox(reddit_frame, height=80)
            reddit_text.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")
            reddit_text.insert("1.0", reddit_reply)

            ctk.CTkButton(
                reddit_frame, text="Copy", width=60,
                command=lambda: self._copy_text(reddit_text),
            ).grid(row=1, column=1, padx=(0, 12), pady=(0, 8))

        # LinkedIn DM
        li_frame = ctk.CTkFrame(popup)
        li_frame.grid(row=next_row, column=0, padx=20, pady=5, sticky="ew")
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
        next_row += 1

        # Email
        email_frame = ctk.CTkFrame(popup)
        email_frame.grid(row=next_row, column=0, padx=20, pady=5, sticky="ew")
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
        next_row += 1

        # Tip
        ctk.CTkLabel(
            popup,
            text="Tip: Edit the messages above before sending — personalization wins deals.",
            text_color="gray", font=ctk.CTkFont(size=11),
        ).grid(row=next_row, column=0, padx=20, pady=(5, 2), sticky="w")
        next_row += 1

        ctk.CTkButton(
            popup, text="Close", width=100, fg_color="gray30",
            command=popup.destroy,
        ).grid(row=next_row, column=0, padx=20, pady=(5, 15))

    def _copy_text(self, textbox):
        content = textbox.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(content)

    def _export_csv(self):
        # Export respects the active filters AND the search box so users
        # can export just 'new' leads, or only leads matching a keyword,
        # etc. Previously this always dumped all leads regardless of UI state.
        from ..pipeline_utils import search_lead_text
        leads = self.db.get_leads(self._build_filters())
        search_query = self.search_entry.get().strip()
        if search_query:
            leads = [l for l in leads if search_lead_text(l, search_query)]

        if not leads:
            return

        # Smart default name reflecting filters in play
        default_name = "leads_export.csv"
        if search_query or any(k != "sort" for k in (self._build_filters() or {})):
            default_name = "leads_export_filtered.csv"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=default_name,
        )
        if not filepath:
            return

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Score", "Severity", "Difficulty", "Est Hours", "Revenue",
                "Title", "Source", "Category", "Software", "Fixability",
                "Author", "URL", "Company", "Status", "Notes", "Summary",
                "Solution Approach", "Content",
            ])
            for lead in leads:
                writer.writerow([
                    lead["lead_score"], lead["severity"],
                    lead.get("difficulty", ""), lead.get("estimated_hours", ""),
                    lead.get("revenue_potential", ""),
                    lead["title"], lead["source"], lead["category"],
                    lead.get("software_product", ""), lead["fixability_score"],
                    lead["author"], lead["url"], lead["company_info"],
                    lead["status"], lead.get("notes", "") or "",
                    lead.get("summary", ""),
                    lead.get("solution_approach", ""),
                    (lead["content"] or "")[:500],
                ])
