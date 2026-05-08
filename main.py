from app.database import Database
from app.config import Config
from app.gui.main_window import MainWindow


def main():
    config = Config()
    db = Database()
    app = MainWindow(db, config)
    app.mainloop()
    db.close()


if __name__ == "__main__":
    main()
