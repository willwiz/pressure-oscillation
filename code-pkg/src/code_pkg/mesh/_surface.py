from typing import TYPE_CHECKING

import numpy as np
from cheartpy.mesh.surface_core import create_new_surface_in_surf

if TYPE_CHECKING:
    from cheartpy.mesh.struct import CheartMesh
    from pytools.arrays import A1
    from pytools.result import Result


def _find_apex_node[F: np.floating, I: np.integer](mesh: CheartMesh[F, I]) -> A1[F]:
    idx = np.argmax(mesh.space.v[:, 1])
    return mesh.space.v[idx]


def create_apex_surface[F: np.floating, I: np.integer](
    mesh: CheartMesh[F, I], in_surf: int, label: int, radius: float
) -> Result[CheartMesh[F, I]]:
    apex_pos = _find_apex_node(mesh)
    return create_new_surface_in_surf(
        mesh,
        [in_surf],
        {
            "X": (apex_pos[0] - radius, apex_pos[0] + radius),
            "Y": (apex_pos[1] - radius, apex_pos[1] + radius),
        },
        label,
    ).next()
