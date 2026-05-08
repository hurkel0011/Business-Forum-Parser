import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Database
from app.config import Config
from app.gui.main_window import MainWindow

config = Config()
db = Database()
app = MainWindow(db, config)
app.mainloop()
db.close()
