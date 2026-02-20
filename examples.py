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
    "loading": {
        "time": [{"type": "Sine", "max_vel": 200.0, "period": 0.5, "cycles": 2}],
        "space": {"type": "parabolic", "width": 15.0},
    },
    "material": {"type": "NeoHookean", "k": (30000,)},
}

PILOT_TESTS: list[ProblemDef] = [
    {
        "prefix": f"neohookean_{k}kPa",
        "output_dir": Path("results"),
        "time": {"start": 1, "end": 1000, "step": 0.001},
        "mesh": DEFAULT_MESH,
        "loading": {
            "time": [{"type": "Sine", "max_vel": 200.0, "period": 0.5, "cycles": 2}],
            "space": {"type": "parabolic", "width": 15.0},
        },
        "material": {"type": "NeoHookean", "k": (k * 1000,)},
    }
    for k in [5, 10, 20, 30, 40, 50]
]

EXP_TESTS: list[ProblemDef] = [
    {
        "prefix": f"exponential-3_{k}kPa",
        "output_dir": Path("results"),
        "time": {"start": 1, "end": 1000, "step": 0.001},
        "mesh": DEFAULT_MESH,
        "loading": {
            "time": [{"type": "Sine", "max_vel": 200.0, "period": 0.5, "cycles": 2}],
            "space": {"type": "parabolic", "width": 15.0},
        },
        "material": {"type": "isotropic-exponential", "k": (k * 1000, 3.0)},
    }
    for k in [5, 10, 20, 30, 40, 50]
]

TWO_EXP_PULSE: list[ProblemDef] = [
    {
        "prefix": f"pulse-2-exp_{k}kPa",
        "output_dir": Path("results"),
        "time": {"start": 1, "end": 1000, "step": 0.001},
        "mesh": DEFAULT_MESH,
        "loading": {
            "time": [
                {"type": "Sine", "max_vel": 400.0, "period": 0.25, "cycles": 2},
                {"type": "Hold", "duration": 0.5},
            ],
            "space": {"type": "parabolic", "width": 15.0},
        },
        "material": {"type": "isotropic-exponential", "k": (k * 1000, 3.0)},
    }
    for k in [5, 10, 20, 30, 40, 50]
]


TWO_NEO_PULSE: list[ProblemDef] = [
    {
        "prefix": f"pulse-2-neo_{k}kPa",
        "output_dir": Path("results"),
        "time": {"start": 1, "end": 1000, "step": 0.001},
        "mesh": DEFAULT_MESH,
        "loading": {
            "time": [
                {"type": "Sine", "max_vel": 400.0, "period": 0.25, "cycles": 2},
                {"type": "Hold", "duration": 0.5},
            ],
            "space": {"type": "parabolic", "width": 15.0},
        },
        "material": {"type": "NeoHookean", "k": (k * 1000,)},
    }
    for k in [5, 10, 20, 30, 40, 50]
]

FOUR_NEO_PULSE: list[ProblemDef] = [
    {
        "prefix": f"pulse-4-neo_{k}kPa",
        "output_dir": Path("results"),
        "time": {"start": 1, "end": 1000, "step": 0.001},
        "mesh": DEFAULT_MESH,
        "loading": {
            "time": [
                {"type": "Sine", "max_vel": 800.0, "period": 0.125, "cycles": 2},
                {"type": "Hold", "duration": 0.5},
            ],
            "space": {"type": "parabolic", "width": 15.0},
        },
        "material": {"type": "NeoHookean", "k": (k * 1000,)},
    }
    for k in [5, 10, 20, 30, 40, 50]
]


NEO_PULSE: dict[int, dict[int, dict[int, ProblemDef]]] = {
    w: {
        f: {
            k: {
                "prefix": f"pulse-neo-{f}Hz-{w}mm_{k}kPa",
                "output_dir": Path("results"),
                "time": {"start": 1, "end": 1000, "step": 0.001},
                "mesh": DEFAULT_MESH,
                "loading": {
                    "time": [
                        {
                            "type": "Sine",
                            "max_vel": f * 100.0 * 15 / w,
                            "period": 1.0 / f,
                            "cycles": 2,
                        },
                        {"type": "Hold", "duration": 1.0 - 1.0 / f},
                    ],
                    "space": {"type": "parabolic", "width": float(w)},
                },
                "material": {"type": "NeoHookean", "k": (k * 1000,)},
            }
            for k in [5, 10, 20, 30, 40, 50]
        }
        for f in [2, 4, 8]
    }
    for w in [5, 15]
}
