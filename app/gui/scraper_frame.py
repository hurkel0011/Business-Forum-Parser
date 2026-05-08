import customtkinter as ctk
import threading

from ..scrapers.google_search import DuckDuckGoScraper
from ..scrapers.bing import BingSearchScraper
from ..scrapers.google import GoogleSearchScraper
from ..scrapers.brave import BraveSearchScraper
from ..scrapers.github_scraper import GitHubScraper
from ..scrapers.hackernews import HackerNewsScraper
from ..scrapers.microsoft import MicrosoftCommunityScraper
from ..scrapers.stackoverflow import StackOverflowScraper
from ..scrapers.trustpilot import TrustpilotScraper
from ..scrapers.g2_reviews import G2ReviewScraper
from ..scrapers.indiehackers import IndieHackersScraper
from ..scrapers.enricher import enrich_post
from ..prescorer import batch_prescore
from ..classifier import LeadClassifier


class ScraperFrame(ctk.CTkFrame):
    def __init__(self, parent, db, config):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.config = config
        self._is_scraping = False

        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            self, text="Scrape Forums", font=ctk.CTkFont(size=24, weight="bold")
        )
        header.grid(row=0, column=0, padx=20, pady=(10, 15), sticky="w")

        # Source toggles
        sources_frame = ctk.CTkFrame(self)
        sources_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(
            sources_frame, text="Search Engines + Forums (11 sources, all free)",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, padx=15, pady=(10, 5), sticky="w")

        self.source_vars = {}
        sources_rows = [
            [("ddg", "DuckDuckGo"), ("bing", "Bing / Edge"), ("google", "Google"), ("brave", "Brave Search")],
            [("github", "GitHub Issues"), ("hackernews", "Hacker News"), ("stackoverflow", "Stack Overflow"), ("microsoft", "Microsoft")],
            [("trustpilot", "Trustpilot"), ("g2", "G2 Reviews"), ("indiehackers", "IndieHackers")],
        ]

        for row_idx, row_sources in enumerate(sources_rows):
            for col_idx, (key, label) in enumerate(row_sources):
                var = ctk.BooleanVar(value=True)
                cb = ctk.CTkCheckBox(sources_frame, text=label, variable=var)
                cb.grid(row=row_idx + 1, column=col_idx, padx=10, pady=2)
                self.source_vars[key] = var

        # Options
        opts_frame = ctk.CTkFrame(self)
        opts_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        opts_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(opts_frame, text="Search Query:").grid(
            row=0, column=0, padx=15, pady=8
        )
        self.query_entry = ctk.CTkEntry(
            opts_frame,
            placeholder_text="e.g. 'CRM integration broken' — leave blank for wide search",
        )
        self.query_entry.grid(row=0, column=1, columnspan=3, padx=(0, 15), pady=8, sticky="ew")

        self.enrich_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="Fetch full page content", variable=self.enrich_var
        ).grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 8), sticky="w")

        self.prescore_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="Pre-filter with keyword scoring (faster)",
            variable=self.prescore_var,
        ).grid(row=1, column=2, columnspan=2, padx=15, pady=(0, 8), sticky="w")

        # Scrape button
        self.scrape_btn = ctk.CTkButton(
            self,
            text="Start Scraping — 11 Sources",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._start_scrape,
        )
        self.scrape_btn.grid(row=3, column=0, padx=20, pady=12, sticky="ew")

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=4, column=0, padx=20, pady=3, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.grid(row=5, column=0, padx=20, pady=3, sticky="w")

        # Log
        self.log_text = ctk.CTkTextbox(self, height=240)
        self.log_text.grid(row=6, column=0, padx=20, pady=(5, 10), sticky="nsew")
        self.grid_rowconfigure(6, weight=1)

    def _log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    def _ui(self, func):
        self.after(0, func)

    def _start_scrape(self):
        if self._is_scraping:
            return
        api_key = self.config.get("anthropic_api_key")
        if not api_key:
            self._log("ERROR: Set your Anthropic API key in Settings first!")
            return
        self._is_scraping = True
        self.scrape_btn.configure(state="disabled", text="Scraping...")
        self.log_text.delete("1.0", "end")
        self.progress_bar.set(0)
        threading.Thread(target=self._run_scrape, daemon=True).start()

    def _run_scrape(self):
        try:
            query = self.query_entry.get().strip() or None

            scraper_map = {
                "ddg": DuckDuckGoScraper(),
                "bing": BingSearchScraper(),
                "google": GoogleSearchScraper(),
                "brave": BraveSearchScraper(),
                "github": GitHubScraper(),
                "hackernews": HackerNewsScraper(),
                "microsoft": MicrosoftCommunityScraper(),
                "stackoverflow": StackOverflowScraper(),
                "trustpilot": TrustpilotScraper(),
                "g2": G2ReviewScraper(),
                "indiehackers": IndieHackersScraper(),
            }
            scrapers = [s for k, s in scraper_map.items() if self.source_vars[k].get()]

            if not scrapers:
                self._ui(lambda: self._log("No sources selected!"))
                return

            # ── PHASE 1: SCRAPE ──────────────────────────────────
            self._ui(lambda: self._log("━━━ PHASE 1: Scraping %d sources ━━━\n" % len(scrapers)))
            all_posts = []
            for i, scraper in enumerate(scrapers):
                self._ui(lambda s=scraper: self._log(f"  [{s.name}] Searching..."))
                self._ui(lambda i=i: self.progress_bar.set(i / (len(scrapers) * 4)))
                try:
                    posts = scraper.scrape(self.config.data, query=query, limit=30)
                    all_posts.extend(posts)
                    self._ui(lambda s=scraper, n=len(posts): self._log(f"  [{s.name}] → {n} posts"))
                except Exception as e:
                    self._ui(lambda s=scraper, e=e: self._log(f"  [{s.name}] ERROR: {e}"))

            if not all_posts:
                self._ui(lambda: self._log("\nNo posts found at all. Try different keywords."))
                return

            self._ui(lambda n=len(all_posts): self._log(f"\n  Total scraped: {n} posts"))

            # ── PHASE 2: PRE-SCORE (local, no API) ───────────────
            if self.prescore_var.get():
                self._ui(lambda: self._log("\n━━━ PHASE 2: Pre-scoring with keywords ━━━\n"))
                self._ui(lambda: self.progress_bar.set(0.25))

                candidates = batch_prescore(all_posts, min_score=1.0)
                skipped = len(all_posts) - len(candidates)

                self._ui(lambda c=len(candidates), s=skipped: self._log(
                    f"  {c} candidates passed pre-filter ({s} skipped as irrelevant)"
                ))

                # Show top pre-scored
                for p in candidates[:5]:
                    self._ui(lambda p=p: self._log(
                        f"  ★ pre={p.get('_prescore', 0):.1f} | {p['title'][:60]}"
                    ))
                if len(candidates) > 5:
                    self._ui(lambda n=len(candidates): self._log(f"  ... and {n - 5} more"))
            else:
                candidates = all_posts

            if not candidates:
                self._ui(lambda: self._log("\nNo posts passed pre-filter. Try broader keywords."))
                return

            # ── PHASE 3: ENRICH (fetch full pages) ───────────────
            if self.enrich_var.get():
                self._ui(lambda: self._log("\n━━━ PHASE 3: Fetching full page content ━━━\n"))
                enriched_count = 0
                # Only enrich top 50 to save time
                to_enrich = candidates[:50]
                for i, post in enumerate(to_enrich):
                    self._ui(lambda: self.progress_bar.set(0.35 + (i / len(to_enrich)) * 0.15))
                    old_len = len(post.get("content", ""))
                    to_enrich[i] = enrich_post(post)
                    new_len = len(to_enrich[i].get("content", ""))
                    if new_len > old_len + 100:
                        enriched_count += 1

                self._ui(lambda e=enriched_count: self._log(f"  Enriched {e} posts with full content"))
                candidates = to_enrich + candidates[50:]

            # ── PHASE 4: CLASSIFY (Claude API) ───────────────────
            self._ui(lambda n=len(candidates): self._log(
                f"\n━━━ PHASE 4: Classifying {n} posts with Claude ━━━\n"
            ))

            def on_classifier_msg(msg):
                self._ui(lambda m=msg: self._log(f"  ⚠ {m}"))

            classifier = LeadClassifier(
                self.config.get("anthropic_api_key"),
                error_callback=on_classifier_msg,
            )

            leads_added = 0
            min_score = float(self.config.get("min_lead_score", 3.0))

            # Classify top candidates (limit to 40 to control API cost)
            to_classify = candidates[:40]

            for i, post in enumerate(to_classify):
                self._ui(lambda: self.progress_bar.set(0.55 + (i / len(to_classify)) * 0.45))
                self._ui(lambda i=i, t=len(to_classify): self.status_label.configure(
                    text=f"Classifying {i + 1}/{t}..."
                ))

                try:
                    result = classifier.classify(post)
                    post.update(result)
                    score = post.get("lead_score", 0)

                    if score >= min_score:
                        self.db.add_lead(post)
                        leads_added += 1
                        sev = post.get("severity", "?").upper()
                        self._ui(lambda s=score, sv=sev, p=post: self._log(
                            f"  ✓ score={s} [{sv}] {p['title'][:55]}"
                        ))
                    else:
                        self._ui(lambda s=score, p=post: self._log(
                            f"  · skip score={s} | {p['title'][:55]}"
                        ))
                except Exception as e:
                    self._ui(lambda e=e: self._log(f"  ✗ Error: {e}"))

            # ── DONE ─────────────────────────────────────────────
            self.db.log_scrape_run(
                "v1.1.0", query or "wide search", len(all_posts), leads_added
            )

            conv = leads_added * 100 // max(len(to_classify), 1)
            self._ui(lambda la=leads_added, ap=len(all_posts), tc=len(to_classify), c=conv: self._log(
                f"\n{'━' * 50}\n"
                f"DONE: {la} leads from {ap} scraped → {tc} classified ({c}% conversion)\n"
                f"{'━' * 50}"
            ))
            self._ui(lambda: self.progress_bar.set(1.0))
            self._ui(lambda la=leads_added: self.status_label.configure(
                text=f"Complete — {la} new leads added"
            ))

        except Exception as e:
            self._ui(lambda e=e: self._log(f"\nFATAL: {e}"))
        finally:
            self._is_scraping = False
            self._ui(lambda: self.scrape_btn.configure(
                state="normal", text="Start Scraping — 11 Sources"
            ))

    def refresh(self):
        pass
