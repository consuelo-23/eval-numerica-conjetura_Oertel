from pathlib import Path
import ast
import numpy as np
import pandas as pd

from get_cpoints import random_vertices_by_fiber
from get_cpoints import obtener_candidatos

csv_path = Path(r"C:\Users\consu\OneDrive\UOH\papers_please\TU_ARCHIVO.csv")
out_path = csv_path.with_name("csv_con_cpoints.csv")

df = pd.read_csv(csv_path)

def parse_point(s):
    return np.array(ast.literal_eval(s), dtype=float)

def t_entre_v1_va(cp, v1, va):
    direccion = va - v1
    denom = np.dot(direccion, direccion)
    if denom == 0:
        return np.nan
    return np.dot(cp - v1, direccion) / denom

rows = []

for _, row in df.iterrows():
    seed = int(row["seed"])
    n_per_z = int(row["n_per_z"])
    n_muestras = int(row["n_muestras"])

    np.random.seed(seed)

    vertices = random_vertices_by_fiber(
        z_vals=[0, 1, 2],
        d=2,
        n_per_z=n_per_z,
    )

    candidatos, ordenados = obtener_candidatos(
        vertices,
        n_muestras=n_muestras,
    )

    v0 = np.asarray(candidatos[0], dtype=float)
    v1 = np.asarray(candidatos[1], dtype=float)
    v2 = np.asarray(candidatos[2], dtype=float)
    va = np.asarray(candidatos[3], dtype=float)

    cp = parse_point(row["best_cp"])
    cara_cp = int(round(cp[0]))

    if cara_cp == 1:
        t = t_entre_v1_va(cp, v1, va)
    else:
        t = np.nan

    rows.append({
        "v0": v0.tolist(),
        "v1": v1.tolist(),
        "v2": v2.tolist(),
        "va": va.tolist(),
        "cp_z": cp[0],
        "cp_x": cp[1],
        "cp_y": cp[2],
        "cara_cp": cara_cp,
        "t_v1_va": t,
    })

extra = pd.DataFrame(rows)
df2 = pd.concat([df, extra], axis=1)

df2.to_csv(out_path, index=False)
print("Guardado en:", out_path)