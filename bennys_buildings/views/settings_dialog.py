"""Settings dialog — API key configuration."""

import customtkinter as ctk
from typing import Optional, Callable

from views.widgets import COLORS, FONTS


class SettingsDialog(ctk.CTkToplevel):
    """Dialog for configuring API keys."""

    def __init__(self, parent, hud_token: str = "", rapidapi_key: str = "",
                 api_ninjas_key: str = "", fred_api_key: str = "",
                 on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Settings — API Keys")
        self.geometry("550x540")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()

        self._on_save = on_save

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 550) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 540) // 2
        self.geometry(f"+{x}+{y}")

        # Scrollable frame for all the key entries
        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
        )
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # ── HUD Token ──
        self._add_key_section(
            scroll, "HUD API Bearer Token:",
            "Get one free at huduser.gov/hudapi/public/register",
            "Bearer token...",
        )
        self.hud_entry = self._last_entry
        if hud_token:
            self.hud_entry.insert(0, hud_token)

        # ── RapidAPI Key ──
        self._add_key_section(
            scroll, "RapidAPI Key (Zip Code API):",
            "Get one at rapidapi.com/mikicode/api/us-zip-code-information",
            "API key...",
        )
        self.rapid_entry = self._last_entry
        if rapidapi_key:
            self.rapid_entry.insert(0, rapidapi_key)

        # ── API Ninjas Key ──
        self._add_key_section(
            scroll, "API Ninjas Key (Tax Rate + Mortgage Rates):",
            "Free at api-ninjas.com — 50,000 calls/month",
            "API key...",
        )
        self.ninjas_entry = self._last_entry
        if api_ninjas_key:
            self.ninjas_entry.insert(0, api_ninjas_key)

        # ── FRED API Key ──
        self._add_key_section(
            scroll, "FRED API Key (Economic Data):",
            "Free at fred.stlouisfed.org — rent growth, rates, vacancy",
            "API key...",
        )
        self.fred_entry = self._last_entry
        if fred_api_key:
            self.fred_entry.insert(0, fred_api_key)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(8, 16))

        ctk.CTkButton(
            btn_frame, text="Cancel", width=100,
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_alt"],
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Save", width=100,
            fg_color=COLORS["accent_teal"],
            hover_color="#00a88a",
            text_color="white",
            command=self._save,
        ).pack(side="right")

    def _add_key_section(self, parent, title: str, hint: str,
                         placeholder: str):
        """Add a labeled API key entry section."""
        ctk.CTkLabel(
            parent, text=title,
            font=FONTS["label"],
            text_color=COLORS["text_primary"],
        ).pack(padx=20, pady=(12, 2), anchor="w")

        ctk.CTkLabel(
            parent, text=hint,
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        ).pack(padx=20, anchor="w")

        entry = ctk.CTkEntry(
            parent,
            width=510,
            font=FONTS["small"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text=placeholder,
        )
        entry.pack(padx=20, pady=(4, 4))
        self._last_entry = entry

    def _save(self):
        hud = self.hud_entry.get().strip()
        rapid = self.rapid_entry.get().strip()
        ninjas = self.ninjas_entry.get().strip()
        fred = self.fred_entry.get().strip()
        if self._on_save:
            self._on_save(hud, rapid, ninjas, fred)
        self.destroy()
