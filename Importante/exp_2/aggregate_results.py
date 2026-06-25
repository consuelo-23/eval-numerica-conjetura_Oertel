import argparse
import csv
import json
from pathlib import Path


FIELDNAMES = [
    "file",
    "seed",
    "n_per_z",
    "nz",
    "nd",
    "n_muestras",
    "n_candidatos",
    "total_area",
    "best_f",
    "best_cp",
    "best_u",
    "best_candidate_index",
    "best_candidate_type",
    "best_t",
    "cara_cp",
    "t_v1_va",
    "v0",
    "v1",
    "v2",
    "va",
    "f_v0",
    "f_v1",
    "f_v2",
    "f_va",
    "oertel_bound_n1",
    "margin_bound_n1",
    "ratio_bound_n1",
    "beats_bound_n1",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Aggregate exp_2 Oertel JSON results into a CSV."
    )
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path, default=Path("summary.csv"))
    return parser.parse_args()


def main():
    args = parse_args()
    rows = []

    for path in sorted(args.results_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            row = json.load(f)
        row["file"] = path.name
        rows.append(row)

    if not rows:
        raise SystemExit(f"No JSON files found in {args.results_dir}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Summary saved to {args.output} with {len(rows)} rows.")


if __name__ == "__main__":
    main()

