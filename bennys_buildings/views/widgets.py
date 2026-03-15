"""Reusable custom widgets for the dashboard.

Provides styled labels and inputs with consistent formatting,
colors, and behaviors for the dark-themed UI.
"""

import customtkinter as ctk
from typing import Optional, Callable


# ── Color Palette ──────────────────────────────────────────────────
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "bg_card_alt": "#0f3460",
    "bg_input": "#1e2a4a",
    "border": "#2a3a5c",
    "text_primary": "#e0e0e0",
    "text_secondary": "#8892a8",
    "text_muted": "#5a6478",
    "accent_cyan": "#00d4ff",
    "accent_teal": "#00bfa6",
    "accent_orange": "#ff9f43",
    "positive": "#00e676",
    "negative": "#ff5252",
    "warning": "#ffab40",
    "header": "#7c8db5",
    "separator": "#2a3a5c",
}

FONTS = {
    "header": ("Segoe UI", 14, "bold"),
    "subheader": ("Segoe UI", 12, "bold"),
    "label": ("Segoe UI", 12),
    "value": ("Segoe UI Semibold", 13),
    "value_large": ("Segoe UI Semibold", 15),
    "input": ("Segoe UI", 12),
    "small": ("Segoe UI", 10),
    "title": ("Segoe UI", 18, "bold"),
}


class SectionFrame(ctk.CTkFrame):
    """A card-style section with a header label."""

    def __init__(self, parent, title: str, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )

        self.header = ctk.CTkLabel(
            self,
            text=title,
            font=FONTS["subheader"],
            text_color=COLORS["header"],
            anchor="w",
        )
        self.header.pack(fill="x", padx=16, pady=(12, 4))

        self.separator = ctk.CTkFrame(
            self, height=1, fg_color=COLORS["separator"]
        )
        self.separator.pack(fill="x", padx=16, pady=(0, 8))

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 12))


class MetricRow(ctk.CTkFrame):
    """A single row displaying a label and a computed value."""

    def __init__(self, parent, label_text: str, initial_value: str = "$0",
                 value_color: Optional[str] = None, large: bool = False,
                 show_rate: bool = False, **kwargs):
        super().__init__(parent, fg_color="transparent", height=28, **kwargs)
        self.pack_propagate(False)

        self._value_color = value_color or COLORS["accent_cyan"]
        self._large = large

        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self.label.pack(side="left", fill="x", expand=True)

        if show_rate:
            self.rate_label = ctk.CTkLabel(
                self,
                text="",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
                anchor="e",
                width=50,
            )
            self.rate_label.pack(side="right", padx=(4, 0))

        self.value_label = ctk.CTkLabel(
            self,
            text=initial_value,
            font=FONTS["value_large"] if large else FONTS["value"],
            text_color=self._value_color,
            anchor="e",
            width=120 if large else 100,
        )
        self.value_label.pack(side="right")

    def set_value(self, text: str, color: Optional[str] = None):
        """Update the displayed value."""
        self.value_label.configure(text=text)
        if color:
            self.value_label.configure(text_color=color)

    def set_rate(self, text: str):
        """Update the rate label (if show_rate was True)."""
        if hasattr(self, "rate_label"):
            self.rate_label.configure(text=text)


