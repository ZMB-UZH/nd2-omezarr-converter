### Purpose
- Convert a Nikon .nd2 file, or a folder of .nd2 files to an OME-Zarr file or plate.

### Outputs
- An OME-Zarr image or plate.

### Limitations
- This task has been tested on a limited set of acquisitions (see https://zenodo.org/records/15411420). It may not work on all Nikon .nd2 acquisitions.

### Expected inputs
The following input layouts are supported. (The names in curly braces `{}` can be freely chosen by the user.)

- Single file acquisition
	- acquisition path input:
		```text
		.../{filename}.nd2
		```
	- output: single OME-Zarr image

- Folder of single file acquisitions
	- acquisition path input:
		```text
		.../{folder}
		----/{filename1}.nd2
		----/{filename2}.nd2
		...
		```
	- output: multiple OME-Zarr images

- Folder of nd2 files belonging to a plate acquisitions
	- acquisition path input:
		```text
		.../{folder}
		----/WellA01{filename1}.nd2
		----/WellC02{filename2}.nd2
		...
		```
	- output: OME-Zarr plate
	- Note:
		- This works for files generated with the standard plate acquisition JOBS script at the ZMB Nikon Spinning Disk
		- The filenames MUST start with `Well` and the well name. Valid options for well names are e.g. `A1`, `A01`
		- If there are other .nd2 files in the folder that do not adhere to this, individual OME-Zarr images will be created instead of a plate
		- Splitting the positions into multiple files is NOT supported at the moment. (e.g. filenames like `WellB02_PointB02_0000_{filename}.nd2`)
