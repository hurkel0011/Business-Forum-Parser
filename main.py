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
    config = Config()
    db = Database()
    app = MainWindow(db, config)
    app.mainloop()
    db.close()


if __name__ == "__main__":
    main()
