from typing import TYPE_CHECKING, Literal, NamedTuple, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cheartpy.fe.trait import IBCPatch


class BCPatches(NamedTuple):
    solid: Sequence[IBCPatch]
    fluid: Sequence[IBCPatch]
    ale: Sequence[IBCPatch]


class DoubleSineCurve(TypedDict, total=True):
    type: Literal["DoubleSine"]
    period: float
    max_vel: float


LoadingCurveDef = DoubleSineCurve


class NeoHookeanMaterial(TypedDict, total=True):
    type: Literal["NeoHookean"]
    k: tuple[float]


MaterialDef = NeoHookeanMaterial
