from code_pkg.plotting import summarize_pressure_diff
from code_pkg.plotting._pressure import summarize_pressure_diff_all

from examples import TWO_EXP_PULSE, TWO_NEO_PULSE


def main() -> None:
    for p in TWO_NEO_PULSE + TWO_EXP_PULSE:
        summarize_pressure_diff(p)
    summarize_pressure_diff_all(TWO_NEO_PULSE, padbottom=0.3)
    summarize_pressure_diff_all(TWO_EXP_PULSE, padbottom=0.3)


if __name__ == "__main__":
    main()
