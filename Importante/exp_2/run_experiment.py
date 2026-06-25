import argparse
import json
from pathlib import Path

import numpy as np

from get_cpoints import obtener_candidatos
from get_cpoints import random_vertices_by_fiber
from new_oertel import area_total
from new_oertel import new_oertel_exp2


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run one exp_2 Oertel experiment with candidate diagnostics."
    )
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--n-per-z", type=int, default=5)
    parser.add_argument("--nz", type=int, default=100, help="Alpha angular grid.")
    parser.add_argument("--nd", type=int, default=100, help="Beta angular grid.")
    parser.add_argument(
        "--n-muestras",
        type=int,
        default=50,
        help="Samples on the segment from v1 to va.",
    )
    parser.add_argument("--outdir", type=Path, default=Path("results"))
    return parser.parse_args()


def as_list(x):
    if x is None:
        return None
    return np.asarray(x, dtype=float).tolist()


def candidate_type(index):
    if index == 0:
        return "v0"
    if index == 1:
        return "v1"
    if index == 2:
        return "v2"
    if index == 3:
        return "va"
    if index is None:
        return None
    return "linea_v1_va"


def candidate_t(index, n_muestras):
    if index == 1:
        return 0.0
    if index == 3:
        return 1.0
    if index is not None and index >= 4:
        return float((index - 3) / n_muestras)
    return None


def t_entre_v1_va(cp, v1, va):
    direction = va - v1
    denom = float(np.dot(direction, direction))
    if denom == 0:
        return None
    return float(np.dot(cp - v1, direction) / denom)


def main():
    args = parse_args()
    old_rng_state = np.random.get_state()
    np.random.seed(args.seed)

    z_vals = [0, 1, 2]
    vertices = random_vertices_by_fiber(z_vals, 2, args.n_per_z)
    candidatos, ordenados_por_slice = obtener_candidatos(
        vertices,
        n_muestras=args.n_muestras,
        z_vals=z_vals,
    )
    ordenados = np.vstack(ordenados_por_slice)

    result_oertel = new_oertel_exp2(
        ordenados,
        candidatos,
        z_vals=z_vals,
        nz=args.nz,
        nd=args.nd,
    )

    best_cp = result_oertel["best_cp"]
    best_u = result_oertel["best_u"]
    best_f = result_oertel["best_f"]
    best_index = result_oertel["best_candidate_index"]

    v0 = np.asarray(candidatos[0], dtype=float)
    v1 = np.asarray(candidatos[1], dtype=float)
    v2 = np.asarray(candidatos[2], dtype=float)
    va = np.asarray(candidatos[3], dtype=float) if len(candidatos) > 3 else None

    cara_cp = int(round(float(best_cp[0]))) if best_cp is not None else None
    t_v1_va = (
        t_entre_v1_va(best_cp, v1, va)
        if best_cp is not None and va is not None and cara_cp == 1
        else None
    )

    # For n=1 in the current experiments, Oertel's conjectured threshold is 1/(2e).
    oertel_bound_n1 = float(1 / (2 * np.e))

    args.outdir.mkdir(parents=True, exist_ok=True)
    stem = (
        f"oertel_seed-{args.seed}_nperz-{args.n_per_z}"
        f"_nz-{args.nz}_nd-{args.nd}_nmuestras-{args.n_muestras}"
    )

    candidate_fs = result_oertel["candidate_fs"]
    result = {
        "seed": args.seed,
        "n_per_z": args.n_per_z,
        "nz": args.nz,
        "nd": args.nd,
        "n_muestras": args.n_muestras,
        "n_candidatos": len(candidatos),
        "total_area": float(area_total(ordenados, z_vals)),
        "best_f": best_f,
        "best_cp": as_list(best_cp),
        "best_u": as_list(best_u),
        "best_candidate_index": best_index,
        "best_candidate_type": candidate_type(best_index),
        "best_t": candidate_t(best_index, args.n_muestras),
        "cara_cp": cara_cp,
        "t_v1_va": t_v1_va,
        "v0": as_list(v0),
        "v1": as_list(v1),
        "v2": as_list(v2),
        "va": as_list(va),
        "f_v0": float(candidate_fs[0]) if len(candidate_fs) > 0 else None,
        "f_v1": float(candidate_fs[1]) if len(candidate_fs) > 1 else None,
        "f_v2": float(candidate_fs[2]) if len(candidate_fs) > 2 else None,
        "f_va": float(candidate_fs[3]) if len(candidate_fs) > 3 else None,
        "oertel_bound_n1": oertel_bound_n1,
        "margin_bound_n1": float(best_f - oertel_bound_n1),
        "ratio_bound_n1": float(best_f / oertel_bound_n1),
        "beats_bound_n1": bool(best_f >= oertel_bound_n1),
    }

    with (args.outdir / f"{stem}.json").open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    np.savez_compressed(
        args.outdir / f"{stem}.npz",
        vertices=vertices,
        ordenados=ordenados,
        candidatos=np.asarray(candidatos, dtype=float),
        candidate_fs=candidate_fs,
        best_cp=best_cp,
        best_f=best_f,
        best_u=best_u,
        v0=v0,
        v1=v1,
        v2=v2,
        va=va,
    )

    np.random.set_state(old_rng_state)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

