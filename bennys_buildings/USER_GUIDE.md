# Benny's Buildings — User & Developer Guide

## Table of Contents

1. [What This App Does](#1-what-this-app-does)
2. [Installation and First Run](#2-installation-and-first-run)
3. [UI Walkthrough](#3-ui-walkthrough)
4. [Real Estate Glossary](#4-real-estate-glossary)
5. [Using the App — Step by Step](#5-using-the-app--step-by-step)
6. [Deal Management](#6-deal-management)
7. [API Setup](#7-api-setup)
8. [Utility Allowance System](#8-utility-allowance-system)
9. [Complete Formula Reference](#9-complete-formula-reference)
10. [Troubleshooting](#10-troubleshooting)
11. [Developer Extension Guide](#11-developer-extension-guide)
12. [Project File Reference](#12-project-file-reference)

---

## 1. What This App Does

Benny's Buildings is a **multifamily real estate investment analyzer** built as a Python desktop application. It helps investors evaluate rental properties by calculating key financial metrics like Net Operating Income (NOI), Cash-on-Cash return, Cap Rate, and Debt Service Coverage Ratio (DSCR).

**What it replaces:** An Excel workbook (`Benny's Buildings.xlsm`) that had 8 worksheets, VBA macros, and Power Query API connections. This app replicates all of that functionality in a single polished dark-themed window.

**Key capabilities:**
- Enter property details (location, units, price, loan terms)
- Automatically fetch Fair Market Rent (FMR) data from the HUD government API
- Auto-populate property tax rates, current mortgage rates, and economic data
- Flood/hazard risk assessment via OpenFEMA
- Rent affordability scoring via HUD Income Limits
- Calculate 30+ financial metrics instantly as you type
- Save and load named property analyses ("deals") for comparison
- Look up utility allowances for expense estimation (Louisiana data included)
- Look up zip code information for property research

---

## 2. Installation and First Run

### Prerequisites
- Python 3.10 or newer (built with 3.13)
- Windows PC (designed for Windows, may work on macOS/Linux with minor font differences)

### Setup

```bash
cd "C:\Z Multifamily Plan\bennys_buildings"
pip install -r requirements.txt
python main.py
```

### What Happens on First Run

1. The app creates a configuration directory at `%APPDATA%\BennysBuildings\`
2. A `config.json` file is generated with pre-loaded API keys (from the original Excel workbook)
3. A `deals\` subdirectory is created for saving property analyses
4. The app loads the state list from the HUD API (requires internet connection)
5. All input fields populate with sensible defaults

### If You See "Failed to load states"

This means the HUD API call failed. Possible causes:
- No internet connection
- The API token has expired — open Settings and update it (see [API Setup](#7-api-setup))
- The HUD API is temporarily down — try again in a few minutes

The app still works without API access — you just can't auto-populate states/counties/FMR rent. You can still enter a manual rent value and all calculations will work.

---

## 3. UI Walkthrough

The app window has three major areas:

### Title Bar (Top)
- **App name:** "Benny's Buildings" in teal
- **Deal name:** Shows "Untitled" or the name of the currently loaded deal
- **Buttons (right side):** New, Save, Save As, Load, Settings

### Left Column — Investment Pro Forma

A professional financial statement laid out in 3 columns with auto-scaling fonts that adjust to fill the available space. The panel hides its scrollbar when everything fits on screen.

#### Column 1: Investment Summary, Financing, Capital Requirements

| Section | Fields |
|---------|--------|
| **Investment Summary** | Acquisition Price, property info, location |
| **Financing** | Loan Amount, Term/Rate, Annual Debt Service (monthly shown below) |
| **Capital Requirements** | Down Payment, Closing Costs, Reserve Account, Cost to Rent Ready → **Total Capital Required** |

#### Column 2: Operating Statement

| Section | Fields |
|---------|--------|
| **Revenue** | Potential Gross Rent, Less: Vacancy, Less: Loss to Lease → **Effective Gross Revenue** |
| **Operating Expenses** | Maintenance, Management, Annual Improvements, Utility Allowance, Insurance, Property Tax → **Total Expenses** (with Expense Ratio) |
| **Bottom line** | **NET OPERATING INCOME** |

#### Column 3: Investment Metrics & Cash Flow

| Section | Fields | Good Target |
|---------|--------|-------------|
| **Investment Metrics** | Cap Rate, Cash on Cash, DSCR, Cash Flow Margin, GRM, Break-even Occupancy, Price/Bedroom, Debt Yield, NOI/Unit, Expenses/Unit, Rent Affordability | Varies (see color coding) |
| **Cash Flow Analysis** | Net Operating Income, Less: Debt Service → Monthly Cash Flow → **Annual Cash Flow** | Positive = profitable |
| **Market Context** | Flood risk warning, current mortgage rate hint, rent CPI growth, national vacancy rate | Informational |

**Color coding:**
- **Green** = positive/strong values
- **Red** = negative/weak values
- **Orange** = moderate or informational

### Right Column — Inputs (Accordion)

All user inputs organized in 3 collapsible sections. Only one section is open at a time — clicking a section header opens it and collapses the others. The panel scrolls vertically if needed.

#### ▼ Property Section
| Field | How to Use |
|-------|-----------|
| **Address** | Street address (e.g., "123 Main St") — used for deal identification |
| **State** | Searchable dropdown — triggers county list fetch from HUD API |
| **County** | Searchable dropdown (populated after state selection) — triggers FMR + income limits + flood risk fetch |
| **Zip Code** | Property zip code — auto-fills state/county, fetches property tax rate |
| **Type** | Radio buttons: Apartment (5+), Duplex/Townhouse (<5 Units), Single Family |
| **Bedrooms** | Dropdown: 0 BR through 5 BR — affects FMR rent lookup (updates immediately) |
| **# Units** | Total number of rental units in the property |
| **$ / Unit** | Purchase price per unit |
| **Total $ (opt)** | Optional: enter a total price directly (overrides $/unit calculation) |
| **Rent Ready $** | Renovation/repair costs before renting (default 0) |

#### ▶ Financials Section (collapsed by default)
Organized into 3 sub-groups:

**LOAN**
| Field | Default | What It Controls |
|-------|---------|-----------------|
| **Term (yr)** | 30 | Mortgage term in years |
| **Rate %** | 6.5 | Annual mortgage interest rate |
| **Down %** | 25 | Down payment as a percentage of purchase price |
| **Closing %** | 2 | Closing costs as a percentage of purchase price |
| **Reserve (mo)** | 6 | Number of months of expenses to keep in reserve |

**REVENUE**
| Field | What It Does |
|-------|-------------|
| **FMR Rent** | Read-only display — the Fair Market Rent fetched from HUD for the selected county and bedroom count |
| **Manual Rent** | If entered, overrides the FMR rent with your own monthly rent estimate |
| **Vacancy %** | Expected vacancy rate (default 5%) |
| **LtL %** | Loss to Lease rate (default 0%) |

**EXPENSES**
| Field | Default | What It Controls |
|-------|---------|-----------------|
| **Maint %** | 15 | Maintenance rate as % of effective rent |
| **Mgmt %** | 10 | Management fee as % of effective rent |
| **Improve %** | 15 | Annual improvements as % of effective rent |
| **Insurance %** | 1.5 | Annual insurance as % of purchase price |
| **Tax %** | 1.0 | Annual property tax as % of purchase price |

#### ▶ Utilities Section (collapsed by default)
| Field | Options | What It Controls |
|-------|---------|-----------------|
| **Use UA?** | Yes / No | Whether to include utility allowance in expense calculations |
| **Has Gas?** | Yes / No | Whether the property has gas service (shown when UA = Yes) |
| **Heating** | Electric / Heat Pump / Natural Gas | Heating system type (shown when UA = Yes) |
| **Cooking** | Electric / Natural Gas | Cooking appliance fuel type (shown when UA = Yes) |
| **Water Htg** | Electric / Natural Gas | Water heater fuel type (shown when UA = Yes) |

### Status Bar (Bottom)
Shows current status: "Ready", loading messages during API calls, or the current county/FMR info after data loads.

---

## 4. Real Estate Glossary

These terms are used throughout the application. Understanding them is essential for interpreting the results.

**Cap Rate (Capitalization Rate):** The ratio of NOI to purchase price, expressed as a percentage. It measures the property's return independent of financing. A 8% cap rate means the property generates 8 cents of NOI per dollar of purchase price. Higher cap rates mean higher returns but often come with higher risk.

**Cash on Cash Return:** The ratio of annual pre-tax cashflow to total cash invested (down payment + closing costs + reserves + rent ready costs). This is the investor's actual return on the money they put in. A 10% cash on cash means you earn 10 cents per year for every dollar you invested.

**DSCR (Debt Service Coverage Ratio):** The ratio of NOI to annual debt payments. A DSCR of 1.25 means the property generates 25% more income than needed to cover mortgage payments. Below 1.0 means the property cannot cover its debt from rental income alone. Most lenders require DSCR of 1.20-1.25 minimum.

**Debt Service:** Total annual mortgage payments (principal + interest). Shown as a negative number because it's a cash outflow.

**Effective Gross Rent (EGR):** The actual expected rental income after subtracting vacancy and loss to lease from Potential Gross Rent.

**FMR (Fair Market Rent):** A government-published estimate of what a typical rental unit should cost in a given area. Published annually by HUD (Department of Housing and Urban Development). Varies by county and number of bedrooms. Used as a baseline rent estimate when you don't have actual market data.

**Loss to Lease:** Revenue lost because existing tenants are paying below current market rates. For example, if market rent is $1,000 but a tenant signed a lease at $950, the $50 difference is loss to lease.

**NOI (Net Operating Income):** Annual rental income minus all operating expenses, but BEFORE debt payments. This is the core measure of a property's profitability. NOI = Effective Gross Rent minus Total Expenses.

**PMT (Payment):** The standard financial formula for calculating a fixed periodic payment on a loan. Used to compute monthly mortgage payments from the interest rate, term, and loan amount.

**Potential Gross Rent (PGR):** The maximum possible annual rent — every unit occupied at full price for 12 months. PGR = (monthly rent per unit) x 12 x (number of units).

**Reserve Account:** An emergency fund set aside at purchase. Calculated as several months' worth of fixed costs (debt service + insurance + taxes). Protects against unexpected vacancies or repairs.

**Total Capital Required:** The total cash an investor needs to close and prepare the property: down payment + closing costs + reserves + rent-ready costs. This is the denominator in the cash-on-cash calculation.

**Total Leverage:** The amount borrowed (Total Price minus Down Payment). This is the loan principal.

**Utility Allowance:** In subsidized housing (Section 8, HUD programs), landlords may need to account for tenant-paid utilities. The utility allowance is a monthly dollar amount per unit that represents expected utility costs. It varies by property type, location, utility types, and bedroom count.

---

## 5. Using the App — Step by Step

### Analyzing a New Property

**Step 1: Select Location**
1. Click the **State** dropdown and select the property's state
2. Wait for the county list to load (status bar shows "Loading counties...")
3. Select the **County** from the populated dropdown
4. The FMR Rent display updates automatically

**Step 2: Enter Property Details**
1. Select the **Property Type** (Apartment, Duplex/Townhouse, Single Family)
2. Select the **Bedrooms** per unit (affects FMR rent lookup)
3. Enter the **# Units** (total rental units)
4. Enter the **$ / Unit** (purchase price per unit)
   - OR enter a **Total $** to override the per-unit calculation

**Step 3: Adjust Rates (optional)**
The defaults are reasonable starting points. Adjust any that differ for your market:
- Insurance and tax rates (right column)
- Loan terms (interest rate, term, down payment percentage)
- Expense rates (maintenance, management, improvements)
- Vacancy rate

**Step 4: Review Results**
Look at the Returns section (middle column):
- Is **Annual Cashflow** positive? (Green = yes)
- Is **Cash on Cash** above 8-10%? (Green = good)
- Is **DSCR** above 1.25? (Green = safe)
- Is **Cap Rate** competitive for the market?

**Step 5: Save the Analysis**
Click **Save** → enter a name like "4-Plex on Main St" → click Save.

### Comparing Properties
1. Analyze Property A and save it
2. Click **New** to reset
3. Analyze Property B and save it
4. Use **Load** to switch between them and compare metrics

### Using Manual Rent Override
If you know the actual rent (from listings, market research, or existing leases):
1. Enter the monthly rent per unit in the **Manual Rent** field
2. This overrides the FMR rent for all calculations
3. Clear the field to revert to FMR rent

### Using Manual Total Price Override
If the listing price is a round number (not exactly $/unit x units):
1. Enter the total purchase price in the **Total $ (opt)** field
2. This overrides the per-unit calculation
3. Clear the field to revert to the calculated price

---

## 6. Deal Management

### Saving a Deal
- **Quick Save (Ctrl+S):** If the deal has a name, saves immediately. If untitled, opens the Save dialog.
- **Save As (Ctrl+Shift+S):** Always opens the Save dialog for a new name.
- All user inputs are saved. Computed values are NOT saved — they're recalculated when loaded.

### Loading a Deal
- **Load (Ctrl+O):** Opens the load dialog showing all saved deals with name, summary, and date.
- Click **Load** next to a deal to restore all its inputs.
- The app will re-fetch county and FMR data from the API for the deal's state/county.

### Creating a New Deal
- **New (Ctrl+N):** Resets all inputs to defaults, clears location fields (state, county, zip, address), and clears the deal name. Gives you a clean slate.

### Deleting a Deal
- Open the **Load** dialog and click **Delete** next to the deal you want to remove.
- This permanently deletes the JSON file from disk.

### Where Deals Are Stored
Deals are saved as JSON files in `%APPDATA%\BennysBuildings\deals\`. Each file contains the deal name, timestamps, and all input values. You can back up this folder or copy deals between computers.

---

## 7. API Setup

The app uses five external APIs. HUD and RapidAPI come pre-configured. The others are optional — the app works without them but provides richer data when configured.

### HUD API (Fair Market Rent + Income Limits)
- **What it provides:** State list, county list, Fair Market Rent data, Area Median Income
- **Authentication:** Bearer token (JWT)
- **Free registration:** https://www.huduser.gov/hudapi/public/register
- **Pre-configured:** Yes (token from original Excel workbook)

### RapidAPI (Zip Code Information)
- **What it provides:** City, county, state, coordinates for a zip code
- **Authentication:** API key in header
- **Free tier:** https://rapidapi.com/mikicode/api/us-zip-code-information
- **Pre-configured:** Yes

### API Ninjas (Property Tax + Mortgage Rates)
- **What it provides:** Property tax rate by ZIP code, current 30yr/15yr/5-1 ARM mortgage rates
- **Authentication:** X-Api-Key header
- **Free tier:** 50,000 calls/month at https://api-ninjas.com
- **How to get a key:**
  1. Go to https://api-ninjas.com and create a free account
  2. Copy your API key from your profile/dashboard
  3. Paste in Settings → "API Ninjas Key"

### FRED (Federal Reserve Economic Data)
- **What it provides:** Current mortgage rate benchmark, rent CPI growth (5yr annualized), national rental vacancy rate
- **Authentication:** api_key query parameter
- **Free tier:** 120 requests/minute at https://fred.stlouisfed.org
- **How to get a key:**
  1. Go to https://fred.stlouisfed.org/docs/api/api_key.html
  2. Create an account and request an API key
  3. Paste in Settings → "FRED API Key"

### OpenFEMA (Flood/Hazard Risk)
- **What it provides:** County-level flood risk score and rating from the National Risk Index
- **Authentication:** None required (open API)
- **Triggered by:** County selection (automatic)

### Updating API Keys in the App
1. Click the **Settings** button (gear icon) in the title bar
2. Fill in the API key fields (HUD, RapidAPI, API Ninjas, FRED)
3. Click **Save**
4. The app will re-fetch the states list and market data

### If API Keys Stop Working
- **401 errors:** The token has expired or is invalid. Get a new one.
- **Rate limiting:** The HUD API has generous limits. If throttled, wait a minute and try again.
- **The app works without APIs:** You can still enter all values manually (skip state/county selection, enter manual rent). Optional APIs (API Ninjas, FRED) degrade gracefully — features just won't show data.

---

## 8. Utility Allowance System

### What Is It?
The utility allowance is a per-unit monthly amount representing expected utility costs for tenants. It's used in HUD subsidized housing programs and in general investment analysis to estimate operating expenses.

### How It Works in the App
1. The app includes a utility allowance lookup table for **Louisiana** (extracted from HUD Form 52667 data)
2. The table has allowance amounts organized by:
   - **Property type** (Apartment 5+, Duplex/Townhouse/5 Units, Single Family)
   - **Utility service** (Electric, Heating, Cooking, Water Heating, Sewer, Water, Trash, etc.)
   - **Bedroom count** (0 BR through 9 BR)
3. Some utilities always apply (electric, AC, sewer, water, trash)
4. Others depend on your selections (heating type, cooking type, water heating type, whether there's gas)

### Enabling Utility Allowance
1. Set **Use UA?** to "Yes" in the Utilities section
2. Select the appropriate heating, cooking, and water heating types
3. Set whether the property has gas service
4. The monthly total appears in the Utility Breakdown panel (left column)
5. The annual utility expense (monthly x 12 x units) is included in Total Expenses

### Adding Data for Other States
Currently only Louisiana data is included. To add another state:

1. Obtain the HUD utility allowance schedule for that state (from the local Public Housing Authority)
2. Create a JSON file at `data/utility_allowances/{state_code}.json` (e.g., `tx.json` for Texas)
3. Use this format:
```json
[
  {
    "property_type": "Apartment (5+ Units)",
    "utility_service": "All Other Electric",
    "0_br": 14,
    "1_br": 16,
    "2_br": 23,
    "3_br": 29,
    "4_br": 35,
    "5_br": 42,
    "6_br": 0,
    "7_br": 0,
    "8_br": 0,
    "9_br": 0
  }
]
```
4. Include all combinations of property types and utility services (typically 39 rows)
5. The app auto-discovers new state files at startup — no code changes needed

### Utility Service Types
The 13 utility services recognized by the app:

| Service | When It Applies |
|---------|----------------|
| All Other Electric | Always |
| Cooking - Electric | When Cooking = "Cooking - Electric" |
| Cooking - Natural Gas | When Cooking = "Cooking - Natural Gas" |
| Electric Air Conditioning | Always |
| Fixed - Gas | When Has Gas? = "Yes" |
| Heating - Electric | When Heating = "Heating - Electric" |
| Heating - Heat Pump | When Heating = "Heating - Heat Pump" |
| Heating - Natural Gas | When Heating = "Heating - Natural Gas" |
| Sewer | Always |
| Trash Collection | Always |
| Water | Always |
| Water Heating - Electric | When Water Htg = "Water Heating - Electric" |
| Water Heating - Natural Gas | When Water Htg = "Water Heating - Natural Gas" |

---

## 9. Complete Formula Reference

Every formula in the application, explained in plain English with the actual computation.

### Purchase Section

**Total Price**
```
IF manual_total_price is provided:
    total_price = manual_total_price
ELSE:
    total_price = price_per_unit × num_units
```
Example: 4 units × $62,499.75/unit = $249,999

**Closing Costs**
```
closing_costs = total_price × closing_cost_rate
```
Example: $249,999 × 2% = $5,000

**Down Payment**
```
down_payment = total_price × down_payment_rate
```
Example: $249,999 × 25% = $62,500

**Total Leverage (Loan Amount)**
```
total_leverage = total_price − down_payment
```
Example: $249,999 − $62,500 = $187,499

**Insurance (annual)**
```
insurance = total_price × insurance_rate (stored as negative)
```
Example: $249,999 × 1.5% = −$3,750

**Taxes (annual)**
```
taxes = total_price × tax_rate (stored as negative)
```
Example: $249,999 × 1.0% = −$2,500

**Debt Service (annual mortgage payments)**
```
monthly_payment = PMT(interest_rate / 12, loan_term × 12, total_leverage)
debt_service = monthly_payment × 12
```
Where PMT is the standard financial payment function. A $187,499 loan at 6.5% for 30 years = approximately −$14,221/year.

**Reserve Account**
```
reserve_account = |debt_service + insurance + taxes| × (reserve_months / 12)
```
Example: |−$14,221 + (−$3,750) + (−$2,500)| × (6/12) = $20,471 × 0.5 = $10,235

**Total Capital Required**
```
total_capital_required = closing_costs + down_payment + reserve_account + cost_to_rent_ready
```
Example: $5,000 + $62,500 + $10,235 + $0 = $77,735

### Income Section

**Effective Rent (per unit per month)**
```
IF manual_rent is provided:
    rent = manual_rent
ELSE:
    rent = fmr_rent (from HUD API, based on county and bedroom count)
```

**Potential Gross Rent (annual)**
```
potential_gross_rent = rent × 12 × num_units
```
Example: $1,047 × 12 × 4 = $50,256

**Vacancy (annual lost rent)**
```
vacancy = −potential_gross_rent × vacancy_rate
```
Example: −$50,256 × 5% = −$2,513

**Loss to Lease (annual)**
```
loss_to_lease = −potential_gross_rent × loss_to_lease_rate
```
Example: −$50,256 × 0% = $0

**Effective Gross Rent (annual)**
```
effective_gross_rent = potential_gross_rent + vacancy + loss_to_lease
```
Example: $50,256 + (−$2,513) + $0 = $47,743

### Expense Section

**Maintenance, Management, Annual Improvements**
```
maintenance = effective_gross_rent × maintenance_rate (stored negative)
management = effective_gross_rent × management_rate (stored negative)
annual_improvements = effective_gross_rent × improvements_rate (stored negative)
```
Example (maintenance): $47,743 × 15% = −$7,161

**Utility Allowance (annual)**
```
IF use_utility_allowance == "Yes":
    utility_allowance_yearly = monthly_allowance × 12 × num_units (stored negative)
ELSE:
    utility_allowance_yearly = 0
```

**Total Expenses**
```
total_expenses = maintenance + management + annual_improvements
                 + utility_allowance_yearly + insurance + taxes
```
All values are negative, so total_expenses is a large negative number.

**Expense Ratio**
```
expense_ratio = |total_expenses| / effective_gross_rent
```
Example: $25,347 / $47,743 = 53.1%

### Returns Section

**Net Operating Income (NOI)**
```
noi = effective_gross_rent − |total_expenses|
```
Example: $47,743 − $25,347 = $22,396

**Annual Cashflow**
```
annual_cashflow = noi + debt_service
```
Note: debt_service is negative, so this subtracts the mortgage payments.
Example: $22,396 + (−$14,221) = $8,175

**Monthly Cashflow**
```
monthly_cashflow = annual_cashflow / 12
```
Example: $8,175 / 12 = $681

**Cashflow Margin**
```
cashflow_margin = annual_cashflow / effective_gross_rent
```
Example: $8,175 / $47,743 = 17.1%

**Cash on Cash Return**
```
cash_on_cash = annual_cashflow / total_capital_required
```
Example: $8,175 / $77,735 = 10.5%

**Cap Rate**
```
cap_rate = noi / total_price
```
Example: $22,396 / $249,999 = 8.96%

**DSCR (Debt Service Coverage Ratio)**
```
dscr = noi / |debt_service|
```
Example: $22,396 / $14,221 = 1.57

### Additional Metrics

**Gross Rent Multiplier (GRM)**
```
grm = total_price / potential_gross_rent
```
Lower GRM = better value. Typically 4-8 for multifamily.

**Break-even Occupancy**
```
breakeven_occupancy = (|total_expenses| + |debt_service|) / potential_gross_rent
```
The minimum occupancy needed to cover all costs. Below 85% is ideal.

**Price per Bedroom**
```
price_per_bedroom = total_price / (bedrooms_per_unit × num_units)
```

**Debt Yield**
```
debt_yield = noi / total_leverage
```
Lender metric. Green >= 10%, Orange 8-10%, Red < 8%.

**NOI per Unit / Expenses per Unit**
```
noi_per_unit = noi / num_units
expenses_per_unit = |total_expenses| / num_units
```

**Rent Affordability**
```
rent_affordability = (effective_rent × 12) / area_median_income
```
Requires HUD Income Limits data. Green < 30% of AMI.

---

## 10. Troubleshooting

### App Won't Start

**"ModuleNotFoundError: No module named 'customtkinter'"**
Run: `pip install customtkinter requests`

**"ModuleNotFoundError: No module named 'models'"**
You must run from the project directory: `cd "C:\Z Multifamily Plan\bennys_buildings" && python main.py`

**Window appears but is blank/frozen**
CustomTkinter may not support your display settings. Try resizing the window or check that your Python has tkinter: `python -c "import tkinter; print('OK')"`

### API Issues

**"Failed to load states" on startup**
- Check internet connection
- Open Settings → verify the HUD API token is present
- The HUD API may be temporarily down — try again later
- You can still use the app by entering manual rent values

**Counties don't load after selecting a state**
- The state code lookup may have failed — check the status bar message
- Try selecting a different state, then re-select the original

**FMR Rent shows "—"**
- Select a county first (the FMR data loads per county)
- Check that the bedroom count is selected (FMR varies by bedroom count)

**Zip code lookup not working**
- Ensure the zip code is exactly 5 digits
- Check the RapidAPI key in Settings
- This feature is informational only — it doesn't affect calculations

### Calculation Issues

**All values show $0**
- Enter a value in **# Units** and **$ / Unit** (or **Total $**)
- The model needs at least a price and unit count to calculate

**Cash on Cash / Cap Rate seem wrong**
- Check that the interest rate is entered as a percentage (e.g., "6.5" not "0.065")
- Check that expense rates look reasonable (15% maintenance + 10% management + 15% improvements = 40% of rent going to expenses)
- Verify the reserve months — a large reserve increases total capital required, which lowers Cash on Cash

**Cashflow is negative (red)**
- This means the property costs more to own than it earns in rent
- Common with high purchase prices, high interest rates, or low rents
- Try: lower purchase price, higher down payment (reduces debt service), or higher rent

**DSCR below 1.0 (red)**
- The property cannot cover its debt payments from rental income
- This deal would require additional cash each month to sustain
- Most lenders won't finance properties with DSCR below 1.20

### Deal Save/Load Issues

**"Save" button doesn't seem to work**
- A dialog should appear asking for a name — check if it opened behind the main window
- Keyboard shortcut: Ctrl+S

**Loaded deal shows different FMR rent than when saved**
- FMR rent is NOT saved in the deal — it's re-fetched from the API
- If HUD has updated their FMR data, the rent may differ
- The deal saves all your inputs; computed values are recalculated fresh

---

## 11. Developer Extension Guide

### Project Architecture Overview

```
main.py ──→ BennysApp (app.py)
              ├── ConfigService (services/config_service.py)
              ├── Dashboard (views/dashboard.py)
              │     ├── ProFormaPanel (3-column auto-scaling financial statement)
              │     └── InputPanel (accordion with 3 collapsible sections)
              └── AppController (controllers/app_controller.py)
                    ├── PropertyModel (models/property_model.py)
                    ├── DealManager (models/deal_manager.py)
                    ├── HUDApiService — FMR, states, counties, income limits
                    ├── RapidApiService — zip code lookup
                    ├── ApiNinjasService — property tax, mortgage rates
                    ├── FREDApiService — rent CPI, vacancy, rates
                    └── OpenFEMAService — flood/hazard risk
```

### Adding a New Financial Metric

Example: Adding a "Gross Rent Multiplier" (GRM = Total Price / Annual Gross Rent).

**Step 1:** Add the attribute and calculation to `models/property_model.py`:
```python
# In __init__:
self.grm: float = 0.0

# In recalculate(), after NOI calculation:
if self.potential_gross_rent != 0:
    self.grm = self.total_price / self.potential_gross_rent
else:
    self.grm = 0.0
```

**Step 2:** Add a display row to `views/proforma_panel.py`:
```python
# In _build_layout(), add a metric line in the appropriate column:
self._add_metric_line("grm", "Gross Rent Mult.", R)

# In update_from_model():
self._set("grm", f"{format_ratio(model.grm)}x", COLORS["accent_orange"])
```

**Step 3:** Add a test in `tests/test_property_model.py`:
```python
def test_grm():
    model = get_test_model()
    expected = 249999 / 50256  # ~4.97
    assert abs(model.grm - expected) < 0.1
```

### Adding a New Input Field

Example: Adding a "Property Age" field.

**Step 1:** Add to `DealInputs` in `models/data_types.py`:
```python
property_age: int = 0
```

**Step 2:** Add the widget in `views/input_panel.py` (in the Property section):
```python
# In _build_property_section():
self.property_age = InputField(container, "Age (yr)", placeholder="0", on_change=self._trigger_input_change)
self.property_age.pack(fill="x", pady=3, padx=12)
```

**Step 3:** Add to `get_all_inputs()` and `set_all_inputs()` in InputPanel.

**Step 4:** Parse it in `AppController._collect_inputs()`:
```python
property_age=parse_int(raw["property_age"], 0),
```

**Step 5:** Use it in formulas as needed in `PropertyModel.recalculate()`.

### Adding a New View Panel

**Step 1:** Create `views/new_panel.py`:
```python
from views.widgets import SectionFrame, MetricRow, COLORS

class NewPanel(SectionFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="MY NEW SECTION", **kwargs)
        self.some_metric = MetricRow(self.content, "Some Metric", value_color=COLORS["accent_cyan"])
        self.some_metric.pack(fill="x", pady=2)

    def update_from_model(self, model):
        self.some_metric.set_value(f"${model.some_value:,.0f}")
```

**Step 2:** Import and add to `views/dashboard.py`:
```python
from views.new_panel import NewPanel

# In __init__:
self.new_panel = NewPanel(self)
self.new_panel.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))

# In refresh_from_model():
self.new_panel.update_from_model(model)
```

Alternatively, add new metrics directly to the existing `ProFormaPanel` by adding lines in `_build_layout()` and updating `update_from_model()`.

### Adding a New API Endpoint

**Step 1:** Add the method to the appropriate service class in `services/api_service.py`:
```python
def get_new_data(self, param: str) -> dict:
    try:
        resp = self._session.get(f"{self.BASE_URL}/new_endpoint/{param}")
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise APIError(f"Failed to fetch new data: {e}")
```

**Step 2:** Add a threading wrapper in `controllers/app_controller.py`:
```python
def _fetch_new_data(self, param):
    try:
        data = self._hud_api.get_new_data(param)
        self._dashboard.after(0, self._on_new_data_loaded, data)
    except APIError as e:
        self._dashboard.after(0, self._set_status, f"Error: {e}")
```

**Step 3:** Connect to a UI trigger.

### Key Reusable Components

| Component | Import From | Purpose |
|-----------|------------|---------|
| `SectionFrame` | `views/widgets.py` | Card-style panel with title header |
| `CollapsibleSection` | `views/widgets.py` | Expandable/collapsible section with clickable header (accordion) |
| `MetricRow` | `views/widgets.py` | Label + value display row |
| `InputField` | `views/widgets.py` | Label + text entry with change callback |
| `DropdownField` | `views/widgets.py` | Label + combobox with change callback |
| `SearchableDropdown` | `views/widgets.py` | Label + filterable popup dropdown |
| `RadioField` | `views/widgets.py` | Label + radio button group (horizontal or vertical) |
| `DisplayField` | `views/widgets.py` | Label + read-only value display |
| `SeparatorRow` | `views/widgets.py` | Horizontal line divider |
| `COLORS` | `views/widgets.py` | 17-color dark theme palette |
| `FONTS` | `views/widgets.py` | 8-style font system |
| `format_currency()` | `utils/formatting.py` | "$1,234" formatting |
| `format_percent()` | `utils/formatting.py` | "5.0%" formatting |
| `format_ratio()` | `utils/formatting.py` | "1.57" formatting |
| `parse_float()` | `utils/formatting.py` | Safe string-to-float parsing |
| `parse_int()` | `utils/formatting.py` | Safe string-to-int parsing |
| `pmt()` | `utils/financial.py` | Excel PMT function equivalent |

---

## 12. Project File Reference

### Core Application Files

| File | Key Classes/Functions | What It Does |
|------|----------------------|-------------|
| `main.py` | `main()` | Entry point. Adds project root to sys.path, creates and runs BennysApp |
| `app.py` | `BennysApp(CTk)` | Root window. Creates title bar (New/Save/Load/Settings buttons), dashboard, status bar. Binds keyboard shortcuts (Ctrl+S/O/N). Initializes ConfigService and AppController |

### Models (Business Logic)

| File | Key Classes/Functions | What It Does |
|------|----------------------|-------------|
| `models/data_types.py` | `State`, `County`, `FMRData`, `ZipInfo`, `UtilityAllowanceEntry`, `PropertyTaxData`, `MortgageRateData`, `IncomeLimitData`, `FloodRiskData`, `DealInputs`, `DealData` | All data structures used throughout the app. DealInputs holds every user-configurable field with defaults |
| `models/property_model.py` | `PropertyModel`, `UtilityAllowanceCalculator` | The core calculation engine. PropertyModel.recalculate() computes 30+ financial metrics. UtilityAllowanceCalculator loads state JSON files and computes conditional utility allowances |
| `models/deal_manager.py` | `DealManager` | Saves deals as JSON to %APPDATA%/BennysBuildings/deals/. Methods: save(), load(), list_deals(), delete(), exists() |

### Views (UI Components)

| File | Key Classes | What It Does |
|------|------------|-------------|
| `views/widgets.py` | `SectionFrame`, `CollapsibleSection`, `MetricRow`, `InputField`, `DropdownField`, `SearchableDropdown`, `RadioField`, `DisplayField`, `SeparatorRow` | Reusable UI building blocks. Also defines COLORS (17 colors) and FONTS (8 styles) dictionaries |
| `views/dashboard.py` | `Dashboard(CTkFrame)` | 2-column layout: ProFormaPanel (left, weight=5) + InputPanel (right, weight=2). refresh_from_model() propagates updates to the pro forma |
| `views/proforma_panel.py` | `ProFormaPanel(CTkScrollableFrame)` | 3-column auto-scaling financial statement. Uniform scaling of fonts, padding, heights, and widths. Hides scrollbar when content fits |
| `views/input_panel.py` | `InputPanel(CTkFrame)` | Accordion layout with 3 CollapsibleSections (Property, Financials, Utilities). Only one section open at a time. Exposes callback attributes for controller wiring. get_all_inputs() / set_all_inputs() for bulk access |
| `views/deal_dialog.py` | `SaveDealDialog(CTkToplevel)`, `LoadDealDialog(CTkToplevel)` | Modal dialogs for deal name entry and deal list browsing with load/delete buttons |
| `views/settings_dialog.py` | `SettingsDialog(CTkToplevel)` | API key configuration with 4 fields: HUD token, RapidAPI, API Ninjas, FRED |

### Services (External Integration)

| File | Key Classes | What It Does |
|------|------------|-------------|
| `services/api_service.py` | `TimeoutSession`, `HUDApiService`, `RapidApiService`, `ApiNinjasService`, `FREDApiService`, `OpenFEMAService`, `APIError` | HTTP clients with caching. HUD: states, counties, FMR, income limits. RapidAPI: zip lookup. API Ninjas: tax rates, mortgage rates. FRED: rent CPI, vacancy rate. OpenFEMA: flood risk. All use TimeoutSession (10-15s) |
| `services/config_service.py` | `AppConfig`, `ConfigService` | Manages %APPDATA%/BennysBuildings/config.json. Pre-populates API keys from workbook on first run. AppConfig stores 4 API keys + all default rates |

### Controllers (Orchestration)

| File | Key Classes | What It Does |
|------|------------|-------------|
| `controllers/app_controller.py` | `AppController` | Central coordinator. _collect_inputs() parses UI into DealInputs. State→County→FMR cascade with zip-driven auto-fill. County change triggers FMR + income limits + flood risk. Zip entry triggers tax rate lookup. App startup fetches mortgage rates + FRED data. All API calls threaded with .after() callbacks. Manages deal save/load lifecycle |

### Utilities

| File | Key Functions | What It Does |
|------|--------------|-------------|
| `utils/financial.py` | `pmt(rate, nper, pv)` | Excel PMT equivalent. Returns negative payment amount. Handles 0% rate edge case |
| `utils/formatting.py` | `format_currency()`, `format_percent()`, `format_ratio()`, `parse_float()`, `parse_int()` | Display formatting (currency, %, ratios) and safe input parsing (strips $, commas, %, handles empty strings) |

### Data Files

| File | What It Contains |
|------|-----------------|
| `data/options.json` | Dropdown values: cooking_types (2), heating_types (3), water_heating_types (2), bedroom_options (6 with FMR key mapping), property_types (3), yes_no (2) |
| `data/utility_allowances/la.json` | Louisiana HUD utility allowance table. 39 rows covering 3 property types x 13 utility services. Each row has monthly dollar amounts for 0-9 bedrooms |

### Test Files

| File | Tests | What It Verifies |
|------|-------|-----------------|
| `tests/test_property_model.py` | 18 tests | Every computed metric against known Excel workbook values (Mississippi, Forrest County, 4 units @ $62,499.75) |
| `tests/test_financial.py` | 4 tests | PMT function accuracy: standard mortgage, 0% rate, 0 leverage, annual debt service |
