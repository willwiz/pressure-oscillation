# pyright: reportUnknownMemberType=false

import os
from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, NamedTuple, TypedDict, Unpack

import numpy as np
from pytools.plotting.api import (
    close_figure,
    create_figure,
    update_figure_setting,
)
from pytools.result import Err, Ok, Result, filter_ok

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
        msg = f"Time n={len(time)} does not match {len(apex)}, {len(inlet)} for {prob['prefix']}"
        return Err(ValueError(msg))
    return Ok(PressureData(time.astype(dtype), apex.astype(dtype), inlet.astype(dtype)))


def summarize_pressure_diff(prob: ProblemDef) -> None:
    match import_pressure_data(prob):
        case Ok(data): ...  # fmt: skip
        case Err(e):
            print(e)
            return
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


def summarize_pressure_diff_all(probs: Iterable[ProblemDef], **kwargs: Unpack[PlotKwargs]) -> None:
    prefixes = [p["prefix"] for p in probs]
    prefix = os.path.commonprefix(prefixes)
    output_dir = next(iter(probs))["output_dir"]
    raw = {prob["prefix"]: import_pressure_data(prob) for prob in probs}
    for prefix, res in raw.items():
        match res:
            case Ok(_): ...  # fmt: skip
            case Err(e):
                print(f"Failed to import {prefix}: {e}")
    data = filter_ok(raw)
    if not data:
        print(f"No data found for {prefix} to plot.")
        return
    kwargs = {"xlabel": "Time [s]", "ylabel": "Inlet - Apex [Pa]", **kwargs}
    plot_time_trace(
        {k.split("_")[-1]: {"x": v.time, "y": v.inlet - v.apex} for k, v in data.items()},
        fout=output_dir / f"{prefix}pressure_diff_all.png",
        **kwargs,
    )


class DPData[F: np.floating](NamedTuple):
    time: A1[F]
    v: A1[F]


def summarize_pressure_oscillations_normalized(
    probs: Iterable[ProblemDef], **kwargs: Unpack[PlotKwargs]
) -> None:
    prefixes = [p["prefix"] for p in probs]
    prefix = os.path.commonprefix(prefixes)
    output_dir = next(iter(probs))["output_dir"]
    raw = {prob["prefix"]: import_pressure_data(prob) for prob in probs}
    for prefix, res in raw.items():
        match res:
            case Ok(_): ...  # fmt: skip
            case Err(e):
                print(f"Failed to import {prefix}: {e}")
    data = filter_ok(raw)
    if not data:
        print(f"No data found for {prefix} to plot.")
        return
    ref_response = {k: v for k, v in data.items() if "1000kPa" in k}
    if len(ref_response) != 1:
        print(f"Expected exactly one reference response with '1000kPa', found {len(ref_response)}.")
        return
    ref = next(iter(ref_response.values()))
    test_responses = {k: v for k, v in data.items() if "1000kPa" not in k}
    diff_res = {
        k: DPData(v.time, (v.inlet - v.apex) - (ref.inlet - ref.apex))
        for k, v in test_responses.items()
    }
    diff_res = {k: DPData(v.time, v.v / v.v.max()) for k, v in diff_res.items()}
    plot_time_trace(
        {k.split("_")[-1]: {"x": v.time, "y": v.v} for k, v in diff_res.items()},
        fout=output_dir / f"{prefix}pressure_diff_normalized.png",
        **kwargs,
    )
