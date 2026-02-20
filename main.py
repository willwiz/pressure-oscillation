from code_pkg import run
from pytools.logging import get_logger
from pytools.parallel import ThreadedRunner
from pytools.path import iter_unpack

from examples import NEO_PULSE, TEST
from summarize import summarize


def main() -> None:
    get_logger(level="INFO")
    with ThreadedRunner(thread=6) as runner:
        for p in iter_unpack(iter_unpack(NEO_PULSE)):
            print(f">>> Submitted on {p['prefix']}...")
            runner.submit(run, p)
    for pset in iter_unpack(NEO_PULSE):
        summarize(pset.values())


def main_pilot() -> None:
    run(TEST)


if __name__ == "__main__":
    # main_pilot()
    main()
