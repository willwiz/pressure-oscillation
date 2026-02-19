from pathlib import Path
from typing import TYPE_CHECKING

from cheartpy.fe.cmd import run_prep, run_problem
from code_pkg.mesh.api import remake_mesh

from examples import TEST
from pfiles.pfile_inflation import create_pfile

if TYPE_CHECKING:
    from code_pkg.types import ProblemDef


def main(prob: ProblemDef) -> None:
    p = create_pfile(prob)
    remake_mesh(prob["mesh"])
    with Path("Test.P").open("w") as f:
        p.write(f)
    run_prep("Test.P")
    run_problem("Test.P", cores=4)


if __name__ == "__main__":
    main(TEST)
