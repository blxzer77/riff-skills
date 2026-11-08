import csv
import sys


def summarize(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"{len(rows)} rows")
    if rows:
        print("columns: " + ", ".join(rows[0].keys()))


if __name__ == "__main__":
    summarize(sys.argv[1])
