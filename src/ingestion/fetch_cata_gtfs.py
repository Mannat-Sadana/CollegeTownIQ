from pathlib import Path
from urllib.request import urlopen

from zipfile import ZipFile
from io import BytesIO

OUTPUT_DIR = Path("data/raw/cata_gtfs")

GTFS_URL = "https://catabus.com/wp-content/uploads/google_transit.zip"


def download_gtfs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading CATA GTFS feed...")

    with urlopen(GTFS_URL) as response:
        archive_data = response.read()

    print("Extracting GTFS files...")

    with ZipFile(BytesIO(archive_data)) as zip_file:
        zip_file.extractall(OUTPUT_DIR)

    print("CATA GTFS feed ready.")


if __name__ == "__main__":
    download_gtfs()