# Benny's Buildings — AI Development Context

Multifamily real estate investment analyzer. Desktop app (CustomTkinter, dark theme) that replicates an Excel workbook's 24 financial formulas with live HUD API integration for Fair Market Rent data, deal save/load, and utility allowance calculations.

## Quick Start

```bash
cd "C:\Z Multifamily Plan\bennys_buildings"
pip install -r requirements.txt        # customtkinter, requests
python main.py                          # launch app
python tests/test_property_model.py     # run formula tests (18 tests)
python tests/test_financial.py          # run PMT function tests (4 tests)
```

## Architecture — MVC

```
User Input ──→ InputPanel callbacks ──→ AppController
                                            │
                            ┌───────────────┼───────────────┐
                            ▼               ▼               ▼
                     API Services    PropertyModel     DealManager
                     (threaded)      (recalculate)     (JSON files)
                            │               │
                            ▼               ▼
                     dashboard.after()  notify listeners
                            │               │
                            └───────┬───────┘
                                    ▼
                            Dashboard.refresh_from_model()
                                    │
                                    ▼
                            ProFormaPanel.update_from_model()
```

**Data flow:** Input change → Controller parses values into `DealInputs` → sets `model._inputs` → calls `model.recalculate()` → model notifies listeners → `dashboard.refresh_from_model(model)` → `ProFormaPanel.update_from_model(model)` updates all labels.

## File Map

```
main.py                          Entry point. Adds project root to sys.path, creates BennysApp
app.py                           Root CTk window. Title bar, status bar, keyboard shortcuts, icon loading, menu actions
models/
  data_types.py                  Dataclasses: State, County, FMRData, ZipInfo, UtilityAllowanceEntry,
                                   DealInputs (all user inputs), DealData (saved deal wrapper)
  property_model.py              PropertyModel (24 formulas, recalculate()), UtilityAllowanceCalculator
  deal_manager.py                DealManager — save/load/list/delete JSON deal files
views/
  widgets.py                     COLORS dict (17 colors), FONTS dict (8 styles), SectionFrame,
                                   CollapsibleSection, MetricRow, SeparatorRow, InputField,
                                   DropdownField, SearchableDropdown, RadioField, DisplayField
  dashboard.py                   2-column grid: left (ProFormaPanel, weight=5),
                                   right (InputPanel, weight=2)
  proforma_panel.py              3-column auto-scaling financial statement (CTkScrollableFrame).
                                   Uniform scaling engine for fonts, padding, heights, widths.
                                   Col1: Investment Summary + Financing + Capital Requirements.
                                   Col2: Operating Statement + NOI. Col3: Metrics + Cash Flow
  input_panel.py                 Accordion layout with 3 CollapsibleSections (Property, Financials,
                                   Utilities). Single-open accordion behavior. 8 dropdowns + 14 fields
  deal_dialog.py                 SaveDealDialog (name entry) + LoadDealDialog (scrollable list)
  settings_dialog.py             API key entry form (HUD token + RapidAPI key)
services/
  api_service.py                 HUDApiService (3 endpoints), RapidApiService (1 endpoint), APIError class
  config_service.py              AppConfig dataclass, ConfigService — persists to %APPDATA%/BennysBuildings/
controllers/
  app_controller.py              Orchestrator: wires callbacks, parses inputs, manages cascading
                                   State→County→FMR flow, threaded API calls, deal save/load
utils/
  financial.py                   pmt() — Excel PMT equivalent (3 lines of math)
  formatting.py                  format_currency(), format_percent(), format_ratio(), parse_float(), parse_int()
data/
  options.json                   Dropdown option lists: cooking/heating/water_heating types, bedrooms, property types
  utility_allowances/la.json     Louisiana utility allowance lookup table (39 rows × 12 columns)
assets/
  icon.ico                       Multi-size app icon (16–256px). Loaded in app.py at startup
  icon.png                       Source PNG used to generate the ICO
tests/
  test_property_model.py         18 formula tests against known Excel workbook values
  test_financial.py              4 PMT function tests
```

## Conventions

### Imports
All imports are **absolute from project root** (e.g., `from models.property_model import PropertyModel`). `main.py` inserts the project root into `sys.path` at startup. No relative imports used.

### View ↔ Controller Communication
Views expose **callback attributes** that the controller sets during initialization:

```python
# In InputPanel.__init__():
self.on_state_changed: Optional[Callable] = None
self.on_county_changed: Optional[Callable] = None
self.on_input_changed: Optional[Callable] = None
self.on_zip_changed: Optional[Callable] = None

# In AppController.__init__():
ip = dashboard.input_panel
ip.on_state_changed = self._on_state_changed
ip.on_county_changed = self._on_county_changed
ip.on_input_changed = self._on_input_changed
ip.on_zip_changed = self._on_zip_changed
```

