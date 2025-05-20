"""Tools to convert nd2 files to ome-zarr."""

import logging
import re
from collections.abc import Generator
from pathlib import Path
from typing import Any

import nd2
import numpy as np
from fractal_converters_tools.tile import Point, Tile, Vector
from fractal_converters_tools.tiled_image import (
    PlatePathBuilder,
    SimplePathBuilder,
    TiledImage,
)
from ngio import PixelSize

logger = logging.getLogger(__name__)


class nd2TileLoader:
    """nd2 tile loader."""

    def __init__(self, path: str, p: int):
        """Initialize LifTileLoader."""
        self.path = path
        self.p = p

    @property
    def dtype(self):
        """Get the data type of the tile."""
        with nd2.ND2File(self.path) as nd2file:
            dtype = nd2file.dtype
        return dtype

    def load(self) -> np.ndarray:
        """Load the tile data."""
        tile_data = nd2.imread(self.path, xarray=True, dask=True)
        if "P" in tile_data.dims:
            tile_data = tile_data.isel(P=self.p)
        if not set(tile_data.dims).issubset(
            ("T", "C", "Z", "Y", "X")
        ): # pragma: no cover
            raise ValueError(
                f"Data can only have dimensions T, C, Z, Y, X. Found: {tile_data.dims}"
            )
        if "Z" not in tile_data.dims:
            tile_data = tile_data.expand_dims(Z=1, axis=0)
        if "C" not in tile_data.dims:
            tile_data = tile_data.expand_dims(C=1, axis=0)
        if "T" not in tile_data.dims:
            tile_data = tile_data.expand_dims(T=1, axis=0)
        if tile_data.dims != ("T", "C", "Z", "Y", "X"):
            tile_data = tile_data.transpose("T", "C", "Z", "Y", "X")

        return tile_data.data.compute()


def build_tiles(nd2file) -> Generator[Tile, Any, None]:
    """Build tiles from nd2 file."""
    shape_x = nd2file.sizes["X"] if "X" in nd2file.sizes else 1
    shape_y = nd2file.sizes["Y"] if "Y" in nd2file.sizes else 1
    shape_z = nd2file.sizes["Z"] if "Z" in nd2file.sizes else 1
    shape_c = nd2file.sizes["C"] if "C" in nd2file.sizes else 1
    shape_t = nd2file.sizes["T"] if "T" in nd2file.sizes else 1

    # scale factors [um]/[px]
    scale_x = nd2file.voxel_size().x
    scale_y = nd2file.voxel_size().y
    scale_z = nd2file.voxel_size().z
    scale_t = 1  # TODO: read correctly from metadata

    # [um]
    length_x = shape_x * scale_x
    length_y = shape_y * scale_y
    length_z = shape_z * scale_z
    length_t = shape_t * scale_t

    if "P" in nd2file.sizes:
        loops = {experiment.type: experiment for experiment in nd2file.experiment}
        if "XYPosLoop" not in loops.keys(): # pragma: no cover
            raise ValueError(
                f"The nd2 file {nd2file.path} contains multiple positions, "
                "but no XYPosLoop was found in metadata."
            )
        for p, pnt in enumerate(loops["XYPosLoop"].parameters.points):
            top_l = Point(
                x=pnt.stagePositionUm.x,
                y=pnt.stagePositionUm.y,
                #z=pnt.stagePositionUm.z,
                z=0,  # TODO: z != 0 needs to be fixed in fractal-converters-tools
                c=0,
                t=0,
            )
            diag = Vector(x=length_x, y=length_y, z=length_z, c=shape_c, t=length_t)
            tile_loader = nd2TileLoader(path=nd2file.path, p=p)
            pixel_size = PixelSize(x=scale_x, y=scale_y, z=scale_z)
            tile = Tile(
                top_l=top_l,
                diag=diag,
                pixel_size=pixel_size,
                data_loader=tile_loader,
            )
            yield tile
    else:
        # TODO: check if this holds...
        pnt = nd2file.frame_metadata(0).channels[0].position
        top_l = Point(
            x=pnt.stagePositionUm.x,
            y=pnt.stagePositionUm.y,
            #z=pnt.stagePositionUm.z,
            z=0,  # TODO: z != 0 needs to be fixed in fractal-converters-tools
            c=0,
            t=0,
        )
        diag = Vector(x=length_x, y=length_y, z=length_z, c=shape_c, t=length_t)
        pixel_size = PixelSize(x=scale_x, y=scale_y, z=scale_z)
        tile_loader = nd2TileLoader(path=nd2file.path, p=None)
        tile = Tile(
            top_l=top_l,
            diag=diag,
            pixel_size=pixel_size,
            data_loader=tile_loader,
        )
        yield tile


