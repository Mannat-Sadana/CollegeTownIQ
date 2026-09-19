from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

YEAR = 2024
STATE_FIPS = "42"
OUTPUT_DIR = Path("data/raw/tiger_2024_pa_tracts")

DOWNLOAD_URL = (
    f"https://www2.census.gov/geo/tiger/TIGER{YEAR}/TRACT/"
    f"tl_{YEAR}_{STATE_FIPS}_tract.zip"
)

ZIP_PATH = OUTPUT_DIR / f"tl_{YEAR}_{STATE_FIPS}_tract.zip"


def download_tract_shapefile() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading Pennsylvania census tract boundaries...")
    urlretrieve(DOWNLOAD_URL, ZIP_PATH)

    print("Extracting shapefile...")
    with ZipFile(ZIP_PATH, "r") as zip_file:
        zip_file.extractall(OUTPUT_DIR)

    print("Census tract shapefile ready.")


if __name__ == "__main__":
    download_tract_shapefile()