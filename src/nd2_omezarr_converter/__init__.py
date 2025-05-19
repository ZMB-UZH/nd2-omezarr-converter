"""
nd2 to OME-Zarr converter
"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("nd2-omezarr-converter")
except PackageNotFoundError:
    __version__ = "uninstalled"