# Electoral College Apportionment PyQt

A PyQt representation of CGP Grey's Electoral College spreadsheet. This animates
the number of representatives, people to representative ratio, and priority
number calculations.

See [Running](#running) for instructions on how to get started

## Usage

```bash
usage: python3.8 run.py [-h]

Show an animation of the Huntington–Hill apportionment method

optional arguments:
  -h, --help  show this help message and exit
```

## Example

Coming soon!

## Running


```bash
python3.8 ./run.py
```

-   Press "Select Data" and choose the CSV file of your choice. (available: [`data/state-populations.csv`](https://github.com/k-donn/ec-apportionment/blob/master/data/state-populations.csv))

## Meta

From this [video](https://www.youtube.com/watch?v=6JN4RI7nkes).

Update/Change the state population data by putting your own data into [`data/state-populations.csv`](https://github.com/k-donn/ec-apportionment/blob/master/data/state-populations.csv).

The CSV file should have a header.

## TODO

-   [ ] Use QTimer instead of FuncAnimation
