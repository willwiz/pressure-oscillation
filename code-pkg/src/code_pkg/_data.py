import dataclasses as dc
from typing import TYPE_CHECKING, Literal, NamedTuple, TypedDict

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from cheartpy.fe.aliases import CheartElementType
    from cheartpy.fe.trait import IBCPatch, ICheartTopology, ITopInterface, IVariable

    from .components.traits import MaterialDef


class BCPatchDef(TypedDict, total=True):
    apex: int
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


class BCPatches(NamedTuple):
    solid: Sequence[IBCPatch]
    fluid: Sequence[IBCPatch]
    ale: Sequence[IBCPatch]


class SineCurve(TypedDict, total=True):
    type: Literal["Sine"]
    max_vel: float
    period: float
    cycles: int


class HoldCurve(TypedDict, total=True):
    type: Literal["Hold"]
    duration: float


class RampCurve(TypedDict, total=True):
    type: Literal["Ramp"]
    max_vel: float
    duration: float


type LoadingCurveDef = SineCurve | HoldCurve | RampCurve


class ParabolicJet(TypedDict, total=True):
    type: Literal["parabolic"]
    width: float


type LoadingSpaceDef = ParabolicJet


class LoadingDef(TypedDict, total=True):
    time: Sequence[LoadingCurveDef]
    space: LoadingSpaceDef


class NeoHookeanMaterial(TypedDict, total=True):
    type: Literal["NeoHookean"]
    k: tuple[float]


class IsotropicExponentialMaterial(TypedDict, total=True):
    type: Literal["isotropic-exponential"]
    k: tuple[float, float]


type MaterialDef = NeoHookeanMaterial | IsotropicExponentialMaterial


class ProblemDef(TypedDict, total=True):
    prefix: str
    output_dir: Path
    time: TimeDef
    mesh: TopDef
    loading: LoadingDef
    material: MaterialDef


@dc.dataclass(slots=True, frozen=True)
class ProblemTopology:
    interfaces: Mapping[int, ITopInterface]
    fluid2: ICheartTopology
    fluid1: ICheartTopology
    fluid0: ICheartTopology
    solid2: ICheartTopology
    solid1: ICheartTopology
    inlet: ICheartTopology
    apex: ICheartTopology
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
