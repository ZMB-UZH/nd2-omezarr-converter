from pathlib import Path

import pytest

from nd2_omezarr_converter.wrappers import (
    Nd2InputModel,
    convert_nd2_to_omezarr,
)


def test_basic_worflow(temp_dir):
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
