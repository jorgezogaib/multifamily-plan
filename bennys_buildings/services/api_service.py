"""API service — HUD and RapidAPI integration.

Handles all external API calls with caching, error handling, and
response parsing. Designed for threaded use from the controller.
"""

import requests
from typing import Optional

from models.data_types import State, County, FMRData, ZipInfo


class APIError(Exception):
    """Raised when an API call fails."""
    pass


class HUDApiService:
    """Client for the HUD User Fair Market Rent API.

    Endpoints:
        - /fmr/listStates — list all US states/territories
        - /fmr/listCounties/{stateCode} — counties in a state
        - /fmr/data/{countyFIPS} — Fair Market Rent data
    """

    BASE_URL = "https://www.huduser.gov/hudapi/public/fmr"

    def __init__(self, token: str):
        self._session = requests.Session()
        self._session.headers["Authorization"] = f"Bearer {token}"
        self._session.timeout = 15

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


class RapidApiService:
    """Client for the US Zip Code Information API on RapidAPI."""

    BASE_URL = "https://us-zip-code-information.p.rapidapi.com/"

    def __init__(self, api_key: str):
        self._session = requests.Session()
        self._session.headers["X-RapidAPI-Key"] = api_key
        self._session.headers["X-RapidAPI-Host"] = (
            "us-zip-code-information.p.rapidapi.com"
        )
        self._session.timeout = 10

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
