from typing import TYPE_CHECKING

import numpy as np
from cheartpy.fe.api import create_bcpatch, create_expr

from code_pkg.types import (
    BCPatches,
    HoldCurve,
    LoadingCurveDef,
    LoadingDef,
    LoadingSpaceDef,
    RampCurve,
    SineCurve,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cheartpy.fe.trait import IExpression

    from code_pkg.types import FluidVariables, SolidVariables, TopDef


def create_sine_curve(name: str, curve_def: SineCurve, start: float) -> IExpression:
    t = curve_def["period"]
    v = curve_def["max_vel"]
    end = start + curve_def["cycles"] * curve_def["period"]
    return create_expr(
        name,
        [f"{v:.8f}*sin({np.pi / t:.8g}*t)*sin({np.pi / t:.8g}*t)*(t>{start:.4f})*(t<{end:.4f})"],
    )


def create_hold_curve(_name: str, _curve_def: HoldCurve, _start: float) -> None:
    return None


def create_ramp_curve(name: str, curve_def: RampCurve, start: float) -> IExpression:
    v = curve_def["max_vel"]
    period = curve_def["duration"]
    return create_expr(
        name,
        [f"{v:.8f}*min((t-{start:.4f})/{period:.4f}, 1)*(t>{start:.4f})*(t<{start + period:.4f})"],
    )


def create_bc_curve(name: str, curve_def: LoadingCurveDef, start: float) -> IExpression | None:
    match curve_def:
        case {"type": "Sine"}:
            return create_sine_curve(name, curve_def, start)
        case {"type": "Hold"}:
            return create_hold_curve(name, curve_def, start)
        case {"type": "Ramp"}:
            return create_ramp_curve(name, curve_def, start)


def calc_bc_duration(curve_def: LoadingCurveDef) -> float:
    match curve_def:
        case {"type": "Sine"}:
            return curve_def["period"] * curve_def["cycles"]
        case {"type": "Hold"}:
            return curve_def["duration"]
        case {"type": "Ramp"}:
            return curve_def["duration"]


def create_time_curve(curve_def: Sequence[LoadingCurveDef]) -> IExpression:
    start = 0.0
    time = [start] + [(start := start + calc_bc_duration(c)) for c in curve_def]
    curves = [
        create_bc_curve(f"bcpart_{i}", d, t)
        for i, (d, t) in enumerate(zip(curve_def, time, strict=False))
    ]
    curves = [c for c in curves if c is not None]
    bc = create_expr("inlet_time_curve", [" + ".join(str(c) for c in curves)])
    bc.add_deps(*curves)
    return bc


def create_jet_curve(dfn: LoadingSpaceDef, fvars: FluidVariables) -> IExpression:
    match dfn:
        case {"type": "parabolic"}:
            return create_expr(
                "inlet_space_curve", [f"max(1 - ({fvars.Xt}.1/{dfn['width']:.4f})^2, 0)"]
            )


def create_bcpatches(
    mesh: TopDef,
    dfn: LoadingDef,
    svars: SolidVariables,
    fvars: FluidVariables,
) -> BCPatches:
    time_curve = create_time_curve(dfn["time"])
    space_curve = create_jet_curve(dfn["space"], fvars)
    inlet_vel = create_expr("inlet_flow_vel", [0, f"{time_curve}*{space_curve}"])
    inlet_vel.add_deps(time_curve, space_curve)
    return BCPatches(
        solid=[create_bcpatch(mesh["solid_bcpatch"]["inlet"], svars.V, "dirichlet", 0.0, 0.0)],
        fluid=[create_bcpatch(mesh["fluid_bcpatch"]["inlet"], fvars.V, "dirichlet", inlet_vel)],
        ale=[
            create_bcpatch(mesh["fluid_bcpatch"]["inlet"], fvars.W, "dirichlet", 0.0, 0.0),
            create_bcpatch(mesh["fluid_bcpatch"]["interface"], fvars.W, "dirichlet", fvars.V),
        ],
    )
