from .bc import create_bcpatches
from .core import create_fluid_variables, create_problem_topology, create_solid_variables
from .fluid import create_ale_problem, create_fluid_problem
from .interface import create_interface_coupling_problem
from .solid import create_solid_problem

__all__ = [
    "create_ale_problem",
    "create_bcpatches",
    "create_fluid_problem",
    "create_fluid_variables",
    "create_interface_coupling_problem",
    "create_problem_topology",
    "create_solid_problem",
    "create_solid_variables",
]
