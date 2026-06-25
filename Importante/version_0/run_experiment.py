import argparse
import json
from pathlib import Path

import numpy as np

from get_cpoints import obtener_candidatos
from get_cpoints import random_vertices_by_fiber
from new_oertel import new_oertel


def parse_args():
    parser = argparse.ArgumentParser(
        description="Corre un experimento para estimar el radio de Oertel."
    )
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--n-per-z", type=int, default=5)
    parser.add_argument("--nz", type=int, default=100, help="Malla angular alpha.")
    parser.add_argument("--nd", type=int, default=100, help="Malla angular beta.")
    parser.add_argument(
        "--n-muestras",
        type=int,
        default=50,
        help="Muestras entre el candidato de z=1 y va.",
    )
    parser.add_argument("--outdir", type=Path, default=Path("results"))
    return parser.parse_args()


def main():
    args = parse_args()
    rng_state = np.random.get_state()
    np.random.seed(args.seed)

    z_vals = [0, 1, 2]
    vertices = random_vertices_by_fiber(z_vals, 2, args.n_per_z)
    candidatos, ordenados = obtener_candidatos(vertices, n_muestras=args.n_muestras)
    ordenados = np.vstack(ordenados)

    oertel_results = new_oertel(
        ordenados,
        candidatos,
        z_vals=z_vals,
        Nz=args.nz,
        Nd=args.nd,
        N_Muestras=args.n_muestras,
    )

    best_cp = oertel_results["best_cp"]
    best_f = oertel_results["best_f"]
    best_u = oertel_results["best_u"]
    best_index = oertel_results["best_candidate_index"]


    args.outdir.mkdir(parents=True, exist_ok=True)
    stem = (
        f"oertel_seed-{args.seed}_nperz-{args.n_per_z}"
        f"_nz-{args.nz}_nd-{args.nd}_nmuestras-{args.n_muestras}"
    )

    result = {
        "seed": args.seed,
        "n_per_z": args.n_per_z,
        "nz": args.nz,
        "nd": args.nd,
        "n_muestras": args.n_muestras,
        "best_f": best_f,
        "best_cp": best_cp.tolist() if best_cp is not None else None,
        "best_u": best_u.tolist() if best_u is not None else None,
	    "best_index": best_index,
        "n_candidatos": len(candidatos),
    }

    with (args.outdir / f"{stem}.json").open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    np.savez_compressed(
        args.outdir / f"{stem}.npz",
        vertices=vertices,
        ordenados=ordenados,
        candidatos=np.asarray(candidatos, dtype=float),
        best_cp=best_cp,
        best_f=best_f,
        best_u=best_u,
    )

    np.random.set_state(rng_state)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
