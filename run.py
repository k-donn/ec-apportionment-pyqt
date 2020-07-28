"""
Show an animation of the Huntington–Hill apportionment method.

usage: python3.8 run.py [-h]

optional arguments:
  -h, --help  show this help message and exit
"""

import sys

from PyQt5.QtWidgets import QApplication

from source import bar_chart

if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        exit()

    app = QApplication(sys.argv)

    ex = bar_chart.App()

    exit(app.exec_())
