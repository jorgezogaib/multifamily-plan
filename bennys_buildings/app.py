"""Root application window — sets up the dark theme, menu bar, status bar,
and instantiates the dashboard and controller."""

import sys
from pathlib import Path
import customtkinter as ctk

from views.widgets import COLORS, FONTS
from views.dashboard import Dashboard
from views.deal_dialog import SaveDealDialog, LoadDealDialog
from views.settings_dialog import SettingsDialog
from services.config_service import ConfigService
from controllers.app_controller import AppController


class BennysApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # ── Window setup ───────────────────────────────────────────
        self.title("Benny's Buildings — Multifamily Investment Analyzer")
        self.geometry("1280x860")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_dark"])

        # Dark mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Determine base directory and data directory
        if getattr(sys, 'frozen', False):
            # Running as a bundled exe
            self._base_dir = Path(sys._MEIPASS)
        else:
            self._base_dir = Path(__file__).parent
        self._data_dir = self._base_dir / "data"

        # Set window icon
        icon_path = self._base_dir / "assets" / "icon.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))
            self.after(200, lambda: self.iconbitmap(str(icon_path)))

        # ── Services ───────────────────────────────────────────────
        self._config_service = ConfigService()

        # ── Title Bar with deal controls ───────────────────────────
        self._build_title_bar()

        # ── Dashboard ──────────────────────────────────────────────
        self._dashboard = Dashboard(self)
        self._dashboard.pack(fill="both", expand=True)

        # ── Status Bar ─────────────────────────────────────────────
        self._build_status_bar()

        # ── Controller ─────────────────────────────────────────────
        self._controller = AppController(
            self._dashboard, self._config_service, self._data_dir
        )
        self._controller.set_status_callback(self._update_status)
        self._controller.set_title_callback(self._update_deal_title)

        # ── Keyboard shortcuts ─────────────────────────────────────
        self.bind("<Control-s>", lambda e: self._save_deal())
        self.bind("<Control-S>", lambda e: self._save_deal_as())
        self.bind("<Control-o>", lambda e: self._load_deal())
        self.bind("<Control-n>", lambda e: self._new_deal())

        # ── Initialize ─────────────────────────────────────────────
        self.after(100, self._controller.initialize)

    # ── Title Bar ──────────────────────────────────────────────────

    def _build_title_bar(self):
        """Build the custom title bar with deal controls."""
        bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=50)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # App title
        title = ctk.CTkLabel(
            bar,
            text="  Benny's Buildings",
            font=FONTS["title"],
            text_color=COLORS["accent_teal"],
        )
        title.pack(side="left", padx=16)

        # Deal name
        self._deal_label = ctk.CTkLabel(
            bar,
            text="Untitled",
            font=FONTS["label"],
            text_color=COLORS["text_muted"],
        )
        self._deal_label.pack(side="left", padx=(20, 0))

        # Buttons (right side)
        btn_frame = ctk.CTkFrame(bar, fg_color="transparent")
        btn_frame.pack(side="right", padx=16)

        ctk.CTkButton(
            btn_frame, text="⚙ Settings", width=90,
            font=FONTS["small"],
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_alt"],
            command=self._open_settings,
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            btn_frame, text="📂 Load", width=80,
            font=FONTS["small"],
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_alt"],
            command=self._load_deal,
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            btn_frame, text="💾 Save As", width=90,
            font=FONTS["small"],
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_alt"],
            command=self._save_deal_as,
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            btn_frame, text="💾 Save", width=80,
            font=FONTS["small"],
            fg_color=COLORS["accent_teal"],
            hover_color="#00a88a",
            text_color="white",
            command=self._save_deal,
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            btn_frame, text="📄 New", width=80,
            font=FONTS["small"],
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_alt"],
            command=self._new_deal,
        ).pack(side="right", padx=4)

    # ── Status Bar ─────────────────────────────────────────────────

    def _build_status_bar(self):
        """Build the bottom status bar."""
        bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=30)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_label = ctk.CTkLabel(
            bar,
            text="Initializing...",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self._status_label.pack(side="left", padx=16, fill="x", expand=True)

    def _update_status(self, text: str):
        """Update status bar text."""
        self._status_label.configure(text=text)

    def _update_deal_title(self, name: str):
        """Update the deal name in the title bar."""
        self._deal_label.configure(text=f"Deal: {name}")

    # ── Deal actions ───────────────────────────────────────────────

    def _new_deal(self):
        self._controller.new_deal()

    def _save_deal(self):
        name = self._controller.current_deal_name
        if name:
            self._controller.save_deal(name)
        else:
            self._save_deal_as()

    def _save_deal_as(self):
        SaveDealDialog(
            self,
            current_name=self._controller.current_deal_name or "",
            on_save=self._controller.save_deal,
        )

    def _load_deal(self):
        deals = self._controller.list_deals()
        LoadDealDialog(
            self,
            deals=deals,
            on_load=self._controller.load_deal,
            on_delete=self._controller.delete_deal,
        )

    def _open_settings(self):
        cfg = self._config_service.config
        SettingsDialog(
            self,
            hud_token=cfg.hud_api_token,
            rapidapi_key=cfg.rapidapi_key,
            on_save=self._controller.update_api_keys,
        )
