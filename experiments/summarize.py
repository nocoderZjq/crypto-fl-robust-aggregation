from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.plotting import generate_figures, generate_tables


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="outputs/csv/results.csv")
    args = parser.parse_args()
    generate_figures(args.results)
    generate_tables(args.results)
    print("Figures written to outputs/figures and tables written to outputs/tables")


if __name__ == "__main__":
    main()
