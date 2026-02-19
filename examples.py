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
    "solid_bcpatch": {"apex": 5, "inlet": 2, "interface": 4},
    "fluid_bcpatch": {"apex": 5, "inlet": 1, "interface": 4},
}


TEST: ProblemDef = {
    "prefix": f"neohookean_{30}",
    "output_dir": Path("results"),
    "time": {"start": 1, "end": 1000, "step": 0.001},
    "mesh": DEFAULT_MESH,
    "loading": [{"type": "Sine", "max_vel": 200.0, "period": 0.5, "cycles": 2}],
    "material": {"type": "NeoHookean", "k": (30000,)},
}

PILOT_TESTS: list[ProblemDef] = [
    {
        "prefix": f"neohookean_{k}kPa",
        "output_dir": Path("results"),
        "time": {"start": 1, "end": 1000, "step": 0.001},
        "mesh": DEFAULT_MESH,
        "loading": [{"type": "Sine", "period": 1.0, "cycles": 1, "max_vel": 200.0}],
        "material": {"type": "NeoHookean", "k": (k * 1000,)},
    }
    for k in [5, 10, 20, 30, 40, 50]
]
