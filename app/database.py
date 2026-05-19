"""SQLite persistence layer for leads and scrape-run history.

The database has two tables:
  leads: one row per discovered lead with classification metadata
  scrape_runs: log of pipeline runs (timestamps, post/lead counts)

The connection is shared across threads via check_same_thread=False
plus WAL journal mode so the GUI can read while the scrape writes.
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, Any

# Ownership watermark — embedded in every database instance
_ORIGIN = "BonnieTheDog420"


class Database:
    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "forum_parser.db")

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # WAL mode allows the GUI thread to query (e.g. refresh leads list)
        # while the background scrape thread is writing. Default 'delete'
        # mode would serialize all access and could cause UI hitches.
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")  # safe + fast in WAL
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT,
                author TEXT,
                content TEXT,
                severity TEXT,
                fixability_score REAL DEFAULT 0,
                category TEXT,
                lead_score REAL DEFAULT 0,
                company_info TEXT,
                status TEXT DEFAULT 'new',
                notes TEXT,
                difficulty TEXT DEFAULT 'unknown',
                estimated_hours REAL DEFAULT 0,
                software_product TEXT DEFAULT '',
                revenue_potential TEXT DEFAULT 'unknown',
                summary TEXT DEFAULT '',
                solution_approach TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_leads_url ON leads(url);
            CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score DESC);
            CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
            CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
            CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC);

            CREATE TABLE IF NOT EXISTS scrape_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                query TEXT,
                posts_found INTEGER DEFAULT 0,
                leads_generated INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS _meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            INSERT OR IGNORE INTO _meta (key, value)
                VALUES ('origin', 'BonnieTheDog420'),
                       ('author', 'Howell Brady');
        """)
        # Migrate older databases that lack new columns
        self._migrate()
        self.conn.commit()

    def _migrate(self):
        """Add new columns to existing databases."""
        existing = {
            row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()
        }
        new_cols = [
            ("difficulty", "TEXT DEFAULT 'unknown'"),
            ("estimated_hours", "REAL DEFAULT 0"),
            ("software_product", "TEXT DEFAULT ''"),
            ("revenue_potential", "TEXT DEFAULT 'unknown'"),
            ("summary", "TEXT DEFAULT ''"),
            ("solution_approach", "TEXT DEFAULT ''"),
        ]
        for col_name, col_def in new_cols:
            if col_name not in existing:
                self.conn.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_def}")

    def url_exists(self, url: str) -> bool:
        """Check if a lead with this URL already exists."""
        if not url:
            return False
        row = self.conn.execute(
            "SELECT 1 FROM leads WHERE url = ? LIMIT 1", (url,)
        ).fetchone()
        return row is not None

    def add_lead(self, lead_data: dict) -> Optional[int]:
        # Skip duplicates by URL
        url = lead_data.get("url", "")
        if url and self.url_exists(url):
            return None

        cursor = self.conn.execute(
            """INSERT INTO leads
               (source, title, url, author, content, severity,
                fixability_score, category, lead_score, company_info,
                difficulty, estimated_hours, software_product,
                revenue_potential, summary, solution_approach,
                status, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                lead_data.get("source", ""),
                lead_data.get("title", ""),
                lead_data.get("url", ""),
                lead_data.get("author", ""),
                lead_data.get("content", ""),
                lead_data.get("severity", ""),
                lead_data.get("fixability_score", 0),
                lead_data.get("category", ""),
                lead_data.get("lead_score", 0),
                lead_data.get("company_info", ""),
                lead_data.get("difficulty", "unknown"),
                lead_data.get("estimated_hours", 0),
                lead_data.get("software_product", ""),
                lead_data.get("revenue_potential", "unknown"),
                lead_data.get("summary", ""),
                lead_data.get("solution_approach", ""),
                lead_data.get("status", "new"),
                lead_data.get("notes", None),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_leads(
        self,
        filters: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> list[dict]:
        query = "SELECT * FROM leads"
        params = []
        conditions = []

        if filters:
            if filters.get("source"):
                conditions.append("source = ?")
                params.append(filters["source"])
            if filters.get("severity"):
                conditions.append("severity = ?")
                params.append(filters["severity"])
            if filters.get("status"):
                conditions.append("status = ?")
                params.append(filters["status"])
            if filters.get("min_score"):
                conditions.append("lead_score >= ?")
                params.append(filters["min_score"])
            if filters.get("difficulty"):
                conditions.append("difficulty = ?")
                params.append(filters["difficulty"])
            if filters.get("software_product"):
                conditions.append("software_product = ?")
                params.append(filters["software_product"])
            if filters.get("company_info"):
                conditions.append("company_info = ?")
                params.append(filters["company_info"])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Sort order
        sort = filters.get("sort", "score") if filters else "score"
        if sort == "easiest":
            query += " ORDER BY CASE difficulty WHEN 'quick_fix' THEN 1 WHEN 'moderate' THEN 2 WHEN 'complex' THEN 3 WHEN 'major_project' THEN 4 ELSE 5 END, lead_score DESC"
        elif sort == "hardest":
            query += " ORDER BY CASE difficulty WHEN 'major_project' THEN 1 WHEN 'complex' THEN 2 WHEN 'moderate' THEN 3 WHEN 'quick_fix' THEN 4 ELSE 5 END, lead_score DESC"
        elif sort == "quickest":
            query += " ORDER BY estimated_hours ASC, lead_score DESC"
        elif sort == "revenue":
            query += " ORDER BY CASE revenue_potential WHEN 'premium' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 WHEN 'low' THEN 4 ELSE 5 END, lead_score DESC"
        elif sort == "newest":
            query += " ORDER BY created_at DESC, lead_score DESC"
        else:
            query += " ORDER BY lead_score DESC, created_at DESC"

        # Optional LIMIT — the dashboard wants the top 20; without this it
        # would pull every row and slice in Python, which doesn't scale.
        if limit is not None and limit > 0:
            query += " LIMIT ?"
            params.append(int(limit))

        # Return dicts (not sqlite3.Row) so callers can use .get() with defaults.
        # sqlite3.Row supports indexing but raises IndexError on missing keys,
        # which breaks the GUI code that uses .get() for optional fields.
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    # Whitelist of columns the GUI is allowed to populate dropdowns from.
    # Restricts the dynamic column name to known values to prevent any
    # accidental SQL injection if a future caller does the wrong thing.
    _FILTER_COLUMNS = {
        "source", "severity", "category", "difficulty",
        "software_product", "company_info", "status",
        "revenue_potential",
    }

    def get_distinct_values(self, column: str) -> list[str]:
        """Return sorted unique non-empty values from a given column.

        Used by the GUI to populate filter dropdowns. Much cheaper than
        reading all leads and deduping in Python — the indexed query
        runs entirely in SQLite.
        """
        if column not in self._FILTER_COLUMNS:
            raise ValueError(f"Column '{column}' not in filterable whitelist")
        rows = self.conn.execute(
            f"SELECT DISTINCT {column} FROM leads "
            f"WHERE {column} IS NOT NULL AND {column} != '' "
            f"AND {column} != 'unknown' "
            f"ORDER BY {column}"
        ).fetchall()
        return [r[column] for r in rows]

    def update_lead_status(
        self,
        lead_id: int,
        status: str,
        notes: Optional[str] = None,
    ) -> None:
        """Update a lead's status, optionally setting notes.

        notes semantics:
        - None (default): leave the notes column untouched
        - "" (empty string): clear the notes column
        - "text": set notes to text
        """
        if notes is None:
            self.conn.execute(
                "UPDATE leads SET status = ? WHERE id = ?", (status, lead_id)
            )
        else:
            self.conn.execute(
                "UPDATE leads SET status = ?, notes = ? WHERE id = ?",
                (status, notes, lead_id),
            )
        self.conn.commit()

    def get_stats(self) -> dict[str, Any]:
        stats = {}
        stats["total"] = self.conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        stats["by_severity"] = dict(
            self.conn.execute(
                "SELECT severity, COUNT(*) FROM leads GROUP BY severity"
            ).fetchall()
        )
        stats["by_source"] = dict(
            self.conn.execute(
                "SELECT source, COUNT(*) FROM leads GROUP BY source"
            ).fetchall()
        )
        stats["by_status"] = dict(
            self.conn.execute(
                "SELECT status, COUNT(*) FROM leads GROUP BY status"
            ).fetchall()
        )
        stats["by_difficulty"] = dict(
            self.conn.execute(
                "SELECT difficulty, COUNT(*) FROM leads WHERE difficulty != 'unknown' GROUP BY difficulty"
            ).fetchall()
        )
        stats["by_software"] = dict(
            self.conn.execute(
                "SELECT software_product, COUNT(*) FROM leads "
                "WHERE software_product != '' AND software_product IS NOT NULL "
                "GROUP BY software_product ORDER BY COUNT(*) DESC LIMIT 15"
            ).fetchall()
        )
        stats["by_company"] = dict(
            self.conn.execute(
                "SELECT company_info, COUNT(*) FROM leads "
                "WHERE company_info != '' AND company_info != 'unknown' "
                "AND company_info IS NOT NULL "
                "GROUP BY company_info ORDER BY COUNT(*) DESC LIMIT 15"
            ).fetchall()
        )
        stats["by_revenue"] = dict(
            self.conn.execute(
                "SELECT revenue_potential, COUNT(*) FROM leads "
                "WHERE revenue_potential != 'unknown' GROUP BY revenue_potential"
            ).fetchall()
        )
        stats["avg_score"] = (
            self.conn.execute("SELECT AVG(lead_score) FROM leads").fetchone()[0] or 0
        )
        stats["high_value"] = self.conn.execute(
            "SELECT COUNT(*) FROM leads WHERE lead_score >= 7"
        ).fetchone()[0]
        stats["quick_wins"] = self.conn.execute(
            "SELECT COUNT(*) FROM leads WHERE difficulty IN ('quick_fix', 'moderate') "
            "AND lead_score >= 5"
        ).fetchone()[0]
        return stats

    def get_leads_by_software(self) -> list[dict]:
        """Group leads by software product."""
        rows = self.conn.execute(
            "SELECT software_product, COUNT(*) as cnt, AVG(lead_score) as avg_score, "
            "AVG(fixability_score) as avg_fix "
            "FROM leads WHERE software_product != '' AND software_product IS NOT NULL "
            "GROUP BY software_product ORDER BY cnt DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_leads_by_company(self) -> list[dict]:
        """Group leads by company."""
        rows = self.conn.execute(
            "SELECT company_info, COUNT(*) as cnt, AVG(lead_score) as avg_score "
            "FROM leads WHERE company_info != '' AND company_info != 'unknown' "
            "AND company_info IS NOT NULL "
            "GROUP BY company_info ORDER BY cnt DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def log_scrape_run(
        self,
        source: str,
        query: str,
        posts_found: int,
        leads_generated: int,
    ) -> None:
        self.conn.execute(
            """INSERT INTO scrape_runs
               (source, query, posts_found, leads_generated, completed_at)
               VALUES (?, ?, ?, ?, ?)""",
            # Use UTC to match the leads table's CURRENT_TIMESTAMP (also UTC).
            # Mixing local time here and UTC there caused inconsistent times
            # between the two tables.
            (source, query, posts_found, leads_generated,
             datetime.utcnow().isoformat(sep=" ", timespec="seconds")),
        )
        self.conn.commit()

    def get_scrape_history(self, limit: int = 20) -> list[dict]:
        """Get recent scrape runs for performance tracking."""
        rows = self.conn.execute(
            "SELECT * FROM scrape_runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_source_performance(self) -> list[dict]:
        """Get lead conversion rate by source — which sources produce the best leads."""
        rows = self.conn.execute(
            """SELECT source, COUNT(*) as count,
                      AVG(lead_score) as avg_score,
                      SUM(CASE WHEN lead_score >= 5 THEN 1 ELSE 0 END) as high_value,
                      AVG(CASE WHEN estimated_hours > 0 THEN estimated_hours END) as avg_hours
               FROM leads
               GROUP BY source
               ORDER BY avg_score DESC"""
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_lead(self, lead_id: int) -> None:
        self.conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
