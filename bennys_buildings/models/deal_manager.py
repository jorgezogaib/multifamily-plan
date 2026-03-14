"""Deal manager — save, load, list, and delete property analysis deals.

Deals are stored as JSON files in %APPDATA%/BennysBuildings/deals/.
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from typing import Optional

from models.data_types import DealData, DealInputs


class DealManager:
    """Manages persistence of deal (property analysis) files."""

    def __init__(self, deals_dir: Path):
        self._deals_dir = deals_dir
        self._deals_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Convert deal name to a safe filename."""
        # Replace unsafe chars with underscores
        safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in name)
        return safe.strip().replace(" ", "_")[:100]

    def _deal_path(self, name: str) -> Path:
        """Get the file path for a deal by name."""
        filename = self._sanitize_filename(name)
        return self._deals_dir / f"{filename}.json"

    def save(self, deal: DealData) -> Path:
        """Save a deal to disk. Updates the modified timestamp.

        Returns the path the deal was saved to.
        """
        deal.modified = datetime.now().isoformat(timespec="seconds")
        path = self._deal_path(deal.name)

        data = {
            "name": deal.name,
            "created": deal.created,
            "modified": deal.modified,
            "inputs": asdict(deal.inputs),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return path

    def load(self, name: str) -> Optional[DealData]:
        """Load a deal by name. Returns None if not found."""
        path = self._deal_path(name)
        if not path.exists():
            return None
        return self._load_from_path(path)

    def _load_from_path(self, path: Path) -> Optional[DealData]:
        """Load a deal from a specific file path."""
        try:
            with open(path, "r") as f:
                data = json.load(f)

            inputs_data = data.get("inputs", {})
            # Handle None values for Optional fields
            for field_name in ("manual_total_price", "manual_rent"):
                if field_name in inputs_data and inputs_data[field_name] is None:
                    inputs_data[field_name] = None

            inputs = DealInputs(**{
                k: v for k, v in inputs_data.items()
                if k in DealInputs.__dataclass_fields__
            })

            return DealData(
                name=data.get("name", path.stem),
                created=data.get("created", ""),
                modified=data.get("modified", ""),
                inputs=inputs,
            )
        except (json.JSONDecodeError, TypeError, KeyError):
            return None

    def list_deals(self) -> list[dict]:
        """List all saved deals with summary info.

        Returns list of dicts: {name, created, modified, summary}.
        """
        deals = []
        for path in sorted(self._deals_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            deal = self._load_from_path(path)
            if deal:
                inp = deal.inputs
                summary = f"{inp.state}"
                if inp.num_units:
                    summary += f" | {inp.num_units} units"
                if inp.price_per_unit:
                    summary += f" | ${inp.price_per_unit:,.0f}/unit"

                deals.append({
                    "name": deal.name,
                    "created": deal.created,
                    "modified": deal.modified,
                    "summary": summary,
                })
        return deals

    def delete(self, name: str) -> bool:
        """Delete a deal by name. Returns True if deleted."""
        path = self._deal_path(name)
        if path.exists():
            path.unlink()
            return True
        return False

    def exists(self, name: str) -> bool:
        """Check if a deal with this name exists."""
        return self._deal_path(name).exists()