Each input widget triggers these via helper methods (`_trigger_input_change`, etc.) that null-check before calling.

### Threading (API Calls)
All API calls run on **daemon threads**. Results are marshalled back to the UI thread via `self._dashboard.after(0, callback, *args)`:

```python
def _on_state_changed(self, state_name):
    thread = threading.Thread(target=self._fetch_counties, args=(state_name,), daemon=True)
    thread.start()

def _fetch_counties(self, state_name):      # runs on background thread
    counties = self._hud_api.list_counties(state_code)
    self._dashboard.after(0, self._on_counties_loaded, county_names, fips_map)  # UI thread
```

### Error Handling
- `APIError` custom exception in `services/api_service.py`
- Caught in controller, displayed in status bar: `self._set_status(f"Failed to load: {e}")`
- Zip code lookup silently fails (informational only)
- JSON parse errors in config/deals return defaults or None

### Colors & Fonts
Centralized in `views/widgets.py`. Always import from there:

```python
from views.widgets import COLORS, FONTS

# Key colors:
COLORS["bg_dark"]       # "#1a1a2e" — main background
COLORS["bg_card"]       # "#16213e" — card/section background
COLORS["accent_cyan"]   # "#00d4ff" — computed values
COLORS["accent_teal"]   # "#00bfa6" — primary actions, positive
COLORS["accent_orange"] # "#ff9f43" — display values, ratios
COLORS["positive"]      # "#00e676" — positive cashflow
COLORS["negative"]      # "#ff5252" — negative values, expenses
COLORS["warning"]       # "#ffab40" — caution (DSCR near 1.0)
```

Fonts are all **Segoe UI** at sizes 11 (small), 13 (label/input/subheader), 14 (value), 15 (header), 16 (value_large), 18 (title). The ProFormaPanel uses its own base font sizes (9–17) with a scaling engine that adjusts all sizes proportionally based on viewport dimensions.

### Data Directory Resolution
```python
# In app.py:
if getattr(sys, 'frozen', False):
    self._data_dir = Path(sys._MEIPASS) / "data"   # PyInstaller bundle
else:
    self._data_dir = Path(__file__).parent / "data"  # Development
```

### User Data Locations
- **Config:** `%APPDATA%/BennysBuildings/config.json` (Windows) or `~/.bennys_buildings/config.json`
- **Deals:** `%APPDATA%/BennysBuildings/deals/*.json`

## Formula Chain — Computation Order Matters

The `PropertyModel.recalculate()` method computes values in this exact order because of dependencies:

```
 1. total_price            = manual_override OR (price_per_unit × num_units)
 2. closing_costs          = total_price × closing_rate
 3. down_payment           = total_price × down_rate
 4. total_leverage         = total_price − down_payment
 5. insurance              = total_price × −insurance_rate
 6. taxes                  = total_price × −tax_rate
 7. debt_service           = PMT(interest/12, term×12, leverage) × 12     ← depends on #4
 8. reserve_account        = |debt_service + insurance + taxes| × (months/12)  ← depends on #5,6,7
 9. total_capital_required = closing + down + reserve + rent_ready         ← depends on #2,3,8
10. rent (effective)       = manual_override OR fmr_rent
11. potential_gross_rent   = rent × 12 × num_units
12. vacancy                = −PGR × vacancy_rate
13. loss_to_lease          = −PGR × ltl_rate
14. effective_gross_rent   = PGR + vacancy + loss_to_lease
15. maintenance            = EGR × −maint_rate                            ← depends on #14
16. management             = EGR × −mgmt_rate
17. annual_improvements    = EGR × −improve_rate
18. utility_allowance_yr   = (monthly × −12 × units) if enabled
19. total_expenses         = sum(maintenance..taxes)
20. noi                    = EGR − |total_expenses|                       ← depends on #14,19
21. annual_cashflow        = NOI + debt_service                           ← depends on #7,20
22. monthly_cashflow       = annual / 12
23. cashflow_margin        = annual_cashflow / EGR
24. cash_on_cash           = annual_cashflow / total_capital_required     ← depends on #9,21
25. cap_rate               = NOI / total_price
26. dscr                   = NOI / |debt_service|
```

