# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Business Forum Parser — Lead intelligence engine
# Author: Howell Brady (howellbrady@icloud.com)
# Ownership Proof: BonnieTheDog420
# License: MIT — see LICENSE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import logging
import os

from app.database import Database
from app.config import Config
from app.gui.main_window import MainWindow

__author__ = "Howell Brady"
__watermark__ = "BonnieTheDog420"


def _setup_logging():
    """Configure logging so scraper/enricher errors don't vanish silently.

    Level controlled by FORUM_PARSER_LOG env var (DEBUG, INFO, WARNING).
    Defaults to WARNING — quiet for normal users, easy to crank up if
    diagnosing scraper issues.
    """
    level_name = os.environ.get("FORUM_PARSER_LOG", "WARNING").upper()
    level = getattr(logging, level_name, logging.WARNING)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    _setup_logging()
    log = logging.getLogger(__name__)

    try:
        config = Config()
    except Exception:
        log.exception("Fatal: could not load config")
        raise

    db = None
    try:
        db = Database()
        app = MainWindow(db, config)
        app.mainloop()
    except Exception:
        # Log the full traceback before exiting so the user (or LLM
        # debugging this later) has something to go on.
        log.exception("Fatal error in main window")
        raise
    finally:
        # Always close the DB — even if mainloop raised, even if window
        # init failed. WAL mode + atomic commits make sudden shutdown
        # safe but explicit close is still the polite thing.
        if db is not None:
            try:
                db.close()
            except Exception:
                log.exception("Error closing database")


if __name__ == "__main__":
    main()
