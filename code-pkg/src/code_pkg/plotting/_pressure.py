# pyright: reportUnknownMemberType=false


import os
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, NamedTuple, TypedDict, Unpack

import numpy as np
from pytools.plotting.api import (
    close_figure,
    create_figure,
    update_figure_setting,
)
from pytools.result import Err, Ok, Result, all_ok

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
    fig.savefig(fout)
    close_figure(fig)


class PressureData[F: np.floating](NamedTuple):
    time: A1[F]
    apex: A1[F]
    inlet: A1[F]


def import_pressure_data[F: np.floating](
    prob: ProblemDef, *, dtype: DType[F] = np.float64
) -> Result[PressureData[F]]:
    apex_file = prob["output_dir"] / prob["prefix"] / "apex_pressure-0.D"
    inlet_file = prob["output_dir"] / prob["prefix"] / "inlet_pressure-0.D"
    apex = np.loadtxt(apex_file)[:, 1]
    inlet = np.loadtxt(inlet_file)[:, 1]
    time = np.arange(prob["time"]["start"], prob["time"]["end"] + 1) * prob["time"]["step"]
    if len(time) != len(apex) or len(time) != len(inlet):
        msg = f"Time length {len(time)} does not match data length {len(apex)}, {len(inlet)}"
        return Err(ValueError(msg))
    return Ok(PressureData(time.astype(dtype), apex.astype(dtype), inlet.astype(dtype)))


def summarize_pressure_diff(prob: ProblemDef) -> None:
    match import_pressure_data(prob):
        case Ok(data):
            pass
        case Err(e):
            print(e)
            raise SystemExit(1)
    plot_time_trace(
        {
            "Apex": {"x": data.time, "y": data.apex},
            "Inlet": {"x": data.time, "y": data.inlet},
            "Inlet - Apex": {"x": data.time, "y": data.inlet - data.apex},
        },
        fout=prob["output_dir"] / f"{prob['prefix']}-pressure_diff.png",
        xlabel="Time [s]",
        ylabel="Pressure [Pa]",
    )


def summarize_pressure_diff_all(probs: Sequence[ProblemDef], **kwargs: Unpack[PlotKwargs]) -> None:
    match all_ok({prob["prefix"]: import_pressure_data(prob) for prob in probs}):
        case Ok(data):
            pass
        case Err(e):
            print(e)
            raise SystemExit(1)
    kwargs = {"xlabel": "Time [s]", "ylabel": "Inlet - Apex [Pa]", **kwargs}
    prefixes = [p["prefix"] for p in probs]
    prefix = os.path.commonprefix(prefixes)
    plot_time_trace(
        {k.split("_")[-1]: {"x": v.time, "y": v.inlet - v.apex} for k, v in data.items()},
        fout=probs[0]["output_dir"] / f"{prefix}pressure_diff_all.png",
        **kwargs,
    )
