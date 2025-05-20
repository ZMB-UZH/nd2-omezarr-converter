from pathlib import Path

from nd2_omezarr_converter.wrappers import (
    Nd2InputModel,
    convert_nd2_to_omezarr,
)


def test_basic_worflow(temp_dir):
    path = temp_dir / "ND_Acquisitions_nd2" / "01_0c_0z.nd2"
    convert_nd2_to_omezarr(
        zarr_dir=temp_dir / "plate",
        acquisitions=path,
    )

    path = temp_dir / "WellPlate_Jobs_3w6p2c0z0t_overlap" / "20250506_124144_018"
    convert_nd2_to_omezarr(
        zarr_dir=temp_dir / "plate",
        acquisitions=[
            Nd2InputModel(path=str(path), plate_name="test_plate", acquisition_id=1)
        ],
    )
