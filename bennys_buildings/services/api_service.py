"""API service — HUD, RapidAPI, API Ninjas, FRED, and FEMA.

Handles all external API calls with caching, error handling, and
response parsing. Designed for threaded use from the controller.
"""

import requests
from datetime import datetime, timedelta
from typing import Optional

from models.data_types import (
    State, County, FMRData, ZipInfo,
    PropertyTaxData, MortgageRateData, IncomeLimitData,
    FloodRiskData,
)


class APIError(Exception):
    """Raised when an API call fails."""
    pass


class TimeoutSession(requests.Session):
    """Session subclass that enforces a default timeout on all requests.

    requests.Session doesn't natively support a default timeout —
    setting session.timeout as an attribute is silently ignored.
    This subclass injects the timeout into every request.
    """

    def __init__(self, timeout: int = 15):
        super().__init__()
        self._default_timeout = timeout

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self._default_timeout)
        return super().request(method, url, **kwargs)


class HUDApiService:
    """Client for the HUD User Fair Market Rent API.

    Endpoints:
        - /fmr/listStates — list all US states/territories
        - /fmr/listCounties/{stateCode} — counties in a state
        - /fmr/data/{countyFIPS} — Fair Market Rent data
    """

    BASE_URL = "https://www.huduser.gov/hudapi/public/fmr"

    def __init__(self, token: str):
        self._session = TimeoutSession(timeout=15)
        self._session.headers["Authorization"] = f"Bearer {token}"

        # Caches
        self._states_cache: Optional[list[State]] = None
        self._counties_cache: dict[str, list[County]] = {}

    def update_token(self, token: str):
        """Update the Bearer token."""
        self._session.headers["Authorization"] = f"Bearer {token}"

    def list_states(self) -> list[State]:
        """Fetch all US states/territories. Cached for session."""
        if self._states_cache is not None:
            return self._states_cache

        try:
            resp = self._session.get(f"{self.BASE_URL}/listStates")
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch states: {e}")

        states = []
        for item in data:
            states.append(State(
                name=item.get("state_name", ""),
                code=item.get("state_code", ""),
                number=str(item.get("state_num", "")),
                category=item.get("category", "State"),
            ))

        # Sort alphabetically
        states.sort(key=lambda s: s.name)
        self._states_cache = states
        return states

    def list_counties(self, state_code: str) -> list[County]:
        """Fetch counties for a state. Cached per state code."""
        if state_code in self._counties_cache:
            return self._counties_cache[state_code]

        try:
            resp = self._session.get(
                f"{self.BASE_URL}/listCounties/{state_code}"
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch counties for {state_code}: {e}")

        counties = []
        for item in data:
            counties.append(County(
                state_code=item.get("state_code", ""),
                fips_code=item.get("fips_code", ""),
                county_name=item.get("county_name", ""),
                town_name=item.get("town_name", ""),
                category=item.get("category", ""),
            ))

        counties.sort(key=lambda c: c.county_name)
        self._counties_cache[state_code] = counties
        return counties

    def get_fmr(self, county_fips: str) -> FMRData:
        """Fetch Fair Market Rent data for a county."""
        try:
            resp = self._session.get(f"{self.BASE_URL}/data/{county_fips}")
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch FMR data: {e}")

        # Navigate to basicdata
        basic = data.get("data", {}).get("basicdata", {})

        return FMRData(
            efficiency=float(basic.get("Efficiency", 0)),
            one_bedroom=float(basic.get("One-Bedroom", 0)),
            two_bedroom=float(basic.get("Two-Bedroom", 0)),
            three_bedroom=float(basic.get("Three-Bedroom", 0)),
            four_bedroom=float(basic.get("Four-Bedroom", 0)),
            year=int(basic.get("year", 0)),
        )

    def get_state_code(self, state_name: str) -> str:
        """Look up the 2-letter state code by name."""
        states = self.list_states()
        for s in states:
            if s.name == state_name:
                return s.code
        return ""

    def get_county_fips(self, state_code: str, county_name: str) -> str:
        """Look up county FIPS code by state code and county name."""
        counties = self.list_counties(state_code)
        for c in counties:
            if c.county_name == county_name:
                return c.fips_code
        return ""

    def find_state_name(self, code_or_name: str) -> str:
        """Find the full state name by 2-letter code or name.

        Returns empty string if states haven't been loaded or no match.
        """
        if self._states_cache is None:
            return ""
        needle = code_or_name.strip().upper()
        for s in self._states_cache:
            if s.code.upper() == needle or s.name.upper() == needle:
                return s.name
        return ""

    def get_income_limits(self, state_code: str,
                          county_fips: str) -> IncomeLimitData:
        """Fetch Area Median Income from HUD Income Limits API."""
        try:
            # The IL endpoint uses a different base path
            url = (
                "https://www.huduser.gov/hudapi/public/il"
                f"/{state_code}/{county_fips}"
            )
            resp = self._session.get(url)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch income limits: {e}")

        # Parse median income from response
        il_data = data.get("data", {})
        median = float(il_data.get("median_income", 0) or 0)
        county = il_data.get("county_name", "")
        year = int(il_data.get("year", 0) or 0)

        return IncomeLimitData(
            median_income=median,
            county_name=county,
            year=year,
        )


class RapidApiService:
    """Client for the US Zip Code Information API on RapidAPI."""

    BASE_URL = "https://us-zip-code-information.p.rapidapi.com/"

    def __init__(self, api_key: str):
        self._session = TimeoutSession(timeout=10)
        self._session.headers["X-RapidAPI-Key"] = api_key
        self._session.headers["X-RapidAPI-Host"] = (
            "us-zip-code-information.p.rapidapi.com"
        )

        # Cache
        self._zip_cache: dict[str, ZipInfo] = {}

    def update_key(self, api_key: str):
        """Update the RapidAPI key."""
        self._session.headers["X-RapidAPI-Key"] = api_key

    def get_zip_info(self, zipcode: str) -> ZipInfo:
        """Fetch zip code information. Cached per zip code."""
        if zipcode in self._zip_cache:
            return self._zip_cache[zipcode]

        try:
            resp = self._session.get(
                self.BASE_URL,
                params={"zipcode": zipcode},
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch zip info for {zipcode}: {e}")

        if isinstance(data, list) and len(data) > 0:
            item = data[0]
        elif isinstance(data, dict):
            item = data
        else:
            return ZipInfo(zip_code=zipcode)

        info = ZipInfo(
            zip_code=str(item.get("ZipCode", zipcode)),
            city=item.get("City", ""),
            state=item.get("State", ""),
            county=item.get("County", item.get("CountyMixedCase", "")),
            latitude=float(item.get("Latitude", 0)),
            longitude=float(item.get("Longitude", 0)),
            area_code=str(item.get("AreaCode", "")),
            time_zone=item.get("TimeZone", ""),
        )

        self._zip_cache[zipcode] = info
        return info


class ApiNinjasService:
    """Client for API Ninjas — property tax rates and mortgage rates.

    Free tier: 50,000 requests/month.
    Endpoints:
        - /v1/propertytax?zip={zip} — tax rate by ZIP
        - /v1/mortgagerate — current mortgage rates
    """

    BASE_URL = "https://api.api-ninjas.com/v1"

    def __init__(self, api_key: str):
        self._session = TimeoutSession(timeout=10)
        self._session.headers["X-Api-Key"] = api_key

        # Caches
        self._tax_cache: dict[str, PropertyTaxData] = {}
        self._rate_cache: Optional[tuple[MortgageRateData, datetime]] = None

    def update_key(self, api_key: str):
        self._session.headers["X-Api-Key"] = api_key

    def get_property_tax(self, zip_code: str) -> PropertyTaxData:
        """Fetch property tax rate for a ZIP code. Cached per ZIP."""
        if zip_code in self._tax_cache:
            return self._tax_cache[zip_code]

        try:
            resp = self._session.get(
                f"{self.BASE_URL}/propertytax",
                params={"zip": zip_code},
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch property tax for {zip_code}: {e}")

        # API returns a list; take first result
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
        elif isinstance(data, dict):
            item = data
        else:
            return PropertyTaxData()

        rate = float(item.get("overall_tax_rate", 0) or 0)
        result = PropertyTaxData(overall_tax_rate=rate)
        self._tax_cache[zip_code] = result
        return result

    def get_mortgage_rates(self) -> MortgageRateData:
        """Fetch current mortgage rates. Cached for 24 hours."""
        if self._rate_cache:
            cached, ts = self._rate_cache
            if datetime.now() - ts < timedelta(hours=24):
                return cached

        try:
            resp = self._session.get(f"{self.BASE_URL}/mortgagerate")
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch mortgage rates: {e}")

        # API returns a dict with rate fields
        result = MortgageRateData(
            thirty_year_fixed=float(data.get("30YearFixedRate", 0) or 0),
            fifteen_year_fixed=float(data.get("15YearFixedRate", 0) or 0),
            five_one_arm=float(data.get("5/1YearAdjustableRate", 0) or 0),
        )
        self._rate_cache = (result, datetime.now())
        return result


class FREDApiService:
    """Client for the FRED (Federal Reserve Economic Data) API.

    Free tier: 120 requests/minute.
    Key series:
        - MORTGAGE30US: 30-year fixed mortgage rate (weekly)
        - CUUR0000SEHA: CPI Rent of Primary Residence
        - RRVRUSQ156N: Rental Vacancy Rate (quarterly)
    """

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._session = TimeoutSession(timeout=15)
        self._cache: dict[str, tuple[list, datetime]] = {}

    def update_key(self, api_key: str):
        self._api_key = api_key

    def _get_series(self, series_id: str,
                    observation_start: str = "") -> list[dict]:
        """Fetch observations for a FRED series. Cached for 24 hours."""
        cache_key = f"{series_id}:{observation_start}"
        if cache_key in self._cache:
            data, ts = self._cache[cache_key]
            if datetime.now() - ts < timedelta(hours=24):
                return data

        params = {
            "series_id": series_id,
            "api_key": self._api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 120,  # Enough for 5yr of monthly or 2yr of weekly data
        }
        if observation_start:
            params["observation_start"] = observation_start

        try:
            resp = self._session.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch FRED series {series_id}: {e}")

        observations = data.get("observations", [])
        self._cache[cache_key] = (observations, datetime.now())
        return observations

    def get_current_mortgage_rate(self) -> Optional[float]:
        """Get the latest 30-year fixed mortgage rate."""
        obs = self._get_series("MORTGAGE30US")
        for o in obs:
            val = o.get("value", ".")
            if val != ".":
                return float(val)
        return None

    def get_rent_cpi_growth(self, years: int = 5) -> Optional[float]:
        """Get annualized CPI rent growth over the last N years."""
        start = datetime.now() - timedelta(days=years * 365)
        obs = self._get_series(
            "CUUR0000SEHA",
            observation_start=start.strftime("%Y-%m-%d"),
        )
        # Need first and last valid observations
        valid = [(o["date"], float(o["value"]))
                 for o in obs if o.get("value", ".") != "."]
        if len(valid) < 2:
            return None
        # obs is sorted desc, so first is newest, last is oldest
        newest_val = valid[0][1]
        oldest_val = valid[-1][1]
        if oldest_val <= 0:
            return None
        total_growth = newest_val / oldest_val
        annualized = total_growth ** (1.0 / years) - 1.0
        return annualized

    def get_vacancy_rate(self) -> Optional[float]:
        """Get the latest national rental vacancy rate."""
        obs = self._get_series("RRVRUSQ156N")
        for o in obs:
            val = o.get("value", ".")
            if val != ".":
                return float(val) / 100.0  # Convert from % to decimal
        return None


class OpenFEMAService:
    """Client for OpenFEMA National Risk Index — no API key required.

    Returns flood/hazard risk data by county.
    """

    BASE_URL = (
        "https://hazards.fema.gov/nri/services/arcgis/rest/services"
        "/public/FEMA_NRI_COUNTIES/MapServer/0/query"
    )

    def __init__(self):
        self._session = TimeoutSession(timeout=15)
        self._cache: dict[str, FloodRiskData] = {}

    def get_flood_risk(self, county_fips: str) -> FloodRiskData:
        """Fetch flood risk for a county. Cached per county FIPS."""
        if county_fips in self._cache:
            return self._cache[county_fips]

        try:
            params = {
                "where": f"STCOFIPS='{county_fips}'",
                "outFields": "RISK_SCORE,RISK_RATNG,COUNTY",
                "f": "json",
                "returnGeometry": "false",
            }
            resp = self._session.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch flood risk: {e}")

        features = data.get("features", [])
        if not features:
            return FloodRiskData()

        attrs = features[0].get("attributes", {})
        result = FloodRiskData(
            risk_score=float(attrs.get("RISK_SCORE", 0) or 0),
            risk_rating=attrs.get("RISK_RATNG", ""),
            county_name=attrs.get("COUNTY", ""),
        )
        self._cache[county_fips] = result
        return result
