from typing import TYPE_CHECKING, Literal, NamedTuple, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cheartpy.fe.trait import IBCPatch


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


LoadingCurveDef = SineCurve | HoldCurve | RampCurve


class NeoHookeanMaterial(TypedDict, total=True):
    type: Literal["NeoHookean"]
    k: tuple[float]


class IsotropicExponentialMaterial(TypedDict, total=True):
    type: Literal["isotropic-exponential"]
    k: tuple[float, float]


MaterialDef = NeoHookeanMaterial | IsotropicExponentialMaterial