**Key dependency:** `reserve_account` (#8) depends on `debt_service` (#7), which depends on `total_leverage` (#4). This means down_payment must be computed before debt_service, and debt_service before reserve. This is why the order matters.

**Expenses are stored as negative values** (matching Excel convention). NOI = EGR − |total_expenses|.

## API Integration

| Endpoint | Auth | Cache | Trigger |
|----------|------|-------|---------|
| `GET huduser.gov/hudapi/public/fmr/listStates` | Bearer token | Session-permanent | App startup |
| `GET huduser.gov/hudapi/public/fmr/listCounties/{stateCode}` | Bearer token | Per state code | State dropdown change |
| `GET huduser.gov/hudapi/public/fmr/data/{countyFIPS}` | Bearer token | None | County dropdown change |
| `GET us-zip-code-information.p.rapidapi.com/?zipcode={zip}` | X-RapidAPI-Key | Per zip code | Zip entry (5 digits, on blur/enter) |

**Cascading flow:** State → `listCounties` → populate County dropdown → County → `data/{fips}` → FMR rent → recalculate.

API keys are pre-populated from the original Excel workbook. User can update via Settings dialog. Stored in config.json.

## How to Add Features

### Adding a new computed metric
1. Add the formula to `PropertyModel.recalculate()` in `models/property_model.py` — respect computation order
2. Add a `self.new_metric: float = 0.0` attribute in `__init__`
3. Add a display line in `views/proforma_panel.py` `_build_layout()` using `_add_line()` or `_add_metric_line()`
4. Update `update_from_model()` in `proforma_panel.py` to set the new value with `_set()`
5. Add a test in `tests/test_property_model.py`

### Adding a new input field
1. Add the field to `DealInputs` dataclass in `models/data_types.py` with a default
2. Add the UI widget in `views/input_panel.py` in the appropriate `_build_*_section()` method (Property, Financials, or Utility)
3. Wire it in `get_all_inputs()` and `set_all_inputs()` in InputPanel
4. Parse it in `AppController._collect_inputs()`
5. Use it in `PropertyModel.recalculate()`

### Adding a new view panel
1. Create `views/new_panel.py` extending `SectionFrame` or `CTkScrollableFrame`
2. Add display widgets and an `update_from_model()` method
3. Import and instantiate in `views/dashboard.py`
4. Call its `update_from_model()` in `Dashboard.refresh_from_model()`
5. Alternatively, add new metrics directly to `ProFormaPanel._build_layout()`

### Adding utility allowance data for a new state
1. Create `data/utility_allowances/{state_code_lowercase}.json` (e.g., `tx.json`)
2. Use the same schema as `la.json`: `[{property_type, utility_service, 0_br..9_br}, ...]`
3. The app auto-discovers new state files at startup — no code changes needed

### Adding a new API endpoint
1. Add the method to `HUDApiService` or `RapidApiService` in `services/api_service.py`
2. Follow the existing pattern: `try/except requests.RequestException → raise APIError`
3. Add a threading wrapper in `controllers/app_controller.py` (thread + `.after()` callback)
4. Connect to a UI trigger (dropdown change, button click, etc.)

## Testing

Tests use **raw assert statements** with tolerance-based float comparison (no pytest/unittest framework):

```python
assert abs(model.total_price - 249999) < 1, f"Expected ~249999, got {model.total_price:.2f}"
```

**Reference values** come from the original Excel workbook (`Benny's Buildings.xlsm`) with these inputs: Mississippi, Forrest County, 4 units, $62,499.75/unit, 6.5% interest, 30yr, 25% down, 2% closing.

Run all tests: `python tests/test_property_model.py && python tests/test_financial.py`

## Gotchas

1. **Input rates are entered as percentages** (e.g., user types "6.5" for 6.5%) but stored as decimals (0.065) in `DealInputs`. The controller divides by 100 in `_collect_inputs()`.
2. **Manual override fields** (Total Price, Manual Rent) use `None` to indicate "not set" — empty string in the UI maps to `None`, which falls through to the calculated value.
3. **Expenses are negative** throughout the model. Total Expenses is a negative sum. NOI = EGR − |Total Expenses|.
4. **The `_pending_county` attribute** in AppController handles the async cascade during deal loading. When a deal is loaded, the state change triggers an async county fetch. `_pending_county` stores the saved county name so that `_on_counties_loaded()` can auto-select it and trigger the FMR fetch once the county list arrives.
5. **CustomTkinter CTkComboBox** is set to `state="readonly"` for all dropdowns to prevent free-text entry.
6. **The HUD API token** is a long-lived JWT (expires ~2034) but should still be user-configurable via Settings.
7. **Utility allowance state detection** uses 2-letter state codes matching filenames in `data/utility_allowances/`. The state code comes from `model.state_code`, set by the controller after HUD API lookup.
