"""Configuration service — manages API keys and app settings.

Stores configuration in %APPDATA%/BennysBuildings/config.json.
Pre-populates with API keys extracted from the Excel workbook on first run.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class AppConfig:
    """Application configuration."""
    hud_api_token: str = ""
    rapidapi_key: str = ""
    api_ninjas_key: str = ""
    fred_api_key: str = ""
    # Default rates (used when creating a new deal)
    default_closing_cost_rate: float = 0.02
    default_down_payment_rate: float = 0.25
    default_reserve_months: int = 6
    default_loan_term: int = 30
    default_interest_rate: float = 0.065
    default_vacancy_rate: float = 0.05
    default_loss_to_lease_rate: float = 0.0
    default_maintenance_rate: float = 0.15
    default_management_rate: float = 0.10
    default_annual_improvements_rate: float = 0.15
    default_insurance_rate: float = 0.015
    default_tax_rate: float = 0.01


# Pre-extracted from the Excel workbook's Power Query connections
_DEFAULT_HUD_TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9."
    "eyJhdWQiOiI2IiwianRpIjoiMTAwMDZhN2VmYjJmZTJjMmJlNzM4NzgxMjUwMDhmZTMx"
    "Y2NjZTIzOWZjYWRmYjAwMjE3NTI3MmRkOWMzZmIxNzE1ODg0Y2FkMDUzNzM4NzQiLCJp"
    "YXQiOjE3MDk4NzAyOTguMjc0Mjk0LCJuYmYiOjE3MDk4NzAyOTguMjc0Mjk2LCJleHAi"
    "OjIwMjU0MDMwOTguMjcwMTk0LCJzdWIiOiI2Njk3MCIsInNjb3BlcyI6W119."
    "CBmGAXUkZnlq9EJqYUMxLEB6SuVgNrbJFtpK7JxsCaMYijaRc-KOZ-PeunHvfdoukykt"
    "OLjnCHPj0qdL0hSWQA"
)
_DEFAULT_RAPIDAPI_KEY = "d5cfe8f20cmsh61e1f85223500f1p1382ddjsn3297c6508759"


class ConfigService:
    """Manages application configuration persistence."""

    def __init__(self):
        self._app_dir = self._get_app_dir()
        self._config_path = self._app_dir / "config.json"
        self._deals_dir = self._app_dir / "deals"
        self._config: AppConfig = AppConfig()
        self._ensure_directories()
        self._load()

    def _get_app_dir(self) -> Path:
        """Get the application data directory."""
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "BennysBuildings"
        # Fallback for non-Windows
        return Path.home() / ".bennys_buildings"

    def _ensure_directories(self):
        """Create app data directories if they don't exist."""
        self._app_dir.mkdir(parents=True, exist_ok=True)
        self._deals_dir.mkdir(parents=True, exist_ok=True)

    def _load(self):
        """Load config from disk, or create with defaults."""
        if self._config_path.exists():
            try:
                with open(self._config_path, "r") as f:
                    data = json.load(f)
                self._config = AppConfig(**{
                    k: v for k, v in data.items()
                    if k in AppConfig.__dataclass_fields__
                })
            except (json.JSONDecodeError, TypeError):
                self._config = self._create_defaults()
                self.save()
        else:
            self._config = self._create_defaults()
            self.save()

    def _create_defaults(self) -> AppConfig:
        """Create config with pre-extracted API keys."""
        return AppConfig(
            hud_api_token=_DEFAULT_HUD_TOKEN,
            rapidapi_key=_DEFAULT_RAPIDAPI_KEY,
        )

    def save(self):
        """Persist current config to disk."""
        with open(self._config_path, "w") as f:
            json.dump(asdict(self._config), f, indent=2)

    @property
    def config(self) -> AppConfig:
        return self._config

    @property
    def deals_dir(self) -> Path:
        return self._deals_dir

    @property
    def app_dir(self) -> Path:
        return self._app_dir

    def update_api_keys(self, hud_token: str, rapidapi_key: str,
                        api_ninjas_key: str = "",
                        fred_api_key: str = ""):
        """Update API keys and save."""
        self._config.hud_api_token = hud_token
        self._config.rapidapi_key = rapidapi_key
        self._config.api_ninjas_key = api_ninjas_key
        self._config.fred_api_key = fred_api_key
        self.save()

    def has_api_keys(self) -> bool:
        """Check if API keys are configured."""
        return bool(self._config.hud_api_token and self._config.rapidapi_key)
