from typing import TYPE_CHECKING, TypedDict, Unpack

import numpy as np
from cheartpy.fe.cmd import run_prep, run_problem
from pytools.result import Err, Ok, Result

from code_pkg.mesh.api import remake_mesh
from pfiles.pfile_inflation import create_pfile

if TYPE_CHECKING:
    from code_pkg.types import ProblemDef


def is_compelete(prob: ProblemDef) -> Result[None]:
    apex = prob["output_dir"] / prob["prefix"] / "apex_pressure-0.D"
    if not apex.exists():
        return Err(FileExistsError("Missing apex pressure file"))
    inlet = prob["output_dir"] / prob["prefix"] / "inlet_pressure-0.D"
    if not inlet.exists():
        return Err(FileExistsError("Missing inlet pressure file"))
    apex_data = np.loadtxt(apex)
    if len(apex_data) != prob["time"]["end"]:
        msg = f"Apex pressure file is incomplete [{len(apex_data)}/{prob['time']['end']}]"
        return Err(ValueError(msg))
    inlet_data = np.loadtxt(inlet)
    if len(inlet_data) != prob["time"]["end"]:
        msg = f"Inlet pressure file is incomplete [{len(inlet_data)}/{prob['time']['end']}]"
        return Err(ValueError(msg))
    return Ok(None)


class MainKwargs(TypedDict, total=False):
    overwrite: bool


def run(prob: ProblemDef, **kwargs: Unpack[MainKwargs]) -> str:
    if is_compelete(prob).ok() and not kwargs.get("overwrite"):
        return f"<<< {prob['prefix']} is already complete"
    remake_mesh(prob["mesh"])
    (prob["output_dir"] / prob["prefix"]).mkdir(parents=True, exist_ok=True)
    pfile = prob["output_dir"] / f"{prob['prefix']}.P"
    with pfile.open("w") as f:
        p = create_pfile(prob)
        p.write(f)
    run_prep(pfile, cores=4, log=prob["output_dir"] / f"{prob['prefix']}_prep.log")
    run_problem(pfile, cores=4, log=prob["output_dir"] / f"{prob['prefix']}.log", output=False)
    return f"<<< {prob['prefix']} is complete"
