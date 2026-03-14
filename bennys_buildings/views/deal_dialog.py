"""Deal management dialogs — Save, Load, and Delete deals."""

import customtkinter as ctk
from typing import Optional, Callable

from views.widgets import COLORS, FONTS


class SaveDealDialog(ctk.CTkToplevel):
    """Dialog for naming and saving a deal."""

    def __init__(self, parent, current_name: str = "",
                 on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Save Deal")
        self.geometry("400x180")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()

        self._on_save = on_save
        self._result: Optional[str] = None

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 180) // 2
        self.geometry(f"+{x}+{y}")

        # Content
        label = ctk.CTkLabel(
            self, text="Deal Name:",
            font=FONTS["label"],
            text_color=COLORS["text_primary"],
        )
        label.pack(padx=20, pady=(20, 8), anchor="w")

        self.name_entry = ctk.CTkEntry(
            self,
            width=360,
            font=FONTS["input"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text="e.g., 4-Plex on Main St",
        )
        self.name_entry.pack(padx=20, pady=(0, 16))
        if current_name:
            self.name_entry.insert(0, current_name)
        self.name_entry.focus()
        self.name_entry.bind("<Return>", lambda e: self._save())

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
        name = self.name_entry.get().strip()
        if name and self._on_save:
            self._on_save(name)
        self.destroy()


class LoadDealDialog(ctk.CTkToplevel):
    """Dialog for browsing and loading saved deals."""

    def __init__(self, parent, deals: list[dict],
                 on_load: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Load Deal")
        self.geometry("500x450")
        self.resizable(False, True)
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()

        self._on_load = on_load
        self._on_delete = on_delete
        self._deals = deals

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 450) // 2
        self.geometry(f"+{x}+{y}")

        # Header
        header = ctk.CTkLabel(
            self, text="Saved Deals",
            font=FONTS["header"],
            text_color=COLORS["text_primary"],
        )
        header.pack(padx=20, pady=(16, 8), anchor="w")

        if not deals:
            empty = ctk.CTkLabel(
                self, text="No saved deals found.",
                font=FONTS["label"],
                text_color=COLORS["text_muted"],
            )
            empty.pack(expand=True)
            return

        # Scrollable list
        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=8,
            scrollbar_button_color=COLORS["border"],
        )
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=8)

        for deal in deals:
            self._create_deal_row(deal)

        # Close button
        ctk.CTkButton(
            self, text="Close", width=100,
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_alt"],
            command=self.destroy,
        ).pack(pady=(8, 16))

    def _create_deal_row(self, deal: dict):
        row = ctk.CTkFrame(
            self.list_frame,
            fg_color=COLORS["bg_card_alt"],
            corner_radius=8,
            height=60,
        )
        row.pack(fill="x", pady=4, padx=4)
        row.pack_propagate(False)

        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=12, pady=8)

        name_label = ctk.CTkLabel(
            info_frame,
            text=deal["name"],
            font=FONTS["subheader"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        name_label.pack(fill="x")

        detail_text = deal.get("summary", "")
        if deal.get("modified"):
            detail_text += f"  |  {deal['modified'][:10]}"

        detail_label = ctk.CTkLabel(
            info_frame,
            text=detail_text,
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        detail_label.pack(fill="x")

        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            btn_frame, text="Load", width=60,
            fg_color=COLORS["accent_teal"],
            hover_color="#00a88a",
            text_color="white",
            font=FONTS["small"],
            command=lambda n=deal["name"]: self._load_deal(n),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            btn_frame, text="Delete", width=60,
            fg_color=COLORS["negative"],
            hover_color="#d32f2f",
            text_color="white",
            font=FONTS["small"],
            command=lambda n=deal["name"]: self._delete_deal(n),
        ).pack(side="left")

    def _load_deal(self, name: str):
        if self._on_load:
            self._on_load(name)
        self.destroy()

    def _delete_deal(self, name: str):
        if self._on_delete:
            self._on_delete(name)
            # Refresh the dialog
            for widget in self.list_frame.winfo_children():
                widget.destroy()
            self._deals = [d for d in self._deals if d["name"] != name]
            for deal in self._deals:
                self._create_deal_row(deal)
