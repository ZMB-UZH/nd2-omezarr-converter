from pathlib import Path

import numpy.testing as npt
import pytest
from ngio import open_ome_zarr_container

from nd2_omezarr_converter.wrappers import (
    Nd2InputModel,
    convert_nd2_to_omezarr,
)


def test_basic_workflow(temp_dir):
    # Test single file conversion
    path = temp_dir / "ND_Acquisitions_nd2" / "01_0c_0z.nd2"
    convert_nd2_to_omezarr(
        zarr_dir=temp_dir / "plate",
        acquisitions=path,
    )

    # Test folder conversion
    path = temp_dir / "ND_Acquisitions_nd2"
    convert_nd2_to_omezarr(
        zarr_dir=temp_dir / "plate",
        acquisitions=path,
    )

    # Test plate conversion
    path = temp_dir / "WellPlate_Jobs_3w6p2c0z0t_overlap" / "20250506_124144_018"
    convert_nd2_to_omezarr(
        zarr_dir=temp_dir / "plate",
        acquisitions=[
            Nd2InputModel(path=str(path), plate_name="test_plate", acquisition_id=1)
        ],
        # tiling_mode="none",
    )
    # TODO: Output can't be read by napari-ome-zarr because well shapes are not
    # consistent across wells. Check why.

    # Test mixed acquisitions
    path1 = temp_dir / "WellPlate_Jobs_3w6p2c0z0t_overlap" / "20250506_124144_018"
    path2 = temp_dir / "ND_Acquisitions_nd2" / "01_0c_0z.nd2"
    with pytest.raises(ValueError):
        convert_nd2_to_omezarr(
            zarr_dir=temp_dir / "plate",
            acquisitions=[
                Nd2InputModel(
                    path=str(path1), plate_name="test_plate", acquisition_id=1
                ),
                Nd2InputModel(
                    path=str(path2), plate_name="test_plate", acquisition_id=1
                ),
            ],
        )


def test_original_coordinates(temp_dir):
    path = temp_dir / "ND_Acquisitions_nd2" / "09_XY2x3tiled_2c_0z.nd2"
    convert_nd2_to_omezarr(
        zarr_dir=temp_dir / "plate",
        acquisitions=path,
    )
    zarr_url = temp_dir / "plate" / "09_XY2x3tiled_2c_0z.zarr"
    ome_zarr_container = open_ome_zarr_container(zarr_url)
    rois = ome_zarr_container.get_roi_table("FOV_ROI_table").rois()
    npt.assert_allclose(rois[0].x_micrometer_original, -17788.549785)
    npt.assert_allclose(rois[0].y_micrometer_original, 7291.308407)
    npt.assert_allclose(rois[0].z_micrometer_original, 0.0)
