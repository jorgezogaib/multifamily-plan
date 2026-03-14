"""Settings dialog — API key configuration."""

import customtkinter as ctk
from typing import Optional, Callable

from views.widgets import COLORS, FONTS


class SettingsDialog(ctk.CTkToplevel):
    """Dialog for configuring API keys."""

    def __init__(self, parent, hud_token: str = "", rapidapi_key: str = "",
                 on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Settings — API Keys")
        self.geometry("550x320")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()

        self._on_save = on_save

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 550) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 320) // 2
        self.geometry(f"+{x}+{y}")

        # HUD Token
        ctk.CTkLabel(
            self, text="HUD API Bearer Token:",
            font=FONTS["label"],
            text_color=COLORS["text_primary"],
        ).pack(padx=20, pady=(20, 4), anchor="w")

        ctk.CTkLabel(
            self,
            text="Get one free at huduser.gov/hudapi/public/register",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        ).pack(padx=20, anchor="w")

        self.hud_entry = ctk.CTkEntry(
            self,
            width=510,
            font=FONTS["small"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text="Bearer token...",
        )
        self.hud_entry.pack(padx=20, pady=(4, 16))
        if hud_token:
            self.hud_entry.insert(0, hud_token)

        # RapidAPI Key
        ctk.CTkLabel(
            self, text="RapidAPI Key (Zip Code API):",
            font=FONTS["label"],
            text_color=COLORS["text_primary"],
        ).pack(padx=20, pady=(0, 4), anchor="w")

        ctk.CTkLabel(
            self,
            text="Get one at rapidapi.com/mikicode/api/us-zip-code-information",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        ).pack(padx=20, anchor="w")

        self.rapid_entry = ctk.CTkEntry(
            self,
            width=510,
            font=FONTS["small"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text="API key...",
        )
        self.rapid_entry.pack(padx=20, pady=(4, 20))
        if rapidapi_key:
            self.rapid_entry.insert(0, rapidapi_key)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

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

    def _save(self):
        hud = self.hud_entry.get().strip()
        rapid = self.rapid_entry.get().strip()
        if self._on_save:
            self._on_save(hud, rapid)
        self.destroy()
