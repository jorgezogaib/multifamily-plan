"""Application controller — wires model, views, and services together.

Handles:
    - Cascading dropdown logic (State → Counties → FMR)
    - Input parsing and model updates
    - Threaded API calls with UI callbacks
    - Deal save/load orchestration
"""

import json
import threading
from pathlib import Path
from typing import Optional

from models.property_model import PropertyModel
from models.data_types import DealInputs, DealData, FMRData
from models.deal_manager import DealManager
from services.api_service import HUDApiService, RapidApiService, APIError
from services.config_service import ConfigService
from views.dashboard import Dashboard
from utils.formatting import parse_float, parse_int


class AppController:
    """Orchestrates the application logic."""

    def __init__(self, dashboard: Dashboard, config_service: ConfigService,
                 data_dir: Path):
        self._dashboard = dashboard
        self._config = config_service
        self._data_dir = data_dir

        # Initialize model
        self._model = PropertyModel(data_dir)
        self._model.add_listener(self._on_model_updated)

        # Initialize deal manager
        self._deal_manager = DealManager(config_service.deals_dir)
        self._current_deal_name: Optional[str] = None

        # Load options
        self._options = self._load_options()

        # Initialize API services
        cfg = config_service.config
        self._hud_api = HUDApiService(cfg.hud_api_token)
        self._rapid_api = RapidApiService(cfg.rapidapi_key)

        # State tracking
        self._states_loaded = False
        self._county_fips_map: dict[str, str] = {}  # county_name -> fips_code
        self._pending_county: Optional[str] = None  # Set during deal load
        self._zip_driven: bool = False  # True when zip is driving state/county

        # Wire up the input panel callbacks
        ip = dashboard.input_panel
        ip.on_state_changed = self._on_state_changed
        ip.on_county_changed = self._on_county_changed
        ip.on_input_changed = self._on_input_changed
        ip.on_zip_changed = self._on_zip_changed
        ip.on_ua_toggled = self._on_ua_toggled

        # Populate dropdowns from options
        ip.populate_dropdowns(self._options)

        # Set defaults
        self._set_defaults()

    def _load_options(self) -> dict:
        """Load dropdown options from JSON file."""
        options_path = self._data_dir / "options.json"
        if options_path.exists():
            with open(options_path, "r") as f:
                return json.load(f)
        return {}

    def _set_defaults(self):
        """Set initial default values in the input panel."""
        cfg = self._config.config
        ip = self._dashboard.input_panel

        # Set default dropdown values
        ip.has_gas_dd.set("No")
        ip.use_utility_dd.set("No")

        # Set default options selections
        opts = self._options
        if opts.get("property_types"):
            ip.property_type_dd.set(opts["property_types"][1])  # Duplex
        if opts.get("bedroom_options"):
            ip.bedrooms_dd.set(opts["bedroom_options"][2]["display"])  # 2 BR
        if opts.get("heating_types"):
            ip.heating_dd.set(opts["heating_types"][0])
        if opts.get("cooking_types"):
            ip.cooking_dd.set(opts["cooking_types"][0])
        if opts.get("water_heating_types"):
            ip.water_heating_dd.set(opts["water_heating_types"][0])

        # Set default rates
        ip.num_units.set("4")
        ip.insurance_rate.set(f"{cfg.default_insurance_rate * 100:g}")
        ip.tax_rate.set(f"{cfg.default_tax_rate * 100:g}")
        ip.loan_term.set(str(cfg.default_loan_term))
        ip.interest_rate.set(f"{cfg.default_interest_rate * 100:g}")
        ip.down_pct.set(f"{cfg.default_down_payment_rate * 100:g}")
        ip.closing_pct.set(f"{cfg.default_closing_cost_rate * 100:g}")
        ip.reserve_months.set(str(cfg.default_reserve_months))
        ip.vacancy_rate.set(f"{cfg.default_vacancy_rate * 100:g}")
        ip.ltl_rate.set(f"{cfg.default_loss_to_lease_rate * 100:g}")
        ip.maintenance_rate.set(f"{cfg.default_maintenance_rate * 100:g}")
        ip.management_rate.set(f"{cfg.default_management_rate * 100:g}")
        ip.improvements_rate.set(
            f"{cfg.default_annual_improvements_rate * 100:g}"
        )

        # Trigger initial calculation
        self._on_input_changed()

    # ── Status bar updates ─────────────────────────────────────────

    def _set_status(self, text: str):
        """Update the status bar."""
        if hasattr(self, '_status_callback') and self._status_callback:
            self._status_callback(text)

    def set_status_callback(self, callback):
        """Set the callback for status bar updates."""
        self._status_callback = callback

    def set_title_callback(self, callback):
        """Set the callback for window title updates."""
        self._title_callback = callback

    def _update_title(self):
        """Update window title with current deal name."""
        if hasattr(self, '_title_callback') and self._title_callback:
            name = self._current_deal_name or "Untitled"
            self._title_callback(name)

    # ── Input handling ─────────────────────────────────────────────

    def _collect_inputs(self) -> DealInputs:
        """Parse all input panel values into a DealInputs object."""
        raw = self._dashboard.input_panel.get_all_inputs()

        return DealInputs(
            state=raw["state"],
            county=raw["county"],
            property_type=raw["property_type"],
            num_bedrooms=raw["num_bedrooms"],
            num_units=parse_int(raw["num_units"], 4),
            price_per_unit=parse_float(raw["price_per_unit"], 0),
            manual_total_price=(
                parse_float(raw["manual_total_price"])
                if raw["manual_total_price"].strip() else None
            ),
            zip_code=raw["zip_code"],
            insurance_rate=parse_float(raw["insurance_rate"], 1.5) / 100,
            tax_rate=parse_float(raw["tax_rate"], 1.0) / 100,
            loan_term=parse_int(raw["loan_term"], 30),
            interest_rate=parse_float(raw["interest_rate"], 6.5) / 100,
            down_payment_rate=parse_float(raw["down_payment_rate"], 25) / 100,
            closing_cost_rate=parse_float(raw["closing_cost_rate"], 2) / 100,
            reserve_months=parse_int(raw["reserve_months"], 6),
            cost_to_rent_ready=parse_float(raw["cost_to_rent_ready"], 0),
            manual_rent=(
                parse_float(raw["manual_rent"])
                if raw["manual_rent"].strip() else None
            ),
            vacancy_rate=parse_float(raw["vacancy_rate"], 5) / 100,
            loss_to_lease_rate=parse_float(raw["loss_to_lease_rate"], 0) / 100,
            maintenance_rate=parse_float(raw["maintenance_rate"], 15) / 100,
            management_rate=parse_float(raw["management_rate"], 10) / 100,
            annual_improvements_rate=(
                parse_float(raw["annual_improvements_rate"], 15) / 100
            ),
            has_gas=raw["has_gas"],
            heating=raw["heating"],
            cooking=raw["cooking"],
            water_heating=raw["water_heating"],
            use_utility_allowance=raw["use_utility_allowance"],
        )

    def _on_input_changed(self):
        """Called when any non-dropdown input changes."""
        inputs = self._collect_inputs()
        self._model._inputs = inputs
        self._model.recalculate()

    def _on_model_updated(self):
        """Called after the model recalculates."""
        self._dashboard.refresh_from_model(self._model)

    def _on_ua_toggled(self, value: str):
        """Show/hide the Utility Breakdown panel when Use UA changes."""
        self._dashboard.show_utility_panel(value == "Yes")

    # ── State / County / FMR cascading ─────────────────────────────

    def initialize(self):
        """Load states list on startup."""
        self._set_status("Loading states...")
        thread = threading.Thread(target=self._fetch_states, daemon=True)
        thread.start()

    def _fetch_states(self):
        """Fetch states list from HUD API (background thread)."""
        try:
            states = self._hud_api.list_states()
            state_names = [s.name for s in states]
            self._dashboard.after(0, self._on_states_loaded, state_names)
        except APIError as e:
            self._dashboard.after(
                0, self._set_status, f"Failed to load states: {e}"
            )

    def _on_states_loaded(self, state_names: list[str]):
        """Update UI with loaded states."""
        self._dashboard.input_panel.set_state_values(state_names)
        self._states_loaded = True
        self._set_status("Ready")

    def _on_state_changed(self, state_name: str):
        """Handle state dropdown change — fetch counties."""
        # Manual state selection clears zip code
        if not self._zip_driven:
            self._dashboard.input_panel.zip_code.set("")
        self._set_status(f"Loading counties for {state_name}...")

        # Get state code
        thread = threading.Thread(
            target=self._fetch_counties,
            args=(state_name,),
            daemon=True,
        )
        thread.start()

    def _fetch_counties(self, state_name: str):
        """Fetch counties for a state (background thread)."""
        try:
            state_code = self._hud_api.get_state_code(state_name)
            if not state_code:
                self._dashboard.after(
                    0, self._set_status, f"Unknown state: {state_name}"
                )
                return

            self._model.state_code = state_code
            counties = self._hud_api.list_counties(state_code)
            county_names = [c.county_name for c in counties]
            fips_map = {c.county_name: c.fips_code for c in counties}

            self._dashboard.after(
                0, self._on_counties_loaded, county_names, fips_map
            )
        except APIError as e:
            self._dashboard.after(
                0, self._set_status, f"Failed to load counties: {e}"
            )

    def _on_counties_loaded(self, county_names: list[str],
                            fips_map: dict[str, str]):
        """Update UI with loaded counties."""
        self._county_fips_map = fips_map
        self._dashboard.input_panel.set_county_values(county_names)

        # If loading a deal or zip-driven, auto-select the county
        if self._pending_county:
            pending = self._pending_county
            self._pending_county = None
            # Try exact match first, then fuzzy
            if pending in county_names:
                self._dashboard.input_panel.county_dd.set(pending)
                self._on_county_changed(pending)
                return
            matched = self._match_county_name(pending)
            if matched:
                self._dashboard.input_panel.county_dd.set(matched)
                self._on_county_changed(matched)
                return
            self._zip_driven = False

        if county_names:
            self._dashboard.input_panel.county_dd.set("")
        self._set_status("Select a county")
        self._on_input_changed()

    def _on_county_changed(self, county_name: str):
        """Handle county dropdown change — fetch FMR data."""
        # Manual county selection clears zip code
        if not self._zip_driven:
            self._dashboard.input_panel.zip_code.set("")
        self._zip_driven = False  # Reset after cascade completes
        fips_code = self._county_fips_map.get(county_name, "")
        if not fips_code:
            return

        self._set_status(f"Loading FMR data for {county_name}...")
        thread = threading.Thread(
            target=self._fetch_fmr,
            args=(fips_code, county_name),
            daemon=True,
        )
        thread.start()

    def _fetch_fmr(self, fips_code: str, county_name: str):
        """Fetch FMR data for a county (background thread)."""
        try:
            fmr = self._hud_api.get_fmr(fips_code)
            self._dashboard.after(
                0, self._on_fmr_loaded, fmr, county_name
            )
        except APIError as e:
            self._dashboard.after(
                0, self._set_status, f"Failed to load FMR: {e}"
            )

    def _on_fmr_loaded(self, fmr: FMRData, county_name: str):
        """Update model and UI with FMR data."""
        self._model.fmr_data = fmr  # This triggers recalculate

        # Update the FMR rent display
        fmr_key = self._model._get_fmr_key()
        rent = fmr.get_rent_by_key(fmr_key)
        self._dashboard.input_panel.set_fmr_rent(rent, fmr.year)

        self._set_status(
            f"{county_name}  |  FMR: ${rent:,.0f}/mo  |  "
            f"{self._model.inputs.num_bedrooms}  |  {fmr.year} data"
        )

    # ── Zip Code ───────────────────────────────────────────────────

    def _on_zip_changed(self):
        """Handle zip code entry — fetch zip info."""
        zip_code = self._dashboard.input_panel.zip_code.get().strip()
        if len(zip_code) == 5 and zip_code.isdigit():
            thread = threading.Thread(
                target=self._fetch_zip_info,
                args=(zip_code,),
                daemon=True,
            )
            thread.start()
        self._on_input_changed()

    def _fetch_zip_info(self, zip_code: str):
        """Fetch zip code info (background thread)."""
        try:
            info = self._rapid_api.get_zip_info(zip_code)
            self._dashboard.after(
                0, self._on_zip_loaded, info
            )
        except APIError:
            pass  # Zip lookup is informational, don't show errors

    def _on_zip_loaded(self, info):
        """Auto-populate state/county from zip lookup, then update status."""
        if not info.state:
            return

        self._set_status(
            f"Zip: {info.zip_code} — {info.city}, {info.state} "
            f"({info.county})"
        )

        ip = self._dashboard.input_panel
        current_state = ip.state_dd.get()

        # Match state name from zip to HUD state list
        target_state = self._find_state_name(info.state)
        if not target_state:
            return

        # Set flag so state/county changes don't clear the zip
        self._zip_driven = True

        # Set pending county for auto-selection after counties load
        if info.county:
            self._pending_county = info.county

        if current_state != target_state:
            # Different state — select it (triggers county cascade)
            ip.state_dd.set(target_state)
            self._on_state_changed(target_state)
        elif info.county:
            # Same state, just need to match county
            self._auto_select_county(info.county)

    def _find_state_name(self, zip_state: str) -> str:
        """Match a state name from zip lookup to the HUD states list.

        The RapidAPI returns the 2-letter state code (e.g. 'LA'),
        so we match on both code and full name.
        """
        if not self._hud_api._states_cache:
            return ""
        zs = zip_state.strip().upper()
        for s in self._hud_api._states_cache:
            if s.code.upper() == zs or s.name.lower() == zs.lower():
                return s.name
        return ""

    def _auto_select_county(self, county_name: str):
        """Find and select a county by name (fuzzy match)."""
        ip = self._dashboard.input_panel
        matched = self._match_county_name(county_name)
        if matched:
            ip.county_dd.set(matched)
            self._on_county_changed(matched)
        else:
            self._zip_driven = False

    def _match_county_name(self, zip_county: str) -> str:
        """Match a county name from zip lookup to the loaded county list."""
        if not self._county_fips_map:
            return ""
        zip_lower = zip_county.lower().replace(" county", "").strip()
        for county_name in self._county_fips_map:
            hud_lower = county_name.lower().replace(" county", "").strip()
            if hud_lower == zip_lower or zip_lower in hud_lower:
                return county_name
        return ""

    # ── Deal management ────────────────────────────────────────────

    def new_deal(self):
        """Reset to a fresh deal with defaults."""
        self._current_deal_name = None
        self._model.fmr_data = FMRData()
        self._set_defaults()
        self._update_title()

    def save_deal(self, name: str):
        """Save the current inputs as a deal."""
        inputs = self._collect_inputs()
        deal = DealData(name=name, inputs=inputs)
        self._deal_manager.save(deal)
        self._current_deal_name = name
        self._update_title()
        self._set_status(f"Saved: {name}")

    def load_deal(self, name: str):
        """Load a deal by name and populate the UI."""
        deal = self._deal_manager.load(name)
        if deal:
            self._current_deal_name = deal.name

            # Populate inputs
            self._dashboard.input_panel.set_all_inputs(deal.inputs)

            # Set model state
            self._model._inputs = deal.inputs
            self._model.recalculate()

            # Trigger state/county cascade if state is set
            if deal.inputs.state:
                self._on_state_changed(deal.inputs.state)
                # After counties load, we need to set the county and fetch FMR
                # This is handled by scheduling after county load
                self._pending_county = deal.inputs.county

            self._update_title()
            self._set_status(f"Loaded: {name}")

    def list_deals(self) -> list[dict]:
        """Get list of saved deals."""
        return self._deal_manager.list_deals()

    def delete_deal(self, name: str):
        """Delete a saved deal."""
        self._deal_manager.delete(name)
        if self._current_deal_name == name:
            self._current_deal_name = None
            self._update_title()

    @property
    def current_deal_name(self) -> Optional[str]:
        return self._current_deal_name

    # ── API key management ─────────────────────────────────────────

    def update_api_keys(self, hud_token: str, rapidapi_key: str):
        """Update API keys and reinitialize services."""
        self._config.update_api_keys(hud_token, rapidapi_key)
        self._hud_api.update_token(hud_token)
        self._rapid_api.update_key(rapidapi_key)
        self._set_status("API keys updated")
        # Re-fetch states with new token
        self.initialize()
