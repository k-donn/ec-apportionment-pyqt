"""Module for creating bar_chart animation."""
# TODO
# Add file input option
# Add sizing variables


import math
import operator
from statistics import geometric_mean
from typing import Callable, List

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import Animation
from matplotlib.artist import Artist
from matplotlib.axes._subplots import Axes
# from matplotlib.backends.backend_qt5 import FigureManagerQT as FigureManager
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.ticker import FuncFormatter, MultipleLocator
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QMessageBox,
                             QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from .tools import (comma_format_int, extract_csv, extract_pop_per_rep,
                    extract_priority, extract_priority_tuple, extract_reps,
                    extract_state_names, parse_states)
from .types import (BarContainer, CsvStateInfo, PlotBarsDict, PlotProps,
                    PlotTextDict, StateInfo, Text)


class App(QMainWindow):
    """Manage everything present in the PyQt window.

    Methods
    -------
        initUI(self) -> None:
            Create the window and create file open dialog
        on_click(self) -> None:
            Handle the file opening and creation of Matplotlib area

    Properties
    ----------
    TODO
    """

    def __init__(self, file: str):
        super().__init__()
        self.title = "CGP Grey spreadsheet"
        self.file = file

        self.initUI()

    def initUI(self):
        """Create the ibitial window with button to open file and register event handlers."""
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 1900, 1068)

        button = QPushButton("Plot data", self)
        button.move(int((1900 / 2) - (150 / 2)), int((1068 / 2) - (75 / 2)))
        button.resize(150, 75)
        button.clicked.connect(self.on_click)

        self.show()

    def on_click(self):
        """Create the Plot with the opened file data."""
        self.m = Plot(self, file=self.file)

        toolbar = NavigationToolbar(self.m, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.m)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()


