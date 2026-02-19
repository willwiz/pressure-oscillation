from typing import TYPE_CHECKING, NamedTuple, Required, TypedDict, Unpack

import numpy as np
from cheartpy.fe.api import create_bcpatch, create_expr

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cheartpy.fe.trait import IBCPatch

    from code_pkg.types import FluidVariables, SolidVariables, TopDef


class BCPatches(NamedTuple):
    solid: Sequence[IBCPatch]
    fluid: Sequence[IBCPatch]
    ale: Sequence[IBCPatch]


class _Kwargs(TypedDict, total=False):
    period: Required[float]
    left: Required[float]
    right: Required[float]
    vel: Required[float]


def create_bcpatches(
    mesh: TopDef, svars: SolidVariables, fvars: FluidVariables, **kwargs: Unpack[_Kwargs]
) -> BCPatches:
    time_curve = f"sin({2 * np.pi / kwargs['period']:.12g}*t)"
    space_curve = f"max(1 - ({fvars.Xt}.1/{kwargs['right']})^2, 0)"
    inlet_vel = create_expr(
        "inlet_flow_vel", [0, f"{kwargs['vel']}*{time_curve}*{time_curve}*{space_curve}"]
    )
    return BCPatches(
        solid=[create_bcpatch(mesh["solid_bcpatch"]["inlet"], svars.V, "dirichlet", 0.0, 0.0)],
        fluid=[create_bcpatch(mesh["fluid_bcpatch"]["inlet"], fvars.V, "dirichlet", inlet_vel)],
        ale=[
            create_bcpatch(mesh["fluid_bcpatch"]["inlet"], fvars.W, "dirichlet", 0.0, 0.0),
            create_bcpatch(mesh["fluid_bcpatch"]["interface"], fvars.W, "dirichlet", fvars.V),
        ],
    )
