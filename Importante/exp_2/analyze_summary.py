import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create descriptive tables from an exp_2 summary CSV."
    )
    parser.add_argument("--summary", type=Path, default=Path("summary.csv"))
    parser.add_argument("--output", type=Path, default=Path("analysis_exp_2.xlsx"))
    return parser.parse_args()


def main():
    args = parse_args()
    df = pd.read_csv(args.summary)

    numeric_cols = [
        "best_f",
        "margin_bound_n1",
        "ratio_bound_n1",
        "best_t",
        "t_v1_va",
        "total_area",
        "f_v0",
        "f_v1",
        "f_v2",
        "f_va",
    ]
    numeric_cols = [col for col in numeric_cols if col in df.columns]

    general = df[numeric_cols].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
    by_face = df.groupby("cara_cp")["best_f"].describe()
    by_type = df.groupby("best_candidate_type")["best_f"].describe()
    beats_by_face = df.groupby("cara_cp")["beats_bound_n1"].mean()
    counts_face = df["cara_cp"].value_counts(dropna=False).sort_index()
    counts_type = df["best_candidate_type"].value_counts(dropna=False)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(args.output) as writer:
        df.to_excel(writer, sheet_name="data", index=False)
        general.to_excel(writer, sheet_name="general")
        by_face.to_excel(writer, sheet_name="best_f_by_face")
        by_type.to_excel(writer, sheet_name="best_f_by_type")
        beats_by_face.to_excel(writer, sheet_name="beats_by_face")
        counts_face.to_excel(writer, sheet_name="counts_face")
        counts_type.to_excel(writer, sheet_name="counts_type")

    print(f"Analysis saved to {args.output}")


if __name__ == "__main__":
    main()

