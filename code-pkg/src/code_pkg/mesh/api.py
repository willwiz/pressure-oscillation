import importlib.resources
from typing import TYPE_CHECKING

from cheartpy.mesh.api import import_cheart_mesh
from pytools.result import Err, Ok, Result

import code_pkg.mesh.data.ventricle_2d

if TYPE_CHECKING:
    from code_pkg.types import TopDef


def remake_mesh(dfn: TopDef) -> Result[None]:
    with importlib.resources.path(code_pkg.mesh.data.ventricle_2d) as path:
        fluid = import_cheart_mesh(path / "fluid")
        solid = import_cheart_mesh(path / "solid")
    dfn["home"].mkdir(exist_ok=True)
    match fluid:
        case Ok(mesh):
            mesh.save(dfn["home"] / dfn["fluid"][1]["name"])
        case Err(err):
            return Err(err)
    match solid:
        case Ok(mesh):
            mesh.save(dfn["home"] / dfn["solid"][1]["name"])
        case Err(err):
            return Err(err)
    return Ok(None)
