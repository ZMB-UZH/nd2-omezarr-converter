"""nd2 to OME-Zarr conversion task initialization."""

import logging
from pathlib import Path

from fractal_converters_tools.omezarr_plate_writers import initiate_ome_zarr_plates
from fractal_converters_tools.task_common_models import (
    AdvancedComputeOptions,
)
from fractal_converters_tools.task_init_tools import build_parallelization_list
from fractal_converters_tools.tiled_image import PlatePathBuilder, SimplePathBuilder
from pydantic import BaseModel, Field, validate_call

from nd2_omezarr_converter.nd2_utils import parse_nd2_acquisition

logger = logging.getLogger(__name__)


class Nd2InputModel(BaseModel):
    """Acquisition metadata.

    Attributes:
        path (str): Path to the nd2 file, or a folder containing nd2 files.
        plate_name (Optional[str]): Optional name of the plate.
            If not provided, the plate name will be inferred from the
            nd2 file name or folder name.
        acquisition_id: Acquisition ID, used to identify multiple rounds
            of acquisitions for the same plate.
    """

    path: str
    plate_name: str | None = None
    acquisition_id: int = Field(default=0, ge=0)


class AdvancedOptions(AdvancedComputeOptions):
    """Advanced options for the conversion.

    Attributes:
        num_levels (int): The number of resolution levels in the pyramid.
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

    # set invert_y to True by default
    # (for use with ZMB Nikon SD microscope, test for others)
    invert_y: bool = True


@validate_call
def convert_nd2_init_task(
    *,
    # Fractal parameters
    zarr_dir: str,
    # Task parameters
    acquisitions: list[Nd2InputModel],
    overwrite: bool = False,
    advanced_options: AdvancedOptions = AdvancedOptions(),  # noqa: B008
):
    """Initialize the nd2 to OME-Zarr conversion task.

    Args:
        zarr_dir (str): Directory to store the Zarr files.
        acquisitions (list[AcquisitionInputModel]): List of raw acquisitions to convert
            to OME-Zarr.
        overwrite (bool): Overwrite existing Zarr files.
        advanced_options (AdvancedComputeOptions): Advanced options for the conversion.
    """
    if not acquisitions:
        raise ValueError("No acquisitions provided.")

    zarr_dir_path = Path(zarr_dir)

    if not zarr_dir_path.exists():
        logger.info(f"Creating directory: {zarr_dir_path}")
        zarr_dir_path.mkdir(parents=True)

    # prepare the parallel list of zarr urls
    tiled_images = []
    for acq in acquisitions:
        _tiled_images = parse_nd2_acquisition(
            acq_path=Path(acq.path),
            plate_name=acq.plate_name,
            acquisition_id=acq.acquisition_id,
        )

        if not _tiled_images:
            logger.warning(f"No images found in {acq.path}")
            continue
        tiled_images.extend(list(_tiled_images))

    # Common fractal-converters-tools functions
    parallelization_list = build_parallelization_list(
        zarr_dir=zarr_dir_path,
        tiled_images=tiled_images,
        overwrite=overwrite,
        advanced_compute_options=advanced_options,
    )
    logger.info(f"Total {len(parallelization_list)} images to convert.")

    types = {type(tiled_image.path_builder) for tiled_image in tiled_images}
    if types == {PlatePathBuilder}:
        initiate_ome_zarr_plates(
            zarr_dir=zarr_dir_path,
            tiled_images=tiled_images,
            overwrite=overwrite,
        )
        logger.info(f"Initialized OME-Zarr Plate at: {zarr_dir_path}")
    elif types == {SimplePathBuilder, PlatePathBuilder}:
        raise ValueError(
            "Detected some plate acquisitions and some non-plate acquisitions. "
            "This is currently not supported. Please run the task separately for "
            "plate and non-plate acquisitions."
        )
    return {"parallelization_list": parallelization_list}


if __name__ == "__main__":
    from fractal_task_tools.task_wrapper import run_fractal_task

    run_fractal_task(task_function=convert_nd2_init_task, logger_name=logger.name)
