from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build KPI reports from synthetic retail data.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/synthetic"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--report-date", help="ISO date such as 2026-08-25; defaults to the latest input date")
    parser.add_argument("--use-llm", action="store_true", help="Use the optional API-backed summary")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    paths = run_pipeline(args.data_dir, args.output_dir, args.report_date, args.use_llm)
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()

