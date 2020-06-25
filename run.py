"""
Show an animation of the Huntington–Hill apportionment method.

usage: python3.8 run.py [-h] -f FILE [-d]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to CSV state population data

"""

import sys
from argparse import ArgumentParser

from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QMessageBox,
                             QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from source import bar_chart

if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser(
        prog="python3.8 run.py",
        description="Show an animation of the Huntington–Hill apportionment method")
    parser.add_argument("-f", "--file", required=True,
                        help="Path to CSV state population data")

    args = parser.parse_args()

    app = QApplication(sys.argv)

    # bar_chart.main(args.file, args.debug)
    ex = bar_chart.App(args.file)
    sys.exit(app.exec_())
