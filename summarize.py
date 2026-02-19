from code_pkg.plotting import summarize_pressure_diff
from code_pkg.plotting._pressure import summarize_pressure_diff_all

from examples import PILOT_TESTS


def main() -> None:
    for p in PILOT_TESTS:
        summarize_pressure_diff(p)
    summarize_pressure_diff_all(PILOT_TESTS, padbottom=0.3)


if __name__ == "__main__":
    main()
