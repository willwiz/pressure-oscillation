from typing import TYPE_CHECKING

from code_pkg.plotting import summarize_pressure_diff, summarize_pressure_diff_all
from pytools.path import iter_unpack

from examples import NEO_PULSE

if TYPE_CHECKING:
    from collections.abc import Iterable

    from code_pkg.types import ProblemDef


def summarize(probs: Iterable[ProblemDef]) -> None:
    for p in probs:
        summarize_pressure_diff(p)
    summarize_pressure_diff_all(probs, padbottom=0.3)


if __name__ == "__main__":
    for p in iter_unpack(NEO_PULSE):
        summarize(p.values())