def parse_well_info(fn):
    """Get well info from filename."""
    pattern = r"Well([A-Z])(\d+)"
    match = re.search(pattern, Path(fn).stem)
    if match:
        row = match.group(1)
        col = int(match.group(2))
        return row, col
    else:
        raise ValueError(f"Well info not found in filename {fn}")


def build_tiled_image(
    nd2_path: str | Path,
    zarr_name: str,
    acquisition_id: int | None = None,
    plate: bool = False,
) -> list[TiledImage]:
    """Build tiled image from nd2 file."""
    nd2file = nd2.ND2File(nd2_path)

    # load channel info
    channel_names = []
    channel_wavelengths = []
    for channel in nd2file.metadata.channels:
        channel_names.append(channel.channel.name)
        # take emission wavelength (excitation wavelength is not loaded correctly)
        channel_wavelengths.append(str(channel.channel.emissionLambdaNm))

    # Define path builder for relative ome-zarr path
    if plate:
        row, col = parse_well_info(nd2_path)
        _path_builder = PlatePathBuilder(
            plate_name=zarr_name,
            row=row,
            column=col,
            acquisition_id=acquisition_id if acquisition_id is not None else 0,
        )
    else:
        if acquisition_id is not None:
            raise NotImplementedError(
                "acquisition_id is not yet supported for non-plate data."
            )
            # TODO: add support for acquisition_id
            # (needs to be implemented in SimplePathBuilder in fractal_converters_tools)
        _path_builder = SimplePathBuilder(
            path=zarr_name,
        )

    # Build tiles
    tiled_image = TiledImage(
        name=nd2_path,
        path_builder=_path_builder,
        channel_names=channel_names,
        wavelength_ids=channel_wavelengths,
    )
    for tile in build_tiles(nd2file):
        tiled_image.add_tile(tile)

    nd2file.close()
    return tiled_image


def parse_input_path(path: str | Path) -> tuple[list[Path], str]:
    """Parse input path and return list of nd2 files and mode.

    mode can be one of:
        'single' - single nd2 file
        'folder' - folder with nd2 files
        'plate'  - folder with nd2 files corresponding to a plate
    """
    path = Path(path)
    if path.is_dir():
        paths = sorted(path.glob("*.nd2"))
        if not paths:
            raise ValueError(f"No nd2 files found in directory {path}")
        # check mode
        mode = "plate"
        for p in paths:
            try:
                parse_well_info(p)
            except ValueError:
                mode = "folder"
    elif path.is_file():
        if path.suffix != ".nd2":
            raise ValueError(f"File {path} is not an nd2 file")
        paths = [path]
        mode = "single"
    else:
        raise ValueError(f"Path {path} is neither a file nor a directory")

    return paths, mode


def parse_nd2_acquisition(
    acq_path: str | Path,
    plate_name: str | None = None,
    acquisition_id: int | None = None,
) -> list[TiledImage]:
    """Parse nd2 acquisition and return list of tiled images."""
    if not acq_path.exists():
        raise FileNotFoundError(f"File not found: {acq_path}")

    nd2_list, mode = parse_input_path(acq_path)

    # get zarr-name for entire plate
    if mode == "plate":
        if not plate_name:
            zarr_name = f"{Path(acq_path).stem}"
            zarr_name = zarr_name.replace(" ", "_")
        else:
            zarr_name = plate_name

    tiled_images = []
    for nd2_file in nd2_list:
        # get zarr-name for individual non-plate files
        if mode == "folder":
            if plate_name:
                zarr_name = f"{plate_name}_{Path(nd2_file).stem}"
            else:
                zarr_name = f"{Path(acq_path).stem}_{Path(nd2_file).stem}"
            zarr_name = zarr_name.replace(" ", "_")
        elif mode == "single":
            if plate_name:
                zarr_name = plate_name
            else:
                zarr_name = f"{Path(nd2_file).stem}"
            zarr_name = zarr_name.replace(" ", "_")

        if acquisition_id and mode != "plate":
            # TODO: add support for acquisition_id
            # (needs to be implemented in SimplePathBuilder in fractal_converters_tools)
            logger.warning(
                "acquisition_id is not supported for non-plate data. "
                "Setting acquisition_id to None."
            )
            acquisition_id = None

        tiled_images.append(
            build_tiled_image(
                nd2_path=nd2_file,
                zarr_name=zarr_name,
                acquisition_id=acquisition_id if mode == "plate" else None,
                plate=True if mode == "plate" else False,
            )
        )
    return tiled_images
