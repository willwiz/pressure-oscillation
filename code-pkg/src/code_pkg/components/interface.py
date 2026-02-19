from typing import TYPE_CHECKING, TypedDict, Unpack

from cheartpy.fe.api import create_bcpatch, create_variable
from cheartpy.fe.physics.fs_coupling import FSCouplingProblem, FSExpr

if TYPE_CHECKING:
    from code_pkg.types import FluidVariables, ProblemTopology, SolidVariables


class OptionalKwargs(TypedDict, total=False):
    binary: bool
    bnd: int
    freq: int


def create_interface_coupling_problem(
    top: ProblemTopology,
    svars: SolidVariables,
    fvars: FluidVariables,
    **kwargs: Unpack[OptionalKwargs],
) -> FSCouplingProblem:
    _fmt = "BINARY" if kwargs.get("binary", False) else "TXT"
    lm = create_variable("IfLM", top.bnd, 2, fmt=_fmt, freq=kwargs.get("freq", -1))
    xb = create_variable("IfX", top.bnd, 2, data=top.bnd.mesh, freq=kwargs.get("freq", -1))
    p = FSCouplingProblem("InterfaceCouplling", space=xb, root_top=top.bnd)
    p.set_lagrange_mult(lm, FSExpr(fvars.V, 1), FSExpr(svars.V, -1))
    p.add_term(fvars.V, FSExpr(lm, 1))
    p.add_term(svars.V, FSExpr(lm, -1))
    p.bc.add_patch(create_bcpatch(kwargs.get("bnd", 1), lm, "dirichlet", 0.0, 0.0))
    return p
