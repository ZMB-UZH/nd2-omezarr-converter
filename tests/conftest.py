import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pytest

CACHE_DIR = Path(tempfile.gettempdir()) / "test_cache"


def download_and_cache(cache_dir, base_temp, zenodo_id, zip_file_name):
    """
    Download a zip file from Zenodo and cache it locally.

    - Download the zip file and unzip it, if it doesn't already exist in the
      cache directory.
    - Copy the unzipped folder to a temporary directory for testing.
    """
    # Ensure the cache directory exists
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Paths for the cached zip file and unzipped folder
    cached_zip_file = cache_dir / zip_file_name
    cached_unzipped_folder = cache_dir / zip_file_name.replace(".zip", "")

    # Download the zip file if it doesn't exist
    if not cached_zip_file.exists():
        subprocess.run(
            [
                "zenodo_get",
                zenodo_id,
                "-o",
                str(cache_dir),
                "-g",
                zip_file_name,
            ],
            check=True,
        )
    else:
        print(f"File {zip_file_name} already exists in cache. Skipping download.")

    # Unzip the folder if it hasn't been unzipped yet
    if not cached_unzipped_folder.exists():
        with zipfile.ZipFile(cached_zip_file, "r") as zip_ref:
            zip_ref.extractall(cache_dir)
    else:
        print(
            f"Unzipped folder {cached_unzipped_folder} already exists. "
            "Skipping extraction."
        )

    # Copy the unzipped folder to the temporary directory
    temp_unzipped_folder = base_temp / cached_unzipped_folder.name
    if not temp_unzipped_folder.exists():
        shutil.copytree(cached_unzipped_folder, temp_unzipped_folder)
    else:
        print(
            f"Unzipped folder already exists in temp directory: {temp_unzipped_folder}"
        )


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    # Create a temporary directory that lasts for the session
    base_temp = tmp_path_factory.mktemp("data")

    download_and_cache(
        CACHE_DIR,
        base_temp,
        "10.5281/zenodo.15411419",
        "WellPlate_Jobs_3w6p2c0z0t_overlap.zip",
    )
    download_and_cache(
        CACHE_DIR,
        base_temp,
        "10.5281/zenodo.15411419",
        "ND_Acquisitions_nd2.zip",
    )

    return base_temp