class SeparatorRow(ctk.CTkFrame):
    """A thin horizontal separator line."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", height=12, **kwargs)
        self.pack_propagate(False)
        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["separator"])
        sep.pack(fill="x", pady=5)


class InputField(ctk.CTkFrame):
    """A labeled input field for the input panel."""

    def __init__(self, parent, label_text: str, width: int = 100,
                 placeholder: str = "", on_change: Optional[Callable] = None,
                 suffix: str = "", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
            anchor="w",
            width=100,
        )
        self.label.pack(side="left", padx=(0, 8))

        self.entry = ctk.CTkEntry(
            self,
            width=width,
            font=FONTS["input"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text=placeholder,
            corner_radius=6,
        )
        self.entry.pack(side="left", fill="x", expand=True)

        if suffix:
            self.suffix_label = ctk.CTkLabel(
                self,
                text=suffix,
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
                width=20,
            )
            self.suffix_label.pack(side="left", padx=(4, 0))

        self._on_change = on_change
        if on_change:
            self.entry.bind("<FocusOut>", lambda e: on_change())
            self.entry.bind("<Return>", lambda e: on_change())

    def get(self) -> str:
        return self.entry.get()

    def set(self, value: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def set_state(self, state: str):
        self.entry.configure(state=state)


class DropdownField(ctk.CTkFrame):
    """A labeled dropdown (combobox) for the input panel."""

    def __init__(self, parent, label_text: str, values: list[str],
                 on_change: Optional[Callable] = None,
                 width: int = 180, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
            anchor="w",
            width=100,
        )
        self.label.pack(side="left", padx=(0, 8))

        self.combobox = ctk.CTkComboBox(
            self,
            values=values,
            width=width,
            font=FONTS["input"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["accent_teal"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_alt"],
            text_color=COLORS["text_primary"],
            dropdown_text_color=COLORS["text_primary"],
            corner_radius=6,
            state="readonly",
        )
        self.combobox.pack(side="left", fill="x", expand=True)

        if on_change:
            self.combobox.configure(command=lambda val: on_change(val))

    def get(self) -> str:
        return self.combobox.get()

    def set(self, value: str):
        self.combobox.set(value)

    def update_values(self, values: list[str]):
        self.combobox.configure(values=values)

    def set_state(self, state: str):
        self.combobox.configure(state=state)


class RadioField(ctk.CTkFrame):
    """A labeled group of radio buttons (horizontal or vertical)."""

    def __init__(self, parent, label_text: str, values: list[str],
                 default: str = "", on_change: Optional[Callable] = None,
                 orientation: str = "horizontal", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._orientation = orientation
        self._on_change = on_change

        if label_text:
            self.label = ctk.CTkLabel(
                self,
                text=label_text,
                font=FONTS["label"],
                text_color=COLORS["text_secondary"],
                anchor="w",
                width=100,
            )
            if orientation == "vertical":
                self.label.pack(anchor="w", pady=(0, 4))
            else:
                self.label.pack(side="left", padx=(0, 8))

        self._var = ctk.StringVar(value=default or (values[0] if values else ""))
        self._buttons: list[ctk.CTkRadioButton] = []

        self._btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        if orientation == "vertical":
            self._btn_frame.pack(fill="x", padx=(16, 0))
        else:
            self._btn_frame.pack(side="left", fill="x", expand=True)

        self._build_buttons(values)

    def _build_buttons(self, values: list[str]):
        for btn in self._buttons:
            btn.destroy()
        self._buttons.clear()

        on_change = self._on_change
        for val in values:
            rb = ctk.CTkRadioButton(
                self._btn_frame,
                text=val,
                variable=self._var,
                value=val,
                font=FONTS["small"],
                text_color=COLORS["text_primary"],
                fg_color=COLORS["accent_teal"],
                border_color=COLORS["border"],
                hover_color=COLORS["accent_teal"],
                command=lambda: on_change(self._var.get()) if on_change else None,
            )
            if self._orientation == "vertical":
                rb.pack(anchor="w", pady=2)
            else:
                rb.pack(side="left", padx=(0, 10))
            self._buttons.append(rb)

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str):
        self._var.set(value)

    def update_values(self, values: list[str]):
        """Rebuild radio buttons with new values."""
        self._build_buttons(values)


class DisplayField(ctk.CTkFrame):
    """A read-only labeled display (for FMR rent, utility allowance, etc.)."""

    def __init__(self, parent, label_text: str, initial_value: str = "",
                 value_color: Optional[str] = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
            anchor="w",
            width=100,
        )
        self.label.pack(side="left", padx=(0, 8))

        self.value_label = ctk.CTkLabel(
            self,
            text=initial_value,
            font=FONTS["value"],
            text_color=value_color or COLORS["accent_orange"],
            anchor="w",
        )
        self.value_label.pack(side="left", fill="x", expand=True)

    def set_value(self, text: str, color: Optional[str] = None):
        self.value_label.configure(text=text)
        if color:
            self.value_label.configure(text_color=color)
