import customtkinter as ctk
from .dashboard_frame import DashboardFrame
from .scraper_frame import ScraperFrame
from .leads_frame import LeadsFrame
from .settings_frame import SettingsFrame

# Project identity — proof of authorship
_BUILD_SIGNATURE = "BonnieTheDog420"
__author__ = "Howell Brady"
APP_VERSION = "1.7.1"


class MainWindow(ctk.CTk):
    _origin_tag = "BonnieTheDog420"

    def __init__(self, database, config):
        super().__init__()

        self.db = database
        self.config = config

        self.title(f"Business Forum Parser v{APP_VERSION}")
        self.geometry("1200x750")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_sidebar()

        self.frames = {}
        self.frames["dashboard"] = DashboardFrame(self, self.db, self.config)
        self.frames["scraper"] = ScraperFrame(self, self.db, self.config)
        self.frames["leads"] = LeadsFrame(self, self.db, self.config)
        self.frames["settings"] = SettingsFrame(self, self.db, self.config)

        self._show_frame("dashboard")

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        logo = ctk.CTkLabel(
            self.sidebar,
            text="Forum Parser",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        logo.grid(row=0, column=0, padx=20, pady=(20, 5))

        version = ctk.CTkLabel(
            self.sidebar,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        version.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.nav_buttons = {}
        buttons = [
            ("dashboard", "Dashboard", 2),
            ("scraper", "Scrape Forums", 3),
            ("leads", "Leads", 4),
            ("settings", "Settings", 5),
        ]

        for name, label, row in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda n=name: self._show_frame(n),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                height=40,
            )
            btn.grid(row=row, column=0, padx=10, pady=2, sticky="ew")
            self.nav_buttons[name] = btn

        # Footer credit
        ctk.CTkLabel(
            self.sidebar,
            text="by Howell Brady",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        ).grid(row=7, column=0, padx=20, pady=(0, 10), sticky="s")

    def _show_frame(self, name):
        for frame in self.frames.values():
            frame.grid_forget()

        self.frames[name].grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

        if hasattr(self.frames[name], "refresh"):
            self.frames[name].refresh()
