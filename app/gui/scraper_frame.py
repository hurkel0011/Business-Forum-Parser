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
from ..scrapers.upwork import UpworkScraper
from ..scrapers.craigslist import CraigslistScraper
from ..scrapers.social_search import SocialMediaScraper
from ..scrapers.capterra import CapterraScraper
from ..scrapers.quora import QuoraScraper
from ..scrapers.producthunt import ProductHuntScraper
from ..scrapers.wordpress import WordPressScraper
from ..scrapers.shopify import ShopifyScraper
from ..scrapers.devto import DevToScraper
from ..scrapers.freelancer import FreelancerScraper
from ..scrapers.spiceworks import SpiceworksScraper
from ..scrapers.discourse import DiscourseScraper
from ..scrapers.atlassian import AtlassianScraper
from ..scrapers.apple import AppleScraper
from ..scrapers.cloud_forums import CloudForumsScraper
from ..scrapers.complaints import ComplaintsScraper
from ..scrapers.more_freelance import MoreFreelanceScraper
from ..scrapers.saas_vendors import SaaSVendorScraper
from ..scrapers.marketing_forums import MarketingForumsScraper
from ..scrapers.ecommerce import EcommerceScraper
from ..scrapers.github_discussions import GitHubDiscussionsScraper
from ..scrapers.accounting import AccountingScraper
from ..scrapers.education import EducationScraper
from ..scrapers.healthcare_it import HealthcareITScraper
from ..scrapers.hr_recruiting import HRRecruitingScraper
from ..scrapers.legal_tech import LegalTechScraper
from ..scrapers.real_estate_tech import RealEstateTechScraper
from ..scrapers.gamedev import GameDevScraper
from ..scrapers.nocode_platforms import NoCodePlatformsScraper
from ..scrapers.reddit_targeted import RedditTargetedScraper
from ..scrapers.enricher import enrich_post, batch_enrich
from ..prescorer import batch_prescore, prescore
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
            sources_frame, text="41 Sources — the widest net on the internet",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, padx=15, pady=(10, 5), sticky="w")

        self.source_vars = {}
        sources_rows = [
            [("ddg", "DuckDuckGo"), ("bing", "Bing / Edge"), ("google", "Google"), ("brave", "Brave Search")],
            [("github", "GitHub Issues"), ("gh_disc", "GitHub Discussions"), ("hackernews", "Hacker News"), ("stackoverflow", "Stack Overflow")],
            [("microsoft", "Microsoft"), ("atlassian", "Atlassian"), ("devto", "Dev.to"), ("cloud", "Cloud (DO/CF/AWS)")],
            [("trustpilot", "Trustpilot"), ("g2", "G2 Reviews"), ("capterra", "Capterra"), ("complaints", "BBB/Sitejabber/etc.")],
            [("indiehackers", "IndieHackers"), ("quora", "Quora"), ("producthunt", "Product Hunt"), ("apple", "Apple Forums")],
            [("wordpress", "WordPress"), ("shopify", "Shopify"), ("ecommerce", "WooCommerce/Magento/Wix"), ("accounting", "QuickBooks/Xero/Sage")],
            [("discourse", "SaaS Communities"), ("spiceworks", "Spiceworks IT"), ("saas_vendors", "Salesforce/HubSpot"), ("marketing", "SEO/Marketing")],
            [("education", "Education / LMS"), ("healthcare", "Healthcare IT"), ("hr_recruiting", "HR / Recruiting"), ("legal_tech", "Legal Tech")],
            [("real_estate", "Real Estate Tech"), ("gamedev", "Game Dev / Creative"), ("nocode", "No-Code / Low-Code"), ("social", "Social Media")],
            [("upwork", "Upwork"), ("craigslist", "Craigslist"), ("freelancer", "Freelancer.com"), ("more_freelance", "Fiverr/Guru/PPH")],
            [("reddit_targeted", "Reddit (Targeted)")],
        ]

        # Load saved toggle state from config (default to True if not set)
        saved_sources = self.config.get("scrape_sources", {}) or {}

        for row_idx, row_sources in enumerate(sources_rows):
            for col_idx, (key, label) in enumerate(row_sources):
                # Use saved value if available, else default to True
                default_on = saved_sources.get(key, True)
                var = ctk.BooleanVar(value=default_on)
                # Persist on toggle so it survives restart
                var.trace_add("write", lambda *_, k=key, v=var: self._save_source_toggle(k, v))
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
            text="Start Scraping — 41 Sources",
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

    def _save_source_toggle(self, key, var):
        """Persist a single toggle state to config so it survives restart."""
        try:
            current = self.config.get("scrape_sources", {}) or {}
            # Make a copy so we don't mutate the live dict before saving
            updated = dict(current)
            updated[key] = bool(var.get())
            self.config.set("scrape_sources", updated)
        except Exception:
            pass  # Don't crash UI on config save failure

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
                "capterra": CapterraScraper(),
                "complaints": ComplaintsScraper(),
                "indiehackers": IndieHackersScraper(),
                "quora": QuoraScraper(),
                "producthunt": ProductHuntScraper(),
                "devto": DevToScraper(),
                "wordpress": WordPressScraper(),
                "shopify": ShopifyScraper(),
                "atlassian": AtlassianScraper(),
                "apple": AppleScraper(),
                "discourse": DiscourseScraper(),
                "spiceworks": SpiceworksScraper(),
                "saas_vendors": SaaSVendorScraper(),
                "cloud": CloudForumsScraper(),
                "marketing": MarketingForumsScraper(),
                "upwork": UpworkScraper(),
                "craigslist": CraigslistScraper(),
                "freelancer": FreelancerScraper(),
                "more_freelance": MoreFreelanceScraper(),
                "gh_disc": GitHubDiscussionsScraper(),
                "ecommerce": EcommerceScraper(),
                "accounting": AccountingScraper(),
                "social": SocialMediaScraper(),
                "education": EducationScraper(),
                "healthcare": HealthcareITScraper(),
                "hr_recruiting": HRRecruitingScraper(),
                "legal_tech": LegalTechScraper(),
                "real_estate": RealEstateTechScraper(),
                "gamedev": GameDevScraper(),
                "nocode": NoCodePlatformsScraper(),
                "reddit_targeted": RedditTargetedScraper(),
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

            # Cross-scraper dedup by URL and fuzzy title
            seen_urls = set()
            seen_titles = set()
            deduped = []
            for p in all_posts:
                url_key = p.get("url", "").rstrip("/").lower()
                # Normalize title: lowercase, strip source suffixes like " - Reddit"
                title_raw = p.get("title", "").lower().strip()
                for suffix in [" - reddit", " : r/", " | atlassian", " - hubspot",
                               " - stack overflow", " - github"]:
                    if suffix in title_raw:
                        title_raw = title_raw[:title_raw.index(suffix)]
                title_key = title_raw[:50]

                if url_key in seen_urls or (title_key and title_key in seen_titles):
                    continue
                seen_urls.add(url_key)
                if title_key:
                    seen_titles.add(title_key)
                deduped.append(p)

            dupes_removed = len(all_posts) - len(deduped)
            if dupes_removed > 0:
                self._ui(lambda d=dupes_removed: self._log(
                    f"  Removed {d} cross-scraper duplicates"
                ))
            all_posts = deduped

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

            # ── PHASE 3: ENRICH (fetch full pages, in parallel) ──
            if self.enrich_var.get():
                self._ui(lambda: self._log("\n━━━ PHASE 3: Fetching full page content ━━━\n"))
                enriched_count = 0
                # Only enrich top 50 to save time
                to_enrich = candidates[:50]
                # Capture original content lengths for the enrichment counter
                old_lens = [len(p.get("content", "")) for p in to_enrich]

                # Parallel fetch — each request is independent network I/O,
                # so we can run them concurrently to slash enrichment time
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                    futures = {pool.submit(enrich_post, p): i for i, p in enumerate(to_enrich)}
                    done = 0
                    for fut in concurrent.futures.as_completed(futures):
                        i = futures[fut]
                        try:
                            to_enrich[i] = fut.result(timeout=30)
                        except Exception:
                            pass  # leave original post on enrichment failure
                        done += 1
                        if done % 5 == 0 or done == len(to_enrich):
                            self._ui(lambda d=done, t=len(to_enrich):
                                self.progress_bar.set(0.35 + (d / t) * 0.15))

                # Count how many posts actually gained content
                for i, post in enumerate(to_enrich):
                    new_len = len(post.get("content", ""))
                    if new_len > old_lens[i] + 100:
                        enriched_count += 1

                self._ui(lambda e=enriched_count: self._log(f"  Enriched {e} posts with full content"))
                candidates = to_enrich + candidates[50:]

                # Re-score enriched posts — full content has better pain signals
                # prescore() stores into post["_prescore"] internally
                for post in candidates:
                    prescore(post)
                candidates.sort(key=lambda p: p.get("_prescore", 0), reverse=True)

            # ── PRE-CLASSIFY: Remove duplicates already in DB ─────
            before_dedup = len(candidates)
            candidates = [p for p in candidates if not self.db.url_exists(p.get("url", ""))]
            dupes_skipped = before_dedup - len(candidates)
            if dupes_skipped > 0:
                self._ui(lambda d=dupes_skipped: self._log(
                    f"  Skipped {d} posts already in database"
                ))

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
            consecutive_low = 0  # Early stop if too many consecutive low scores

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
                        lead_id = self.db.add_lead(post)
                        if lead_id is None:
                            self._ui(lambda p=post: self._log(
                                f"  ↩ duplicate | {p['title'][:55]}"
                            ))
                        else:
                            leads_added += 1
                            consecutive_low = 0
                            sev = post.get("severity", "?").upper()
                            self._ui(lambda s=score, sv=sev, p=post: self._log(
                                f"  ✓ score={s} [{sv}] {p['title'][:55]}"
                            ))
                    else:
                        consecutive_low += 1
                        self._ui(lambda s=score, p=post: self._log(
                            f"  · skip score={s} | {p['title'][:55]}"
                        ))

                    # Early stop: if last 10 posts all scored below threshold, stop
                    if consecutive_low >= 10 and i >= 15:
                        self._ui(lambda: self._log(
                            f"  ⏹ Stopping early — last 10 posts all below threshold"
                        ))
                        break
                except Exception as e:
                    self._ui(lambda e=e: self._log(f"  ✗ Error: {e}"))

            # ── DONE ─────────────────────────────────────────────
            self.db.log_scrape_run(
                "v1.6.1", query or "wide search", len(all_posts), leads_added
            )

            conv = leads_added * 100 // max(len(to_classify), 1)
            self._ui(lambda la=leads_added, ap=len(all_posts), tc=len(to_classify), c=conv: self._log(
                f"\n{'━' * 50}\n"
                f"DONE: {la} leads from {ap} scraped → {tc} classified ({c}% conversion)\n"
                f"{'━' * 50}"
            ))

            # Log prompt cache performance — Sonnet 4.5 caches system prompt
            # for 90% input cost reduction on calls after the first
            cache_stats = classifier.get_cache_stats()
            if cache_stats["cache_hits"] + cache_stats["cache_misses"] > 0:
                self._ui(lambda s=cache_stats: self._log(
                    f"Prompt cache: {s['cache_hits']} hits / {s['cache_misses']} misses "
                    f"({s['hit_rate']*100:.0f}% hit rate)"
                ))
                if cache_stats["cached_input_tokens"] > 0:
                    # Sonnet 4.5: $3/M input, $0.30/M cached input (10x cheaper)
                    cached = cache_stats["cached_input_tokens"]
                    saved_dollars = cached * (3.0 - 0.30) / 1_000_000
                    self._ui(lambda c=cached, sd=saved_dollars: self._log(
                        f"  {c:,} tokens served from cache (saved ~${sd:.3f})"
                    ))
            self._ui(lambda: self.progress_bar.set(1.0))
            self._ui(lambda la=leads_added: self.status_label.configure(
                text=f"Complete — {la} new leads added"
            ))

        except Exception as e:
            # Include the traceback so a user can paste it back for diagnosis
            import traceback
            tb = traceback.format_exc()
            self._ui(lambda e=e, t=tb: self._log(
                f"\nFATAL: {type(e).__name__}: {e}\n\n{t}"
            ))
        finally:
            self._is_scraping = False
            self._ui(lambda: self.scrape_btn.configure(
                state="normal", text="Start Scraping — 41 Sources"
            ))

    def refresh(self):
        pass
