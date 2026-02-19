import dataclasses as dc
from typing import TYPE_CHECKING, NamedTuple, TypedDict

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from cheartpy.fe.aliases import CheartElementType
    from cheartpy.fe.trait import ICheartTopology, ITopInterface, IVariable


class BCPatchDef(TypedDict, total=True):
    inlet: int
    interface: int


class MeshDef(TypedDict, total=True):
    name: str
    elem: CheartElementType


class TopDef(TypedDict, total=True):
    home: Path
    solid: Mapping[int, MeshDef]
    fluid: Mapping[int, MeshDef]
    solid_bcpatch: BCPatchDef
    fluid_bcpatch: BCPatchDef


class TimeDef(TypedDict, total=True):
    start: int
    end: int
    step: float


class ProblemDef(TypedDict, total=True):
    output_dir: Path
    time: TimeDef
    mesh: TopDef


@dc.dataclass(slots=True, frozen=True)
class ProblemTopology:
    interfaces: Mapping[int, ITopInterface]
    fluid2: ICheartTopology
    fluid1: ICheartTopology
    fluid0: ICheartTopology
    solid2: ICheartTopology
    solid1: ICheartTopology
    bnd: ICheartTopology


class FluidVariables(NamedTuple):
    Xt: IVariable
    X0: IVariable
    V: IVariable
    P: IVariable
    W: IVariable


class SolidVariables(NamedTuple):
    X: IVariable
    V: IVariable
    U: IVariable
    P: IVariable
