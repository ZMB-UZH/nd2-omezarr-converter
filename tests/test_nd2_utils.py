import nd2
import numpy as np
import numpy.testing as npt

from nd2_omezarr_converter.nd2_utils import (
    build_tiled_image,
    build_tiles,
    nd2TileLoader,
    parse_input_path,
    parse_nd2_acquisition,
    parse_well_info,
)


def test_nd2TileLoader(temp_dir):
    path = (
        temp_dir
        / "WellPlate_Jobs_3w6p2c0z0t_overlap"
        / "20250506_124144_018"
        / "WellB02_ChannelSD DAPI- EM,SD GFP - EM_Seq0000.nd2"
    )
    tile_loader = nd2TileLoader(path=str(path), p=0)

    # Check if the tile loader is initialized correctly
    assert tile_loader is not None
    assert tile_loader.path == str(path)
    assert tile_loader.p == 0
    assert tile_loader.dtype == "uint16"
    data = tile_loader.load()
    assert data is not None
    assert isinstance(data, np.ndarray)
    assert data.shape == (1, 2, 1, 512, 1024)


def test_build_tiles(temp_dir):
    path = (
        temp_dir
        / "WellPlate_Jobs_3w6p2c0z0t_overlap"
        / "20250506_124144_018"
        / "WellB02_ChannelSD DAPI- EM,SD GFP - EM_Seq0000.nd2"
    )
    nd2file = nd2.ND2File(path)
    tiles = list(build_tiles(nd2file))
    assert len(tiles) == 6
    tile = tiles[0]
    npt.assert_allclose(tile.top_l.x, 40162.8)
    npt.assert_allclose(tile.top_l.y, -22751.2)
    npt.assert_allclose(tile.top_l.z, 5720.22)
    npt.assert_allclose(tile.top_l.c, 0)
    npt.assert_allclose(tile.top_l.t, 0)


def test_parse_well_info():
    # Test with a valid filename
    fn = "some/path/WellB02_ChannelSD DAPI- EM,SD GFP - EM_Seq0000.nd2"
    row, col = parse_well_info(fn)
    assert row == "B"
    assert col == 2

    # Test with an invalid filename
    fn = "InvalidFilename.nd2"
    try:
        parse_well_info(fn)
    except ValueError as e:
        assert str(e) == "Well info not found in filename InvalidFilename.nd2"


def test_build_tiled_image(temp_dir):
    path = (
        temp_dir
        / "WellPlate_Jobs_3w6p2c0z0t_overlap"
        / "20250506_124144_018"
        / "WellB02_ChannelSD DAPI- EM,SD GFP - EM_Seq0000.nd2"
    )
    tiled_image = build_tiled_image(
        nd2_path=str(path),
        zarr_name="test_zarr",
        acquisition_id=1,
        plate=True,
    )

    assert len(tiled_image.tiles) == 6
    assert tiled_image.path == "test_zarr.zarr/B/2/1"
    assert tiled_image.channel_names == ["SD DAPI- EM", "SD GFP - EM"]
    assert tiled_image.wavelength_ids == ["438.0", "511.0"]


def test_parse_input_path(temp_dir):
    path = (
        temp_dir
        / "WellPlate_Jobs_3w6p2c0z0t_overlap"
        / "20250506_124144_018"
        / "WellB02_ChannelSD DAPI- EM,SD GFP - EM_Seq0000.nd2"
    )

    nd2_list, mode = parse_input_path(path)

    assert nd2_list == [path]
    assert mode == "single"

    path = temp_dir / "WellPlate_Jobs_3w6p2c0z0t_overlap" / "20250506_124144_018"

    nd2_list, mode = parse_input_path(path)

    assert nd2_list == [
        path / "WellB02_ChannelSD DAPI- EM,SD GFP - EM_Seq0000.nd2",
        path / "WellB03_ChannelSD DAPI- EM,SD GFP - EM_Seq0001.nd2",
        path / "WellC02_ChannelSD DAPI- EM,SD GFP - EM_Seq0002.nd2",
    ]
    assert mode == "plate"


def test_parse_nd2_acquisition(temp_dir):
    # Test with a single ND2 file
    path = temp_dir / "ND_Acquisitions_nd2" / "01_0c_0z.nd2"

    tiled_images = parse_nd2_acquisition(
        acq_path=path,
        plate_name="test_plate",
        acquisition_id=1,
    )
    assert len(tiled_images) == 1
    assert tiled_images[0].path == "test_plate.zarr"

    tiled_images = parse_nd2_acquisition(
        acq_path=path,
    )
    assert len(tiled_images) == 1
    assert tiled_images[0].path == "01_0c_0z.zarr"

    # Test with a folder containing ND2 files (non-plate)
    path = temp_dir / "ND_Acquisitions_nd2"

    tiled_images = parse_nd2_acquisition(
        acq_path=path,
        plate_name="test_plate",
        acquisition_id=1,
    )
    assert len(tiled_images) == 13
    assert tiled_images[0].path == "test_plate_01_0c_0z.zarr"

    tiled_images = parse_nd2_acquisition(
        acq_path=path,
    )
    assert len(tiled_images) == 13
    assert tiled_images[0].path == "ND_Acquisitions_nd2_01_0c_0z.zarr"

    # Test with a plate folder
    path = temp_dir / "WellPlate_Jobs_3w6p2c0z0t_overlap" / "20250506_124144_018"

    tiled_images = parse_nd2_acquisition(
        acq_path=path,
        plate_name="test_plate",
        acquisition_id=1,
    )
    assert len(tiled_images) == 3
    assert tiled_images[0].path == "test_plate.zarr/B/2/1"
    assert tiled_images[1].path == "test_plate.zarr/B/3/1"
    assert tiled_images[2].path == "test_plate.zarr/C/2/1"

    tiled_images = parse_nd2_acquisition(
        acq_path=path,
    )
    assert len(tiled_images) == 3
    assert tiled_images[0].path == "20250506_124144_018.zarr/B/2/0"
    assert tiled_images[1].path == "20250506_124144_018.zarr/B/3/0"
    assert tiled_images[2].path == "20250506_124144_018.zarr/C/2/0"
