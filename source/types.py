"""All types present in ec-apportionment code."""
from typing import Dict, List, Tuple, TypedDict

from matplotlib.container import BarContainer
from matplotlib.lines import Line2D
from matplotlib.text import Text

# TODO
# - Use TypedDict on other types to whitelist proper keys


class StateInfo(TypedDict):
    """Dict with name, pop, reps, prio, pop_per_rep, and is max_pri."""

    name: str
    pop: int
    reps: int
    pop_per_rep: float
    priority: float
    max_pri: bool


# list containing name and pop
CsvStateInfo = List[str]

PlotTextDict = Dict[str, Text]


# class PlotTextDict(TypedDict):
#     """dict with all the plot's text objects."""

#     seat_txt: Text
#     state_txt: Text
#     mean_txt: Text
#     std_dev_txt: Text
#     range_txt: Text
#     geo_mean_txt: Text


# attribute objects related to plot graphics
PlotProps = Tuple[BarContainer, Line2D, PlotTextDict]

PlotBarsDict = Dict[str, BarContainer]


# TypedDict still doesn't work nicely with pyright/jedi/anything.
# Calling .values() on a dist defaults to just object.
# Type hinting for a custom class doesn't work
# class PlotBarsDict(TypedDict):
#     """Relates state names to respective bar objects."""

#     plt_1_bars: BarContainer
#     plt_2_bars: BarContainer
#     plt_3_bars: BarContainer
