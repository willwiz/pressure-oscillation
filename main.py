from code_pkg import run
from code_pkg.io import iter_problem_defs
from pytools.logging import get_logger
from pytools.parallel import ThreadedRunner
from pytools.path import iter_unpack

from examples import NEO_PULSE, TEST
from summarize import summarize


def main() -> None:
    with ThreadedRunner(thread=6) as runner:
        for p in iter_problem_defs(NEO_PULSE):
            print(f">>> Submitted {p['prefix']}...")
            runner.submit(run, p)
    for pset in iter_unpack(NEO_PULSE):
        summarize(pset.values())


def main_pilot() -> None:
    run(TEST)


if __name__ == "__main__":
    get_logger(level="INFO")
    # main_pilot()
    main()
