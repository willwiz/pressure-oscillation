from typing import TYPE_CHECKING

from cheartpy.fe.cmd import run_prep, run_problem
from code_pkg.mesh.api import remake_mesh
from pytools.logging import get_logger
from pytools.parallel import ThreadedRunner

from examples import TEST, TWO_EXP_PULSE, TWO_NEO_PULSE
from pfiles.pfile_inflation import create_pfile

if TYPE_CHECKING:
    from code_pkg.types import ProblemDef


def run(prob: ProblemDef) -> str:
    remake_mesh(prob["mesh"])
    (prob["output_dir"] / prob["prefix"]).mkdir(parents=True, exist_ok=True)
    pfile = prob["output_dir"] / f"{prob['prefix']}.P"
    with pfile.open("w") as f:
        p = create_pfile(prob)
        p.write(f)
    run_prep(pfile, log=prob["output_dir"] / f"{prob['prefix']}_prep.log")
    run_problem(pfile, cores=4, log=prob["output_dir"] / f"{prob['prefix']}.log", output=False)
    return f"<<< {prob['prefix']} is complete"


def main() -> None:
    get_logger(level="INFO")
    with ThreadedRunner(thread=6) as runner:
        for p in TWO_NEO_PULSE + TWO_EXP_PULSE:
            print(f">>> Working on {p['prefix']}...")
            runner.submit(run, p)


def main_pilot() -> None:
    run(TEST)


if __name__ == "__main__":
    main()
