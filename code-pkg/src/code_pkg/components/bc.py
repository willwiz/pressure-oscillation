from typing import TYPE_CHECKING, Required, TypedDict, Unpack

import numpy as np
from cheartpy.fe.api import create_bcpatch, create_expr

from .traits import BCPatches, HoldCurve, LoadingCurveDef, SineCurve

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cheartpy.fe.trait import IExpression

    from code_pkg.types import FluidVariables, SolidVariables, TopDef


class _Kwargs(TypedDict, total=False):
    left: Required[float]
    right: Required[float]


def create_sine_curve(name: str, curve_def: SineCurve, start: float) -> IExpression:
    t = curve_def["period"]
    v = curve_def["max_vel"]
    end = start + curve_def["cycles"] * curve_def["period"]
    return create_expr(
        name,
        [
            f"{v:.8f}*sin({2 * np.pi / t:.8g}*t)*sin({2 * np.pi / t:.8g}*t)"
            f"*(t>{start:.4f})*(t<{end:.4f})"
        ],
    )


def create_hold_curve(_name: str, _curve_def: HoldCurve, _start: float) -> None:
    return None


def create_bc_curve(name: str, curve_def: LoadingCurveDef, start: float) -> IExpression | None:
    match curve_def:
        case {"type": "Sine"}:
            return create_sine_curve(name, curve_def, start)
        case {"type": "Hold"}:
            return create_hold_curve(name, curve_def, start)


def calc_bc_duration(curve_def: LoadingCurveDef) -> float:
    match curve_def:
        case {"type": "Sine"}:
            return curve_def["period"] * curve_def["cycles"]
        case {"type": "Hold"}:
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


def create_bcpatches(
    mesh: TopDef,
    dfn: Sequence[LoadingCurveDef],
    svars: SolidVariables,
    fvars: FluidVariables,
    **kwargs: Unpack[_Kwargs],
) -> BCPatches:
    time_curve = create_time_curve(dfn)
    space_curve = f"max(1 - ({fvars.Xt}.1/{kwargs['right']})^2, 0)"
    inlet_vel = create_expr("inlet_flow_vel", [0, f"{time_curve}*{space_curve}"])
    inlet_vel.add_deps(time_curve)
    return BCPatches(
        solid=[create_bcpatch(mesh["solid_bcpatch"]["inlet"], svars.V, "dirichlet", 0.0, 0.0)],
        fluid=[create_bcpatch(mesh["fluid_bcpatch"]["inlet"], fvars.V, "dirichlet", inlet_vel)],
        ale=[
            create_bcpatch(mesh["fluid_bcpatch"]["inlet"], fvars.W, "dirichlet", 0.0, 0.0),
            create_bcpatch(mesh["fluid_bcpatch"]["interface"], fvars.W, "dirichlet", fvars.V),
        ],
    )
