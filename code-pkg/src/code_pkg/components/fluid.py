from typing import TYPE_CHECKING, TypedDict, Unpack

from cheartpy.fe.api import create_bc, create_variable
from cheartpy.fe.physics.fluids import (
    ALEElementDependentStiffness,
    TransientALENonConvNavierStokesFlow,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cheartpy.fe.trait import IBCPatch

    from code_pkg.types import FluidVariables, ProblemTopology


class _Kwargs(TypedDict, total=False):
    binary: bool
    rho: float
    bnd: int
    freq: int


def create_fluid_problem(
    top: ProblemTopology,
    v: FluidVariables,
    nu: float,
    bc: Sequence[IBCPatch],
    **kwargs: Unpack[_Kwargs],
) -> TransientALENonConvNavierStokesFlow:
    p = TransientALENonConvNavierStokesFlow(
        "Fluid",
        space=v.Xt,
        vel=v.V,
        pres=v.P,
        dom_vel=v.W,
        viscosity=nu,
        density=kwargs.get("rho", 1.0e-3),
        root_topology=top.fluid2,
    )
    p.set_flag("True-Navier-Poisson")
    p.bc = create_bc(*bc)
    return p


def create_ale_problem(
    top: ProblemTopology,
    v: FluidVariables,
    penalty: float,
    bc: Sequence[IBCPatch],
    **kwargs: Unpack[_Kwargs],
) -> ALEElementDependentStiffness:
    _fmt = "BINARY" if kwargs.get("binary", False) else "TXT"
    elem_quality = create_variable(
        "ALEquality", top.fluid0, 1, fmt=_fmt, freq=kwargs.get("freq", -1)
    )
    elem_stiffness = create_variable(
        "ALEstiffness", top.fluid0, 1, fmt=_fmt, freq=kwargs.get("freq", -1)
    )
    p = ALEElementDependentStiffness(
        "ALE",
        space=v.X0,
        dom_vel=v.W,
        ale_space=v.Xt,
        quality=elem_quality,
        stiffness=elem_stiffness,
        penalty=penalty,
        root_topology=top.fluid2,
    )
    p.set_flag("Radius-ratio-metric")
    p.bc.add_patch(*bc)
    return p
