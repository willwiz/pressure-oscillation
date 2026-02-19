# /// script
# dependencies: []
# ///
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from code_pkg.types import ProblemDef, TopDef

DEFAULT_MESH: TopDef = {
    "home": Path("mesh"),
    "solid": {
        1: {"name": "solid_lin", "elem": "TRIANGLE_ELEMENT"},
        2: {"name": "solid_quad", "elem": "TRIANGLE_ELEMENT"},
    },
    "fluid": {
        0: {"name": "fluid_const", "elem": "TRIANGLE_ELEMENT"},
        1: {"name": "fluid_lin", "elem": "TRIANGLE_ELEMENT"},
        2: {"name": "fluid_quad", "elem": "TRIANGLE_ELEMENT"},
    },
    "solid_bcpatch": {"inlet": 2, "interface": 4},
    "fluid_bcpatch": {"inlet": 1, "interface": 4},
}


TEST: ProblemDef = {
    "output_dir": Path("test"),
    "time": {"start": 1, "end": 1000, "step": 0.001},
    "mesh": DEFAULT_MESH,
}
