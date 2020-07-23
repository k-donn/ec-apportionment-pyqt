"""
Show an animation of the Huntington–Hill apportionment method.

usage: python3.8 run.py [-h]

optional arguments:
  -h, --help  show this help message and exit

"""

import sys
from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication

from source import bar_chart

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="python3.8 run.py",
        description="Show an animation of the Huntington–Hill apportionment method")

    args = parser.parse_args()

    app = QApplication(sys.argv)

    ex = bar_chart.App()
    sys.exit(app.exec_())
