"""Utility for running the init and compute tasks with a single function call."""

from pathlib import Path
from typing import Literal

def convert_nd2_to_omezarr(
    zarr_dir: Path | str,
    nd2_path: Path | str,
    overwrite: bool = False,
    num_levels: int = 5,
    tiling_mode: Literal["auto", "grid", "free", "none"] = "auto",
    swap_xy: bool = False,
    invert_x: bool = False,
    invert_y: bool = False,
    max_xy_chunk: int = 4096,
    z_chunk: int = 10,
    c_chunk: int = 1,
    t_chunk: int = 1,
):
    """Convert ND2 file(s) to OME-Zarr format.

    Args:
        zarr_dir (Path | str): Output path to save the OME-Zarr file.
        nd2_path (Path | str: Path to raw data (either a single .nd2 file or a
            folder containing .nd2 files).
        overwrite (bool): If True, the zarr store will be overwritten.
        num_levels (int): The number of resolution levels. Defaults to 5.
        tiling_mode (Literal["auto", "grid", "free", "none"]): Specify the tiling mode.
            "auto" will automatically determine the tiling mode.
            "grid" if the input data is a grid, it will be tiled using snap-to-grid.
            "free" will remove any overlap between tiles using a snap-to-corner
            approach.
            "none" will write the positions as is, using the microscope metadata.
        swap_xy (bool): Swap x and y axes coordinates in the metadata. This is sometimes
            necessary to ensure correct image tiling and registration.
        invert_x (bool): Invert x axis coordinates in the metadata. This is
            sometimes necessary to ensure correct image tiling and registration.
        invert_y (bool): Invert y axis coordinates in the metadata. This is
            sometimes necessary to ensure correct image tiling and registration.
        max_xy_chunk (int): XY chunk size is set as the minimum of this value and the
            microscope tile size.
        z_chunk (int): Z chunk size.
        c_chunk (int): C chunk size.
        t_chunk (int): T chunk size.
    """
    raise NotImplementedError("This function is not implemented yet.")