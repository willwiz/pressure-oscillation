from typing import TYPE_CHECKING

from code_pkg.io import is_problem_def
from code_pkg.plotting import (
    summarize_pressure_diff,
    summarize_pressure_diff_all,
    summarize_pressure_oscillations_normalized,
)

from examples import NEO_PULSE

if TYPE_CHECKING:
    from collections.abc import Iterable

    from code_pkg.types import ProblemDef


def summarize(probs: Iterable[ProblemDef]) -> None:
    for p in probs:
        summarize_pressure_diff(p)
    summarize_pressure_diff_all(probs, padbottom=0.3)
    summarize_pressure_oscillations_normalized(probs, padbottom=0.3)


if __name__ == "__main__":
    print(is_problem_def(NEO_PULSE))
    for k, v in NEO_PULSE.items():
        print(f"{k}: {is_problem_def(v)}")
        for kk, vv in v.items():
            print(f"  {kk}: {is_problem_def(vv)}")
            for kkk, vvv in vv.items():
                print(f"    {kkk}: {is_problem_def(vvv)}")
