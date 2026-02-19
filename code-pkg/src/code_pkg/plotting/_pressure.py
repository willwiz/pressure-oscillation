# pyright: reportUnknownMemberType=false


from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, NamedTuple, TypedDict, Unpack

import numpy as np
from pytools.plotting.api import (
    close_figure,
    create_figure,
    update_axis_setting,
    update_figure_setting,
)

if TYPE_CHECKING:
    from pathlib import Path

    from pytools.arrays import A1, DType
    from pytools.plotting.trait import PlotKwargs

    from code_pkg._data import ProblemDef


class PlotData[F: np.floating](TypedDict, total=True):
    x: A1[F]
    y: A1[F]


_TOO_TALL = 3


def plot_time_trace[F: np.floating](
    data: Sequence[PlotData[F]] | Mapping[str, PlotData[F]],
    fout: Path,
    **kwargs: Unpack[PlotKwargs],
) -> None:
    kwargs = {**kwargs}
    fig, ax = create_figure(**kwargs)
    update_figure_setting(fig, **kwargs)
    match data:
        case Sequence():
            for d in data:
                ax.plot(d["x"], d["y"])
        case Mapping():
            for k, v in data.items():
                ax.plot(v["x"], v["y"], label=k)
            ax.legend() if len(data) <= _TOO_TALL else fig.legend(
                loc="outside lower center", ncol=_TOO_TALL
            )
    update_axis_setting(ax, **kwargs)
    fig.savefig(fout)
    close_figure(fig)


class PressureData[F: np.floating](NamedTuple):
    time: A1[F]
    apex: A1[F]
    inlet: A1[F]


def import_pressure_data[F: np.floating](
    prob: ProblemDef, *, dtype: DType[F] = np.float64
) -> PressureData[F]:
    apex_file = prob["output_dir"] / prob["prefix"] / "apex_pressure-0.D"
    inlet_file = prob["output_dir"] / prob["prefix"] / "inlet_pressure-0.D"
    apex = np.loadtxt(apex_file)[:, 1]
    inlet = np.loadtxt(inlet_file)[:, 1]
    time = np.arange(prob["time"]["start"], prob["time"]["end"] + 1) * prob["time"]["step"]
    return PressureData(time.astype(dtype), apex.astype(dtype), inlet.astype(dtype))


def summarize_pressure_diff(prob: ProblemDef) -> None:
    data = import_pressure_data(prob)
    plot_time_trace(
        {
            "Apex": {"x": data.time, "y": data.apex},
            "Inlet": {"x": data.time, "y": data.inlet},
            "Apex-Inlet": {"x": data.time, "y": data.apex - data.inlet},
        },
        fout=prob["output_dir"] / f"{prob['prefix']}-pressure_diff.png",
        xlabel="Time [s]",
        ylabel="Pressure [Pa]",
    )


def summarize_pressure_diff_all(probs: Sequence[ProblemDef], **kwargs: Unpack[PlotKwargs]) -> None:
    data = {prob["prefix"]: import_pressure_data(prob) for prob in probs}
    kwargs = {"xlabel": "Time [s]", "ylabel": "Apex - Inlet [Pa]", **kwargs}
    plot_time_trace(
        {k.split("_")[-1]: {"x": v.time, "y": v.apex - v.inlet} for k, v in data.items()},
        fout=probs[0]["output_dir"] / "pressure_diff_all.png",
        **kwargs,
    )