class Plot(FigureCanvas):
    """Manage the plotting of all four subplots.

    Methods
    -------
    TODO

    Properties
    ----------
    TODO
    """

    def __init__(self, parent=None, file=""):
        self.file = file

        self.fig = Figure(figsize=(16, 9), dpi=100)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.rows: List[CsvStateInfo] = extract_csv(self.file)
        self.state_info_list: List[StateInfo] = parse_states(self.rows)

        self.format_plt()

        self.plt_1: Axes = self.fig.add_subplot(221)
        self.plt_2: Axes = self.fig.add_subplot(222)
        self.plt_3: Axes = self.fig.add_subplot(223)
        self.plt_4: Axes = self.fig.add_subplot(224)

        self.x_vals: np.ndarray = np.arange(len(self.state_info_list))

        (plt_1_bars, self.mean_line, self.txt_dict) = self.format_plot_1()
        plt_2_bars: BarContainer = self.format_plot_2()
        plt_3_bars: BarContainer = self.format_plot_3()
        self.format_plot_4()

        self.plt_bars_dict: PlotBarsDict = {"plt_1_bars": plt_1_bars,
                                            "plt_2_bars": plt_2_bars,
                                            "plt_3_bars": plt_3_bars}

        frames: int = 385
        # This doesn't work if FuncAnimation isn't assigned to a value,
        #  therefore, add disable-unused for `anim`
        anim: Animation = animation.FuncAnimation(  # pylint: disable=unused-variable
            self.fig, self.animate,
            init_func=self.init_anim_factory(),
            frames=frames, repeat=False, blit=True, interval=170)

        self.show()

    def format_plt(self) -> None:
        """Format the plot after rendering."""
        plt.style.use("seaborn-dark")

        self.fig.subplots_adjust(top=0.955,
                                 bottom=0.125,
                                 left=0.095,
                                 right=0.93,
                                 hspace=0.365,
                                 wspace=0.105)

    def init_anim_factory(self) -> Callable:
        """Create an init_anim function that returns the needed artists.

        init_anim() doesn't allow for custom parameters to be passed. Therefore, we make them
        here.

        Returns
        -------
        `Callable`
            The init_anim function that returns the initial artists on the plot

        """
        def init_anim() -> List[Artist]:
            """Return the initial artists on the plot.

            This is needed for the blitting algorithm to
            use.

            Returns
            -------
            `List[Artist]`
                All of the bars, texts, and the mean line on the plot.

            """
            # All the containers for each of the states in each plot
            plot_containers: List[BarContainer] = list(
                self.plt_bars_dict.values())
            bars: List[Rectangle] = [artist
                                     for container in plot_containers for artist in container]
            txts: List[Text] = list(self.txt_dict.values())

            return [*bars, *txts, self.mean_line]
        return init_anim

    def animate(self,
                frame: int) -> List[Artist]:
        """Calculate the new priority values and reps in each state.

        Called every frame of Matplotlib's `FuncAnimation`.This is passed the properties about
        each of the subplots that we need to update and the previous frame's
        finished calculations. This makes calls to other functions that update each
        individual plot.

        Returns
        -------
        `List[Artist]`
            All of the artists that the blitting algorithm needs to update

        """
        # This adds the representative from the last frame's calculated max_pri
        for state_info in self.state_info_list:
            if state_info["max_pri"]:
                # print(f"{frame=} {state_info['name']=}")
                state_info["reps"] = state_info["reps"] + 1
                state_info["max_pri"] = False

        # This calculates the next state to give a rep in the next frame
        for state_info in self.state_info_list:
            state_info["priority"] = (
                state_info["pop"] *
                (1 / math.sqrt((state_info["reps"] + 1) * ((state_info["reps"] + 1) - 1))))
            state_info["pop_per_rep"] = state_info["pop"] / \
                state_info["reps"]

        max_index, _ = max(
            enumerate(self.state_info_list), key=extract_priority_tuple)

        # print(f"{frame=} {max_index=} {max_value=}")

        self.state_info_list[max_index]["max_pri"] = True

        self.update_plt1(frame)
        self.update_plt2()
        self.update_plt3()

        bars: List[Rectangle] = [artist for container in list(
            self.plt_bars_dict.values()) for artist in container]
        txts: List[Text] = list(self.txt_dict.values())

        return [*bars, *txts, self.mean_line]

    def update_plt1(self, frame: int) -> None:
        """Insert the new data on the plot.

        Re-plot all of the bars, move the mean line, and set the text of
        everything on plot 1 with newly calculated data.

        Parameters
        ----------
        frame : `int`
            The current frame number

        """
        pop_per_rep_list = extract_pop_per_rep(self.state_info_list)

        mean_pop_per_seat: float = np.mean(pop_per_rep_list)
        std_dev_pop_per_seat: float = np.std(pop_per_rep_list)
        range_pop_per_seat: float = max(
            pop_per_rep_list) - min(pop_per_rep_list)
        geo_mean_pop_per_seat: float = geometric_mean(pop_per_rep_list)

        max_state: str = max(
            self.state_info_list, key=operator.itemgetter("priority"))["name"]

        self.txt_dict["seat_txt"].set_text(
            f"Seat# {frame + 1}")
        self.txt_dict["state_txt"].set_text(
            f"State: {max_state}")
        self.txt_dict["mean_txt"].set_text(
            f"Mean: {mean_pop_per_seat:,.2f}")
        self.txt_dict["std_dev_txt"].set_text(
            f"Std. Dev. {std_dev_pop_per_seat:,.2f}")
        self.txt_dict["range_txt"].set_text(
            f"Range: {range_pop_per_seat:,.2f}")
        self.txt_dict["geo_mean_txt"].set_text(
            f"Geo. Mean: {geo_mean_pop_per_seat:,.2f}")

        self.mean_line.set_xdata([0, 1.0])
        self.mean_line.set_ydata([mean_pop_per_seat])

        for state, state_info in zip(
                self.plt_bars_dict["plt_1_bars"], self.state_info_list):
            state.set_height(state_info["pop_per_rep"])

    def update_plt2(self) -> None:
        """Insert the new data on the plot.

        Parameters
        ----------
        plt_2_bars : `BarContainer`
            The objects describing the plotted bars
        state_info_list : `List[StateInfo]`
            Continually updated list of state calculation info

        """
        for state, state_info in zip(
                self.plt_bars_dict["plt_2_bars"], self.state_info_list):
            state.set_height(state_info["reps"])

    def update_plt3(self) -> None:
        """Insert the new data on the plot.

        Parameters
        ----------
        plt_3_bars : `BarContainer`
            The objects describing the plotted bars
        state_info_list : `List[StateInfo]`
            Continually updated list of state calculation info

        """
        for state, state_info in zip(
                self.plt_bars_dict["plt_3_bars"], self.state_info_list):
            state.set_color("g")
            if state_info["max_pri"]:
                state.set_color("r")
            state.set_height(state_info["priority"])

    def format_plot_1(self) -> PlotProps:
        """Adjust all properties of plot 1 to make it look nice.

        Add the x & y ticks, format those ticks, set the title, draw the mean
        line, and place the text on the plot for the pop_per_rep plot.

        Parameters
        ----------
        plt_1 : `Axes`
            The object that describes the graph
        x_vals : `List[int]`
            The list of ints that shows the states' positions
        state_info_list : `List[StateInfo]`
            Continually updated list of state calculation info

        Returns
        -------
        `PlotProps`
            A tuple of the plotted bars, text, and line objects

        """
        state_names = extract_state_names(self.state_info_list)
        pop_per_rep_list = extract_pop_per_rep(self.state_info_list)

        plt_1_bars: BarContainer = self.plt_1.bar(self.x_vals, pop_per_rep_list,
                                                  align="center")

        self.plt_1.set_xticks(self.x_vals)
        self.plt_1.set_xticklabels(state_names, rotation="vertical")

        y_formatter = FuncFormatter(comma_format_int())

        self.plt_1.set_ylabel("People/Representative")
        self.plt_1.set_yscale("log")
        self.plt_1.get_yaxis().set_major_formatter(y_formatter)

        self.plt_1.set_title("People per representative per state")

        self.plt_1.grid(axis="y", which="major", lw=2)
        self.plt_1.grid(axis="y", which="minor", lw=0.75)
        self.plt_1.grid(axis="x", lw=0.75)

        mean_pop_per_seat: float = np.mean(pop_per_rep_list)
        std_dev_pop_per_seat: float = np.std(pop_per_rep_list)
        range_pop_per_seat: float = max(
            pop_per_rep_list) - min(pop_per_rep_list)
        geo_mean_pop_per_seat: float = geometric_mean(pop_per_rep_list)

        res_dict: PlotTextDict = {}

        res_dict["seat_txt"] = self.plt_1.text(
            0.25, 0.75, f"Seat# 1", transform=self.plt_1.transAxes)
        res_dict["state_txt"] = self.plt_1.text(
            0.15, 0.85, "State: ", transform=self.plt_1.transAxes)
        res_dict["mean_txt"] = self.plt_1.text(
            0.45, 0.75, f"Mean: {mean_pop_per_seat:,.2f}", transform=self.plt_1.transAxes)
        res_dict["std_dev_txt"] = self.plt_1.text(
            0.35, 0.85, f"Std. Dev. {std_dev_pop_per_seat:,.2f}", transform=self.plt_1.transAxes)
        res_dict["range_txt"] = self.plt_1.text(
            0.70, 0.75, f"Range: {range_pop_per_seat:,.2f}", transform=self.plt_1.transAxes)
        res_dict["geo_mean_txt"] = self.plt_1.text(
            0.6, 0.85, f"Geo. Mean: {geo_mean_pop_per_seat:,.2f}", transform=self.plt_1.transAxes)
        mean_line: Line2D = self.plt_1.axhline(y=mean_pop_per_seat,
                                               xmin=0.0, xmax=1.0, color="r")

        return (plt_1_bars, mean_line, res_dict)

    def format_plot_2(self) -> BarContainer:
        """Adjust all properties of plot 2 to make it look nice.

        Add the x & y ticks, format those ticks, set the title, and place the
        text on the plot for the number of reps plot.

        Returns
        -------
        `BarContainer`
            The objects describing the plotted bars

        """
        state_names = extract_state_names(self.state_info_list)
        reps_list = extract_reps(self.state_info_list)

        plt_2_bars: BarContainer = self.plt_2.bar(
            self.x_vals, reps_list, align="center", color="r")
        self.plt_2.set_xticks(self.x_vals)
        self.plt_2.set_xticklabels(state_names, rotation="vertical")

        y_axis = self.plt_2.get_yaxis()

        minor_loc = MultipleLocator(5)
        y_axis.set_minor_locator(minor_loc)

        self.plt_2.set_ylabel("Representatives")
        self.plt_2.set_ylim(top=60, bottom=0)

        self.plt_2.grid(axis="y", which="major", lw=2)
        self.plt_2.grid(axis="y", which="minor", lw=0.75)
        self.plt_2.grid(axis="x", lw=0.75)

        self.plt_2.set_title("Representatives per state")

        return plt_2_bars

    def format_plot_3(self) -> BarContainer:
        """Adjust all properties of plot 3 to make it look nice.

        Add the x & y ticks, format those ticks, set the title, and place the
        text on the plot for the priority num plot.

        Parameters
        ----------
        plt_3 : `Axes`
            The object that describes the graph
        x_vals : `List[int]`
            The list of ints that shows the states' position's
        state_info_list : `List[StateInfo]`
            Continually updated list of state calculation info

        Returns
        -------
        `BarContainer`
            The objects describing the plotted bars

        """
        state_names = extract_state_names(self.state_info_list)
        priority_list = extract_priority(self.state_info_list)

        plt_3_bars: BarContainer = self.plt_3.bar(self.x_vals, priority_list,
                                                  align="center", color="g")
        self.plt_3.set_xticks(self.x_vals)
        self.plt_3.set_xticklabels(state_names, rotation="vertical")

        y_formatter: FuncFormatter = FuncFormatter(comma_format_int())

        self.plt_3.set_ylabel("Priority value")
        self.plt_3.set_yscale("log")
        self.plt_3.get_yaxis().set_major_formatter(y_formatter)
        self.plt_3.text(0.3, 0.9, "Highlighted, is the state with the highest priority value",
                        transform=self.plt_3.transAxes)

        self.plt_3.grid(axis="y", which="major", lw=2)
        self.plt_3.grid(axis="y", which="minor", lw=0.75)
        self.plt_3.grid(axis="x", lw=0.75)

        self.plt_3.set_title("Priority values per state")

        return plt_3_bars

    def format_plot_4(self) -> None:
        """Adjust all properties of plot 4 to make it look nice.

        Add the x & y ticks, format those ticks, set the title, and place the
        text on the plot for the empty text plot.

        """
        self.plt_4.text(0.5, 0.5, "CGP Grey Electoral College Spreadsheet graphed.",
                        transform=self.plt_4.transAxes, fontsize=20, horizontalalignment="center")
        self.plt_4.axis("off")
