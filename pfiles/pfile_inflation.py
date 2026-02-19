# /// script
# dependencies: []
# ///


from typing import TYPE_CHECKING

from cheartpy.fe.api import (
    PFile,
    create_solver_group,
    create_solver_matrix,
    create_solver_subgroup,
    create_time_scheme,
)
from code_pkg.components import (
    create_ale_problem,
    create_bcpatches,
    create_fluid_problem,
    create_fluid_variables,
    create_interface_coupling_problem,
    create_pressure_calculation,
    create_problem_topology,
    create_solid_problem,
    create_solid_variables,
)

if TYPE_CHECKING:
    from code_pkg.types import ProblemDef


def create_pfile(prob: ProblemDef) -> PFile:
    time = create_time_scheme(
        "Time", prob["time"]["start"], prob["time"]["end"], prob["time"]["step"]
    )
    top = create_problem_topology(prob["mesh"])
    svars = create_solid_variables(top)
    fvars = create_fluid_variables(top)
    bc = create_bcpatches(prob["mesh"], prob["loading"], svars, fvars, left=-15.0, right=15.0)
    solid = create_solid_problem(prob["material"], svars, bc.solid)
    fluid = create_fluid_problem(top, fvars, 4e-3, bc.fluid)
    ale = create_ale_problem(top, fvars, 1.0, bc.ale)
    coupling = create_interface_coupling_problem(top, svars, fvars)
    solve_matrix = create_solver_matrix("MainMatrix", "SOLVER_MUMPS", fluid, solid, coupling)
    solve_matrix.add_setting("SolverMatrixCalculation", "EVALUATE_EVERY_BUILD")
    ale_matrix = create_solver_matrix("ALEMatrix", "SOLVER_MUMPS", ale)
    ale_matrix.add_setting("SolverMatrixCalculation", "EVALUATE_EVERY_BUILD")
    apex_p, inlet_p = create_pressure_calculation(top, fvars)
    sg = create_solver_subgroup("seq_fp_linesearch", solve_matrix, ale_matrix)
    sg.scale_first_residual = 1000.0
    pres_sg = [create_solver_subgroup("seq_fp", apex_p), create_solver_subgroup("seq_fp", inlet_p)]
    g = create_solver_group("Main", time)
    g.add_solversubgroup(sg, *pres_sg)
    g.set_iteration("SUBITERATION", 12)
    g.set_convergence("L2TOL", 1.0e-8)
    p = PFile()
    p.add_solvergroup(g)
    p.add_interface(*top.interfaces.values())
    p.set_outputpath(prob["output_dir"] / prob["prefix"])
    return p
