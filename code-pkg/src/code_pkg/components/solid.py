from typing import TYPE_CHECKING, TypedDict, Unpack

from cheartpy.fe.api import create_solid_mechanics_problem
from cheartpy.fe.physics.solid_mechanics.matlaws import Matlaw

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cheartpy.fe.physics.solid_mechanics.solid_problems import SolidProblem
    from cheartpy.fe.trait import IBCPatch

    from code_pkg.types import SolidVariables

    from .traits import MaterialDef


class _Kwargs(TypedDict, total=False):
    rho: float


def create_solid_problem(
    dfn: MaterialDef,
    v: SolidVariables,
    bc: Sequence[IBCPatch],
    **kwargs: Unpack[_Kwargs],
) -> SolidProblem:
    mp = create_solid_mechanics_problem("Solid", "TRANSIENT", v.X, v.U, vel=v.V, pres=v.P)
    matlaw = Matlaw(dfn["type"], list(dfn["k"]))
    mp.add_matlaw(matlaw)
    mp.use_option("Density", kwargs.get("rho", 1.0e-3))
    mp.bc.add_patch(*bc)
    if v.U.order == v.P.order:
        mp.stabilize("Nearly-incompressible", 100)
    return mp
