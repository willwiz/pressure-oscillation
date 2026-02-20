# ruff: noqa: C901, PLR0911
import json
from pathlib import Path
from typing import TYPE_CHECKING, TypeIs, get_args

from cheartpy.fe.aliases import CheartElementType
from pytools.result import Err, Ok, Result, all_ok

from code_pkg.types import (
    BCPatchDef,
    HoldCurve,
    IsotropicExponentialMaterial,
    LoadingCurveDef,
    LoadingDef,
    LoadingSpaceDef,
    MaterialDef,
    MeshDef,
    NeoHookeanMaterial,
    ParabolicJet,
    ProblemDef,
    RampCurve,
    SineCurve,
    TimeDef,
    TopDef,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from pytools.json import AnyObject, AnyValue


def is_cheart_element_type(value: object) -> TypeIs[CheartElementType]:
    return value in get_args(CheartElementType)


def _parse_dir(path: object | None) -> Result[Path]:
    if not isinstance(path, str):
        return Err(ValueError("Invalid: 'output_dir' is not a string"))
    path = Path(path)
    if not path.exists():
        return Err(ValueError(f"Invalid: 'output_dir' path {path} does not exist"))
    return Ok(path)


def _parse_time_def(time_dict: AnyValue) -> Result[TimeDef]:
    if not isinstance(time_dict, dict):
        return Err(ValueError("Invalid: 'time' is not a dictionary"))
    match time_dict.get("start"):
        case int(start): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'time.start' is not an integer"))
    match time_dict.get("end"):
        case int(end): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'time.end' is not an integer"))
    match time_dict.get("step"):
        case float(step): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'time.step' is not a float"))
    return Ok(TimeDef(start=int(start), end=int(end), step=float(step)))


def _parse_mesh_def(mesh_dict: AnyValue) -> Result[MeshDef]:
    if not isinstance(mesh_dict, dict):
        return Err(ValueError("Invalid: mesh definition is not a dictionary"))
    match mesh_dict.get("name"):
        case str(name): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'mesh.name' is not a string"))
    match mesh_dict.get("elem"):
        case str(elem):
            if not is_cheart_element_type(elem):
                return Err(ValueError("Invalid: 'mesh.elem' is not a valid element type"))
        case _:
            return Err(ValueError("Invalid: 'mesh.elem' is not a string"))
    return Ok(MeshDef(name=name, elem=elem))


def _parse_mesh_top_def(mesh_top_dict: AnyValue) -> Result[Mapping[int, MeshDef]]:
    if not isinstance(mesh_top_dict, dict):
        return Err(ValueError("Invalid: mesh topology definition is not a dictionary"))
    mesh_top: dict[int, MeshDef] = {}
    for k, v in mesh_top_dict.items():
        if not isinstance(k, int):
            return Err(ValueError("Invalid: mesh topology keys must be integers"))
        match _parse_mesh_def(v):
            case Ok(mesh_def):
                mesh_top[k] = mesh_def
            case Err(err):
                return Err(err)
    return Ok(mesh_top)


def _parse_top_bcpatch_def(bcpatch_dict: AnyValue) -> Result[BCPatchDef]:
    if not isinstance(bcpatch_dict, dict):
        return Err(ValueError("Invalid: bcpatch definition is not a dictionary"))
    match bcpatch_dict.get("apex"):
        case int(apex): ...  # fmt: skip
        case None:
            return Err(ValueError("Invalid: 'apex' is required for bc"))
        case _:
            return Err(ValueError("Invalid: 'apex' is not an integer"))
    match bcpatch_dict.get("inlet"):
        case int(inlet): ...  # fmt: skip
        case None:
            return Err(ValueError("Invalid: 'inlet' is required for bc"))
        case _:
            return Err(ValueError("Invalid: 'inlet' is not an integer"))
    match bcpatch_dict.get("interface"):
        case int(interface): ...  # fmt: skip
        case None:
            return Err(ValueError("Invalid: 'interface' is required for bc"))
        case _:
            return Err(ValueError("Invalid: 'interface' is not an integer"))
    return Ok(BCPatchDef(apex=int(apex), inlet=int(inlet), interface=int(interface)))


def _parse_top_def(top_dict: AnyValue) -> Result[TopDef]:
    if not isinstance(top_dict, dict):
        return Err(ValueError("Invalid: 'mesh' definition is not a dictionary"))
    match _parse_dir(top_dict.get("home")):
        case Ok(home): ...  # fmt: skip
        case Err(err):
            return Err(ValueError(f"Invalid: 'mesh.home' is not a valid path: {err}"))
    match _parse_mesh_top_def(top_dict.get("solid")):
        case Ok(solid): ...  # fmt: skip
        case Err(err):
            return Err(err)
    match _parse_mesh_top_def(top_dict.get("fluid")):
        case Ok(fluid): ...  # fmt: skip
        case Err(err):
            return Err(err)
    match _parse_top_bcpatch_def(top_dict.get("solid_bcpatch")):
        case Ok(solid_bcpatch): ...  # fmt: skip
        case Err(err):
            return Err(err)
    match _parse_top_bcpatch_def(top_dict.get("fluid_bcpatch")):
        case Ok(fluid_bcpatch): ...  # fmt: skip
        case Err(err):
            return Err(err)
    return Ok(
        TopDef(
            home=home,
            solid=solid,
            fluid=fluid,
            solid_bcpatch=solid_bcpatch,
            fluid_bcpatch=fluid_bcpatch,
        )
    )


def _parse_sine_curve_def(curve_dict: Mapping[str, AnyValue]) -> Result[SineCurve]:
    match curve_dict.get("max_vel"):
        case float(max_vel): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'max_vel' for Sine curve is not a float"))
    match curve_dict.get("period"):
        case float(period): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'period' for Sine curve is not a float"))
    match curve_dict.get("cycles"):
        case int(cycles): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'cycles' for Sine curve is not an integer"))
    return Ok(
        SineCurve(type="Sine", max_vel=float(max_vel), period=float(period), cycles=int(cycles))
    )


def _parse_hold_curve_def(curve_dict: Mapping[str, AnyValue]) -> Result[HoldCurve]:
    match curve_dict.get("duration"):
        case float(duration): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'duration' for Hold curve is not a float"))
    return Ok(HoldCurve(type="Hold", duration=float(duration)))


def _parse_ramp_curve_def(curve_dict: Mapping[str, AnyValue]) -> Result[RampCurve]:
    match curve_dict.get("max_vel"):
        case float(max_vel): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'max_vel' for Ramp curve is not a float"))
    match curve_dict.get("duration"):
        case float(duration): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'duration' for Ramp curve is not a float"))
    return Ok(RampCurve(type="Ramp", max_vel=float(max_vel), duration=float(duration)))


def _parse_loading_curve(curve_dict: AnyValue) -> Result[LoadingCurveDef]:
    if not isinstance(curve_dict, dict):
        return Err(ValueError("Invalid: loading curve definition is not a dictionary"))
    match curve_dict:
        case {"type": "Sine"}:
            return _parse_sine_curve_def(curve_dict)
        case {"type": "Hold"}:
            return _parse_hold_curve_def(curve_dict)
        case {"type": "Ramp"}:
            return _parse_ramp_curve_def(curve_dict)
        case _:
            return Err(ValueError("Invalid: loading curve type must be 'Sine', 'Hold', or 'Ramp'"))


def _parse_loading_time(loading_dict: AnyValue) -> Result[Sequence[LoadingCurveDef]]:
    if not isinstance(loading_dict, list):
        return Err(ValueError("Invalid: 'loading' definition must be a list"))
    match all_ok([_parse_loading_curve(c) for c in loading_dict]):
        case Ok(loading): ...  # fmt: skip
        case Err(err):
            return Err(err)
    return Ok(loading)


def _parse_jet_space_curve(loading_dict: AnyValue) -> Result[LoadingSpaceDef]:
    if not isinstance(loading_dict, dict):
        return Err(ValueError("Invalid: 'loading' definition must be a dictionary"))
    match loading_dict.get("space"):
        case "parabolic": ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'loading.space' must be 'parabolic'"))
    return Ok(ParabolicJet(type="parabolic", width=15.0))


def _parse_loading_def(loading_dict: AnyValue) -> Result[LoadingDef]:
    if not isinstance(loading_dict, dict):
        return Err(ValueError("Invalid: 'loading' definition must be a dictionary"))
    match _parse_loading_time(loading_dict.get("time")):
        case Ok(time): ...  # fmt: skip
        case Err(err):
            return Err(err)
    match _parse_jet_space_curve(loading_dict):
        case Ok(space): ...  # fmt: skip
        case Err(err):
            return Err(err)
    return Ok(LoadingDef(time=time, space=space))


def _parse_neo_hookean(material_dict: Mapping[str, AnyValue]) -> Result[NeoHookeanMaterial]:
    match material_dict.get("k"):
        case [float(k)]: ...  # fmt: skip
        case _:
            msg = "Invalid: 'material.k' for NeoHookean must be one float"
            return Err(ValueError(msg))
    return Ok(NeoHookeanMaterial(type="NeoHookean", k=(k,)))


def _parse_isotropic_exponential(
    material_dict: Mapping[str, AnyValue],
) -> Result[IsotropicExponentialMaterial]:
    match material_dict.get("k"):
        case [float(k), float(b)]: ...  # fmt: skip
        case _:
            msg = "Invalid: 'material.k' for isotropic-exponential must be a tuple of two floats"
            return Err(ValueError(msg))
    return Ok(IsotropicExponentialMaterial(type="isotropic-exponential", k=(k, b)))


def _parse_material_def(material_dict: AnyValue) -> Result[MaterialDef]:
    if not isinstance(material_dict, dict):
        return Err(ValueError("Invalid: material definition is not a dictionary"))
    match material_dict:
        case {"type": "NeoHookean"}:
            return _parse_neo_hookean(material_dict)
        case {"type": "isotropic-exponential"}:
            return _parse_isotropic_exponential(material_dict)
        case _:
            return Err(
                ValueError("Invalid: material type must be 'NeoHookean' or 'isotropic-exponential'")
            )


def parse_problem_def(raw_dict: AnyObject) -> Result[ProblemDef]:
    match raw_dict.get("prefix"):
        case str(prefix): ...  # fmt: skip
        case _:
            return Err(ValueError("Invalid: 'prefix' not a valid string"))
    match _parse_dir(raw_dict.get("output_dir")):
        case Ok(path): ...  # fmt: skip
        case Err(err):
            return Err(err)
    match _parse_time_def(raw_dict.get("time")):
        case Ok(time): ...  # fmt: skip
        case Err(err):
            return Err(err)
    match _parse_top_def(raw_dict.get("mesh")):
        case Ok(mesh): ...  # fmt: skip
        case Err(err):
            return Err(err)
    match _parse_loading_def(raw_dict.get("loading")):
        case Ok(loading): ...  # fmt: skip
        case Err(err):
            return Err(err)
    match _parse_material_def(raw_dict.get("material")):
        case Ok(material): ...  # fmt: skip
        case Err(err):
            return Err(err)
    return Ok(
        ProblemDef(
            prefix=prefix, output_dir=path, time=time, mesh=mesh, loading=loading, material=material
        )
    )


def import_problem_def(file: Path) -> Result[ProblemDef]:
    """Return a ProblemDef parsed from a JSON file.

    Parameters
    ----------
    file: Path
        Path to the JSON file containing the problem definition.

    Returns
    -------
    Result[ProblemDef]
        Ok(ProblemDef) if the file was successfully parsed, Err otherwise.

    """
    with file.open("r", encoding="utf-8") as f:
        raw_dict: AnyValue = json.load(f)
    if not isinstance(raw_dict, dict):
        return Err(ValueError("Invalid: root of JSON is not a dictionary"))
    return parse_problem_def(raw_dict)
