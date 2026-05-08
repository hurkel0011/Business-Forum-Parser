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
        self.conn.commit()

    def add_lead(self, lead_data):
        cursor = self.conn.execute(
            """INSERT INTO leads
               (source, title, url, author, content, severity,
                fixability_score, category, lead_score, company_info)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

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
        stats["avg_score"] = (
            self.conn.execute("SELECT AVG(lead_score) FROM leads").fetchone()[0] or 0
        )
        stats["high_value"] = self.conn.execute(
            "SELECT COUNT(*) FROM leads WHERE lead_score >= 7"
        ).fetchone()[0]
        return stats

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
