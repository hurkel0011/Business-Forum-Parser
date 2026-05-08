# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Business Forum Parser — Lead intelligence engine
# Author: Howell Brady (howellbrady@icloud.com)
# Ownership Proof: BonnieTheDog420
# License: MIT — see LICENSE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from app.database import Database
from app.config import Config
from app.gui.main_window import MainWindow

__author__ = "Howell Brady"
__watermark__ = "BonnieTheDog420"


def main():
    config = Config()
    db = Database()
    app = MainWindow(db, config)
    app.mainloop()
    db.close()


if __name__ == "__main__":
    main()
