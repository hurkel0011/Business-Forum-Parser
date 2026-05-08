import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "forum_parser.db")

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
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

            CREATE TABLE IF NOT EXISTS scrape_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                query TEXT,
                posts_found INTEGER DEFAULT 0,
                leads_generated INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );
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

    def add_lead(self, lead_data):
        cursor = self.conn.execute(
            """INSERT INTO leads
               (source, title, url, author, content, severity,
                fixability_score, category, lead_score, company_info,
                difficulty, estimated_hours, software_product,
                revenue_potential, summary, solution_approach)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_leads(self, filters=None):
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
        else:
            query += " ORDER BY lead_score DESC, created_at DESC"

        return self.conn.execute(query, params).fetchall()

    def update_lead_status(self, lead_id, status, notes=None):
        if notes:
            self.conn.execute(
                "UPDATE leads SET status = ?, notes = ? WHERE id = ?",
                (status, notes, lead_id),
            )
        else:
            self.conn.execute(
                "UPDATE leads SET status = ? WHERE id = ?", (status, lead_id)
            )
        self.conn.commit()

    def get_stats(self):
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

    def get_leads_by_software(self):
        """Group leads by software product."""
        return self.conn.execute(
            "SELECT software_product, COUNT(*) as cnt, AVG(lead_score) as avg_score, "
            "AVG(fixability_score) as avg_fix "
            "FROM leads WHERE software_product != '' AND software_product IS NOT NULL "
            "GROUP BY software_product ORDER BY cnt DESC"
        ).fetchall()

    def get_leads_by_company(self):
        """Group leads by company."""
        return self.conn.execute(
            "SELECT company_info, COUNT(*) as cnt, AVG(lead_score) as avg_score "
            "FROM leads WHERE company_info != '' AND company_info != 'unknown' "
            "AND company_info IS NOT NULL "
            "GROUP BY company_info ORDER BY cnt DESC"
        ).fetchall()

    def log_scrape_run(self, source, query, posts_found, leads_generated):
        self.conn.execute(
            """INSERT INTO scrape_runs
               (source, query, posts_found, leads_generated, completed_at)
               VALUES (?, ?, ?, ?, ?)""",
            (source, query, posts_found, leads_generated, datetime.now().isoformat()),
        )
        self.conn.commit()

    def delete_lead(self, lead_id):
        self.conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
