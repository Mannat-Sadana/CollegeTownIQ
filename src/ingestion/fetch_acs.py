import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from dotenv import load_dotenv
import os


# Project configuration
YEAR = 2024
STATE_FIPS = "42"
COUNTY_FIPS = "027"

BASE_URL = f"https://api.census.gov/data/{YEAR}/acs/acs5"

VARIABLES = [
    "NAME",
    "B25064_001E",  # Median gross rent
    "B25031_001E",  # Median gross rent, total
    "B25031_002E",  # No bedroom
    "B25031_003E",  # 1 bedroom
    "B25031_004E",  # 2 bedrooms
    "B25031_005E",  # 3 bedrooms
    "B25031_006E",  # 4 bedrooms
    "B25031_007E",  # 5+ bedrooms
    "B25071_001E",  # Median gross rent as a percentage of household income
    "B19013_001E",  # Median household income
    "B08201_001E",  # Total households
    "B08201_002E",  # Households with no vehicle
]


def fetch_acs_data() -> list[list[str]]:
    """Fetch 2024 ACS 5-year tract-level data for Centre County, Pennsylvania."""

    load_dotenv()

    api_key = os.getenv("CENSUS_API_KEY")

    if not api_key:
        raise RuntimeError(
            "CENSUS_API_KEY was not found. Check your .env file."
        )

    params = {
        "get": ",".join(VARIABLES),
        "for": "tract:*",
        "in": f"state:{STATE_FIPS} county:{COUNTY_FIPS}",
        "key": api_key,
    }

    url = f"{BASE_URL}?{urlencode(params)}"

    with urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def save_raw_data(data: list[list[str]]) -> None:
    """Save the raw Census API response to the project's raw data directory."""

    output_path = Path("data/raw/acs_2024_centre_county_tracts.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Saved Census data to {output_path}")


if __name__ == "__main__":
    acs_data = fetch_acs_data()

    print(f"Downloaded {len(acs_data) - 1} census tracts.")

    save_raw_data(acs_data)