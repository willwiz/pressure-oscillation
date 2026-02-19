from typing import TYPE_CHECKING, Required, TypedDict, Unpack

import numpy as np
from cheartpy.fe.api import create_bcpatch, create_expr

from .traits import BCPatches, LoadingCurveDef

if TYPE_CHECKING:
    from code_pkg.types import FluidVariables, SolidVariables, TopDef


class _Kwargs(TypedDict, total=False):
    left: Required[float]
    right: Required[float]


def create_bc_curve(curve_def: LoadingCurveDef) -> str:
    t = curve_def["period"]
    v = curve_def["max_vel"]
    return f"{v:.8f}*sin({2 * np.pi / t:.8g}*t)*sin({2 * np.pi / t:.8g}*t)"


def create_bcpatches(
    mesh: TopDef,
    dfn: LoadingCurveDef,
    svars: SolidVariables,
    fvars: FluidVariables,
    **kwargs: Unpack[_Kwargs],
) -> BCPatches:
    time_curve = create_bc_curve(dfn)
    space_curve = f"max(1 - ({fvars.Xt}.1/{kwargs['right']})^2, 0)"
    inlet_vel = create_expr("inlet_flow_vel", [0, f"{time_curve}*{space_curve}"])
    return BCPatches(
        solid=[create_bcpatch(mesh["solid_bcpatch"]["inlet"], svars.V, "dirichlet", 0.0, 0.0)],
        fluid=[create_bcpatch(mesh["fluid_bcpatch"]["inlet"], fvars.V, "dirichlet", inlet_vel)],
        ale=[
            create_bcpatch(mesh["fluid_bcpatch"]["inlet"], fvars.W, "dirichlet", 0.0, 0.0),
            create_bcpatch(mesh["fluid_bcpatch"]["interface"], fvars.W, "dirichlet", fvars.V),
        ],
    )
