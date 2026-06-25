import argparse
import csv
import json
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Agrupa resultados JSON de experimentos Oertel en un CSV."
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
        raise SystemExit(f"No se encontraron JSON en {args.results_dir}")

    fieldnames = [
        "file",
        "seed",
        "n_per_z",
        "nz",
        "nd",
        "n_muestras",
        "n_candidatos",
        "best_f",
        "best_cp",
        "best_u",
	"best_index",
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Resumen guardado en {args.output} con {len(rows)} filas.")


if __name__ == "__main__":
    main()
