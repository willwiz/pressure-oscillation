from typing import TYPE_CHECKING

from cheartpy.fe.api import create_variable
from cheartpy.fe.physics.norm_calculation import NormProblem

if TYPE_CHECKING:
    from code_pkg.types import FluidVariables, ProblemTopology


def create_pressure_calculation(
    top: ProblemTopology, fvars: FluidVariables
) -> tuple[NormProblem, NormProblem]:
    xb = create_variable("ApexX", top.apex, 2, data=top.apex.mesh, freq=-1)
    apex = NormProblem("P_ApexPressure", xb, fvars.P, 1)
    apex.export_to_file("apex_pressure-0.D")
    apex.scale_by_measure = True
    xi = create_variable("InletX", top.inlet, 2, data=top.inlet.mesh, freq=-1)
    inlet = NormProblem("P_InletPressure", xi, fvars.P, 1)
    inlet.export_to_file("inlet_pressure-0.D")
    inlet.scale_by_measure = True
    return apex, inlet
