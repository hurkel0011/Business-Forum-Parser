import customtkinter as ctk
import threading

from ..scrapers.google_search import DuckDuckGoScraper
from ..scrapers.github_scraper import GitHubScraper
from ..scrapers.hackernews import HackerNewsScraper
from ..scrapers.microsoft import MicrosoftCommunityScraper
from ..scrapers.stackoverflow import StackOverflowScraper
from ..scrapers.enricher import enrich_post
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
        header.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="w")

        # Source toggles - two rows
        sources_frame = ctk.CTkFrame(self)
        sources_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(
            sources_frame, text="Sources", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=5, padx=15, pady=(10, 5), sticky="w")

        self.source_vars = {}
        sources = [
            ("websearch", "Web Search"),
            ("github", "GitHub Issues"),
            ("hackernews", "Hacker News"),
            ("microsoft", "Microsoft Community"),
            ("stackoverflow", "Stack Overflow"),
        ]
        for i, (key, label) in enumerate(sources):
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(sources_frame, text=label, variable=var)
            cb.grid(row=1, column=i, padx=12, pady=(0, 10))
            self.source_vars[key] = var

        # Enrich toggle
        self.enrich_var = ctk.BooleanVar(value=True)
        enrich_cb = ctk.CTkCheckBox(
            sources_frame, text="Fetch full page content (slower but better leads)",
            variable=self.enrich_var,
        )
        enrich_cb.grid(row=2, column=0, columnspan=5, padx=15, pady=(0, 10), sticky="w")

        # Query
        query_frame = ctk.CTkFrame(self)
        query_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        query_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(query_frame, text="Search Query:").grid(
            row=0, column=0, padx=15, pady=10
        )
        self.query_entry = ctk.CTkEntry(
            query_frame,
            placeholder_text="e.g. 'CRM integration broken' or leave blank for wide search...",
        )
        self.query_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")

        ctk.CTkLabel(query_frame, text="Max per source:").grid(
            row=0, column=2, padx=(10, 5), pady=10
        )
        self.limit_entry = ctk.CTkEntry(query_frame, width=50, placeholder_text="30")
        self.limit_entry.grid(row=0, column=3, padx=(0, 15), pady=10)

        # Scrape button
        self.scrape_btn = ctk.CTkButton(
            self,
            text="Start Scraping",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._start_scrape,
        )
        self.scrape_btn.grid(row=3, column=0, padx=20, pady=15, sticky="ew")

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self, text="Ready — 5 sources, no API keys needed for scraping",
            text_color="gray",
        )
        self.status_label.grid(row=5, column=0, padx=20, pady=5, sticky="w")

        # Log
        ctk.CTkLabel(
            self, text="Activity Log", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=6, column=0, padx=20, pady=(15, 5), sticky="w")

        self.log_text = ctk.CTkTextbox(self, height=220)
        self.log_text.grid(row=7, column=0, padx=20, pady=5, sticky="nsew")
        self.grid_rowconfigure(7, weight=1)

    def _log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def _update_ui(self, func):
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

        thread = threading.Thread(target=self._run_scrape, daemon=True)
        thread.start()

    def _run_scrape(self):
        try:
            query = self.query_entry.get().strip() or None
            limit_text = self.limit_entry.get().strip()
            limit = int(limit_text) if limit_text else 30

            scraper_map = {
                "websearch": DuckDuckGoScraper(),
                "github": GitHubScraper(),
                "hackernews": HackerNewsScraper(),
                "microsoft": MicrosoftCommunityScraper(),
                "stackoverflow": StackOverflowScraper(),
            }

            scrapers = [
                s for key, s in scraper_map.items() if self.source_vars[key].get()
            ]

            if not scrapers:
                self._update_ui(lambda: self._log("No sources selected!"))
                return

            # --- Phase 1: Scrape ---
            self._update_ui(lambda: self._log("=== PHASE 1: Scraping forums ===\n"))
            all_posts = []

            for i, scraper in enumerate(scrapers):
                self._update_ui(lambda s=scraper: self._log(f"[{s.name}] Searching..."))
                self._update_ui(
                    lambda i=i: self.progress_bar.set(i / (len(scrapers) * 3))
                )

                try:
                    posts = scraper.scrape(self.config.data, query=query, limit=limit)
                    all_posts.extend(posts)
                    self._update_ui(
                        lambda s=scraper, p=len(posts): self._log(
                            f"[{s.name}] Found {p} posts"
                        )
                    )
                except Exception as e:
                    self._update_ui(
                        lambda s=scraper, e=e: self._log(
                            f"[{s.name}] Error: {e}"
                        )
                    )

            if not all_posts:
                self._update_ui(
                    lambda: self._log("\nNo posts found. Try different keywords.")
                )
                return

            self._update_ui(
                lambda t=len(all_posts): self._log(
                    f"\nTotal: {t} posts scraped"
                )
            )

            # --- Phase 2: Enrich ---
            if self.enrich_var.get():
                self._update_ui(
                    lambda: self._log("\n=== PHASE 2: Fetching full content ===\n")
                )
                enriched = 0
                for i, post in enumerate(all_posts):
                    progress = len(scrapers) / (len(scrapers) * 3) + (
                        i / len(all_posts)
                    ) / 3
                    self._update_ui(lambda p=progress: self.progress_bar.set(p))

                    old_len = len(post.get("content", ""))
                    post = enrich_post(post)
                    all_posts[i] = post
                    new_len = len(post.get("content", ""))

                    if new_len > old_len + 100:
                        enriched += 1

                self._update_ui(
                    lambda e=enriched: self._log(
                        f"Enriched {e} posts with full page content"
                    )
                )

            # --- Phase 3: Classify ---
            self._update_ui(
                lambda t=len(all_posts): self._log(
                    f"\n=== PHASE 3: Classifying {t} posts with Claude ===\n"
                )
            )
            classifier = LeadClassifier(self.config.get("anthropic_api_key"))

            leads_added = 0
            min_score = self.config.get("min_lead_score", 3.0)

            for i, post in enumerate(all_posts):
                progress = 2 / 3 + (i / len(all_posts)) / 3
                self._update_ui(lambda p=progress: self.progress_bar.set(p))
                self._update_ui(
                    lambda i=i, t=len(all_posts): self.status_label.configure(
                        text=f"Classifying {i + 1}/{t}..."
                    )
                )

                try:
                    result = classifier.classify(post)
                    post.update(result)
                    score = post.get("lead_score", 0)

                    if score >= min_score:
                        self.db.add_lead(post)
                        leads_added += 1
                        self._update_ui(
                            lambda p=post, s=score: self._log(
                                f"  ✓ [{p.get('severity', '?').upper()}] "
                                f"score={s} | {p['title'][:55]}"
                            )
                        )
                    else:
                        self._update_ui(
                            lambda p=post, s=score: self._log(
                                f"  · skip (score={s}) {p['title'][:55]}"
                            )
                        )
                except Exception as e:
                    self._update_ui(
                        lambda e=e: self._log(f"  ✗ Classification error: {e}")
                    )

            self.db.log_scrape_run(
                "multiple", query or "default keywords", len(all_posts), leads_added
            )

            self._update_ui(
                lambda la=leads_added, ap=len(all_posts): self._log(
                    f"\n{'='*50}\n"
                    f"DONE: {la} leads from {ap} posts "
                    f"({la*100//max(ap,1)}% conversion)\n"
                    f"{'='*50}"
                )
            )
            self._update_ui(lambda: self.progress_bar.set(1.0))
            self._update_ui(
                lambda la=leads_added: self.status_label.configure(
                    text=f"Complete — {la} new leads added"
                )
            )

        except Exception as e:
            self._update_ui(lambda e=e: self._log(f"\nFatal error: {e}"))
        finally:
            self._is_scraping = False
            self._update_ui(
                lambda: self.scrape_btn.configure(
                    state="normal", text="Start Scraping"
                )
            )

    def refresh(self):
        pass
