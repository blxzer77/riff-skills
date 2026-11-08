import argparse
import json
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mkt")
    parser.add_argument("command", choices=["export", "import"])
    parser.add_argument("--format", default="json", choices=["json", "csv"])
    args = parser.parse_args(argv)
    if args.command == "export":
        json.dump({"orders": []}, sys.stdout)
    return 0
