import json
from pathlib import Path

import nd2_omezarr_converter

PACKAGE = "nd2_omezarr_converter"
PACKAGE_DIR = Path(nd2_omezarr_converter.__file__).parent
MANIFEST_FILE = PACKAGE_DIR / "__FRACTAL_MANIFEST__.json"
with MANIFEST_FILE.open("r") as f:
    MANIFEST = json.load(f)
    TASK_LIST = MANIFEST["task_list"]
