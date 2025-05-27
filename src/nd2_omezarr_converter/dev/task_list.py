"""Contains the list of tasks available to fractal."""

from fractal_task_tools.task_models import (
    ConverterCompoundTask,
)

AUTHORS = "Flurin Sturzenegger"
DOCS_LINK = None
INPUT_MODELS = []

TASK_LIST = [
    ConverterCompoundTask(
        name="Convert nd2 to OME-Zarr",
        executable_init="convert_nd2_init_task.py",
        executable="convert_nd2_compute_task.py",
        meta_init={"cpus_per_task": 1, "mem": 4000},
        meta={"cpus_per_task": 1, "mem": 12000},
        category="Conversion",
        tags=[
            "Nikon",
            "ND2",
            "Converter",
        ],
        docs_info="file:docs_info/convert_nd2_task.md",
    ),
]
